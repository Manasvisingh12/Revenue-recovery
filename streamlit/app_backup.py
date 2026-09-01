import time
import textwrap

import pandas as pd
import streamlit as st

from api import (
    execute_case,
    get_failure_state,
    get_health,
    get_observability_summary,
    get_recovery_cases,
    inject_failure,
    reset_failures,
    run_pipeline,
)

from styles import load_css


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Revenue Reliability",
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()


# ============================================================
# HTML HELPER
# ============================================================

def html(content):
    cleaned = textwrap.dedent(content).strip()

    st.markdown(
        cleaned,
        unsafe_allow_html=True,
    )


# ============================================================
# HELPERS
# ============================================================

def money(value):
    try:
        return f"₹{float(value or 0):,.0f}"
    except (TypeError, ValueError):
        return "₹0"


def metric_card(label, value, description=""):
    html(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                {label}
            </div>

            <div class="metric-value">
                {value}
            </div>

            <div class="metric-small">
                {description}
            </div>
        </div>
        """
    )


def page_header(
    title,
    subtitle,
    eyebrow="REVENUE RELIABILITY",
):
    html(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">
                {eyebrow}
            </div>

            <div class="hero-title">
                {title}
            </div>

            <div class="hero-subtitle">
                {subtitle}
            </div>
        </div>
        """
    )


def system_strip():
    html(
        """
        <div class="system-strip">

            <div class="system-node">
                <span class="system-dot"></span>
                FASTAPI
            </div>

            <div class="system-node">
                <span class="system-dot"></span>
                POSTGRESQL
            </div>

            <div class="system-node">
                <span class="system-dot"></span>
                AI ENGINE
            </div>

            <div class="system-node">
                <span class="system-dot"></span>
                PROMETHEUS
            </div>

            <div class="system-node">
                <span class="system-dot"></span>
                GRAFANA
            </div>

        </div>
        """
    )


def architecture_footer():
    html(
        """
        <div class="architecture-footer">

            <div class="architecture-title">
                CONTROL PLANE
            </div>

            <div class="system-node">
                <span class="system-dot"></span>
                EVENTS
            </div>

            <div class="system-node">
                <span class="system-dot"></span>
                DETECTION
            </div>

            <div class="system-node">
                <span class="system-dot"></span>
                AI
            </div>

            <div class="system-node">
                <span class="system-dot"></span>
                GUARDRAILS
            </div>

            <div class="system-node">
                <span class="system-dot"></span>
                RECOVERY
            </div>

            <div class="system-node">
                <span class="system-dot"></span>
                OBSERVABILITY
            </div>

        </div>
        """
    )


def safe_summary():
    try:
        return get_observability_summary()
    except Exception as exc:
        st.error(f"API unavailable: {exc}")
        return None


def status_class(value):
    if value in [
        "CLOSED",
        "SUCCESS",
        "HEALTHY",
        "RECOVERED",
    ]:
        return "status-good"

    if value in [
        "HALF_OPEN",
        "WAIT",
        "AT_RISK",
    ]:
        return "status-warning"

    return "status-danger"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    html(
        """
        <div style="
            font-size:26px;
            font-weight:850;
            letter-spacing:-1px;
        ">
            REVENUE
        </div>

        <div style="
            font-size:26px;
            font-weight:850;
            color:#818cf8;
            letter-spacing:-1px;
            margin-bottom:8px;
        ">
            RELIABILITY
        </div>

        <div style="
            color:#64748b;
            font-size:12px;
            margin-bottom:30px;
            line-height:1.5;
        ">
            Autonomous Revenue Recovery Control Plane
        </div>
        """
    )

    page = st.radio(
        "CONTROL ROOM",
        [
            "Command Center",
            "Live Batch",
            "Recovery Case",
            "Failure Lab",
        ],
    )

    st.divider()

    try:
        health = get_health()

        if health.get("status") == "healthy":
            html(
                """
                <span class="status-good">
                    ● SYSTEM HEALTHY
                </span>
                """
            )
        else:
            html(
                """
                <span class="status-warning">
                    ● DEGRADED
                </span>
                """
            )

    except Exception:
        html(
            """
            <span class="status-danger">
                ● API OFFLINE
            </span>
            """
        )


# ============================================================
# PAGE 1 — COMMAND CENTER
# ============================================================

