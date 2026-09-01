import random
import uuid
from datetime import datetime, timedelta, timezone


# ============================================================
# CONFIGURATION
# ============================================================

NUM_PAYMENT_EVENTS = 520
NUM_CHECKOUT_SESSIONS = 200

MERCHANTS = [
    "merchant_001",
    "merchant_002",
    "merchant_003",
    "merchant_004",
    "merchant_005",
]

BANKS = [
    "HDFC",
    "ICICI",
    "SBI",
    "AXIS",
    "KOTAK",
]

GATEWAYS = [
    "gateway_primary",
    "gateway_secondary",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_id(prefix: str) -> str:
    """Generate a unique identifier."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def random_amount() -> int:
    """Generate realistic INR payment amounts."""
    return random.choice([
        199,
        299,
        499,
        799,
        999,
        1299,
        1499,
        1999,
        2499,
        2999,
        4999,
        9999,
        14999,
        24999,
    ])


# ============================================================
# PAYMENT EVENTS
# ============================================================

def generate_payment_events():
    """
    Generate 500 payment events.

    Distribution:

SUCCESS              330
INSUFFICIENT_FUNDS    55
GATEWAY_TIMEOUT       40
BANK_TIMEOUT          30
CARD_EXPIRED          20
DUPLICATE_EVENT       25
UNKNOWN_ERROR         10
TEMPORARY_AUTH_ERROR  10

    Special pattern:

    30 GATEWAY_TIMEOUT events happen within 5 minutes.
    """

    events = []
    successful_events = []

    # --------------------------------------------------------
    # Base timeline
    # --------------------------------------------------------

    base_time = datetime.now(timezone.utc) - timedelta(hours=2)

    # --------------------------------------------------------
    # SUCCESS EVENTS - 330
    # --------------------------------------------------------

    for _ in range(330):

        payment_id = generate_id("pay")

        event = {
            "event_id": generate_id("evt"),
            "merchant_id": random.choice(MERCHANTS),
            "event_type": "payment.success",
            "payment_id": payment_id,
            "status": "SUCCESS",
            "amount": random_amount(),
            "payload": {
                "customer_id": generate_id("cust"),
                "gateway": random.choice(GATEWAYS),
                "bank": random.choice(BANKS),
                "currency": "INR",
            },
            "created_at": base_time + timedelta(
                seconds=random.randint(0, 7200)
            ),
        }

        events.append(event)
        successful_events.append(event)

    # --------------------------------------------------------
    # INSUFFICIENT FUNDS - 55
    # --------------------------------------------------------

    for _ in range(55):

        event = {
            "event_id": generate_id("evt"),
            "merchant_id": random.choice(MERCHANTS),
            "event_type": "payment.failed",
            "payment_id": generate_id("pay"),
            "status": "INSUFFICIENT_FUNDS",
            "amount": random_amount(),
            "payload": {
                "customer_id": generate_id("cust"),
                "gateway": random.choice(GATEWAYS),
                "bank": random.choice(BANKS),
                "currency": "INR",
                "failure_category": "CUSTOMER",
            },
            "created_at": base_time + timedelta(
                seconds=random.randint(0, 7200)
            ),
        }

        events.append(event)

    # --------------------------------------------------------
    # GATEWAY TIMEOUT - 10 NORMAL
    # --------------------------------------------------------

    for _ in range(10):

        event = {
            "event_id": generate_id("evt"),
            "merchant_id": random.choice(MERCHANTS),
            "event_type": "payment.failed",
            "payment_id": generate_id("pay"),
            "status": "GATEWAY_TIMEOUT",
            "amount": random_amount(),
            "payload": {
                "customer_id": generate_id("cust"),
                "gateway": random.choice(GATEWAYS),
                "bank": random.choice(BANKS),
                "currency": "INR",
                "failure_category": "INFRASTRUCTURE",
            },
            "created_at": base_time + timedelta(
                seconds=random.randint(0, 7200)
            ),
        }

        events.append(event)

    # --------------------------------------------------------
    # CRITICAL PATTERN:
    #
    # 30 GATEWAY_TIMEOUT EVENTS IN 5 MINUTES
    # --------------------------------------------------------

    outage_start = base_time + timedelta(hours=1)

    for i in range(30):

        event = {
            "event_id": generate_id("evt"),
            "merchant_id": random.choice(MERCHANTS),
            "event_type": "payment.failed",
            "payment_id": generate_id("pay"),
            "status": "GATEWAY_TIMEOUT",
            "amount": random_amount(),
            "payload": {
                "customer_id": generate_id("cust"),
                "gateway": "gateway_primary",
                "bank": random.choice(BANKS),
                "currency": "INR",
                "failure_category": "INFRASTRUCTURE",
                "incident": "gateway_outage_simulation",
            },
            "created_at": outage_start + timedelta(
                seconds=random.randint(0, 299)
            ),
        }

        events.append(event)

    # --------------------------------------------------------
    # BANK TIMEOUT - 30
    # --------------------------------------------------------

    bank_spike_start = base_time + timedelta(hours=1, minutes=30)

    for i in range(30):

        event = {
            "event_id": generate_id("evt"),
            "merchant_id": random.choice(MERCHANTS),
            "event_type": "payment.failed",
            "payment_id": generate_id("pay"),
            "status": "BANK_TIMEOUT",
            "amount": random_amount(),
            "payload": {
                "customer_id": generate_id("cust"),
                "gateway": random.choice(GATEWAYS),
                "bank": "HDFC",
                "currency": "INR",
                "failure_category": "INFRASTRUCTURE",
                "incident": "bank_timeout_spike",
            },
            "created_at": bank_spike_start + timedelta(
                seconds=random.randint(0, 599)
            ),
        }

        events.append(event)

    # --------------------------------------------------------
    # CARD EXPIRED - 20
    # --------------------------------------------------------

    for _ in range(20):

        event = {
            "event_id": generate_id("evt"),
            "merchant_id": random.choice(MERCHANTS),
            "event_type": "payment.failed",
            "payment_id": generate_id("pay"),
            "status": "CARD_EXPIRED",
            "amount": random_amount(),
            "payload": {
                "customer_id": generate_id("cust"),
                "gateway": random.choice(GATEWAYS),
                "bank": random.choice(BANKS),
                "currency": "INR",
                "failure_category": "CUSTOMER",
            },
            "created_at": base_time + timedelta(
                seconds=random.randint(0, 7200)
            ),
        }

        events.append(event)
    # --------------------------------------------------------
    # UNKNOWN ERROR - 10
    #
    # These events have no deterministic rule.
    # They must be routed to the AI classifier.
    # --------------------------------------------------------

    for _ in range(10):

        event = {
            "event_id": generate_id("evt"),
            "merchant_id": random.choice(MERCHANTS),
            "event_type": "payment.failed",
            "payment_id": generate_id("pay"),
            "status": "UNKNOWN_ERROR",
            "amount": random_amount(),
            "payload": {
                "customer_id": generate_id("cust"),
                "gateway": random.choice(GATEWAYS),
                "bank": random.choice(BANKS),
                "currency": "INR",
                "failure_category": "UNKNOWN",
            },
            "created_at": base_time + timedelta(
                seconds=random.randint(0, 7200)
            ),
        }

        events.append(event)
        # --------------------------------------------------------
    # TEMPORARY AUTH ERROR - 10
    #
    # No deterministic rule exists for this failure.
    # The AI classifier should identify it as a
    # potentially recoverable SOFT_FAILURE.
    # --------------------------------------------------------

    for _ in range(10):

        event = {
            "event_id": generate_id("evt"),
            "merchant_id": random.choice(MERCHANTS),
            "event_type": "payment.failed",
            "payment_id": generate_id("pay"),
            "status": "TEMPORARY_AUTH_ERROR",
            "amount": random_amount(),
            "payload": {
                "customer_id": generate_id("cust"),
                "gateway": random.choice(GATEWAYS),
                "bank": random.choice(BANKS),
                "currency": "INR",
                "failure_category": "UNKNOWN",
            },
            "created_at": base_time + timedelta(
                seconds=random.randint(0, 7200)
            ),
        }

        events.append(event)

    # --------------------------------------------------------
    # DUPLICATE EVENTS - 25
    #
    # These deliberately reuse payment_ids from SUCCESS
    # payments so they represent TRUE duplicate events.
    # --------------------------------------------------------

    successful_payments = [
        event
        for event in events
        if event["status"] == "SUCCESS"
    ]

    duplicate_sources = random.sample(
        successful_payments,
        25
    )

    for source_event in duplicate_sources:

        event = {
            "event_id": generate_id("evt"),
            "merchant_id": source_event["merchant_id"],
            "event_type": "payment.duplicate",
            "payment_id": source_event["payment_id"],
            "status": "DUPLICATE_EVENT",
            "amount": source_event["amount"],
            "payload": {
                "customer_id": source_event["payload"]["customer_id"],
                "gateway": source_event["payload"]["gateway"],
                "bank": source_event["payload"]["bank"],
                "currency": "INR",
                "failure_category": "PROCESSING",
                "duplicate_of": source_event["event_id"],
            },
            "created_at": source_event["created_at"] + timedelta(
                seconds=random.randint(1, 30)
            ),
        }

        events.append(event)

    # --------------------------------------------------------
    # Shuffle events
    # --------------------------------------------------------

    random.shuffle(events)

    return events


# ============================================================
# CHECKOUT SESSIONS
# ============================================================

def generate_checkout_sessions():
    """
    Generate 200 checkout sessions.

    140 COMPLETED
    60 CHECKOUT_ABANDONED
    """

    sessions = []

    base_time = datetime.now(timezone.utc) - timedelta(hours=2)

    # --------------------------------------------------------
    # COMPLETED - 140
    # --------------------------------------------------------

    for _ in range(140):

        started_at = base_time + timedelta(
            seconds=random.randint(0, 7200)
        )

        completed_at = started_at + timedelta(
            seconds=random.randint(10, 300)
        )

        session = {
            "session_id": generate_id("session"),
            "merchant_id": random.choice(MERCHANTS),
            "customer_id": generate_id("cust"),
            "amount": random_amount(),
            "status": "COMPLETED",
            "started_at": started_at,
            "completed_at": completed_at,
            "session_metadata": {
                "device": random.choice([
                    "mobile",
                    "desktop",
                    "tablet",
                ]),
                "browser": random.choice([
                    "chrome",
                    "safari",
                    "firefox",
                ]),
            },
        }

        sessions.append(session)

    # --------------------------------------------------------
    # ABANDONED - 60
    # --------------------------------------------------------

    for _ in range(60):

        started_at = base_time + timedelta(
            seconds=random.randint(0, 7200)
        )

        # Some deliberately high-value abandoned checkouts
        amount = random.choice([
            499,
            999,
            1999,
            4999,
            9999,
            14999,
            24999,
        ])

        session = {
            "session_id": generate_id("session"),
            "merchant_id": random.choice(MERCHANTS),
            "customer_id": generate_id("cust"),
            "amount": amount,
            "status": "CHECKOUT_ABANDONED",
            "started_at": started_at,
            "completed_at": None,
            "session_metadata": {
                "device": random.choice([
                    "mobile",
                    "desktop",
                    "tablet",
                ]),
                "browser": random.choice([
                    "chrome",
                    "safari",
                    "firefox",
                ]),
                "abandonment_reason": random.choice([
                    "timeout",
                    "user_exit",
                    "payment_page_exit",
                    "unknown",
                ]),
            },
        }

        sessions.append(session)

    random.shuffle(sessions)

    return sessions


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    payments = generate_payment_events()
    sessions = generate_checkout_sessions()

    print(f"Generated payment events: {len(payments)}")
    print(f"Generated checkout sessions: {len(sessions)}")

    print("\nPayment status distribution:")

    from collections import Counter

    payment_counts = Counter(
        event["status"]
        for event in payments
    )

    for status, count in payment_counts.items():
        print(f"{status}: {count}")

    print("\nCheckout status distribution:")

    checkout_counts = Counter(
        session["status"]
        for session in sessions
    )

    for status, count in checkout_counts.items():
        print(f"{status}: {count}")