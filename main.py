"""
The command-line menu. This file should stay "thin" -- it only asks
for input, calls functions from the other modules, and prints results.
All the real logic lives in validation.py / storage.py / transactions.py
/ reports.py / budgets.py.
"""

from finance_tracker import storage, transactions, reports, budgets
from finance_tracker.validation import ValidationError


def add_income():
    source = input("Income source: ")
    amount = input("Amount: ")
    date = input("Date (YYYY-MM-DD): ")
    try:
        t = transactions.add_transaction("income", source, amount, date)
        print(f"Added income #{t['id']}.")
    except ValidationError as e:
        print(f"Could not add income: {e}")


def add_expense():
    category = input("Expense category: ")
    amount = input("Amount: ")
    date = input("Date (YYYY-MM-DD): ")
    try:
        t = transactions.add_transaction("expense", category, amount, date)
        print(f"Added expense #{t['id']}.")
    except ValidationError as e:
        print(f"Could not add expense: {e}")


def view_records():
    all_transactions, errors = storage.load_transactions()

    for msg in errors:
        print(f"[WARNING] {msg}")

    if not all_transactions:
        print("No transactions yet.")
        return

    for t in all_transactions:
        label = "INCOME " if t["type"] == "income" else "EXPENSE"
        print(f"[{t['id']}] {label} {t['amount']} - {t['category_or_source']} - {t['date']}")

    total_income = sum((t["amount"] for t in all_transactions if t["type"] == "income"), start=type(all_transactions[0]["amount"])(0))
    total_expense = sum((t["amount"] for t in all_transactions if t["type"] == "expense"), start=type(all_transactions[0]["amount"])(0))
    print("-" * 40)
    print(f"Total income:  {total_income}")
    print(f"Total expense: {total_expense}")
    print(f"Balance:       {total_income - total_expense}")


def edit_record():
    try:
        transaction_id = int(input("ID to edit: "))
    except ValueError:
        print("ID must be a number.")
        return

    print("Leave a field blank to keep it unchanged.")
    amount = input("New amount: ").strip() or None
    category_or_source = input("New category/source: ").strip() or None
    date = input("New date (YYYY-MM-DD): ").strip() or None

    try:
        transactions.edit_transaction(transaction_id, amount, category_or_source, date)
        print("Updated.")
    except (ValidationError, ValueError) as e:
        print(f"Could not edit: {e}")


def delete_record():
    try:
        transaction_id = int(input("ID to delete: "))
    except ValueError:
        print("ID must be a number.")
        return

    try:
        transactions.delete_transaction(transaction_id)
        print("Deleted.")
    except ValueError as e:
        print(f"Could not delete: {e}")


def monthly_report():
    year_month = input("Month to report (YYYY-MM): ").strip()
    all_transactions, _errors = storage.load_transactions()

    income, expense, balance = reports.monthly_summary(all_transactions, year_month)
    print(f"\n--- Report for {year_month} ---")
    print(f"Income:  {income}")
    print(f"Expense: {expense}")
    print(f"Balance: {balance}")

    by_category = reports.expenses_by_category(all_transactions, year_month)
    if by_category:
        print("\nExpenses by category:")
        for category, total in by_category.items():
            print(f"  {category}: {total}")


def set_budget():
    year_month = input("Month (YYYY-MM): ").strip()
    category = input("Category: ")
    amount = input("Budget amount: ")
    try:
        budgets.set_budget(year_month, category, amount)
        print("Budget saved.")
    except ValidationError as e:
        print(f"Could not save budget: {e}")


def budget_report():
    year_month = input("Month (YYYY-MM): ").strip()
    all_transactions, _errors = storage.load_transactions()
    results = budgets.compare_budget_to_actual(all_transactions, year_month)

    if not results:
        print("No budgets set for this month.")
        return

    for r in results:
        status = "OVER" if r["remaining"] < 0 else "OK"
        print(f"{r['category']}: budget={r['budget']} actual={r['actual']} remaining={r['remaining']} [{status}]")


MENU = {
    "1": ("Add income", add_income),
    "2": ("Add expense", add_expense),
    "3": ("View records", view_records),
    "4": ("Edit a transaction", edit_record),
    "5": ("Delete a transaction", delete_record),
    "6": ("Monthly report", monthly_report),
    "7": ("Set a budget", set_budget),
    "8": ("Budget vs actual report", budget_report),
    "9": ("Exit", None),
}


def main():
    while True:
        print("\n--- Personal Finance Tracker ---")
        for key, (label, _fn) in MENU.items():
            print(f"{key}. {label}")

        choice = input("Choose an option: ").strip()

        if choice == "9":
            print("Goodbye!")
            break

        entry = MENU.get(choice)
        if entry is None:
            print("Invalid choice.")
            continue

        _label, fn = entry
        fn()


if __name__ == "__main__":
    main()