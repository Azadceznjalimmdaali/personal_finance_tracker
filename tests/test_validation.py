import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from decimal import Decimal
from finance_tracker.validation import (
    parse_amount,
    parse_date,
    normalize_category,
    ValidationError,
)


class TestParseAmount(unittest.TestCase):

    def test_accepts_two_decimal_places(self):
        self.assertEqual(parse_amount("100.50"), Decimal("100.50"))

    def test_accepts_whole_number(self):
        self.assertEqual(parse_amount("100"), Decimal("100"))

    def test_rejects_three_decimal_places(self):
        with self.assertRaises(ValidationError):
            parse_amount("100.505")

    def test_rejects_zero(self):
        with self.assertRaises(ValidationError):
            parse_amount("0")

    def test_rejects_negative(self):
        with self.assertRaises(ValidationError):
            parse_amount("-5")

    def test_rejects_non_numeric(self):
        with self.assertRaises(ValidationError):
            parse_amount("abc")


class TestParseDate(unittest.TestCase):

    def test_accepts_valid_leap_year_date(self):
        self.assertEqual(parse_date("2028-02-29"), "2028-02-29")

    def test_rejects_invalid_leap_year_date(self):
        with self.assertRaises(ValidationError):
            parse_date("2027-02-29")

    def test_rejects_wrong_format(self):
        with self.assertRaises(ValidationError):
            parse_date("29-02-2028")

    def test_rejects_nonsense(self):
        with self.assertRaises(ValidationError):
            parse_date("not-a-date")


class TestNormalizeCategory(unittest.TestCase):

    def test_is_case_insensitive(self):
        self.assertEqual(normalize_category("Food"), normalize_category("FOOD"))
        self.assertEqual(normalize_category("Food"), normalize_category("food"))

    def test_rejects_empty(self):
        with self.assertRaises(ValidationError):
            normalize_category("   ")


if __name__ == "__main__":
    unittest.main()