if page == "Command Center":

    page_header(
        "Revenue Command Center",
        "Real-time revenue exposure, autonomous recovery performance and reliability intelligence.",
    )

    system_strip()

    summary = safe_summary()

    if summary:

        revenue = summary.get("revenue", {})
        recovery = summary.get("recovery", {})
        reliability = summary.get("reliability", {})
        ai = summary.get("ai_decisions", {})

        # ----------------------------------------------------
        # TOP METRICS
        # ----------------------------------------------------

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            metric_card(
                "Revenue At Risk",
                money(revenue.get("at_risk")),
                "Currently exposed",
            )

        with col2:
            metric_card(
                "Recovered",
                money(revenue.get("recovered")),
                "Revenue successfully won back",
            )

        with col3:
            metric_card(
                "Recovery Success",
                f"{float(recovery.get('success_rate_percent') or 0):.1f}%",
                "Successful recovery attempts",
            )

        with col4:
            metric_card(
                "Execution Latency",
                f"{float(reliability.get('average_latency_seconds') or 0):.3f}s",
                "Average recovery execution",
            )

        with col5:

            breaker = reliability.get(
                "circuit_breaker",
                "UNKNOWN",
            )

            html(
                f"""
                <div class="metric-card">

                    <div class="metric-label">
                        Circuit Breaker
                    </div>

                    <div style="margin-top:20px">

                        <span class="{status_class(breaker)}">
                            ● {breaker}
                        </span>

                    </div>

                    <div class="metric-small">
                        Recovery execution safety state
                    </div>

                </div>
                """
            )

        st.write("")

        # ----------------------------------------------------
        # AI DISTRIBUTION + CHART
        # ----------------------------------------------------

        left, right = st.columns([1.2, 1])

        with left:

            html(
                """
                <div class="panel">

                    <div class="panel-title">
                        AI Recovery Intelligence
                    </div>

                    <div class="panel-description">
                        How autonomous recovery intelligence is routing revenue cases.
                    </div>

                </div>
                """
            )

            if ai:

                clean_ai = {}

                for action, count in ai.items():

                    try:
                        numeric_count = float(count)

                        if pd.notna(numeric_count):
                            clean_ai[str(action)] = numeric_count

                    except (TypeError, ValueError):
                        continue

                if clean_ai:

                    decision_df = pd.DataFrame(
                        {
                            "Action": list(clean_ai.keys()),
                            "Cases": list(clean_ai.values()),
                        }
                    )

                    decision_df = decision_df.sort_values(
                        "Cases",
                        ascending=False,
                    )

                    st.bar_chart(
                        decision_df.set_index("Action")
                    )

                else:
                    st.info(
                        "No AI decision data available yet."
                    )

            else:
                st.info(
                    "No AI decisions available yet."
                )

        with right:

            html(
                """
                <div class="panel">

                    <div class="panel-title">
                        Decision Summary
                    </div>

                    <div class="panel-description">
                        Current AI recommendation volume.
                    </div>

                </div>
                """
            )

            if ai:

                sorted_ai = sorted(
                    ai.items(),
                    key=lambda item: (
                        float(item[1])
                        if str(item[1]).replace(".", "", 1).isdigit()
                        else 0
                    ),
                    reverse=True,
                )

                for action, count in sorted_ai:

                    html(
                        f"""
                        <div class="decision-card">

                            <div class="decision-label">
                                {action}
                            </div>

                            <div class="decision-value">
                                {count}
                            </div>

                        </div>
                        """
                    )

        # ----------------------------------------------------
        # RECOVERY FUNNEL
        # ----------------------------------------------------

        html(
            """
            <div class="panel">

                <div class="panel-title">
                    Revenue Reliability Pipeline
                </div>

                <div class="panel-description">
                    The complete journey from revenue incident to verified recovery.
                </div>

                <div class="funnel-container">

                    <div class="funnel-step">
                        <div class="funnel-number">01</div>
                        <div class="funnel-title">EVENTS</div>
                    </div>

                    <div class="funnel-step">
                        <div class="funnel-number">02</div>
                        <div class="funnel-title">DETECTION</div>
                    </div>

                    <div class="funnel-step">
                        <div class="funnel-number">03</div>
                        <div class="funnel-title">AI DECISION</div>
                    </div>

                    <div class="funnel-step">
                        <div class="funnel-number">04</div>
                        <div class="funnel-title">GUARDRAILS</div>
                    </div>

                    <div class="funnel-step">
                        <div class="funnel-number">05</div>
                        <div class="funnel-title">EXECUTION</div>
                    </div>

                    <div class="funnel-step">
                        <div class="funnel-number">06</div>
                        <div class="funnel-title">OUTCOME</div>
                    </div>

                </div>

            </div>
            """
        )

    architecture_footer()


# ============================================================
# PAGE 2 — LIVE BATCH
# ============================================================

