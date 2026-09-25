"""
Monthly reports.

Key decision: filtering by month is a simple string check, since we
always store dates as "YYYY-MM-DD". A transaction belongs to month
"2026-09" if its date STARTS WITH "2026-09". This correctly separates
2026-09-30 (belongs to September) from 2026-10-01 (does not) without
needing to parse dates into datetime objects at all.
"""

from decimal import Decimal


def filter_by_month(transactions, year_month):
    """year_month must look like 'YYYY-MM', e.g. '2026-09'."""
    return [t for t in transactions if t["date"].startswith(year_month)]


def monthly_summary(transactions, year_month):
    """Returns (total_income, total_expense, balance) for that month."""
    month_transactions = filter_by_month(transactions, year_month)

    total_income = sum((t["amount"] for t in month_transactions if t["type"] == "income"), Decimal("0"))
    total_expense = sum((t["amount"] for t in month_transactions if t["type"] == "expense"), Decimal("0"))

    return total_income, total_expense, total_income - total_expense


def expenses_by_category(transactions, year_month):
    """
    Returns {category: total_spent} for a given month.
    Only expenses count here -- income must never appear in this
    breakdown, since budgets are compared against spending only.
    """
    month_transactions = filter_by_month(transactions, year_month)
    totals = {}

    for t in month_transactions:
        if t["type"] != "expense":
            continue
        category = t["category_or_source"]  # already normalized (lowercase) by validation
        totals[category] = totals.get(category, Decimal("0")) + t["amount"]

    return totals