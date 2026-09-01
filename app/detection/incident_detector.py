from collections import defaultdict
from datetime import timedelta

from app.models import PaymentEvent


GATEWAY_WINDOW_MINUTES = 5
GATEWAY_FAILURE_THRESHOLD = 10

BANK_WINDOW_MINUTES = 10
BANK_FAILURE_THRESHOLD = 10


def detect_gateway_incidents(
    events: list[PaymentEvent]
) -> list[dict]:
    """
    Detect gateway-wide failure spikes.

    A gateway is considered degraded when multiple
    gateway timeout events occur within a short window.
    """

    gateway_events = defaultdict(list)

    for event in events:

        if event.status != "GATEWAY_TIMEOUT":
            continue

        payload = event.payload or {}

        gateway = payload.get("gateway")

        if not gateway:
            continue

        gateway_events[gateway].append(event)

    incidents = []

    for gateway, failures in gateway_events.items():

        failures.sort(
            key=lambda event: event.created_at
        )

        for i, start_event in enumerate(failures):

            window_end = (
                start_event.created_at
                + timedelta(
                    minutes=GATEWAY_WINDOW_MINUTES
                )
            )

            affected = [
                event
                for event in failures[i:]
                if event.created_at <= window_end
            ]

            if len(affected) >= GATEWAY_FAILURE_THRESHOLD:

                incidents.append({
                    "incident_type":
                        "GATEWAY_INCIDENT",

                    "provider":
                        gateway,

                    "failure_count":
                        len(affected),

                    "revenue_at_risk":
                        sum(
                            event.amount or 0
                            for event in affected
                        ),

                    "start_time":
                        start_event.created_at,

                    "end_time":
                        affected[-1].created_at,

                    "payment_ids": [
                        event.payment_id
                        for event in affected
                    ]
                })

                break

    return incidents


def detect_bank_incidents(
    events: list[PaymentEvent]
) -> list[dict]:
    """
    Detect bank-wide timeout spikes.
    """

    bank_events = defaultdict(list)

    for event in events:

        if event.status != "BANK_TIMEOUT":
            continue

        payload = event.payload or {}

        bank = payload.get("bank")

        if not bank:
            continue

        bank_events[bank].append(event)

    incidents = []

    for bank, failures in bank_events.items():

        failures.sort(
            key=lambda event: event.created_at
        )

        for i, start_event in enumerate(failures):

            window_end = (
                start_event.created_at
                + timedelta(
                    minutes=BANK_WINDOW_MINUTES
                )
            )

            affected = [
                event
                for event in failures[i:]
                if event.created_at <= window_end
            ]

            if len(affected) >= BANK_FAILURE_THRESHOLD:

                incidents.append({
                    "incident_type":
                        "BANK_INCIDENT",

                    "provider":
                        bank,

                    "failure_count":
                        len(affected),

                    "revenue_at_risk":
                        sum(
                            event.amount or 0
                            for event in affected
                        ),

                    "start_time":
                        start_event.created_at,

                    "end_time":
                        affected[-1].created_at,

                    "payment_ids": [
                        event.payment_id
                        for event in affected
                    ]
                })

                break

    return incidents


def detect_incidents(
    events: list[PaymentEvent]
) -> dict:

    gateway_incidents = detect_gateway_incidents(
        events
    )

    bank_incidents = detect_bank_incidents(
        events
    )

    return {
        "gateway_incidents":
            gateway_incidents,

        "bank_incidents":
            bank_incidents,

        "total_incidents":
            len(gateway_incidents)
            + len(bank_incidents)
    }