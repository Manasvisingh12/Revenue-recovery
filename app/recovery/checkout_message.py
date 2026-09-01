from app.models import RecoveryCase


def generate_checkout_message(
    case: RecoveryCase,
    payment_link: str
) -> str:

    amount = case.amount
    currency = case.currency

    return (
        f"Your payment of {currency} {amount} "
        f"could not be completed. "
        f"You can securely complete your payment here: "
        f"{payment_link}"
    )