"""
Financial Spreader — Stage 5 of Extraction Pipeline
Maps extracted labels to standardized taxonomy and normalizes statements.

This tool is DETERMINISTIC — no LLM involved.
Handles label mapping, period alignment, and statement separation.

Label taxonomy derived from:
    - FASB US GAAP XBRL Taxonomy (6,000+ concepts)
    - IFRS Taxonomy equivalents
    - Common financial statement label variants (10-K, annual reports, private companies)
"""

import re
from dataclasses import dataclass, field
from typing import Optional

import structlog

logger = structlog.get_logger()


# ─── XBRL US GAAP Taxonomy — Standardized Label Mappings ─────────────────────
#
# Each dict maps {normalized_label: standardized_key}.
# Sources:
#   - FASB XBRL Taxonomy: https://fasb.org/xbrl
#   - SEC EDGAR XBRL filings (common label variations)
#   - IFRS taxonomy equivalents for international companies
#
# Format: lowercase, stripped, single-spaced variations → canonical key

INCOME_STATEMENT_MAPPINGS: dict[str, str] = {
    # ── Revenue ───────────────────────────────────────────────────────
    "revenue": "total_revenue",
    "revenues": "total_revenue",
    "net revenue": "total_revenue",
    "net revenues": "total_revenue",
    "net sales": "total_revenue",
    "total revenue": "total_revenue",
    "total revenues": "total_revenue",
    "total net revenue": "total_revenue",
    "total net revenues": "total_revenue",
    "sales": "total_revenue",
    "turnover": "total_revenue",
    "revenue net": "total_revenue",
    "sales revenue net": "total_revenue",  # XBRL: SalesRevenueNet
    "revenue from contract with customer excluding assessed tax": "total_revenue",  # XBRL: ASC 606
    "revenue from contract with customer": "total_revenue",
    "product revenue": "product_revenue",
    "product sales": "product_revenue",
    "products net revenues": "product_revenue",
    "service revenue": "service_revenue",
    "services net revenues": "service_revenue",
    "service sales": "service_revenue",
    "subscription revenue": "subscription_revenue",
    "interest and dividend income": "interest_and_dividend_income",
    "noninterest revenue": "noninterest_revenue",
    "fee income": "fee_income",
    "commission income": "commission_income",
    "other revenue": "other_revenue",
    "other income": "other_income",

    # ── Cost of Revenue / COGS ────────────────────────────────────────
    "cost of revenue": "cost_of_revenue",
    "cost of revenues": "cost_of_revenue",
    "cost of goods sold": "cost_of_revenue",
    "cost of sales": "cost_of_revenue",
    "cogs": "cost_of_revenue",
    "cost of products sold": "cost_of_revenue",
    "cost of services": "cost_of_services",
    "cost of goods and services sold": "cost_of_revenue",
    "cost of product revenue": "cost_of_revenue",
    "cost of service revenue": "cost_of_services",

    # ── Gross Profit ──────────────────────────────────────────────────
    "gross profit": "gross_profit",
    "gross margin": "gross_profit",
    "gross income": "gross_profit",
    "gross profit (loss)": "gross_profit",

    # ── Operating Expenses ────────────────────────────────────────────
    "operating expenses": "total_operating_expenses",
    "total operating expenses": "total_operating_expenses",
    "operating costs and expenses": "total_operating_expenses",
    "costs and expenses": "total_operating_expenses",
    "total costs and expenses": "total_operating_expenses",
    # SG&A
    "selling general and administrative": "sga_expense",
    "selling general and administrative expenses": "sga_expense",
    "selling general & administrative": "sga_expense",
    "sg&a": "sga_expense",
    "sga": "sga_expense",
    "general and administrative": "general_and_admin",
    "general and administrative expenses": "general_and_admin",
    "general & administrative": "general_and_admin",
    "g&a": "general_and_admin",
    "selling and marketing": "selling_expense",
    "selling expenses": "selling_expense",
    "sales and marketing": "selling_expense",
    "marketing expense": "selling_expense",
    # R&D
    "research and development": "rd_expense",
    "research and development expenses": "rd_expense",
    "research & development": "rd_expense",
    "r&d": "rd_expense",
    "r&d expense": "rd_expense",
    "technology and development": "rd_expense",
    # D&A
    "depreciation and amortization": "depreciation_amortization",
    "depreciation & amortization": "depreciation_amortization",
    "depreciation amortization and accretion": "depreciation_amortization",
    "d&a": "depreciation_amortization",
    "depreciation": "depreciation",
    "depreciation expense": "depreciation",
    "amortization": "amortization",
    "amortization of intangible assets": "amortization_intangibles",
    "amortization of intangibles": "amortization_intangibles",
    # Stock-based compensation (XBRL: ShareBasedCompensation)
    "stock-based compensation": "stock_based_compensation",
    "stock based compensation": "stock_based_compensation",
    "share-based compensation": "stock_based_compensation",
    "share based compensation expense": "stock_based_compensation",
    "equity-based compensation": "stock_based_compensation",
    # Restructuring
    "restructuring charges": "restructuring_charges",
    "restructuring and related charges": "restructuring_charges",
    "restructuring costs": "restructuring_charges",
    "impairment charges": "impairment_charges",
    "impairment of goodwill": "goodwill_impairment",
    "goodwill impairment": "goodwill_impairment",
    "asset impairment charges": "impairment_charges",
    # Other operating
    "other operating expenses": "other_operating_expense",
    "other operating income": "other_operating_income",
    "other operating income (expense)": "other_operating_income",

    # ── Operating Income ──────────────────────────────────────────────
    "operating income": "operating_income",
    "operating income (loss)": "operating_income",
    "income from operations": "operating_income",
    "income (loss) from operations": "operating_income",
    "operating profit": "operating_income",
    "operating profit (loss)": "operating_income",
    "ebit": "operating_income",

    # ── Non-Operating Items ───────────────────────────────────────────
    "interest expense": "interest_expense",
    "interest expense net": "net_interest_expense",
    "interest income": "interest_income",
    "net interest expense": "net_interest_expense",
    "net interest income": "net_interest_income",
    "interest and other income": "interest_and_other_income",
    "interest and other expense": "interest_and_other_expense",
    "other non-operating income": "other_nonoperating_income",
    "other non-operating expense": "other_nonoperating_expense",
    "other income (expense) net": "other_income_expense_net",
    "other income expense net": "other_income_expense_net",
    "gain on sale of assets": "gain_on_asset_sale",
    "gain (loss) on sale of assets": "gain_on_asset_sale",
    "gain on investments": "gain_on_investments",
    "loss on extinguishment of debt": "loss_on_debt_extinguishment",
    "foreign currency gain (loss)": "foreign_currency_gain_loss",
    "equity method investment income": "equity_method_income",
    "income from equity method investments": "equity_method_income",

    # ── Pre-Tax / Tax ─────────────────────────────────────────────────
    "income before taxes": "income_before_tax",
    "income (loss) before taxes": "income_before_tax",
    "income before income taxes": "income_before_tax",
    "income (loss) before income taxes": "income_before_tax",
    "pre-tax income": "income_before_tax",
    "earnings before income taxes": "income_before_tax",
    "pretax income": "income_before_tax",
    "provision for income taxes": "income_tax_expense",
    "income tax expense": "income_tax_expense",
    "income tax expense (benefit)": "income_tax_expense",
    "income taxes": "income_tax_expense",
    "tax provision": "income_tax_expense",

    # ── Net Income ────────────────────────────────────────────────────
    "net income": "net_income",
    "net income (loss)": "net_income",
    "net earnings": "net_income",
    "net profit": "net_income",
    "net loss": "net_income",
    "net income attributable to": "net_income",
    "net income attributable to common stockholders": "net_income",
    "net income attributable to common shareholders": "net_income",
    "profit (loss) for the period": "net_income",  # IFRS
    "profit for the period": "net_income",  # IFRS
    "net income attributable to parent": "net_income",
    "net income attributable to noncontrolling interests": "net_income_nci",
    "minority interest": "net_income_nci",
    # Comprehensive income
    "comprehensive income": "comprehensive_income",
    "total comprehensive income": "comprehensive_income",
    "comprehensive income (loss)": "comprehensive_income",
    "other comprehensive income": "other_comprehensive_income",
    "other comprehensive income (loss)": "other_comprehensive_income",

    # ── EPS ────────────────────────────────────────────────────────────
    "earnings per share basic": "eps_basic",
    "basic eps": "eps_basic",
    "basic earnings per share": "eps_basic",
    "net income per share basic": "eps_basic",
    "earnings per share diluted": "eps_diluted",
    "diluted eps": "eps_diluted",
    "diluted earnings per share": "eps_diluted",
    "net income per share diluted": "eps_diluted",
    "weighted average shares outstanding basic": "shares_basic",
    "weighted average shares outstanding diluted": "shares_diluted",
    "weighted average number of shares outstanding basic": "shares_basic",
    "weighted average number of shares outstanding diluted": "shares_diluted",

    # ── EBITDA (calculated) ───────────────────────────────────────────
    "ebitda": "ebitda",
    "adjusted ebitda": "adjusted_ebitda",
}

