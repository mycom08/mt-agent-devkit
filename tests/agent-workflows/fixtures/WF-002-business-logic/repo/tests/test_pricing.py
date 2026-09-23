import unittest

from pricing import shipping_fee_cents


class ShippingFeeTests(unittest.TestCase):
    def test_standard_below_threshold(self):
        self.assertEqual(shipping_fee_cents(4_999), 500)

    def test_standard_at_threshold(self):
        self.assertEqual(shipping_fee_cents(5_000), 0)

    def test_standard_above_threshold(self):
        self.assertEqual(shipping_fee_cents(5_001), 0)

    def test_express_below_threshold(self):
        self.assertEqual(shipping_fee_cents(4_999, express=True), 1_200)

    def test_express_at_threshold(self):
        self.assertEqual(shipping_fee_cents(5_000, express=True), 1_200)

    def test_express_above_threshold(self):
        self.assertEqual(shipping_fee_cents(5_001, express=True), 1_200)


if __name__ == "__main__":
    unittest.main()