elif page == "Live Batch":

    page_header(
        "Live Recovery Pipeline",
        "Run the revenue reliability engine and observe how incidents move through autonomous recovery.",
        "LIVE OPERATIONS",
    )

    system_strip()

    html(
        """
        <div class="panel">

            <div class="panel-title">
                Autonomous Batch Execution
            </div>

            <div class="panel-description">
                Detect revenue incidents, run recovery intelligence,
                apply safety guardrails and execute eligible recovery actions.
            </div>

        </div>
        """
    )

    if st.button("▶ RUN RECOVERY BATCH"):

        progress = st.progress(0)
        status = st.empty()

        status.info(
            "Detecting revenue incidents..."
        )

        progress.progress(15)
        time.sleep(0.4)

        status.info(
            "Classifying failure patterns..."
        )

        progress.progress(30)
        time.sleep(0.4)

        status.info(
            "Calculating recovery opportunity..."
        )

        progress.progress(50)
        time.sleep(0.4)

        status.info(
            "Running AI recovery intelligence..."
        )

        progress.progress(70)
        time.sleep(0.4)

        status.info(
            "Applying safety guardrails..."
        )

        progress.progress(85)
        time.sleep(0.4)

        try:

            result = run_pipeline()

            progress.progress(100)

            status.success(
                "Recovery pipeline completed successfully."
            )

            result_data = result.get(
                "result",
                result,
            )

            st.write("")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Payment Cases",
                result_data.get(
                    "payment_cases_created",
                    0,
                ),
            )

            col2.metric(
                "Checkout Cases",
                result_data.get(
                    "checkout_cases_created",
                    0,
                ),
            )

            col3.metric(
                "Total Cases",
                result_data.get(
                    "total_cases",
                    0,
                ),
            )

            col4.metric(
                "Pipeline Status",
                "COMPLETE",
            )

            html(
                """
                <div class="panel">

                    <div class="panel-title">
                        Execution Complete
                    </div>

                    <div class="panel-description">
                        Revenue incidents have been processed through
                        detection, AI intelligence and recovery guardrails.
                    </div>

                </div>
                """
            )

        except Exception as exc:

            progress.empty()

            status.error(
                f"Pipeline execution failed: {exc}"
            )

    architecture_footer()


# ============================================================
# PAGE 3 — RECOVERY CASE
# ============================================================

