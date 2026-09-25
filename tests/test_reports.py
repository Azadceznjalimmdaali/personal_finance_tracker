import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from decimal import Decimal
from finance_tracker import reports


def _t(type_, category, amount, date):
    return {"id": 0, "type": type_, "category_or_source": category,
            "amount": Decimal(amount), "date": date}


class TestReports(unittest.TestCase):

    def test_month_boundary_is_exact(self):
        data = [
            _t("expense", "food", "10", "2026-09-30"),  # belongs to September
            _t("expense", "food", "20", "2026-10-01"),  # belongs to October, NOT September
        ]
        september = reports.filter_by_month(data, "2026-09")
        self.assertEqual(len(september), 1)
        self.assertEqual(september[0]["date"], "2026-09-30")

    def test_income_excluded_from_expenses_by_category(self):
        data = [
            _t("income", "salary", "1000", "2026-09-01"),
            _t("expense", "food", "50", "2026-09-02"),
        ]
        totals = reports.expenses_by_category(data, "2026-09")
        self.assertNotIn("salary", totals)
        self.assertEqual(totals["food"], Decimal("50"))

    def test_monthly_summary_totals(self):
        data = [
            _t("income", "salary", "1000", "2026-09-01"),
            _t("expense", "food", "50", "2026-09-02"),
        ]
        income, expense, balance = reports.monthly_summary(data, "2026-09")
        self.assertEqual(income, Decimal("1000"))
        self.assertEqual(expense, Decimal("50"))
        self.assertEqual(balance, Decimal("950"))


if __name__ == "__main__":
    unittest.main()