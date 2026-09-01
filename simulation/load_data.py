from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models import (
    PaymentEvent,
    CheckoutSession,
)

from simulation.generator import (
    generate_payment_events,
    generate_checkout_sessions,
)


def load_payment_events(
    db: Session,
    events: list[dict]
):
    """Insert payment events in one batch."""

    payment_objects = [
        PaymentEvent(
            event_id=event["event_id"],
            merchant_id=event["merchant_id"],
            event_type=event["event_type"],
            payment_id=event["payment_id"],
            status=event["status"],
            amount=event["amount"],
            payload=event["payload"],
            created_at=event["created_at"],
        )
        for event in events
    ]

    db.add_all(payment_objects)

    print(
        f"✓ Prepared {len(payment_objects)} payment events"
    )


def load_checkout_sessions(
    db: Session,
    sessions: list[dict]
):
    """Insert checkout sessions in one batch."""

    session_objects = [
        CheckoutSession(
            session_id=session["session_id"],
            merchant_id=session["merchant_id"],
            customer_id=session["customer_id"],
            amount=session["amount"],
            status=session["status"],
            started_at=session["started_at"],
            completed_at=session["completed_at"],
            session_metadata=session["session_metadata"],
        )
        for session in sessions
    ]

    db.add_all(session_objects)

    print(
        f"✓ Prepared {len(session_objects)} checkout sessions"
    )


def main():

    print("=" * 60)
    print("REVENUE EVENT SIMULATOR")
    print("=" * 60)

    # --------------------------------------------------------
    # Generate data
    # --------------------------------------------------------

    print("\nGenerating payment events...")

    payment_events = generate_payment_events()

    print(
        f"✓ Generated {len(payment_events)} payment events"
    )

    print("\nGenerating checkout sessions...")

    checkout_sessions = generate_checkout_sessions()

    print(
        f"✓ Generated {len(checkout_sessions)} checkout sessions"
    )

    # --------------------------------------------------------
    # Connect to PostgreSQL
    # --------------------------------------------------------

    print("\nConnecting to PostgreSQL...")

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # Insert payment events
        # ----------------------------------------------------

        load_payment_events(
            db,
            payment_events
        )

        # ----------------------------------------------------
        # Insert checkout sessions
        # ----------------------------------------------------

        load_checkout_sessions(
            db,
            checkout_sessions
        )

        # ----------------------------------------------------
        # Commit everything together
        # ----------------------------------------------------

        db.commit()

        print("\n✓ Database transaction committed")

        print("\n" + "=" * 60)
        print("PHASE 1 DATA LOAD COMPLETE")
        print("=" * 60)

        print(
            f"\nPayment events:     {len(payment_events)}"
        )

        print(
            f"Checkout sessions:  {len(checkout_sessions)}"
        )

    except Exception as e:

        db.rollback()

        print("\n✗ ERROR")
        print(e)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()