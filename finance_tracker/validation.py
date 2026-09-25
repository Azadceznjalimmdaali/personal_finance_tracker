"""
Validation utilities for the Personal Finance Tracker.

This module turns raw user input (always strings, since it comes from
the CLI or a file) into safe, correctly-typed values, and raises a
ValidationError with a clear message whenever the input is invalid.

Keeping validation in its own module (separate from the CLI menu and
from storage) means:
- we can unit test it without touching the filesystem or the terminal
- the same rules apply whether the data came from a user prompt or
  from a line we just read back out of a file
"""

from decimal import Decimal, InvalidOperation
from datetime import datetime


class ValidationError(ValueError):
    """Raised when user-provided data fails a validation rule."""
    pass


def parse_amount(raw: str) -> Decimal:
    """
    Convert a raw string into a validated Decimal amount.

    Rules:
    - must be a valid number
    - must be strictly greater than zero
    - must have at most 2 decimal places

    We use Decimal instead of float everywhere money is involved.
    float represents numbers in binary, so values like 0.1 or 0.2 can't
    be stored exactly -- 0.1 + 0.2 == 0.30000000000000004 in real Python.
    That's fine for most math, but it silently corrupts financial totals.
    Decimal stores the digits exactly as written, so this problem
    doesn't happen.
    """
    raw = raw.strip()
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        raise ValidationError(f"'{raw}' is not a valid number")

    if amount <= 0:
        raise ValidationError("Amount must be greater than zero")

    # Decimal remembers exactly how it was written. as_tuple().exponent
    # tells us how many digits come after the decimal point:
    #   Decimal("100.50").as_tuple()  -> exponent = -2  (2 decimal places)
    #   Decimal("100.505").as_tuple() -> exponent = -3  (3 decimal places)
    #   Decimal("100").as_tuple()     -> exponent =  0  (0 decimal places)
    exponent = amount.as_tuple().exponent
    if exponent < -2:
        raise ValidationError("Amount must have at most 2 decimal places")

    return amount


def parse_date(raw: str) -> str:
    """
    Validate a date string in YYYY-MM-DD format.

    Returns the same string back if it's valid (we store dates as
    plain strings in that format everywhere -- there's no need to
    convert to a datetime object outside of this validation step).

    datetime.strptime already understands the real calendar, so it
    rejects impossible dates like 2027-02-29 (2027 isn't a leap year)
    while accepting valid ones like 2028-02-29 (2028 is a leap year).
    We don't need to write any leap-year logic ourselves.
    """
    raw = raw.strip()
    try:
        datetime.strptime(raw, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(f"'{raw}' is not a valid date in YYYY-MM-DD format")
    return raw


def normalize_category(raw: str) -> str:
    """
    Normalize a category/source name for case-insensitive matching.

    "Food", "food", and "FOOD" must all be treated as the same category
    for budgeting and reporting. The convention used across this project:
    - normalize_category(...) is the KEY used for comparisons, storage
      lookups, and grouping (always lowercase)
    - the original text the user typed can still be kept/displayed as-is
      if you want nicer-looking output later
    """
    raw = raw.strip()
    if not raw:
        raise ValidationError("Category/source cannot be empty")
    return raw.lower()