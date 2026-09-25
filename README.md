# Personal Finance Tracker

A command-line application for tracking personal income and expenses,
built in pure Python. Data is stored in CSV files, with automatic
backups before any change and validation on every input.

## Features

- Add income and expenses
- Edit and delete transactions by ID (IDs never change or get reused)
- View all records with a running total
- Monthly reports (income, expense, balance, breakdown by category)
- Monthly, per-category budgets with a budget-vs-actual comparison
- Automatic backup before every change to the data
- Input validation: amounts (positive, max 2 decimal places), dates
  (real calendar dates only), and case-insensitive categories
- Graceful handling of corrupted rows in the data file

## Requirements

- Python 3.8 or newer
- No external libraries needed -- everything uses the Python standard
  library (`csv`, `decimal`, `datetime`, `unittest`)

## Project Structure

```
personal_finance_tracker/
├── main.py                     # CLI menu -- entry point
├── finance_tracker/
│   ├── __init__.py
│   ├── validation.py           # input validation (amount, date, category)
│   ├── id_generator.py         # persistent, never-reused transaction IDs
│   ├── storage.py              # CSV read/write + backups
│   ├── transactions.py         # add / edit / delete operations
│   ├── reports.py              # monthly filtering and summaries
│   └── budgets.py              # monthly per-category budgets
├── tests/                      # automated tests (unittest)
└── data/                       # created automatically on first run
    ├── transactions.csv
    ├── next_id.txt
    ├── budgets.csv
    └── backups/
```

## Setup

1. Make sure Python 3.8+ is installed:
   ```
   python --version
   ```
2. Download/clone this project, keeping the folder structure above intact.
3. No installation step is needed -- there are no external dependencies.

## Usage

From inside the project's root folder (where `main.py` lives), run:

```
python main.py
```

(On some systems the command is `python3 main.py` instead.)

You'll see a menu:

```
--- Personal Finance Tracker ---
1. Add income
2. Add expense
3. View records
4. Edit a transaction
5. Delete a transaction
6. Monthly report
7. Set a budget
8. Budget vs actual report
9. Exit
```

Pick a number and follow the prompts. Data is saved automatically to
the `data/` folder, which is created the first time you add something.

### Examples

**Adding an expense:**
```
Choose an option: 2
Expense category: Food
Amount: 45.50
Date (YYYY-MM-DD): 2026-09-05
Added expense #1.
```

**Viewing a monthly report:**
```
Choose an option: 6
Month to report (YYYY-MM): 2026-09

--- Report for 2026-09 ---
Income:  1000
Expense: 45.50
Balance: 954.50

Expenses by category:
  food: 45.50
```

## Running the Tests

From the project's root folder:

```
python -m unittest discover -s tests -v
```

This runs 24 automated tests covering:
- amount validation (rejects negative, zero, and 3+ decimal places)
- date validation (rejects impossible calendar dates like Feb 29 on a
  non-leap year)
- case-insensitive category matching
- unique, never-reused transaction IDs (even after deletions)
- CSV storage, including fields that contain commas
- corrupted-row handling (bad rows are skipped, not crashed on)
- backups capturing the pre-change state
- monthly filtering (exact month boundaries)
- add / edit / delete behavior

## Notes on Design Decisions

- **Money is stored as `Decimal`, not `float`**, to avoid floating-point
  rounding errors in financial totals.
- **Transaction IDs** are generated from a separate counter file that
  only ever increases, so deleting the highest-numbered transaction
  never causes an ID to be reused.
- **Dates are validated with `datetime.strptime`**, which already knows
  the real calendar (leap years included), so no manual leap-year
  logic is needed.
- **CSV fields are read/written with Python's `csv` module**, not
  manual string splitting, so fields containing commas (e.g. "Salary,
  Company XYZ") are stored and loaded correctly.
- **Backups are taken before a change is written**, so a backup file
  always reflects the data as it was immediately before that change.