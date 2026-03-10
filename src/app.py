import streamlit as st
import asyncio
import time
from dotenv import load_dotenv

from src.demo_postcodes import DEMO_POSTCODES  # noqa: E402

load_dotenv()

st.set_page_config(
    page_title="Aloft Compliance Firewall",
    page_icon="🛡️",
    layout="wide",
)

# --- Custom CSS for professional look ---
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6c757d;
        margin-top: 0;
    }
    .verdict-green {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .verdict-amber {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .verdict-red {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .cost-badge {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
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


# --- Header ---
st.markdown(
    '<p class="main-header">Aloft Compliance Firewall</p>', unsafe_allow_html=True
)
st.markdown(
    '<p class="sub-header">Pre-leasing regulatory compliance checking powered by multi-agent AI</p>',
    unsafe_allow_html=True,
)
st.divider()

# --- Sidebar ---
with st.sidebar:
    st.header("How It Works")
    st.markdown("""
    **Multi-Agent AI Architecture:**

    1. **Legal Rules Agent** (Gemini 2.5 Flash)
       RAG search across UK housing legislation

    2. **Property Audit Agent** (Deterministic)
       Real EPC + Companies House API checks

    3. **Risk Scorer** (GPT-4o-mini)
       Scores compliance risk 0–100

    4. **Orchestrator** (GPT-4o)
       Generates human-readable summary

    ---

    **Data Sources:**
    - EPC Open Data API
    - Companies House API
    - legislation.gov.uk
    - Housing Act 2004
    - Energy Efficiency Regs 2015
    - Renters' Rights Act 2025

    ---

    **Cost:** ~£0.01 per check
    **Latency:** <10 seconds
    """)

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

# Below the input section, before the processing block
st.markdown("**Quick Demo:**")

demo_col1, demo_col2, demo_col3 = st.columns(3)
with demo_col1:
    if st.button("🟢 GREEN Example", use_container_width=True):
        st.session_state["postcode_input"] = DEMO_POSTCODES["GREEN"]["postcode"]
        st.session_state["company_input"] = DEMO_POSTCODES["GREEN"]["company"]
        st.rerun()
with demo_col2:
    if st.button("🟡 AMBER Example", use_container_width=True):
        st.session_state["postcode_input"] = DEMO_POSTCODES["AMBER"]["postcode"]
        st.session_state["company_input"] = DEMO_POSTCODES["AMBER"]["company"]
        st.rerun()
with demo_col3:
    if st.button("🔴 RED Example", use_container_width=True):
        st.session_state["postcode_input"] = DEMO_POSTCODES["RED"]["postcode"]
        st.session_state["company_input"] = DEMO_POSTCODES["RED"]["company"]
        st.rerun()

# --- Processing & Results ---
if run_check and postcode:
    start_time = time.time()

    # Show agent status
    status_container = st.container()
    with status_container:
        st.subheader("Agent Activity")
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        with col_a1:
            agent1_status = st.empty()
            agent1_status.info("🔍 Legal Rules Agent\n\nQuerying legislation...")
        with col_a2:
            agent2_status = st.empty()
            agent2_status.info("🏠 Property Audit Agent\n\nChecking EPC & Company...")
        with col_a3:
            agent3_status = st.empty()
            agent3_status.warning("⏳ Risk Scorer\n\nWaiting for data...")
        with col_a4:
            agent4_status = st.empty()
            agent4_status.warning("⏳ Orchestrator\n\nWaiting for assessment...")

    # Run the graph
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    with col_a1:
        agent1_status.success("✅ Legal Rules Agent\n\nComplete")
    with col_a2:
        agent2_status.success("✅ Property Audit Agent\n\nComplete")
    with col_a3:
        agent3_status.success("✅ Risk Scorer\n\nComplete")
    with col_a4:
        agent4_status.success("✅ Orchestrator\n\nComplete")

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
        <h2 style="margin:0">{level_icon} {level}: {level_text}</h2>
        <p style="margin:0.3rem 0 0 0; font-size: 0.95rem; opacity: 0.8">📍 {address}</p>
        <p style="margin:0.5rem 0 0 0; font-size: 1.1rem">Risk Score: <strong>{score}/100</strong></p>
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
    st.subheader("Compliance Summary")
    st.write(result.get("summary", ""))

    # --- Violations & Warnings ---
    col_v, col_w = st.columns(2)
    with col_v:
        violations = result.get("violations", [])
        if violations:
            st.subheader(f"🚫 Violations ({len(violations)})")
            for v in violations:
                severity_color = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}.get(
                    v.get("severity", ""), "⚪"
                )
                st.markdown(
                    f"**{severity_color} {v.get('severity', 'HIGH')}:** {v['description']}"
                )
                if v.get("legislation"):
                    st.caption(f"📜 {v['legislation']}")
        else:
            st.subheader("✅ No Violations")
            st.write("No compliance violations detected.")

    with col_w:
        warnings = result.get("warnings", [])
        if warnings:
            st.subheader(f"⚠️ Warnings ({len(warnings)})")
            for w in warnings:
                st.markdown(f"**{w['description']}**")
                if w.get("expires_in_days"):
                    st.caption(f"⏰ Expires in {w['expires_in_days']} days")
        else:
            st.subheader("✅ No Warnings")
            st.write("No compliance warnings.")

    # --- Property Details (expandable) ---
    with st.expander("📋 Property Details"):
        epc_data = result.get("epc_data", {})
        if epc_data.get("found"):
            st.json(epc_data)
        else:
            st.warning(f"No EPC data found: {epc_data.get('error', 'Unknown error')}")

    with st.expander("🏢 Company Verification"):
        company_data = result.get("company_data", {})
        if company_data.get("found"):
            st.json(company_data)
        elif company_name:
            st.warning(f"Company not found: {company_data.get('error', 'Unknown')}")
        else:
            st.info("No company name provided — skipped verification.")

    with st.expander("📜 Legal Requirements Checked"):
        for req in result.get("legal_requirements", []):
            st.markdown(f"- **{req.get('requirement', '')}**")
            st.caption(f"  {req.get('legislation', '')} — {req.get('section', '')}")

    # --- PDF Download ---
    st.divider()
    from src.report.pdf_generator import generate_compliance_pdf

    pdf_bytes = generate_compliance_pdf(result, postcode, company_name, elapsed)
    st.download_button(
        label="📄 Download Compliance Report (PDF)",
        data=pdf_bytes,
        file_name=f"compliance_report_{postcode.replace(' ', '_')}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

    # --- Raw Data (for technical demo) ---
    with st.expander("🔧 Raw Agent Outputs (Debug)"):
        st.json(result.get("raw_agent_outputs", []))

    st.divider()
    st.caption(
        "Aloft Compliance Firewall Demo • Built by Kaide LABS • "
        "Powered by Gemini 2.5 Flash, GPT-4o-mini, GPT-4o • "
        "Real UK government data sources • Not legal advice"
    )

elif run_check and not postcode:
    st.error("Please enter a UK postcode.")
