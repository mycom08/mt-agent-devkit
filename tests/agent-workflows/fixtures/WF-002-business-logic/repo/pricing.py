"""Shipping fee rules for the WF-002 benchmark fixture."""

FREE_STANDARD_SHIPPING_THRESHOLD_CENTS = 5_000
STANDARD_SHIPPING_CENTS = 500
EXPRESS_SHIPPING_CENTS = 1_200


def shipping_fee_cents(subtotal_cents: int, *, express: bool = False) -> int:
    """Return the shipping fee for an already validated order subtotal."""
    if express:
        return EXPRESS_SHIPPING_CENTS
    if subtotal_cents > FREE_STANDARD_SHIPPING_THRESHOLD_CENTS:
        return 0
    return STANDARD_SHIPPING_CENTS
