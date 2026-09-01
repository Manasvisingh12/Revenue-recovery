import time
import textwrap

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
    st.html(cleaned)


# ============================================================
# HELPERS
# ============================================================

def money(value):
    try:
        return f"₹{float(value or 0):,.0f}"
    except (TypeError, ValueError):
        return "₹0"


def safe_float(value, default=0.0):
    try:
        return float(value or default)
    except (TypeError, ValueError):
        return default


def metric_card(label, value, description=""):
    html(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-small">{description}</div>
        </div>
        """
    )


def page_header(title, subtitle, eyebrow="REVENUE RELIABILITY"):
    html(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">{eyebrow}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
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


def decision_bar(action, count, maximum):
    try:
        count = int(count or 0)
        maximum = max(int(maximum or 1), 1)
        percentage = min((count / maximum) * 100, 100)
    except (TypeError, ValueError):
        count = 0
        percentage = 0

    html(
        f"""
        <div style="margin-bottom:18px;">

            <div style="
                display:flex;
                justify-content:space-between;
                margin-bottom:7px;
            ">
                <span style="
                    color:#cbd5e1;
                    font-size:12px;
                    font-weight:700;
                ">
                    {action}
                </span>

                <span style="
                    color:#818cf8;
                    font-size:12px;
                    font-weight:800;
                ">
                    {count}
                </span>
            </div>

            <div style="
                width:100%;
                height:8px;
                background:#1e293b;
                border-radius:999px;
                overflow:hidden;
            ">

                <div style="
                    width:{percentage:.1f}%;
                    height:100%;
                    background:#6366f1;
                    border-radius:999px;
                "></div>

            </div>

        </div>
        """
    )


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
            "Observability",
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

        revenue = summary.get("revenue", {}) or {}
        recovery = summary.get("recovery", {}) or {}
        reliability = summary.get("reliability", {}) or {}
        ai = summary.get("ai_decisions", {}) or {}

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
            success_rate = safe_float(
                recovery.get(
                    "success_rate_percent",
                    0,
                )
            )

            metric_card(
                "Recovery Success",
                f"{success_rate:.1f}%",
                "Successful recovery attempts",
            )

        with col4:
            latency_seconds = safe_float(
                reliability.get(
                    "average_latency_seconds",
                    0,
                )
            )

            latency_ms = latency_seconds * 1000

            metric_card(
                "Execution Latency",
                f"{latency_ms:.2f} ms",
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
        # AI INTELLIGENCE
        # ----------------------------------------------------

        left, right = st.columns([1.25, 1])

        with left:

            html(
                """
                <div class="panel">

                    <div class="panel-title">
                        AI Recovery Intelligence
                    </div>

                    <div class="panel-description">
                        How autonomous recovery intelligence is
                        routing revenue cases.
                    </div>

                </div>
                """
            )

            if ai:

                numeric_ai = {}

                for action, count in ai.items():

                    try:
                        numeric_ai[str(action)] = int(count or 0)

                    except (TypeError, ValueError):
                        numeric_ai[str(action)] = 0

                maximum = max(
                    numeric_ai.values(),
                    default=1,
                )

                for action, count in sorted(
                    numeric_ai.items(),
                    key=lambda item: item[1],
                    reverse=True,
                ):

                    decision_bar(
                        action,
                        count,
                        maximum,
                    )

            else:

                st.info(
                    "No AI decision data available yet."
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

                for action, count in sorted(
                    ai.items(),
                    key=lambda item: int(item[1] or 0),
                    reverse=True,
                ):

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
                    The complete journey from revenue incident
                    to verified recovery.
                </div>

                <div class="funnel-container">

                    <div class="funnel-step">
                        <div class="funnel-number">01</div>
                        <div class="funnel-title">
                            EVENTS
                        </div>
                    </div>

                    <div class="funnel-step">
                        <div class="funnel-number">02</div>
                        <div class="funnel-title">
                            DETECTION
                        </div>
                    </div>

                    <div class="funnel-step">
                        <div class="funnel-number">03</div>
                        <div class="funnel-title">
                            AI DECISION
                        </div>
                    </div>

                    <div class="funnel-step">
                        <div class="funnel-number">04</div>
                        <div class="funnel-title">
                            GUARDRAILS
                        </div>
                    </div>

                    <div class="funnel-step">
                        <div class="funnel-number">05</div>
                        <div class="funnel-title">
                            EXECUTION
                        </div>
                    </div>

                    <div class="funnel-step">
                        <div class="funnel-number">06</div>
                        <div class="funnel-title">
                            OUTCOME
                        </div>
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

    if st.button(
        "▶ RUN RECOVERY BATCH",
        key="run_recovery_batch",
    ):

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

            result_data = (
                result.get("result", result)
                if isinstance(result, dict)
                else {}
            )

            st.write("")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Payment Cases",
                    result_data.get(
                        "payment_cases_created",
                        0,
                    ),
                )

            with col2:
                st.metric(
                    "Checkout Cases",
                    result_data.get(
                        "checkout_cases_created",
                        0,
                    ),
                )

            with col3:
                st.metric(
                    "Total Cases",
                    result_data.get(
                        "total_cases",
                        0,
                    ),
                )

            with col4:
                st.metric(
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

            value = case.get(
                "revenue_at_risk",
                0,
            )

            label = (
                f"{case_id} | {money(value)}"
            )

            case_map[label] = case

        selected_label = st.selectbox(
            "SELECT RECOVERY CASE",
            list(case_map.keys()),
        )

        case = case_map[selected_label]

        case_id = case.get(
            "case_id",
            "UNKNOWN",
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

            score = safe_float(
                case.get(
                    "opportunity_score",
                    0,
                )
            )

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
        # AI DECISION EXPLANATION
        # ----------------------------------------------------

        ai_diagnosis = (
            case.get("ai_diagnosis")
            or "No AI diagnosis available."
        )

        action_reason = (
            case.get("action_reason")
            or "No action reasoning available."
        )

        classification_reason = (
            case.get("classification_reason")
            or "No classification reasoning available."
        )

        recovery_probability = safe_float(
            case.get(
                "recovery_probability",
                0,
            )
        )

        ai_confidence = safe_float(
            case.get(
                "ai_confidence",
                0,
            )
        )

        incident_type = (
            case.get("incident_type")
            or "NONE"
        )

        incident_provider = (
            case.get("incident_provider")
            or "UNKNOWN"
        )

        incident_detected = bool(
            case.get(
                "incident_detected",
                False,
            )
        )

        html(
            f"""
            <div class="panel">

                <div class="panel-title">
                    Why the AI Made This Decision
                </div>

                <div class="panel-description">
                    Backend intelligence signals used to determine
                    the recovery intervention.
                </div>

                <div style="
                    margin-top:20px;
                    display:grid;
                    grid-template-columns:repeat(
                        2,
                        minmax(0, 1fr)
                    );
                    gap:14px;
                ">

                    <div class="decision-card">

                        <div class="decision-label">
                            AI CONFIDENCE
                        </div>

                        <div class="decision-value">
                            {ai_confidence * 100:.1f}%
                        </div>

                    </div>

                    <div class="decision-card">

                        <div class="decision-label">
                            RECOVERY PROBABILITY
                        </div>

                        <div class="decision-value">
                            {recovery_probability * 100:.1f}%
                        </div>

                    </div>

                </div>

                <div style="margin-top:22px;">

                    <div class="metric-label">
                        AI DIAGNOSIS
                    </div>

                    <div style="
                        color:#cbd5e1;
                        margin-top:8px;
                        line-height:1.7;
                    ">
                        {ai_diagnosis}
                    </div>

                </div>

                <div style="margin-top:20px;">

                    <div class="metric-label">
                        DECISION REASON
                    </div>

                    <div style="
                        color:#cbd5e1;
                        margin-top:8px;
                        line-height:1.7;
                    ">
                        {action_reason}
                    </div>

                </div>

                <div style="margin-top:20px;">

                    <div class="metric-label">
                        CLASSIFICATION REASON
                    </div>

                    <div style="
                        color:#cbd5e1;
                        margin-top:8px;
                        line-height:1.7;
                    ">
                        {classification_reason}
                    </div>

                </div>

                <div style="
                    margin-top:20px;
                    padding-top:16px;
                    border-top:1px solid #1e293b;
                ">

                    <span class="metric-label">
                        INCIDENT
                    </span>

                    <span style="
                        color:#818cf8;
                        margin-left:10px;
                        font-weight:700;
                    ">
                        {
                            "DETECTED"
                            if incident_detected
                            else "NOT DETECTED"
                        }
                    </span>

                    <span style="
                        color:#64748b;
                        margin-left:10px;
                    ">
                        {incident_type} · {incident_provider}
                    </span>

                </div>

            </div>
            """
        )

        left, right = st.columns([1.25, 1])

        with left:

            html(
                """
                <div class="panel">

                    <div class="panel-title">
                        Recovery Timeline
                    </div>

                    <div class="panel-description">
                        How this incident moved through the
                        Revenue Reliability Engine.
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

                    result_data = (
                        result.get("result", {})
                        if isinstance(result, dict)
                        else {}
                    )

                    action = result_data.get(
                        "action",
                        "UNKNOWN",
                    )

                    reason = result_data.get(
                        "reason",
                        "UNKNOWN",
                    )

                    if result_data.get("executed"):

                        st.success(
                            f"Recovery action executed: {action}"
                        )

                    elif result_data.get("escalated"):

                        st.warning(
                            f"Case escalated for review: {reason}"
                        )

                    elif result_data.get("blocked"):

                        st.error(
                            f"Action safely blocked: {reason}"
                        )

                    else:

                        st.info(
                            f"Recovery action completed: {action}"
                        )

                    st.json(
                        result_data
                    )

                    time.sleep(0.5)

                    st.rerun()

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

        active = bool(
            failure_state.get(
                scenario["key"],
                False,
            )
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
        "RESET ALL FAILURE SCENARIOS",
        key="reset_failures",
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


# ============================================================
# PAGE 5 — OBSERVABILITY
# ============================================================

elif page == "Observability":

    page_header(
        "Revenue Reliability Observability",
        "Real-time and historical visibility into recovery performance, reliability and system health.",
        "OBSERVABILITY",
    )

    system_strip()

    # --------------------------------------------------------
    # INTRODUCTION
    # --------------------------------------------------------

    html(
        """
        <div class="panel">

            <div class="panel-title">
                Revenue Reliability Observability
            </div>

            <div class="panel-description">
                Prometheus continuously collects reliability metrics
                from the recovery engine, while Grafana provides
                real-time and historical operational visibility.
            </div>

        </div>
        """
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    html(
        """
        <div class="panel">

            <div class="panel-title">
                Metrics Monitored
            </div>

            <div class="panel-description">
                Operational signals used to monitor autonomous
                revenue recovery.
            </div>

        </div>
        """
    )

    summary = safe_summary()

    if summary:

        revenue = summary.get(
            "revenue",
            {}
        ) or {}

        recovery = summary.get(
            "recovery",
            {}
        ) or {}

        reliability = summary.get(
            "reliability",
            {}
        ) or {}

        latency_seconds = safe_float(
            reliability.get(
                "average_latency_seconds",
                0,
            )
        )

        latency_ms = latency_seconds * 1000

        col1, col2, col3 = st.columns(3)

        # ----------------------------------------------------
        # COLUMN 1
        # ----------------------------------------------------

        with col1:

            metric_card(
                "Recovery Attempts",
                recovery.get(
                    "attempts",
                    0,
                ),
                "Total recovery executions",
            )

            metric_card(
                "Guardrail Blocks",
                reliability.get(
                    "guardrail_blocks",
                    0,
                ),
                "Safety interventions",
            )

        # ----------------------------------------------------
        # COLUMN 2
        # ----------------------------------------------------

        with col2:

            metric_card(
                "Recovery Success Rate",
                f"{safe_float(
                    recovery.get(
                        "success_rate_percent",
                        0,
                    )
                ):.1f}%",
                "Successful recovery attempts",
            )

            metric_card(
                "Execution Latency",
                f"{latency_ms:.2f} ms",
                "Average recovery execution",
            )

        # ----------------------------------------------------
        # COLUMN 3
        # ----------------------------------------------------

        with col3:

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

            metric_card(
                "Revenue Recovered",
                money(
                    revenue.get(
                        "recovered",
                        0,
                    )
                ),
                "Revenue successfully recovered",
            )

    else:

        st.warning(
            "Observability metrics are currently unavailable."
        )

    # --------------------------------------------------------
    # GRAFANA
    # --------------------------------------------------------

    html(
        """
        <div class="panel">

            <div class="panel-title">
                Grafana Reliability Dashboard
            </div>

            <div class="panel-description">
                Explore real-time and historical recovery reliability,
                execution performance and safety metrics in Grafana.
            </div>

        </div>
        """
    )

    st.link_button(
        "OPEN GRAFANA DASHBOARD",
        "http://localhost:3000",
        use_container_width=True,
    )

    st.write("")

    # --------------------------------------------------------
    # OBSERVABILITY ARCHITECTURE
    # --------------------------------------------------------

    html(
        """
        <div class="panel">

            <div class="panel-title">
                Observability Architecture
            </div>

            <div class="panel-description">
                The recovery engine exposes reliability metrics.
                Prometheus collects and stores those metrics, while
                Grafana visualizes system behaviour over time.
            </div>

            <div class="funnel-container">

                <div class="funnel-step">

                    <div class="funnel-number">
                        01
                    </div>

                    <div class="funnel-title">
                        RECOVERY ENGINE
                    </div>

                </div>

                <div class="funnel-step">

                    <div class="funnel-number">
                        02
                    </div>

                    <div class="funnel-title">
                        PROMETHEUS
                    </div>

                </div>

                <div class="funnel-step">

                    <div class="funnel-number">
                        03
                    </div>

                    <div class="funnel-title">
                        GRAFANA
                    </div>

                </div>

            </div>

        </div>
        """
    )

    architecture_footer()