BALANCE_SHEET_MAPPINGS: dict[str, str] = {
    # ── Current Assets ────────────────────────────────────────────────
    "cash and cash equivalents": "cash_and_equivalents",
    "cash & cash equivalents": "cash_and_equivalents",
    "cash": "cash_and_equivalents",
    "cash and cash equivalents at carrying value": "cash_and_equivalents",  # XBRL
    "restricted cash": "restricted_cash",
    "restricted cash and cash equivalents": "restricted_cash",
    "short-term investments": "short_term_investments",
    "short term investments": "short_term_investments",
    "marketable securities": "short_term_investments",
    "available-for-sale securities": "short_term_investments",
    "trading securities": "trading_securities",
    "cash cash equivalents and short-term investments": "cash_and_short_term_investments",
    "accounts receivable": "accounts_receivable",
    "accounts receivable net": "accounts_receivable",
    "accounts receivable net of allowance": "accounts_receivable",
    "trade receivables": "accounts_receivable",
    "trade and other receivables": "accounts_receivable",  # IFRS
    "net receivables": "accounts_receivable",
    "receivables net": "accounts_receivable",
    "notes receivable": "notes_receivable",
    "inventories": "inventories",
    "inventory": "inventories",
    "inventory net": "inventories",
    "merchandise inventories": "inventories",
    "finished goods": "finished_goods",
    "raw materials": "raw_materials",
    "work in process": "work_in_process",
    "prepaid expenses": "prepaid_expenses",
    "prepaid expenses and other current assets": "prepaid_expenses",
    "other current assets": "other_current_assets",
    "deferred tax assets current": "deferred_tax_assets_current",
    "income taxes receivable": "income_taxes_receivable",
    "contract assets": "contract_assets",  # ASC 606
    "total current assets": "total_current_assets",
    "current assets": "total_current_assets",
    "total current assets total": "total_current_assets",

    # ── Non-Current Assets ────────────────────────────────────────────
    "property plant and equipment": "ppe_net",
    "property plant and equipment net": "ppe_net",
    "property plant & equipment": "ppe_net",
    "property plant & equipment net": "ppe_net",
    "pp&e": "ppe_net",
    "pp&e net": "ppe_net",
    "net property plant and equipment": "ppe_net",
    "property and equipment net": "ppe_net",
    "property plant and equipment gross": "ppe_gross",
    "accumulated depreciation": "accumulated_depreciation",
    "goodwill": "goodwill",
    "goodwill net": "goodwill",
    "intangible assets": "intangible_assets",
    "intangible assets net": "intangible_assets",
    "other intangible assets": "intangible_assets",
    "finite-lived intangible assets net": "finite_lived_intangibles",
    "indefinite-lived intangible assets": "indefinite_lived_intangibles",
    "operating lease right-of-use assets": "operating_lease_rou_assets",
    "operating lease right of use assets": "operating_lease_rou_assets",
    "right-of-use assets": "operating_lease_rou_assets",
    "finance lease right-of-use assets": "finance_lease_rou_assets",
    "long-term investments": "long_term_investments",
    "long term investments": "long_term_investments",
    "investments": "long_term_investments",
    "equity method investments": "equity_method_investments",
    "deferred tax assets": "deferred_tax_assets",
    "deferred income tax assets": "deferred_tax_assets",
    "deferred tax assets noncurrent": "deferred_tax_assets",
    "other non-current assets": "other_noncurrent_assets",
    "other noncurrent assets": "other_noncurrent_assets",
    "other assets": "other_noncurrent_assets",
    "contract assets noncurrent": "contract_assets_noncurrent",
    "total non-current assets": "total_noncurrent_assets",
    "total noncurrent assets": "total_noncurrent_assets",
    "total assets": "total_assets",

    # ── Current Liabilities ───────────────────────────────────────────
    "accounts payable": "accounts_payable",
    "trade payables": "accounts_payable",
    "trade and other payables": "accounts_payable",  # IFRS
    "accounts payable and accrued liabilities": "accounts_payable_and_accrued",
    "accrued liabilities": "accrued_liabilities",
    "accrued expenses": "accrued_liabilities",
    "accrued expenses and other current liabilities": "accrued_liabilities",
    "other accrued liabilities": "accrued_liabilities",
    "short-term debt": "short_term_debt",
    "short term debt": "short_term_debt",
    "short-term borrowings": "short_term_debt",
    "commercial paper": "commercial_paper",
    "current portion of long-term debt": "current_portion_ltd",
    "current portion of long term debt": "current_portion_ltd",
    "current maturities of long-term debt": "current_portion_ltd",
    "deferred revenue": "deferred_revenue",
    "deferred revenue current": "deferred_revenue",
    "unearned revenue": "deferred_revenue",
    "contract liabilities": "deferred_revenue",  # ASC 606
    "contract liabilities current": "deferred_revenue",
    "operating lease liabilities current": "operating_lease_liabilities_current",
    "current operating lease liabilities": "operating_lease_liabilities_current",
    "finance lease liabilities current": "finance_lease_liabilities_current",
    "income taxes payable": "income_taxes_payable",
    "dividends payable": "dividends_payable",
    "other current liabilities": "other_current_liabilities",
    "total current liabilities": "total_current_liabilities",
    "current liabilities": "total_current_liabilities",

    # ── Non-Current Liabilities ───────────────────────────────────────
    "long-term debt": "long_term_debt",
    "long term debt": "long_term_debt",
    "long-term debt net of current portion": "long_term_debt",
    "long-term borrowings": "long_term_debt",
    "notes payable": "long_term_debt",
    "senior notes": "long_term_debt",
    "term loan": "long_term_debt",
    "convertible debt": "convertible_debt",
    "operating lease liabilities noncurrent": "operating_lease_liabilities_noncurrent",
    "noncurrent operating lease liabilities": "operating_lease_liabilities_noncurrent",
    "finance lease liabilities noncurrent": "finance_lease_liabilities_noncurrent",
    "deferred tax liabilities": "deferred_tax_liabilities",
    "deferred income tax liabilities": "deferred_tax_liabilities",
    "deferred tax liabilities noncurrent": "deferred_tax_liabilities",
    "deferred revenue noncurrent": "deferred_revenue_noncurrent",
    "contract liabilities noncurrent": "deferred_revenue_noncurrent",
    "pension and post-retirement benefit obligations": "pension_obligations",
    "pension obligations": "pension_obligations",
    "other non-current liabilities": "other_noncurrent_liabilities",
    "other noncurrent liabilities": "other_noncurrent_liabilities",
    "other long-term liabilities": "other_noncurrent_liabilities",
    "other liabilities": "other_noncurrent_liabilities",
    "total non-current liabilities": "total_noncurrent_liabilities",
    "total noncurrent liabilities": "total_noncurrent_liabilities",
    "total liabilities": "total_liabilities",

    # ── Equity ────────────────────────────────────────────────────────
    "common stock": "common_stock",
    "common stock and additional paid-in capital": "common_stock_and_apic",
    "common shares": "common_stock",  # IFRS
    "preferred stock": "preferred_stock",
    "additional paid-in capital": "additional_paid_in_capital",
    "additional paid in capital": "additional_paid_in_capital",
    "apic": "additional_paid_in_capital",
    "capital surplus": "additional_paid_in_capital",
    "share premium": "additional_paid_in_capital",  # IFRS
    "retained earnings": "retained_earnings",
    "retained earnings (accumulated deficit)": "retained_earnings",
    "accumulated deficit": "retained_earnings",
    "accumulated other comprehensive income": "accumulated_oci",
    "accumulated other comprehensive income (loss)": "accumulated_oci",
    "accumulated other comprehensive loss": "accumulated_oci",
    "aoci": "accumulated_oci",
    "treasury stock": "treasury_stock",
    "treasury stock at cost": "treasury_stock",
    "treasury shares": "treasury_stock",  # IFRS
    "noncontrolling interests": "noncontrolling_interests",
    "noncontrolling interest": "noncontrolling_interests",
    "non-controlling interests": "noncontrolling_interests",
    "minority interest": "noncontrolling_interests",
    "total stockholders equity": "total_equity",
    "total stockholders' equity": "total_equity",
    "total equity": "total_equity",
    "total shareholders equity": "total_equity",
    "total shareholders' equity": "total_equity",
    "stockholders equity": "total_equity",
    "shareholders equity": "total_equity",
    "equity attributable to owners of the parent": "total_equity",  # IFRS
    "total equity attributable to parent": "total_equity",
    "total liabilities and equity": "total_liabilities_and_equity",
    "total liabilities and stockholders equity": "total_liabilities_and_equity",
    "total liabilities and stockholders' equity": "total_liabilities_and_equity",
    "total liabilities and shareholders equity": "total_liabilities_and_equity",
    "total liabilities shareholders equity": "total_liabilities_and_equity",
}

