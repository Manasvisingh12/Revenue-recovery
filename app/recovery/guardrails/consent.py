CONTACT_ACTIONS = [
    "MESSAGE"
]


def check_customer_consent(
    case,
    action: str
) -> dict:

    if action not in CONTACT_ACTIONS:

        return {
            "allowed": True,
            "reason":
                "Customer consent is not required for this action."
        }

    if case.customer_consent is True:

        return {
            "allowed": True,
            "reason":
                "Customer has consented to contact."
        }

    return {
        "allowed": False,
        "reason":
            "Customer consent is required before contact."
    }