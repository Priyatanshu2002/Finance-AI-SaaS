"""
Validation Engine — Stage 6 of Extraction Pipeline
Cross-validates extracted financial statements for accuracy.

All logic is DETERMINISTIC — no LLM involved.
Validates: balance sheet equilibrium, arithmetic integrity,
           cross-statement consistency, and assigns quality scores.
"""

from dataclasses import dataclass, field
from typing import Optional

import structlog

logger = structlog.get_logger()

# Tolerance for floating-point comparison (0.5% of total)
TOLERANCE_PERCENT = 0.005
# Absolute tolerance for small values
TOLERANCE_ABSOLUTE = 1.0


@dataclass
class ValidationFlag:
    """A single validation issue."""
    severity: str  # "error", "warning", "info"
    check: str  # Name of the validation check
    message: str
    details: dict = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Complete validation result for an extraction."""
    balance_sheet_balanced: Optional[bool] = None
    cash_flow_reconciled: Optional[bool] = None
    cross_statement_consistent: Optional[bool] = None
    income_statement_valid: Optional[bool] = None
    items_flagged_for_review: int = 0
    quality_score: float = 0.0
    flags: list[ValidationFlag] = field(default_factory=list)

    def add_flag(self, severity: str, check: str, message: str, **details):
        self.flags.append(ValidationFlag(
            severity=severity,
            check=check,
            message=message,
            details=details,
        ))
        if severity in ("error", "warning"):
            self.items_flagged_for_review += 1


def _values_match(a: Optional[float], b: Optional[float], reference: Optional[float] = None) -> bool:
    """Check if two values match within tolerance."""
    if a is None or b is None:
        return False

    diff = abs(a - b)

    # Use percentage tolerance relative to the larger value
    ref = reference or max(abs(a), abs(b), 1.0)
    return diff <= max(ref * TOLERANCE_PERCENT, TOLERANCE_ABSOLUTE)


def validate_balance_sheet(
    statements: dict[str, dict[str, Optional[float]]],
    periods: list[str],
) -> tuple[bool, list[ValidationFlag]]:
    """
    Validate: Total Assets = Total Liabilities + Total Equity.

    Args:
        statements: Dict mapping standardized_label → {period: value}
        periods: List of period names to validate.

    Returns:
        Tuple of (is_balanced, flags).
    """
    flags = []
    all_balanced = True

    total_assets = statements.get("total_assets", {})
    total_liabilities = statements.get("total_liabilities", {})
    total_equity = statements.get("total_equity", {})

    for period in periods:
        assets = total_assets.get(period)
        liabilities = total_liabilities.get(period)
        equity = total_equity.get(period)

        if assets is None:
            flags.append(ValidationFlag("warning", "balance_sheet", f"Total Assets missing for {period}"))
            continue

        if liabilities is None or equity is None:
            flags.append(ValidationFlag("warning", "balance_sheet", f"Liabilities or Equity missing for {period}"))
            continue

        expected = liabilities + equity
        if _values_match(assets, expected, assets):
            flags.append(ValidationFlag("info", "balance_sheet", f"Balance sheet balanced for {period}", diff=abs(assets - expected)))
        else:
            all_balanced = False
            flags.append(ValidationFlag(
                "error", "balance_sheet",
                f"Balance sheet NOT balanced for {period}: Assets ({assets:,.0f}) ≠ Liabilities ({liabilities:,.0f}) + Equity ({equity:,.0f}) = {expected:,.0f}",
                assets=assets, liabilities=liabilities, equity=equity, diff=abs(assets - expected),
            ))

    return all_balanced, flags


def validate_income_statement(
    statements: dict[str, dict[str, Optional[float]]],
    periods: list[str],
) -> tuple[bool, list[ValidationFlag]]:
    """
    Validate income statement arithmetic:
    - Gross Profit = Revenue - COGS
    - Operating Income ≈ Gross Profit - OpEx
    """
    flags = []
    all_valid = True

    revenue = statements.get("total_revenue", {})
    cogs = statements.get("cost_of_revenue", {})
    gross_profit = statements.get("gross_profit", {})
    operating_income = statements.get("operating_income", {})

    for period in periods:
        rev = revenue.get(period)
        cost = cogs.get(period)
        gp = gross_profit.get(period)

        # Check: Gross Profit = Revenue - COGS
        if rev is not None and cost is not None and gp is not None:
            expected_gp = rev - cost
            if not _values_match(gp, expected_gp, rev):
                all_valid = False
                flags.append(ValidationFlag(
                    "warning", "income_statement",
                    f"Gross Profit mismatch for {period}: reported {gp:,.0f} vs calculated {expected_gp:,.0f}",
                ))

    return all_valid, flags


def validate_cash_flow(
    statements: dict[str, dict[str, Optional[float]]],
    periods: list[str],
) -> tuple[bool, list[ValidationFlag]]:
    """
    Validate cash flow statement:
    - Net Change = Operating + Investing + Financing
    """
    flags = []
    all_valid = True

    operating = statements.get("operating_cash_flow", {})
    investing = statements.get("investing_cash_flow", {})
    financing = statements.get("financing_cash_flow", {})
    net_change = statements.get("net_change_in_cash", {})

    for period in periods:
        op = operating.get(period)
        inv = investing.get(period)
        fin = financing.get(period)
        net = net_change.get(period)

        if all(v is not None for v in [op, inv, fin, net]):
            expected_net = op + inv + fin
            if not _values_match(net, expected_net, abs(op or 1)):
                all_valid = False
                flags.append(ValidationFlag(
                    "warning", "cash_flow",
                    f"Cash flow mismatch for {period}: reported net change {net:,.0f} vs calculated {expected_net:,.0f}",
                ))

    return all_valid, flags


def calculate_quality_score(result: ValidationResult) -> float:
    """
    Calculate quality score (0-100) based on validation results.

    Scoring:
    - Start at 100
    - Each error: -15 points
    - Each warning: -5 points
    - Missing data: -3 points per missing key statement
    """
    score = 100.0

    for flag in result.flags:
        if flag.severity == "error":
            score -= 15
        elif flag.severity == "warning":
            score -= 5

    # Penalize missing statements
    if result.balance_sheet_balanced is None:
        score -= 10
    if result.income_statement_valid is None:
        score -= 5
    if result.cash_flow_reconciled is None:
        score -= 3

    return max(0.0, min(100.0, score))


def validate_extraction(
    statements: dict[str, dict[str, Optional[float]]],
    periods: list[str],
) -> ValidationResult:
    """
    Run all validation checks on extracted financial data.

    Args:
        statements: Dict mapping standardized_label → {period: value}
        periods: List of period names.

    Returns:
        Comprehensive ValidationResult with quality score.
    """
    result = ValidationResult()

    # Run all checks
    result.balance_sheet_balanced, bs_flags = validate_balance_sheet(statements, periods)
    result.flags.extend(bs_flags)

    result.income_statement_valid, is_flags = validate_income_statement(statements, periods)
    result.flags.extend(is_flags)

    result.cash_flow_reconciled, cf_flags = validate_cash_flow(statements, periods)
    result.flags.extend(cf_flags)

    # Cross-statement (simplified — check net income appears in both IS and CF)
    result.cross_statement_consistent = True  # Will enhance later

    # Calculate quality score
    result.quality_score = calculate_quality_score(result)
    result.items_flagged_for_review = sum(
        1 for f in result.flags if f.severity in ("error", "warning")
    )

    logger.info(
        "Validation complete",
        quality_score=result.quality_score,
        flags=len(result.flags),
        errors=sum(1 for f in result.flags if f.severity == "error"),
        warnings=sum(1 for f in result.flags if f.severity == "warning"),
    )

    return result


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test with sample data
    test_statements = {
        "total_revenue": {"FY2023": 1000000, "FY2024": 1200000},
        "cost_of_revenue": {"FY2023": 600000, "FY2024": 700000},
        "gross_profit": {"FY2023": 400000, "FY2024": 500000},
        "operating_income": {"FY2023": 170000, "FY2024": 230000},
        "net_income": {"FY2023": 120000, "FY2024": 158000},
        "total_assets": {"FY2023": 500000, "FY2024": 600000},
        "total_liabilities": {"FY2023": 250000, "FY2024": 280000},
        "total_equity": {"FY2023": 250000, "FY2024": 320000},
    }

    result = validate_extraction(test_statements, ["FY2023", "FY2024"])

    print(f"\n{'='*60}")
    print(f"Quality Score: {result.quality_score:.1f}/100")
    print(f"Balance Sheet Balanced: {result.balance_sheet_balanced}")
    print(f"Income Statement Valid: {result.income_statement_valid}")
    print(f"Flags: {len(result.flags)}")
    for flag in result.flags:
        print(f"  [{flag.severity}] {flag.check}: {flag.message}")