CASH_FLOW_MAPPINGS: dict[str, str] = {
    # ── Operating Activities ──────────────────────────────────────────
    "net income": "cf_net_income",
    "net income (loss)": "cf_net_income",
    "profit (loss)": "cf_net_income",  # IFRS
    "cash from operations": "operating_cash_flow",
    "net cash from operating activities": "operating_cash_flow",
    "net cash provided by operating activities": "operating_cash_flow",
    "net cash provided by (used in) operating activities": "operating_cash_flow",
    "cash flows from operating activities": "operating_cash_flow",
    "net cash used in operating activities": "operating_cash_flow",
    # Common non-cash adjustments
    "depreciation and amortization": "cf_depreciation_amortization",
    "depreciation & amortization": "cf_depreciation_amortization",
    "stock-based compensation": "cf_stock_based_compensation",
    "stock based compensation": "cf_stock_based_compensation",
    "share-based compensation": "cf_stock_based_compensation",
    "deferred income taxes": "cf_deferred_income_taxes",
    "deferred income tax expense": "cf_deferred_income_taxes",
    "amortization of debt issuance costs": "cf_amortization_debt_costs",
    "impairment charges": "cf_impairment_charges",
    "gain (loss) on sale of investments": "cf_gain_loss_investments",
    "provision for doubtful accounts": "cf_provision_doubtful_accounts",
    "unrealized gain (loss)": "cf_unrealized_gain_loss",
    # Changes in working capital
    "changes in operating assets and liabilities": "cf_working_capital_changes",
    "changes in assets and liabilities": "cf_working_capital_changes",
    "accounts receivable": "cf_change_receivables",
    "change in accounts receivable": "cf_change_receivables",
    "increase (decrease) in accounts receivable": "cf_change_receivables",
    "inventories": "cf_change_inventories",
    "change in inventories": "cf_change_inventories",
    "increase (decrease) in inventories": "cf_change_inventories",
    "accounts payable": "cf_change_payables",
    "change in accounts payable": "cf_change_payables",
    "increase (decrease) in accounts payable": "cf_change_payables",
    "accrued liabilities": "cf_change_accrued_liabilities",
    "deferred revenue": "cf_change_deferred_revenue",
    "change in deferred revenue": "cf_change_deferred_revenue",
    "other operating activities": "cf_other_operating",

    # ── Investing Activities ──────────────────────────────────────────
    "cash from investing": "investing_cash_flow",
    "net cash from investing activities": "investing_cash_flow",
    "net cash used in investing activities": "investing_cash_flow",
    "net cash provided by (used in) investing activities": "investing_cash_flow",
    "cash flows from investing activities": "investing_cash_flow",
    "capital expenditures": "capex",
    "purchases of property and equipment": "capex",
    "payments to acquire property plant and equipment": "capex",  # XBRL
    "payments for capital expenditures": "capex",
    "additions to property and equipment": "capex",
    "purchases of investments": "cf_purchases_investments",
    "purchases of marketable securities": "cf_purchases_investments",
    "purchases of short-term investments": "cf_purchases_investments",
    "maturities of investments": "cf_maturities_investments",
    "maturities of marketable securities": "cf_maturities_investments",
    "sales of investments": "cf_sales_investments",
    "proceeds from sales of investments": "cf_sales_investments",
    "proceeds from maturities of investments": "cf_maturities_investments",
    "acquisitions net of cash acquired": "cf_acquisitions",
    "business combinations net of cash acquired": "cf_acquisitions",  # XBRL
    "payments to acquire businesses": "cf_acquisitions",
    "other investing activities": "cf_other_investing",

    # ── Financing Activities ──────────────────────────────────────────
    "cash from financing": "financing_cash_flow",
    "net cash from financing activities": "financing_cash_flow",
    "net cash used in financing activities": "financing_cash_flow",
    "net cash provided by (used in) financing activities": "financing_cash_flow",
    "cash flows from financing activities": "financing_cash_flow",
    "dividends paid": "dividends_paid",
    "payments of dividends": "dividends_paid",
    "cash dividends paid": "dividends_paid",
    "share repurchases": "share_repurchases",
    "repurchases of common stock": "share_repurchases",
    "treasury stock acquired": "share_repurchases",
    "payments for repurchase of common stock": "share_repurchases",  # XBRL
    "proceeds from issuance of common stock": "cf_stock_issuance",
    "proceeds from stock issuance": "cf_stock_issuance",
    "proceeds from exercise of stock options": "cf_stock_option_proceeds",
    "proceeds from issuance of debt": "cf_debt_issuance",
    "proceeds from long-term debt": "cf_debt_issuance",
    "proceeds from borrowings": "cf_debt_issuance",
    "repayments of debt": "cf_debt_repayment",
    "repayments of long-term debt": "cf_debt_repayment",
    "principal payments on debt": "cf_debt_repayment",
    "payments of debt": "cf_debt_repayment",
    "debt issuance costs": "cf_debt_issuance_costs",
    "other financing activities": "cf_other_financing",

    # ── Net Change / FX ───────────────────────────────────────────────
    "effect of exchange rate changes": "cf_fx_effect",
    "effect of exchange rate on cash": "cf_fx_effect",
    "net change in cash": "net_change_in_cash",
    "net increase in cash": "net_change_in_cash",
    "net decrease in cash": "net_change_in_cash",
    "net increase (decrease) in cash": "net_change_in_cash",
    "net increase (decrease) in cash and cash equivalents": "net_change_in_cash",
    "cash at beginning of period": "beginning_cash",
    "cash and cash equivalents beginning of period": "beginning_cash",
    "cash at end of period": "ending_cash",
    "cash and cash equivalents end of period": "ending_cash",
    "free cash flow": "free_cash_flow",

    # ── Supplemental ──────────────────────────────────────────────────
    "cash paid for income taxes": "cf_taxes_paid",
    "income taxes paid": "cf_taxes_paid",
    "cash paid for interest": "cf_interest_paid",
    "interest paid": "cf_interest_paid",
}

