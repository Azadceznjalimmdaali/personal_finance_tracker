import sys
import os
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from decimal import Decimal
from finance_tracker import storage


class TestStorage(unittest.TestCase):

    def test_round_trip_preserves_comma_in_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "transactions.csv")
            data = [{
                "id": 1, "type": "income",
                "category_or_source": "salary, company xyz",
                "amount": Decimal("1000.00"), "date": "2026-09-01",
            }]
            storage.save_transactions(data, path)
            loaded, errors = storage.load_transactions(path)
            self.assertEqual(errors, [])
            self.assertEqual(loaded[0]["category_or_source"], "salary, company xyz")

    def test_corrupted_row_is_skipped_not_crashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "transactions.csv")
            with open(path, "w", encoding="utf-8") as f:
                f.write("id,type,category_or_source,amount,date\n")
                f.write("1,income,salary,1000.00,2026-09-01\n")
                f.write("2,expense,food,NOT_A_NUMBER,2026-09-02\n")

            loaded, errors = storage.load_transactions(path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(len(errors), 1)

    def test_backup_captures_state_before_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "transactions.csv")
            backup_dir = os.path.join(tmp, "backups")

            original = [{
                "id": 1, "type": "income", "category_or_source": "salary",
                "amount": Decimal("100"), "date": "2026-09-01",
            }]
            storage.save_transactions(original, path)

            storage.backup_before_change(path, backup_dir)
            storage.save_transactions([], path)  # simulate a delete

            backups = os.listdir(backup_dir)
            self.assertEqual(len(backups), 1)

            backed_up, _ = storage.load_transactions(os.path.join(backup_dir, backups[0]))
            self.assertEqual(len(backed_up), 1)  # backup has the OLD state


if __name__ == "__main__":
    unittest.main()