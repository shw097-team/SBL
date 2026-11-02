from decimal import Decimal
from src.demo.billing import total


def test_total_rounds_once_on_the_invoice_total():
    # three lines of 0.005 must sum to 0.015 -> 0.02, not 3 * 0.01 = 0.03
    lines = [("0.005", 1), ("0.005", 1), ("0.005", 1)]
    assert total(lines) == Decimal("0.02")


def test_total_keeps_exact_cents():
    assert total([("1.23", 2), ("0.02", 1)]) == Decimal("2.48")