# ─── XBRL Element Name → Standard Label ──────────────────────────────────────
# Maps raw XBRL tag names (as they appear in SEC filings) to our standard keys.
# This enables direct XBRL-to-pipeline translation without label normalization.

XBRL_TAG_TO_STANDARD: dict[str, tuple[str, str]] = {
    # (xbrl_element_name, (standardized_label, statement_type))
    # Income Statement
    "Revenues": ("total_revenue", "income_statement"),
    "RevenueFromContractWithCustomerExcludingAssessedTax": ("total_revenue", "income_statement"),
    "SalesRevenueNet": ("total_revenue", "income_statement"),
    "CostOfRevenue": ("cost_of_revenue", "income_statement"),
    "CostOfGoodsAndServicesSold": ("cost_of_revenue", "income_statement"),
    "GrossProfit": ("gross_profit", "income_statement"),
    "OperatingExpenses": ("total_operating_expenses", "income_statement"),
    "SellingGeneralAndAdministrativeExpense": ("sga_expense", "income_statement"),
    "ResearchAndDevelopmentExpense": ("rd_expense", "income_statement"),
    "DepreciationDepletionAndAmortization": ("depreciation_amortization", "income_statement"),
    "ShareBasedCompensation": ("stock_based_compensation", "income_statement"),
    "RestructuringCharges": ("restructuring_charges", "income_statement"),
    "OperatingIncomeLoss": ("operating_income", "income_statement"),
    "InterestExpense": ("interest_expense", "income_statement"),
    "InterestIncomeExpenseNet": ("net_interest_expense", "income_statement"),
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxes": ("income_before_tax", "income_statement"),
    "IncomeTaxExpenseBenefit": ("income_tax_expense", "income_statement"),
    "NetIncomeLoss": ("net_income", "income_statement"),
    "NetIncomeLossAttributableToParent": ("net_income", "income_statement"),
    "NetIncomeLossAttributableToNoncontrollingInterest": ("net_income_nci", "income_statement"),
    "EarningsPerShareBasic": ("eps_basic", "income_statement"),
    "EarningsPerShareDiluted": ("eps_diluted", "income_statement"),
    "WeightedAverageNumberOfSharesOutstandingBasic": ("shares_basic", "income_statement"),
    "WeightedAverageNumberOfDilutedSharesOutstanding": ("shares_diluted", "income_statement"),
    "ComprehensiveIncomeNetOfTax": ("comprehensive_income", "income_statement"),
    # Balance Sheet
    "CashAndCashEquivalentsAtCarryingValue": ("cash_and_equivalents", "balance_sheet"),
    "RestrictedCash": ("restricted_cash", "balance_sheet"),
    "ShortTermInvestments": ("short_term_investments", "balance_sheet"),
    "MarketableSecuritiesCurrent": ("short_term_investments", "balance_sheet"),
    "AccountsReceivableNetCurrent": ("accounts_receivable", "balance_sheet"),
    "InventoryNet": ("inventories", "balance_sheet"),
    "PrepaidExpenseAndOtherAssetsCurrent": ("prepaid_expenses", "balance_sheet"),
    "AssetsCurrent": ("total_current_assets", "balance_sheet"),
    "PropertyPlantAndEquipmentNet": ("ppe_net", "balance_sheet"),
    "Goodwill": ("goodwill", "balance_sheet"),
    "IntangibleAssetsNetExcludingGoodwill": ("intangible_assets", "balance_sheet"),
    "OperatingLeaseRightOfUseAsset": ("operating_lease_rou_assets", "balance_sheet"),
    "DeferredIncomeTaxAssetsNet": ("deferred_tax_assets", "balance_sheet"),
    "Assets": ("total_assets", "balance_sheet"),
    "AccountsPayableCurrent": ("accounts_payable", "balance_sheet"),
    "AccruedLiabilitiesCurrent": ("accrued_liabilities", "balance_sheet"),
    "ShortTermBorrowings": ("short_term_debt", "balance_sheet"),
    "LongTermDebtCurrent": ("current_portion_ltd", "balance_sheet"),
    "ContractWithCustomerLiabilityCurrent": ("deferred_revenue", "balance_sheet"),
    "OperatingLeaseLiabilityCurrent": ("operating_lease_liabilities_current", "balance_sheet"),
    "LiabilitiesCurrent": ("total_current_liabilities", "balance_sheet"),
    "LongTermDebtNoncurrent": ("long_term_debt", "balance_sheet"),
    "OperatingLeaseLiabilityNoncurrent": ("operating_lease_liabilities_noncurrent", "balance_sheet"),
    "DeferredIncomeTaxLiabilitiesNet": ("deferred_tax_liabilities", "balance_sheet"),
    "Liabilities": ("total_liabilities", "balance_sheet"),
    "CommonStockValue": ("common_stock", "balance_sheet"),
    "AdditionalPaidInCapital": ("additional_paid_in_capital", "balance_sheet"),
    "RetainedEarningsAccumulatedDeficit": ("retained_earnings", "balance_sheet"),
    "AccumulatedOtherComprehensiveIncomeLossNetOfTax": ("accumulated_oci", "balance_sheet"),
    "TreasuryStockValue": ("treasury_stock", "balance_sheet"),
    "StockholdersEquity": ("total_equity", "balance_sheet"),
    "MinorityInterest": ("noncontrolling_interests", "balance_sheet"),
    "LiabilitiesAndStockholdersEquity": ("total_liabilities_and_equity", "balance_sheet"),
    # Cash Flow
    "NetCashProvidedByUsedInOperatingActivities": ("operating_cash_flow", "cash_flow"),
    "PaymentsToAcquirePropertyPlantAndEquipment": ("capex", "cash_flow"),
    "NetCashProvidedByUsedInInvestingActivities": ("investing_cash_flow", "cash_flow"),
    "PaymentsOfDividends": ("dividends_paid", "cash_flow"),
    "PaymentsForRepurchaseOfCommonStock": ("share_repurchases", "cash_flow"),
    "NetCashProvidedByUsedInFinancingActivities": ("financing_cash_flow", "cash_flow"),
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect": ("net_change_in_cash", "cash_flow"),
}


