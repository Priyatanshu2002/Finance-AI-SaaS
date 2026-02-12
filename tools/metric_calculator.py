"""
Metric Calculator — Stage 7 of Extraction Pipeline
Calculates financial ratios and metrics from normalized statements.

All logic is DETERMINISTIC — no LLM involved.
"""

from typing import Optional

import structlog

logger = structlog.get_logger()


def safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    """Safely divide two numbers, returning None if either is None or denominator is zero."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def safe_subtract(a: Optional[float], b: Optional[float]) -> Optional[float]:
    """Safely subtract, returning None if either is None."""
    if a is None or b is None:
        return None
    return a - b


def calculate_metrics(
    statements: dict[str, dict[str, Optional[float]]],
    periods: list[str],
) -> dict[str, dict[str, Optional[float]]]:
    """
    Calculate financial metrics from normalized statements.

    Args:
        statements: Dict mapping standardized_label → {period: value}
        periods: List of period names.

    Returns:
        Dict mapping metric_name → {period: value}

    Metrics calculated:
        Profitability: gross_margin, ebitda_margin, operating_margin, net_margin, roe, roa
        Liquidity: current_ratio, quick_ratio
        Leverage: debt_to_equity, debt_to_assets, interest_coverage
        Growth: revenue_growth, net_income_growth
    """
    metrics: dict[str, dict[str, Optional[float]]] = {}

    for period in periods:
        # Helper to get a value for this period
        def get(label: str) -> Optional[float]:
            return statements.get(label, {}).get(period)

        # ─── Profitability Ratios ─────────────────────────────────────

        # Gross Margin = Gross Profit / Revenue
        metrics.setdefault("gross_margin", {})[period] = safe_divide(
            get("gross_profit"), get("total_revenue")
        )

        # EBITDA Margin = EBITDA / Revenue
        ebitda = get("ebitda")
        if ebitda is None:
            # Calculate EBITDA from components if available
            op_income = get("operating_income")
            da = get("depreciation_amortization")
            if op_income is not None and da is not None:
                ebitda = op_income + abs(da)
        metrics.setdefault("ebitda_margin", {})[period] = safe_divide(
            ebitda, get("total_revenue")
        )

        # Operating Margin = Operating Income / Revenue
        metrics.setdefault("operating_margin", {})[period] = safe_divide(
            get("operating_income"), get("total_revenue")
        )

        # Net Margin = Net Income / Revenue
        metrics.setdefault("net_margin", {})[period] = safe_divide(
            get("net_income"), get("total_revenue")
        )

        # ROE = Net Income / Total Equity
        metrics.setdefault("return_on_equity", {})[period] = safe_divide(
            get("net_income"), get("total_equity")
        )

        # ROA = Net Income / Total Assets
        metrics.setdefault("return_on_assets", {})[period] = safe_divide(
            get("net_income"), get("total_assets")
        )

        # ─── Liquidity Ratios ─────────────────────────────────────────

        # Current Ratio = Current Assets / Current Liabilities
        metrics.setdefault("current_ratio", {})[period] = safe_divide(
            get("total_current_assets"), get("total_current_liabilities")
        )

        # Quick Ratio = (Current Assets - Inventories) / Current Liabilities
        current_assets = get("total_current_assets")
        inventories = get("inventories") or 0
        if current_assets is not None:
            quick_assets = current_assets - inventories
            metrics.setdefault("quick_ratio", {})[period] = safe_divide(
                quick_assets, get("total_current_liabilities")
            )
        else:
            metrics.setdefault("quick_ratio", {})[period] = None

        # ─── Leverage Ratios ──────────────────────────────────────────

        # Debt-to-Equity = Total Liabilities / Total Equity
        metrics.setdefault("debt_to_equity", {})[period] = safe_divide(
            get("total_liabilities"), get("total_equity")
        )

        # Debt-to-Assets = Total Liabilities / Total Assets
        metrics.setdefault("debt_to_assets", {})[period] = safe_divide(
            get("total_liabilities"), get("total_assets")
        )

        # Interest Coverage = Operating Income / Interest Expense
        interest = get("interest_expense")
        if interest is not None:
            interest = abs(interest)  # Interest expense is sometimes negative
        metrics.setdefault("interest_coverage", {})[period] = safe_divide(
            get("operating_income"), interest
        )

    # ─── Growth Rates (require consecutive periods) ───────────────────

    for i in range(1, len(periods)):
        curr_period = periods[i]
        prev_period = periods[i - 1]

        # Revenue Growth
        curr_rev = statements.get("total_revenue", {}).get(curr_period)
        prev_rev = statements.get("total_revenue", {}).get(prev_period)
        metrics.setdefault("revenue_growth", {})[curr_period] = (
            safe_divide(safe_subtract(curr_rev, prev_rev), prev_rev)
        )

        # Net Income Growth
        curr_ni = statements.get("net_income", {}).get(curr_period)
        prev_ni = statements.get("net_income", {}).get(prev_period)
        metrics.setdefault("net_income_growth", {})[curr_period] = (
            safe_divide(safe_subtract(curr_ni, prev_ni), prev_ni)
        )

        # Operating Cash Flow Growth
        curr_ocf = statements.get("operating_cash_flow", {}).get(curr_period)
        prev_ocf = statements.get("operating_cash_flow", {}).get(prev_period)
        metrics.setdefault("operating_cf_growth", {})[curr_period] = (
            safe_divide(safe_subtract(curr_ocf, prev_ocf), prev_ocf)
        )

    # Round all metrics to 4 decimal places
    for metric_name in metrics:
        for period in metrics[metric_name]:
            val = metrics[metric_name][period]
            if val is not None:
                metrics[metric_name][period] = round(val, 4)

    logger.info(
        "Metric calculation complete",
        metrics_calculated=len(metrics),
        periods=periods,
    )

    return metrics


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test with sample data
    test_statements = {
        "total_revenue": {"FY2023": 1000000, "FY2024": 1200000},
        "cost_of_revenue": {"FY2023": 600000, "FY2024": 700000},
        "gross_profit": {"FY2023": 400000, "FY2024": 500000},
        "operating_income": {"FY2023": 170000, "FY2024": 230000},
        "depreciation_amortization": {"FY2023": 30000, "FY2024": 35000},
        "interest_expense": {"FY2023": 20000, "FY2024": 22000},
        "net_income": {"FY2023": 120000, "FY2024": 158000},
        "total_assets": {"FY2023": 500000, "FY2024": 600000},
        "total_current_assets": {"FY2023": 200000, "FY2024": 250000},
        "inventories": {"FY2023": 50000, "FY2024": 55000},
        "total_liabilities": {"FY2023": 250000, "FY2024": 280000},
        "total_current_liabilities": {"FY2023": 130000, "FY2024": 140000},
        "total_equity": {"FY2023": 250000, "FY2024": 320000},
    }

    metrics = calculate_metrics(test_statements, ["FY2023", "FY2024"])

    print(f"\n{'='*60}")
    print("Financial Metrics")
    print(f"{'='*60}")
    for name, values in metrics.items():
        print(f"\n{name}:")
        for period, value in values.items():
            if value is not None:
                if "growth" in name or "margin" in name or "return" in name:
                    print(f"  {period}: {value:.2%}")
                else:
                    print(f"  {period}: {value:.2f}")
            else:
                print(f"  {period}: N/A")
