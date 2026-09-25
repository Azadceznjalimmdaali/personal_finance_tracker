import sys
import os
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from finance_tracker import transactions, storage
from finance_tracker.validation import ValidationError


class TestTransactions(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_path = os.path.join(self.tmp.name, "transactions.csv")
        self.backup_dir = os.path.join(self.tmp.name, "backups")
        self.id_path = os.path.join(self.tmp.name, "next_id.txt")

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_transaction_assigns_incrementing_ids(self):
        t1 = transactions.add_transaction("income", "Salary", "1000", "2026-09-01",
                                           self.data_path, self.backup_dir, self.id_path)
        t2 = transactions.add_transaction("expense", "Food", "50", "2026-09-02",
                                           self.data_path, self.backup_dir, self.id_path)
        self.assertEqual(t1["id"], 1)
        self.assertEqual(t2["id"], 2)

    def test_add_transaction_rejects_invalid_amount(self):
        with self.assertRaises(ValidationError):
            transactions.add_transaction("income", "Salary", "-5", "2026-09-01",
                                          self.data_path, self.backup_dir, self.id_path)

    def test_delete_does_not_change_other_ids(self):
        t1 = transactions.add_transaction("income", "Salary", "1000", "2026-09-01",
                                           self.data_path, self.backup_dir, self.id_path)
        t2 = transactions.add_transaction("expense", "Food", "50", "2026-09-02",
                                           self.data_path, self.backup_dir, self.id_path)

        transactions.delete_transaction(t1["id"], self.data_path, self.backup_dir)

        remaining, _errors = storage.load_transactions(self.data_path)
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["id"], t2["id"])  # t2's ID is untouched

    def test_edit_keeps_the_same_id(self):
        t1 = transactions.add_transaction("expense", "Food", "50", "2026-09-02",
                                           self.data_path, self.backup_dir, self.id_path)

        transactions.edit_transaction(t1["id"], amount_raw="75",
                                       data_path=self.data_path, backup_dir=self.backup_dir)

        updated, _errors = storage.load_transactions(self.data_path)
        self.assertEqual(len(updated), 1)
        self.assertEqual(updated[0]["id"], t1["id"])
        self.assertEqual(str(updated[0]["amount"]), "75")


if __name__ == "__main__":
    unittest.main()