# ─── Data Types ──────────────────────────────────────────────────────────────

@dataclass
class NormalizedLineItem:
    """A normalized financial line item."""
    original_label: str
    standardized_label: str
    values: dict[str, Optional[float]]
    statement_type: str  # "income_statement", "balance_sheet", "cash_flow"
    confidence: float = 1.0
    match_method: str = "exact"  # "exact", "prefix", "xbrl_tag", "fuzzy"


@dataclass
class SpreadResult:
    """Result of financial spreading (normalization)."""
    income_statement: list[NormalizedLineItem] = field(default_factory=list)
    balance_sheet: list[NormalizedLineItem] = field(default_factory=list)
    cash_flow: list[NormalizedLineItem] = field(default_factory=list)
    unmapped_items: list[dict] = field(default_factory=list)
    periods: list[str] = field(default_factory=list)
    mapping_stats: dict = field(default_factory=lambda: {
        "exact": 0, "prefix": 0, "xbrl_tag": 0, "fuzzy": 0, "unmapped": 0
    })


# ─── Label Normalization & Matching ──────────────────────────────────────────

def normalize_label(label: str) -> str:
    """Normalize a label for matching."""
    # Lowercase, strip, remove extra whitespace
    normalized = label.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    # Remove common noise
    normalized = normalized.replace(',', '')
    normalized = normalized.replace('.', '')
    normalized = normalized.replace(':', '')
    normalized = normalized.replace('$', '')
    normalized = normalized.replace('(', '').replace(')', '')
    # Remove trailing numbers / footnote references
    normalized = re.sub(r'\s*\(\d+\)\s*$', '', normalized)
    normalized = re.sub(r'\s*\d+$', '', normalized)
    # Remove leading/trailing hyphens and underscores
    normalized = normalized.strip('-_ ')
    return normalized.strip()


