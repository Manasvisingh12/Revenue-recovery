import streamlit as st


def load_css():
    st.markdown(
        """
        <style>

        /* ================================
           GLOBAL APP
        ================================= */

        .stApp {
            background: #070a10;
            color: #f8fafc;
        }

        .main .block-container {
            max-width: 1500px;
            padding-top: 2rem;
            padding-bottom: 3rem;
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


        /* ================================
           SIDEBAR
        ================================= */

        section[data-testid="stSidebar"] {
            background: #090d15;
            border-right: 1px solid rgba(148, 163, 184, 0.12);
        }

        section[data-testid="stSidebar"] * {
            color: #e5e7eb;
        }


        /* ================================
           HERO
        ================================= */

        .hero {
            padding: 10px 0 25px 0;
        }

        .hero-eyebrow {
            color: #818cf8;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }

        .hero-title {
            color: #ffffff;
            font-size: 42px;
            font-weight: 800;
            letter-spacing: -1.5px;
            line-height: 1.1;
            margin-bottom: 10px;
        }

        .hero-subtitle {
            color: #94a3b8;
            font-size: 15px;
            line-height: 1.6;
            max-width: 800px;
        }


        /* ================================
           SYSTEM STRIP
        ================================= */

        .system-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 5px 0 25px 0;
        }

        .system-node {
            display: inline-flex;
            align-items: center;
            padding: 8px 13px;
            border-radius: 999px;
            background: #0f172a;
            border: 1px solid rgba(148, 163, 184, 0.16);
            color: #cbd5e1;
            font-size: 11px;
            font-weight: 700;
        }

        .system-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #34d399;
            margin-right: 7px;
            box-shadow: 0 0 10px rgba(52, 211, 153, 0.8);
        }


        /* ================================
           METRIC CARDS
        ================================= */

        .metric-card {
            background: #0f141f;
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 18px;
            padding: 22px;
            min-height: 145px;
            box-sizing: border-box;
        }

        .metric-card:hover {
            border-color: rgba(129, 140, 248, 0.45);
            transform: translateY(-2px);
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
            font-size: 30px;
            font-weight: 800;
            margin-top: 14px;
        }

        .metric-small {
            color: #64748b;
            font-size: 12px;
            margin-top: 8px;
        }


        /* ================================
           STATUS
        ================================= */

        .status-good,
        .status-warning,
        .status-danger {
            display: inline-flex;
            align-items: center;
            padding: 7px 13px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 800;
        }

        .status-good {
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #6ee7b7;
        }

        .status-warning {
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.3);
            color: #fbbf24;
        }

        .status-danger {
            background: rgba(239, 68, 68, 0.12);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
        }


        /* ================================
           PANELS
        ================================= */

        .panel {
            background: #0d121c;
            border: 1px solid rgba(148, 163, 184, 0.12);
            border-radius: 18px;
            padding: 24px;
            margin-bottom: 20px;
        }

        .panel-title {
            color: #f8fafc;
            font-size: 18px;
            font-weight: 750;
            margin-bottom: 7px;
        }

        .panel-description {
            color: #64748b;
            font-size: 13px;
            line-height: 1.5;
            margin-bottom: 16px;
        }


        /* ================================
           DECISION CARDS
        ================================= */

        .decision-card {
            background: #111827;
            border: 1px solid rgba(99, 102, 241, 0.28);
            border-radius: 14px;
            padding: 17px;
            margin-bottom: 10px;
        }

        .decision-label {
            color: #94a3b8;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
        }

        .decision-value {
            color: #f8fafc;
            font-size: 27px;
            font-weight: 800;
            margin-top: 5px;
        }


        /* ================================
           FUNNEL
        ================================= */

        .funnel-container {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .funnel-step {
            flex: 1;
            min-width: 120px;
            background: #0f172a;
            border: 1px solid rgba(148, 163, 184, 0.13);
            border-radius: 14px;
            padding: 18px;
            text-align: center;
        }

        .funnel-number {
            color: #818cf8;
            font-size: 11px;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .funnel-title {
            color: #e2e8f0;
            font-size: 12px;
            font-weight: 750;
        }


        /* ================================
           TIMELINE
        ================================= */

        .timeline {
            border-left: 2px solid rgba(99, 102, 241, 0.35);
            padding-left: 24px;
            margin-left: 10px;
        }

        .timeline-item {
            position: relative;
            margin-bottom: 25px;
        }

        .timeline-item:before {
            content: "";
            position: absolute;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            left: -30px;
            top: 5px;
            background: #818cf8;
            box-shadow: 0 0 12px rgba(129, 140, 248, 0.8);
        }

        .timeline-title {
            color: #f8fafc;
            font-size: 15px;
            font-weight: 750;
        }

        .timeline-detail {
            color: #94a3b8;
            font-size: 13px;
            margin-top: 5px;
        }


        /* ================================
           FAILURE LAB
        ================================= */

        .lab-card {
            background: #111018;
            border: 1px solid rgba(239, 68, 68, 0.18);
            border-radius: 18px;
            padding: 24px;
            min-height: 185px;
            box-sizing: border-box;
        }

        .lab-title {
            color: #f8fafc;
            font-size: 17px;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .lab-description {
            color: #94a3b8;
            font-size: 13px;
            line-height: 1.5;
            min-height: 45px;
        }


        /* ================================
           CASE BANNER
        ================================= */

        .case-banner {
            background: #10152a;
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 20px;
            padding: 28px;
            margin-bottom: 24px;
        }

        .case-id {
            color: #94a3b8;
            font-size: 12px;
            font-family: monospace;
        }

        .case-value {
            color: #ffffff;
            font-size: 40px;
            font-weight: 800;
            margin-top: 8px;
        }


        /* ================================
           ARCHITECTURE FOOTER
        ================================= */

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
            color: #64748b;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.2px;
            margin-right: 8px;
        }


        /* ================================
           STREAMLIT BUTTONS
        ================================= */

        .stButton > button {
            width: 100%;
            border-radius: 12px;
            border: 1px solid rgba(129, 140, 248, 0.4);
            background: #4f46e5;
            color: white;
            font-weight: 750;
            padding: 12px 18px;
        }

        .stButton > button:hover {
            border-color: #818cf8;
            background: #6366f1;
        }


        /* ================================
           SELECTBOX
        ================================= */

        div[data-baseweb="select"] > div {
            background: #0f172a;
            border-color: rgba(148, 163, 184, 0.2);
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
