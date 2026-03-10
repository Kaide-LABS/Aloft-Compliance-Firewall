import streamlit as st
import asyncio
import time
import base64
import os
from dotenv import load_dotenv

from src.demo_postcodes import DEMO_POSTCODES

load_dotenv()

# --- Load Aloft logo ---
LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ALOFT LOGO.svg")


def get_logo_b64():
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "r") as f:
            return base64.b64encode(f.read().encode()).decode()
    return None


st.set_page_config(
    page_title="Aloft Compliance Firewall",
    page_icon="🛡️",
    layout="wide",
)

# --- Aloft-branded CSS ---
st.markdown(
    """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    /* Global overrides */
    .stApp {
        background-color: #f5f0ea;
        font-family: 'DM Sans', sans-serif;
    }

    /* Hide default Streamlit header */
    header[data-testid="stHeader"] {
        background-color: #1a3a2a;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1a3a2a;
        color: #ffffff;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown strong {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.15);
    }
    section[data-testid="stSidebar"] .stMarkdown a {
        color: #49F9C4 !important;
    }

    /* Custom classes */
    .aloft-header {
        background-color: #1a3a2a;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .aloft-header img {
        height: 36px;
    }
    .aloft-header-text {
        color: #ffffff;
        font-family: 'DM Sans', sans-serif;
    }
    .aloft-header-text h1 {
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
        color: #ffffff;
    }
    .aloft-header-text p {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.85);
        margin: 0.2rem 0 0 0;
    }

    .aloft-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(0,0,0,0.06);
        color: #2d2d2d;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    .verdict-green {
        background-color: #e8f7ef;
        border-left: 5px solid #1a3a2a;
        padding: 1.5rem 2rem;
        border-radius: 0 16px 16px 0;
        margin: 1rem 0;
    }
    .verdict-green h2 { color: #1a3a2a; }

    .verdict-amber {
        background-color: #fef8e8;
        border-left: 5px solid #d4a017;
        padding: 1.5rem 2rem;
        border-radius: 0 16px 16px 0;
        margin: 1rem 0;
    }
    .verdict-amber h2 { color: #8a6914; }

    .verdict-red {
        background-color: #fde8e8;
        border-left: 5px solid #c0392b;
        padding: 1.5rem 2rem;
        border-radius: 0 16px 16px 0;
        margin: 1rem 0;
    }
    .verdict-red h2 { color: #922b21; }

    .metric-card {
        background: #ffffff;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.06);
    }
    .cost-badge {
        background: #e8f7ef;
        color: #1a3a2a;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* Agent status cards */
    .agent-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.06);
        min-height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .agent-card-running {
        border-left: 3px solid #49F9C4;
    }
    .agent-card-done {
        border-left: 3px solid #1a3a2a;
    }
    .agent-name {
        font-weight: 600;
        font-size: 0.85rem;
        color: #1a3a2a;
        margin-bottom: 0.3rem;
    }
    .agent-status {
        font-size: 0.78rem;
        color: #555555;
    }

    /* Quick demo buttons */
    .demo-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #1a3a2a;
        margin-bottom: 0.5rem;
    }

    /* Override Streamlit button styling */
    .stButton > button[kind="primary"] {
        background-color: #1a3a2a;
        color: #ffffff !important;
        border: none;
        border-radius: 8px;
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #2a5a3a;
        color: #ffffff !important;
        border: none;
    }
    .stButton > button[kind="secondary"],
    .stButton > button:not([kind="primary"]) {
        border-radius: 8px;
        font-family: 'DM Sans', sans-serif;
        border: 1.5px solid #1a3a2a !important;
        color: #1a3a2a !important;
        background-color: #ffffff !important;
    }
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind="primary"]):hover {
        background-color: #e8f7ef !important;
        color: #1a3a2a !important;
    }

    /* Input styling */
    .stTextInput label {
        color: #1a3a2a !important;
        font-weight: 600 !important;
        font-family: 'DM Sans', sans-serif;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1.5px solid #b8b2a8;
        font-family: 'DM Sans', sans-serif;
        background-color: #ffffff;
        color: #1a1a1a;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1a3a2a;
        box-shadow: 0 0 0 1px #1a3a2a;
    }
    .stTextInput > div > div > input::placeholder {
        color: #757068;
    }

    /* Expander styling */
    [data-testid="stExpander"] {
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.08);
        overflow: hidden;
    }
    [data-testid="stExpander"] summary {
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        color: #1a3a2a !important;
        padding: 0.75rem 1rem;
    }
    [data-testid="stExpander"] summary span {
        color: #1a3a2a !important;
    }
    [data-testid="stExpander"] summary svg {
        color: #1a3a2a !important;
        fill: #1a3a2a !important;
    }

    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a3a2a;
        margin: 1.5rem 0 0.8rem 0;
        font-family: 'DM Sans', sans-serif;
    }

    /* Footer */
    .aloft-footer {
        text-align: center;
        padding: 1.5rem 0;
        color: #5c5650;
        font-size: 0.8rem;
        font-family: 'DM Sans', sans-serif;
    }

    /* Metric override */
    [data-testid="stMetric"] {
        background: #ffffff;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.06);
    }
    [data-testid="stMetricLabel"] {
        color: #4a4a4a !important;
        font-family: 'DM Sans', sans-serif;
    }
    [data-testid="stMetricValue"] {
        color: #1a3a2a !important;
        font-family: 'DM Sans', sans-serif;
    }
</style>
""",
    unsafe_allow_html=True,
)


