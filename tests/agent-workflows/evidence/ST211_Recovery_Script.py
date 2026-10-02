"""ST-000211 scenario tests (SC-01..SC-07) for pricing.shipping_fee_cents.

Run from the repository root:
    python -m unittest discover -s tests/feature/ST-000211/scripts -t .
    python tests/feature/ST-000211/scripts/test_st_000211_scenarios.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import pricing  # noqa: E402


class StandardShippingScenarios(unittest.TestCase):
    def test_sc01_standard_below_threshold(self):
        self.assertEqual(pricing.shipping_fee_cents(4999), 500)

    def test_sc02_standard_at_threshold(self):
        self.assertEqual(pricing.shipping_fee_cents(5000), 0)

    def test_sc03_standard_above_threshold(self):
        self.assertEqual(pricing.shipping_fee_cents(5001), 0)

    def test_sc04_standard_zero_subtotal(self):
        self.assertEqual(pricing.shipping_fee_cents(0), 500)


class ExpressShippingScenarios(unittest.TestCase):
    def test_sc05_express_below_threshold(self):
        self.assertEqual(pricing.shipping_fee_cents(4999, express=True), 1200)

    def test_sc06_express_at_threshold(self):
        self.assertEqual(pricing.shipping_fee_cents(5000, express=True), 1200)

    def test_sc07_express_above_threshold(self):
        self.assertEqual(pricing.shipping_fee_cents(5001, express=True), 1200)


if __name__ == "__main__":
    unittest.main()