elif page == "Recovery Case":

    page_header(
        "Recovery Investigation",
        "Inspect how a single revenue incident moves through intelligence, safety and recovery execution.",
        "INCIDENT INTELLIGENCE",
    )

    system_strip()

    try:
        cases = get_recovery_cases()

    except Exception as exc:

        st.error(
            f"Unable to load recovery cases: {exc}"
        )

        cases = []

    if not cases:

        st.warning(
            "No recovery cases available."
        )

    else:

        case_map = {}

        for case in cases:

            case_id = case.get(
                "case_id",
                "UNKNOWN",
            )

            amount = case.get(
                "revenue_at_risk",
                0,
            )

            label = (
                f"{case_id} | "
                f"{money(amount)}"
            )

            case_map[label] = case

        selected_label = st.selectbox(
            "SELECT RECOVERY CASE",
            list(case_map.keys()),
        )

        case = case_map[selected_label]

        case_id = case.get(
            "case_id"
        )

        revenue_at_risk = case.get(
            "revenue_at_risk",
            0,
        )

        recovered = case.get(
            "recovered",
            False,
        )

        status = (
            "RECOVERED"
            if recovered
            else case.get(
                "recovery_status",
                "AT_RISK",
            )
        )

        html(
            f"""
            <div class="case-banner">

                <div class="case-id">
                    {case_id}
                </div>

                <div class="case-value">
                    {money(revenue_at_risk)}
                </div>

                <div style="margin-top:12px">

                    <span class="{status_class(status)}">
                        ● {status}
                    </span>

                </div>

            </div>
            """
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            metric_card(
                "Classification",
                case.get(
                    "classification",
                    "UNKNOWN",
                ),
                "Incident classification",
            )

        with col2:
            metric_card(
                "AI Decision",
                case.get(
                    "recommended_action",
                    "UNKNOWN",
                ),
                "Recommended intervention",
            )

        with col3:

            score = case.get(
                "recovery_opportunity_score",
                0,
            )

            try:
                score = float(score or 0)
            except (TypeError, ValueError):
                score = 0

            metric_card(
                "Recovery Score",
                f"{score:.2f}",
                "Recovery opportunity",
            )

        with col4:

            metric_card(
                "Expected Value",
                money(
                    case.get(
                        "expected_recovery_value",
                        0,
                    )
                ),
                "Predicted recovery value",
            )

        st.write("")

        # ----------------------------------------------------
        # TIMELINE
        # ----------------------------------------------------

        left, right = st.columns([1.25, 1])

        with left:

            html(
                """
                <div class="panel">

                    <div class="panel-title">
                        Recovery Timeline
                    </div>

                    <div class="panel-description">
                        How this incident moved through the Revenue Reliability Engine.
                    </div>

                    <div class="timeline">

                        <div class="timeline-item">

                            <div class="timeline-title">
                                Revenue incident detected
                            </div>

                            <div class="timeline-detail">
                                Payment or checkout behavior triggered
                                a recovery investigation.
                            </div>

                        </div>

                        <div class="timeline-item">

                            <div class="timeline-title">
                                Failure classified
                            </div>

                            <div class="timeline-detail">
                                Incident classified as a recoverable
                                revenue event.
                            </div>

                        </div>

                        <div class="timeline-item">

                            <div class="timeline-title">
                                AI recovery intelligence
                            </div>

                            <div class="timeline-detail">
                                AI diagnosis generated the recommended
                                intervention.
                            </div>

                        </div>

                        <div class="timeline-item">

                            <div class="timeline-title">
                                Guardrails evaluated
                            </div>

                            <div class="timeline-detail">
                                Safety limits, retry policies and
                                recovery constraints were checked.
                            </div>

                        </div>

                        <div class="timeline-item">

                            <div class="timeline-title">
                                Recovery outcome
                            </div>

                            <div class="timeline-detail">
                                Recovery execution and outcome tracking
                                completed.
                            </div>

                        </div>

                    </div>

                </div>
                """
            )

        with right:

            html(
                """
                <div class="panel">

                    <div class="panel-title">
                        Recovery Execution
                    </div>

                    <div class="panel-description">
                        Manually execute this case for the demo.
                    </div>

                </div>
                """
            )

            if st.button(
                "EXECUTE RECOVERY ACTION",
                key=f"execute_{case_id}",
            ):

                try:

                    with st.spinner(
                        "Executing recovery action..."
                    ):

                        result = execute_case(
                            case_id
                        )

                    st.success(
                        "Recovery action completed."
                    )

                    st.json(result)

                except Exception as exc:

                    st.error(
                        f"Execution failed: {exc}"
                    )

    architecture_footer()


# ============================================================
# PAGE 4 — FAILURE LAB
# ============================================================

elif page == "Failure Lab":

    page_header(
        "Failure Engineering Lab",
        "Inject controlled failures and demonstrate how the Revenue Reliability Engine remains safe under adverse conditions.",
        "CHAOS TESTING",
    )

    system_strip()

    try:
        failure_state = get_failure_state()

    except Exception as exc:

        st.error(
            f"Unable to load failure state: {exc}"
        )

        failure_state = {}

    scenarios = [
        {
            "key": "gateway_failure",
            "title": "Gateway Failure",
            "description": (
                "Simulate a payment provider or gateway outage."
            ),
        },
        {
            "key": "llm_failure",
            "title": "AI Engine Failure",
            "description": (
                "Simulate an AI or LLM intelligence failure."
            ),
        },
        {
            "key": "duplicate_event",
            "title": "Duplicate Event",
            "description": (
                "Test idempotency and duplicate event protection."
            ),
        },
        {
            "key": "recovery_exhaustion",
            "title": "Recovery Exhaustion",
            "description": (
                "Simulate retry exhaustion and safety limits."
            ),
        },
    ]

    col1, col2 = st.columns(2)

    for index, scenario in enumerate(scenarios):

        column = (
            col1
            if index % 2 == 0
            else col2
        )

        active = failure_state.get(
            scenario["key"],
            False,
        )

        state_text = (
            "● ACTIVE"
            if active
            else "○ READY"
        )

        state_class = (
            "status-danger"
            if active
            else "status-good"
        )

        with column:

            html(
                f"""
                <div class="lab-card">

                    <div class="lab-title">
                        {scenario["title"]}
                    </div>

                    <div class="lab-description">
                        {scenario["description"]}
                    </div>

                    <div style="margin-top:20px">

                        <span class="{state_class}">
                            {state_text}
                        </span>

                    </div>

                </div>
                """
            )

            if not active:

                if st.button(
                    f"INJECT {scenario['key'].upper()}",
                    key=scenario["key"],
                ):

                    try:

                        inject_failure(
                            scenario["key"]
                        )

                        st.success(
                            f"{scenario['title']} injected."
                        )

                        time.sleep(0.5)

                        st.rerun()

                    except Exception as exc:

                        st.error(
                            f"Injection failed: {exc}"
                        )

            else:

                st.button(
                    "FAILURE ACTIVE",
                    disabled=True,
                    key=f"{scenario['key']}_active",
                )

    st.write("")

    html(
        """
        <div class="panel">

            <div class="panel-title">
                Failure Lab Controls
            </div>

            <div class="panel-description">
                Reset all simulated failures and return the
                Revenue Reliability Engine to a clean state.
            </div>

        </div>
        """
    )

    if st.button(
        "RESET ALL FAILURE SCENARIOS"
    ):

        try:

            reset_failures()

            st.success(
                "All failure scenarios reset successfully."
            )

            time.sleep(0.5)

            st.rerun()

        except Exception as exc:

            st.error(
                f"Reset failed: {exc}"
            )

    architecture_footer()