def run_async(coro):
    """Run an async coroutine from sync Streamlit context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# --- Header with Aloft logo ---
logo_b64 = get_logo_b64()
if logo_b64:
    st.markdown(
        f"""
    <div class="aloft-header">
        <img src="data:image/svg+xml;base64,{logo_b64}" alt="Aloft">
        <div class="aloft-header-text">
            <h1>Compliance Firewall</h1>
            <p>Pre-leasing regulatory compliance checking powered by multi-agent AI</p>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
    <div class="aloft-header">
        <div class="aloft-header-text">
            <h1>Aloft Compliance Firewall</h1>
            <p>Pre-leasing regulatory compliance checking powered by multi-agent AI</p>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# --- Sidebar ---
with st.sidebar:
    if logo_b64:
        st.markdown(
            f'<img src="data:image/svg+xml;base64,{logo_b64}" style="height:32px; margin-bottom:1.5rem;">',
            unsafe_allow_html=True,
        )

    st.markdown("### How It Works")
    st.markdown(
        """
**Multi-Agent AI Architecture**

1. **Legal Rules Agent**
   Gemini 2.5 Flash — RAG search across UK housing legislation

2. **Property Audit Agent**
   Deterministic — Real EPC + Companies House API checks

3. **Risk Scorer**
   GPT-4o-mini — Scores compliance risk 0–100

4. **Orchestrator**
   GPT-4o — Generates human-readable summary

---

**Data Sources**
- EPC Open Data API
- Companies House API
- legislation.gov.uk
- Housing Act 2004
- Energy Efficiency Regs 2015
- Renters' Rights Act 2025

---

**Cost:** ~£0.01 per check
**Latency:** <10 seconds
    """
    )

# --- Input Section ---
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    postcode = st.text_input(
        "UK Postcode", placeholder="e.g. SW1A 2AA", key="postcode_input"
    )
with col2:
    company_name = st.text_input(
        "Property Management Company (optional)",
        placeholder="e.g. Foxtons",
        key="company_input",
    )
with col3:
    st.write("")  # Spacer
    st.write("")  # Spacer
    run_check = st.button(
        "Run Compliance Check", type="primary", use_container_width=True
    )

# --- Quick Demo Buttons ---
st.markdown('<p class="demo-label">Quick Demo</p>', unsafe_allow_html=True)
demo_col1, demo_col2, demo_col3 = st.columns(3)
demo_clicked = None
with demo_col1:
    if st.button("🟢 GREEN Example", use_container_width=True):
        demo_clicked = "GREEN"
