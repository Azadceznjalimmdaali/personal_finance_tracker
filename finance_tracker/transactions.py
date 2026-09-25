"""
add / edit / delete transactions.
This is the layer that connects validation.py + id_generator.py + storage.py.

Every path argument defaults to the real project paths, but can be
overridden -- that's what lets the tests run against temp files
instead of your actual data folder.
"""

from . import storage
from . import id_generator
from .validation import parse_amount, parse_date, normalize_category


def add_transaction(type_, category_or_source_raw, amount_raw, date_raw,
                     data_path=storage.DATA_FILE,
                     backup_dir=storage.BACKUP_DIR,
                     next_id_path=id_generator.DEFAULT_NEXT_ID_FILE):
    """
    Validate first (may raise ValidationError -- nothing gets written
    if validation fails), then back up, then append and save.
    """
    amount = parse_amount(amount_raw)
    date = parse_date(date_raw)
    category_or_source = normalize_category(category_or_source_raw)

    transactions, _errors = storage.load_transactions(data_path)
    new_id = id_generator.get_next_id(next_id_path)

    transaction = {
        "id": new_id,
        "type": type_,
        "category_or_source": category_or_source,
        "amount": amount,
        "date": date,
    }

    storage.backup_before_change(data_path, backup_dir)  # backup BEFORE the change
    transactions.append(transaction)
    storage.save_transactions(transactions, data_path)

    return transaction


def delete_transaction(transaction_id,
                        data_path=storage.DATA_FILE,
                        backup_dir=storage.BACKUP_DIR):
    """Delete by ID. Every other transaction, and its ID, stays untouched."""
    transactions, _errors = storage.load_transactions(data_path)
    remaining = [t for t in transactions if t["id"] != transaction_id]

    if len(remaining) == len(transactions):
        raise ValueError(f"No transaction with id {transaction_id}")

    storage.backup_before_change(data_path, backup_dir)
    storage.save_transactions(remaining, data_path)


def edit_transaction(transaction_id,
                      amount_raw=None, category_or_source_raw=None, date_raw=None,
                      data_path=storage.DATA_FILE,
                      backup_dir=storage.BACKUP_DIR):
    """Edit by ID. The ID itself never changes. Only pass the fields you want to update."""
    transactions, _errors = storage.load_transactions(data_path)

    target = next((t for t in transactions if t["id"] == transaction_id), None)
    if target is None:
        raise ValueError(f"No transaction with id {transaction_id}")

    if amount_raw is not None:
        target["amount"] = parse_amount(amount_raw)
    if category_or_source_raw is not None:
        target["category_or_source"] = normalize_category(category_or_source_raw)
    if date_raw is not None:
        target["date"] = parse_date(date_raw)

    storage.backup_before_change(data_path, backup_dir)
    storage.save_transactions(transactions, data_path)

    return target