def _tokenize(label: str) -> set[str]:
    """Split a label into meaningful tokens for fuzzy matching."""
    stop_words = {"and", "the", "of", "or", "in", "for", "to", "from", "at", "on", "by", "net", "total"}
    tokens = set(re.split(r'[\s&/\-_]+', label.lower()))
    return tokens - stop_words - {""}


def _fuzzy_score(label_tokens: set[str], mapping_tokens: set[str]) -> float:
    """Calculate token overlap score between two labels (Jaccard-like)."""
    if not label_tokens or not mapping_tokens:
        return 0.0
    intersection = label_tokens & mapping_tokens
    union = label_tokens | mapping_tokens
    return len(intersection) / len(union) if union else 0.0


FUZZY_THRESHOLD = 0.6  # Minimum token overlap score to consider a fuzzy match


def map_label(label: str) -> tuple[Optional[str], str, str, float]:
    """
    Map a financial label to its standardized form.

    Returns:
        Tuple of (standardized_label, statement_type, match_method, confidence).
        If no mapping found, returns (None, "unknown", "none", 0.0).
    """
    normalized = normalize_label(label)

    # 1. Try XBRL tag name (CamelCase element names from XBRL filings)
    # Strip any namespace prefix like "us-gaap:"
    tag_name = label.strip()
    if ":" in tag_name:
        tag_name = tag_name.split(":", 1)[1]
    if tag_name in XBRL_TAG_TO_STANDARD:
        std, stmt = XBRL_TAG_TO_STANDARD[tag_name]
        return std, stmt, "xbrl_tag", 1.0

    # 2. Exact match in mappings
    mappings_with_types = [
        (INCOME_STATEMENT_MAPPINGS, "income_statement"),
        (BALANCE_SHEET_MAPPINGS, "balance_sheet"),
        (CASH_FLOW_MAPPINGS, "cash_flow"),
    ]
    for mapping, stmt_type in mappings_with_types:
        if normalized in mapping:
            return mapping[normalized], stmt_type, "exact", 1.0

    # 3. Prefix match (label starts with a known mapping key)
    for mapping, stmt_type in mappings_with_types:
        for key, value in mapping.items():
            if normalized.startswith(key):
                return value, stmt_type, "prefix", 0.9

    # 4. Fuzzy token overlap matching
    label_tokens = _tokenize(normalized)
    best_score = 0.0
    best_match = None

    for mapping, stmt_type in mappings_with_types:
        for key, value in mapping.items():
            key_tokens = _tokenize(key)
            score = _fuzzy_score(label_tokens, key_tokens)
            if score > best_score:
                best_score = score
                best_match = (value, stmt_type)

    if best_score >= FUZZY_THRESHOLD and best_match:
        return best_match[0], best_match[1], "fuzzy", round(best_score, 2)

    return None, "unknown", "none", 0.0


