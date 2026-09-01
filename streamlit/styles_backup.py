import textwrap
import streamlit as st


def load_css():
    css = """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 15% 0%,
                rgba(99, 102, 241, 0.14),
                transparent 28%
            ),
            radial-gradient(
                circle at 95% 15%,
                rgba(16, 185, 129, 0.08),
                transparent 25%
            ),
            radial-gradient(
                circle at 50% 100%,
                rgba(59, 130, 246, 0.05),
                transparent 35%
            ),
            #070a10;
        color: #f8fafc;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0b1019 0%,
                #080b12 100%
            );
        border-right:
            1px solid rgba(148, 163, 184, 0.10);
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    .hero {
        padding: 20px 0 25px 0;
    }

    .hero-eyebrow {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        color: #818cf8;
        margin-bottom: 10px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 850;
        letter-spacing: -1.5px;
        line-height: 1.1;
        margin-bottom: 10px;
        background:
            linear-gradient(
                90deg,
                #ffffff,
                #c7d2fe
            );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 15px;
        max-width: 760px;
        line-height: 1.6;
    }

    .system-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 8px 0 25px 0;
    }

    .system-node {
        display: inline-flex;
        align-items: center;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.15);
        color: #cbd5e1;
    }

    .system-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #34d399;
        margin-right: 7px;
        box-shadow: 0 0 12px rgba(52, 211, 153, 0.8);
    }

    .metric-card {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(
                145deg,
                rgba(22, 28, 42, 0.95),
                rgba(9, 13, 21, 0.98)
            );
        border: 1px solid rgba(148, 163, 184, 0.13);
        border-radius: 20px;
        padding: 22px;
        min-height: 145px;
        transition:
            transform 0.2s ease,
            border 0.2s ease,
            box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(129, 140, 248, 0.45);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
    }

    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(129, 140, 248, 0.8),
                transparent
            );
    }

    .metric-label {
        color: #94a3b8;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 31px;
        font-weight: 850;
        margin-top: 12px;
        letter-spacing: -1px;
    }

    .metric-small {
        color: #64748b;
        font-size: 12px;
        margin-top: 8px;
    }

    .status-good,
    .status-warning,
    .status-danger {
        display: inline-flex;
        align-items: center;
        padding: 7px 13px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.4px;
    }

    .status-good {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.28);
        color: #6ee7b7;
    }

    .status-warning {
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.28);
        color: #fbbf24;
    }

    .status-danger {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.28);
        color: #fca5a5;
    }

    .panel {
        background:
            linear-gradient(
                145deg,
                rgba(15, 20, 31, 0.95),
                rgba(8, 11, 18, 0.98)
            );
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .panel-title {
        font-size: 18px;
        font-weight: 750;
        color: #f8fafc;
        margin-bottom: 6px;
    }

    .panel-description {
        color: #64748b;
        font-size: 13px;
        line-height: 1.5;
        margin-bottom: 16px;
    }

    .decision-card {
        background:
            linear-gradient(
                135deg,
                rgba(99, 102, 241, 0.13),
                rgba(59, 130, 246, 0.04)
            );
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .decision-label {
        color: #94a3b8;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .decision-value {
        font-size: 28px;
        font-weight: 850;
        margin-top: 5px;
    }

    .funnel-container {
        display: flex;
        align-items: stretch;
        gap: 10px;
        flex-wrap: wrap;
    }

    .funnel-step {
        flex: 1;
        min-width: 120px;
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 15px;
        padding: 16px;
        text-align: center;
    }

    .funnel-number {
        font-size: 11px;
        color: #818cf8;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .funnel-title {
        font-size: 12px;
        font-weight: 750;
        color: #e2e8f0;
    }

    .timeline {
        border-left: 2px solid rgba(99, 102, 241, 0.35);
        padding-left: 24px;
        margin-left: 10px;
    }

    .timeline-item {
        position: relative;
        margin-bottom: 25px;
    }

    .timeline-item::before {
        content: "";
        position: absolute;
        width: 11px;
        height: 11px;
        border-radius: 50%;
        left: -30px;
        top: 5px;
        background: #818cf8;
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.8);
    }

    .timeline-title {
        font-size: 15px;
        font-weight: 750;
        color: #f8fafc;
    }

    .timeline-detail {
        color: #94a3b8;
        font-size: 13px;
        margin-top: 5px;
    }

    .lab-card {
        background:
            linear-gradient(
                145deg,
                rgba(35, 20, 29, 0.9),
                rgba(11, 13, 20, 0.98)
            );
        border: 1px solid rgba(239, 68, 68, 0.18);
        border-radius: 20px;
        padding: 24px;
        min-height: 190px;
        transition:
            transform 0.2s ease,
            border 0.2s ease;
    }

    .lab-card:hover {
        transform: translateY(-3px);
        border-color: rgba(239, 68, 68, 0.5);
    }

    .lab-title {
        font-size: 17px;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 8px;
    }

    .lab-description {
        font-size: 13px;
        color: #94a3b8;
        min-height: 45px;
    }

    .case-banner {
        background:
            linear-gradient(
                135deg,
                rgba(99, 102, 241, 0.15),
                rgba(14, 165, 233, 0.05)
            );
        border: 1px solid rgba(99, 102, 241, 0.28);
        border-radius: 22px;
        padding: 28px;
        margin-bottom: 24px;
    }

    .case-id {
        color: #94a3b8;
        font-size: 12px;
        font-family: monospace;
    }

    .case-value {
        font-size: 40px;
        font-weight: 850;
        margin-top: 8px;
    }

    .architecture-footer {
        margin-top: 45px;
        padding: 18px 20px;
        border-top: 1px solid rgba(148, 163, 184, 0.12);
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        align-items: center;
    }

    .architecture-title {
        font-size: 11px;
        color: #64748b;
        font-weight: 800;
        letter-spacing: 1.2px;
        margin-right: 8px;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(129, 140, 248, 0.4);
        background:
            linear-gradient(
                135deg,
                #6366f1,
                #4f46e5
            );
        color: white;
        font-weight: 750;
        padding: 12px 18px;
        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.35);
    }

    </style>
    """

    st.markdown(
        textwrap.dedent(css),
        unsafe_allow_html=True,
    )