with demo_col2:
    if st.button("🟡 AMBER Example", use_container_width=True):
        demo_clicked = "AMBER"
with demo_col3:
    if st.button("🔴 RED Example", use_container_width=True):
        demo_clicked = "RED"

# If a demo button was clicked, override postcode/company and auto-run
if demo_clicked:
    postcode = DEMO_POSTCODES[demo_clicked]["postcode"]
    company_name = DEMO_POSTCODES[demo_clicked]["company"]
    run_check = True

# --- Processing & Results ---
if run_check and postcode:
    start_time = time.time()

    # Show agent status cards
    st.markdown('<p class="section-header">Agent Activity</p>', unsafe_allow_html=True)
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        agent1_status = st.empty()
        agent1_status.markdown(
            '<div class="agent-card agent-card-running"><div class="agent-name">Legal Rules Agent</div><div class="agent-status">Querying legislation...</div></div>',
            unsafe_allow_html=True,
        )
    with col_a2:
        agent2_status = st.empty()
        agent2_status.markdown(
            '<div class="agent-card agent-card-running"><div class="agent-name">Property Audit Agent</div><div class="agent-status">Checking EPC & Company...</div></div>',
            unsafe_allow_html=True,
        )
    with col_a3:
        agent3_status = st.empty()
        agent3_status.markdown(
            '<div class="agent-card"><div class="agent-name">Risk Scorer</div><div class="agent-status">Waiting for data...</div></div>',
            unsafe_allow_html=True,
        )
    with col_a4:
        agent4_status = st.empty()
        agent4_status.markdown(
            '<div class="agent-card"><div class="agent-name">Orchestrator</div><div class="agent-status">Waiting for assessment...</div></div>',
            unsafe_allow_html=True,
        )

    # Run the graph
    from src.agents.graph import compliance_graph

    with st.spinner("Running compliance check..."):
        result = run_async(
            compliance_graph.ainvoke(
                {
                    "postcode": postcode,
                    "company_name": company_name,
                    "legal_requirements": [],
                    "epc_data": {},
                    "company_data": {},
                    "risk_score": 0,
                    "risk_level": "",
                    "violations": [],
                    "warnings": [],
                    "summary": "",
                    "raw_agent_outputs": [],
                }
            )
        )

    elapsed = time.time() - start_time

    # Update agent statuses to complete
    for col, status, name in [
        (col_a1, agent1_status, "Legal Rules Agent"),
        (col_a2, agent2_status, "Property Audit Agent"),
        (col_a3, agent3_status, "Risk Scorer"),
        (col_a4, agent4_status, "Orchestrator"),
    ]:
        with col:
            status.markdown(
                f'<div class="agent-card agent-card-done"><div class="agent-name">{name}</div><div class="agent-status">Complete</div></div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # --- Verdict Banner ---
    level = result.get("risk_level", "UNKNOWN")
    score = result.get("risk_score", 0)
    level_class = {
        "GREEN": "verdict-green",
        "AMBER": "verdict-amber",
        "RED": "verdict-red",
    }.get(level, "verdict-amber")
    level_icon = {"GREEN": "✅", "AMBER": "⚠️", "RED": "🚫"}.get(level, "❓")
    level_text = {
        "GREEN": "CLEAR TO LEASE",
        "AMBER": "PROCEED WITH CAUTION",
        "RED": "DO NOT LEASE",
    }.get(level, "UNKNOWN")

    address = result.get("epc_data", {}).get("address", postcode)

    st.markdown(
        f"""
    <div class="{level_class}">
        <h2 style="margin:0; font-family:'DM Sans',sans-serif;">{level_icon} {level}: {level_text}</h2>
        <p style="margin:0.3rem 0 0 0; font-size:0.95rem; color:#3d3d3d; font-family:'DM Sans',sans-serif;">📍 {address}</p>
        <p style="margin:0.3rem 0 0 0; font-size:1.1rem; font-family:'DM Sans',sans-serif;">Risk Score: <strong>{score}/100</strong></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # --- Metrics Row ---
    met1, met2, met3, met4 = st.columns(4)
    with met1:
        epc = result.get("epc_data", {})
        st.metric("EPC Rating", epc.get("rating", "N/A"))
    with met2:
        st.metric("Legal Checks", len(result.get("legal_requirements", [])))
    with met3:
        st.metric("Check Time", f"{elapsed:.1f}s")
    with met4:
        st.markdown(
            '<div class="metric-card"><span class="cost-badge">~£0.01 per check</span></div>',
            unsafe_allow_html=True,
        )

    # --- Summary ---
    st.markdown(
        '<p class="section-header">Compliance Summary</p>', unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="aloft-card">{result.get("summary", "")}</div>',
        unsafe_allow_html=True,
    )

    # --- Violations & Warnings ---
    col_v, col_w = st.columns(2)
    with col_v:
        violations = result.get("violations", [])
        if violations:
            st.markdown(
                f'<p class="section-header">Violations ({len(violations)})</p>',
                unsafe_allow_html=True,
            )
            for v in violations:
                severity_color = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}.get(
                    v.get("severity", ""), "⚪"
                )
                st.markdown(
                    f'<div class="aloft-card"><strong>{severity_color} {v.get("severity", "HIGH")}:</strong> {v["description"]}<br><small style="color:#555555">📜 {v.get("legislation", "")}</small></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<p class="section-header">No Violations</p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="aloft-card">No compliance violations detected.</div>',
                unsafe_allow_html=True,
            )

    with col_w:
        warnings = result.get("warnings", [])
        if warnings:
            st.markdown(
                f'<p class="section-header">Warnings ({len(warnings)})</p>',
                unsafe_allow_html=True,
            )
            for w in warnings:
                expiry = ""
                if w.get("expires_in_days"):
                    expiry = f'<br><small style="color:#555555">⏰ Expires in {w["expires_in_days"]} days</small>'
                st.markdown(
                    f'<div class="aloft-card"><strong>{w["description"]}</strong>{expiry}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<p class="section-header">No Warnings</p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="aloft-card">No compliance warnings.</div>',
                unsafe_allow_html=True,
            )

    # --- Property Details (expandable) ---
    with st.expander("Property Details"):
        epc_data = result.get("epc_data", {})
        if epc_data.get("found"):
            st.json(epc_data)
        else:
            st.warning(f"No EPC data found: {epc_data.get('error', 'Unknown error')}")

    with st.expander("Company Verification"):
        company_data = result.get("company_data", {})
        if company_data.get("found"):
            st.json(company_data)
        elif company_name:
            st.warning(f"Company not found: {company_data.get('error', 'Unknown')}")
        else:
            st.info("No company name provided — skipped verification.")

    with st.expander("Legal Requirements Checked"):
        for req in result.get("legal_requirements", []):
            st.markdown(f"- **{req.get('requirement', '')}**")
            st.caption(f"  {req.get('legislation', '')} — {req.get('section', '')}")

    # --- PDF Download ---
    st.divider()
    from src.report.pdf_generator import generate_compliance_pdf

    pdf_bytes = generate_compliance_pdf(result, postcode, company_name, elapsed)
    st.download_button(
        label="Download Compliance Report (PDF)",
        data=pdf_bytes,
        file_name=f"compliance_report_{postcode.replace(' ', '_')}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

    # --- Raw Data (for technical demo) ---
    with st.expander("Raw Agent Outputs (Debug)"):
        st.json(result.get("raw_agent_outputs", []))

    # --- Footer ---
    st.markdown(
        '<div class="aloft-footer">Aloft Compliance Firewall Demo · Built by Kaide LABS · '
        "Powered by Gemini 2.5 Flash, GPT-4o-mini, GPT-4o · "
        "Real UK government data sources · Not legal advice</div>",
        unsafe_allow_html=True,
    )

elif run_check and not postcode:
    st.error("Please enter a UK postcode.")
