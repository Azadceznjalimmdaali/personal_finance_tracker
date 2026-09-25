"""
Monthly, per-category budgets.

Key decision: a budget is keyed by (year_month, category) together --
NOT by category alone. That's why "Food" for 2026-09 and "Food" for
2026-10 are stored as two completely separate entries. We use a
dictionary with a tuple key: {("2026-09", "food"): Decimal("500")}.

Budgets are stored in their own small CSV file, separate from
transactions.csv.
"""

import csv
import os
from decimal import Decimal, InvalidOperation

from .reports import expenses_by_category
from .validation import parse_amount, normalize_category

BUDGETS_FILE = os.path.join("data", "budgets.csv")
FIELDNAMES = ["year_month", "category", "amount"]


def load_budgets(path=BUDGETS_FILE):
    """Returns {(year_month, category): Decimal amount}."""
    budgets = {}
    if not os.path.exists(path):
        return budgets

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                key = (row["year_month"], row["category"])
                budgets[key] = Decimal(row["amount"])
            except (KeyError, InvalidOperation):
                continue  # skip a corrupted budget row rather than crash

    return budgets


def save_budgets(budgets, path=BUDGETS_FILE):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for (year_month, category), amount in budgets.items():
            writer.writerow({"year_month": year_month, "category": category, "amount": str(amount)})


def set_budget(year_month, category_raw, amount_raw, path=BUDGETS_FILE):
    """Create or overwrite the budget for one (month, category) pair."""
    category = normalize_category(category_raw)
    amount = parse_amount(amount_raw)

    budgets = load_budgets(path)
    budgets[(year_month, category)] = amount
    save_budgets(budgets, path)

    return amount


def compare_budget_to_actual(transactions, year_month, budgets_path=BUDGETS_FILE):
    """
    Returns a list of dicts:
    [{"category": ..., "budget": ..., "actual": ..., "remaining": ...}, ...]
    Only categories that have a budget set for that month are included.
    """
    budgets = load_budgets(budgets_path)
    actual_by_category = expenses_by_category(transactions, year_month)

    results = []
    for (b_year_month, category), budget_amount in budgets.items():
        if b_year_month != year_month:
            continue
        actual = actual_by_category.get(category, Decimal("0"))
        results.append({
            "category": category,
            "budget": budget_amount,
            "actual": actual,
            "remaining": budget_amount - actual,
        })

    return results