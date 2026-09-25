"""
Reads/writes transactions to a CSV file, and handles backups.

Three decisions here are the ones worth being able to explain:

1. We use Python's `csv` module instead of manual split(','). A field
   like "Salary, Company XYZ" contains a comma itself -- csv.writer
   quotes it automatically when writing, and csv.reader un-quotes it
   correctly when reading. Manual splitting would wrongly cut that
   field into two.

2. backup_before_change() must be called BEFORE save_transactions().
   That order is what guarantees the backup holds the data as it was
   right before the change, not the already-changed state.

3. load_transactions() never lets one bad row crash the whole program.
   It skips corrupted rows and returns them separately as `errors`, so
   the caller can report the problem while still using the good data.
"""

import csv
import os
import shutil
from datetime import datetime
from decimal import Decimal, InvalidOperation

DATA_FILE = os.path.join("data", "transactions.csv")
BACKUP_DIR = os.path.join("data", "backups")
FIELDNAMES = ["id", "type", "category_or_source", "amount", "date"]


def load_transactions(path=DATA_FILE):
    """Returns (transactions, errors). errors is a list of skipped-row messages."""
    transactions = []
    errors = []

    if not os.path.exists(path):
        return transactions, errors

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_number, row in enumerate(reader, start=2):  # line 1 is the header
            try:
                transactions.append({
                    "id": int(row["id"]),
                    "type": row["type"],
                    "category_or_source": row["category_or_source"],
                    "amount": Decimal(row["amount"]),
                    "date": row["date"],
                })
            except (KeyError, ValueError, InvalidOperation, TypeError):
                errors.append(f"Skipped corrupted row at line {row_number}: {row}")

    return transactions, errors


def save_transactions(transactions, path=DATA_FILE):
    """Overwrite the file with the full current list (used after add/edit/delete)."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for t in transactions:
            writer.writerow({
                "id": t["id"],
                "type": t["type"],
                "category_or_source": t["category_or_source"],
                "amount": str(t["amount"]),
                "date": t["date"],
            })


def backup_before_change(path=DATA_FILE, backup_dir=BACKUP_DIR):
    """Copy the file as it currently is, before any modification touches it."""
    if not os.path.exists(path):
        return  # nothing to back up yet

    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = os.path.join(backup_dir, f"transactions_{timestamp}.csv")
    shutil.copy2(path, backup_path)