def spread_financial_data(
    labels: list[str],
    values_by_period: dict[str, list[Optional[float]]],
) -> SpreadResult:
    """
    Normalize financial data into standardized statements.

    Args:
        labels: List of financial line item labels (as extracted).
        values_by_period: Dict mapping period names to value lists
                          (same length as labels).

    Returns:
        SpreadResult with normalized statements.
    """
    result = SpreadResult(periods=list(values_by_period.keys()))

    for i, label in enumerate(labels):
        if not label or not label.strip():
            continue

        std_label, statement_type, match_method, confidence = map_label(label)

        # Build values dict for this line item
        item_values = {}
        for period, values in values_by_period.items():
            if i < len(values):
                item_values[period] = values[i]

        if std_label:
            item = NormalizedLineItem(
                original_label=label,
                standardized_label=std_label,
                values=item_values,
                statement_type=statement_type,
                confidence=confidence,
                match_method=match_method,
            )

            if statement_type == "income_statement":
                result.income_statement.append(item)
            elif statement_type == "balance_sheet":
                result.balance_sheet.append(item)
            elif statement_type == "cash_flow":
                result.cash_flow.append(item)

            result.mapping_stats[match_method] = result.mapping_stats.get(match_method, 0) + 1
        else:
            result.unmapped_items.append({
                "label": label,
                "values": item_values,
                "suggestion": "Review manually or add to mapping",
            })
            result.mapping_stats["unmapped"] += 1

    mapped = (
        len(result.income_statement)
        + len(result.balance_sheet)
        + len(result.cash_flow)
    )
    logger.info(
        "Financial spreading complete",
        mapped_items=mapped,
        unmapped_items=len(result.unmapped_items),
        periods=result.periods,
        stats=result.mapping_stats,
    )

    return result


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test with expanded labels including XBRL tags and fuzzy matches
    test_labels = [
        # Exact matches
        "Revenue", "Cost of Goods Sold", "Gross Profit",
        "SG&A", "R&D", "Stock-Based Compensation", "Operating Income",
        "Interest Expense", "Income Before Taxes", "Net Income",
        # XBRL tag names
        "us-gaap:CashAndCashEquivalentsAtCarryingValue",
        "PropertyPlantAndEquipmentNet",
        "OperatingLeaseRightOfUseAsset",
        "Goodwill",
        # Balance sheet items
        "Total Assets", "Total Liabilities", "Total Equity",
        "Accumulated Other Comprehensive Loss",
        "Treasury Stock at Cost",
        # Cash flow items
        "Capital Expenditures", "Dividends Paid",
        "Payments for Repurchase of Common Stock",
        # Fuzzy match candidates
        "Revenue from Contract with Customer",
        "Selling General Administrative Expenses",
        # Unmappable
        "Segment Operating Margin",
    ]

    test_values = {
        "FY2023": [1000000 + i * 10000 for i in range(len(test_labels))],
        "FY2024": [1200000 + i * 12000 for i in range(len(test_labels))],
    }

    result = spread_financial_data(test_labels, test_values)

    print(f"\n{'='*70}")
    print(f"Financial Spreader — XBRL-Enhanced (250+ mappings)")
    print(f"{'='*70}")

    print(f"\nIncome Statement Items ({len(result.income_statement)}):")
    for item in result.income_statement:
        print(f"  [{item.match_method}|{item.confidence}] {item.original_label} → {item.standardized_label}")

    print(f"\nBalance Sheet Items ({len(result.balance_sheet)}):")
    for item in result.balance_sheet:
        print(f"  [{item.match_method}|{item.confidence}] {item.original_label} → {item.standardized_label}")

    print(f"\nCash Flow Items ({len(result.cash_flow)}):")
    for item in result.cash_flow:
        print(f"  [{item.match_method}|{item.confidence}] {item.original_label} → {item.standardized_label}")

    print(f"\nUnmapped: {len(result.unmapped_items)}")
    for item in result.unmapped_items:
        print(f"  ❌ {item['label']}")

    print(f"\nMapping Stats: {result.mapping_stats}")
    total_mappings = (
        len(INCOME_STATEMENT_MAPPINGS) + len(BALANCE_SHEET_MAPPINGS)
        + len(CASH_FLOW_MAPPINGS) + len(XBRL_TAG_TO_STANDARD)
    )
    print(f"Total taxonomy entries: {total_mappings}")
