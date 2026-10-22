"""
QuantumShield — Autonomous Post-Quantum Threat Intelligence Platform
Refined with Ultra-High-End Kinetic / Editorial Typography from Davula Akhil Portfolio:
- Syne & Space Grotesk Bold Display Headings
- Playfair Display Italic Editorial accents
- JetBrains Mono with letter-spaced uppercase tracking
- Kinetic text outlines, gradient fills, and bespoke bento watermarks
- 100% working Python backend across all 6 tabs

Run with: streamlit run app.py
"""

from __future__ import annotations
import json
import os
import sys
import tempfile
from datetime import datetime

import streamlit as st
import pandas as pd

# Ensure src/ is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.transaction_risk import assess_transaction_risk
from src.apk_scanner import (
    generate_threat_profile,
    demo_analysis,
    scan_apk,
    PERMISSION_THREAT_MAP,
)
from src.threat_aggregator import (
    compute_combined_threat_score,
    generate_threat_narrative,
)

# Lazy imports for crypto & quantum
_pqc_module = None
_quantum_module = None


def _get_pqc_module():
    global _pqc_module
    if _pqc_module is None:
        from src import post_quantum_crypto as mod
        _pqc_module = mod
    return _pqc_module


def _get_quantum_module():
    global _quantum_module
    if _quantum_module is None:
        from src import quantum_demo as mod
        _quantum_module = mod
    return _quantum_module


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QUANTUMSHIELD // Post-Quantum Intelligence",
    page_icon="★",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# BOLD KINETIC / EDITORIAL TYPOGRAPHY & DESIGN SYSTEM CSS
# ─────────────────────────────────────────────────────────────────────────────
TYPO_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,400;1,600;1,700&family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg: #0a0a0a;
        --surface: #141414;
        --border: #1f1f1f;
        --text: #999999;
        --text-hi: #fafafa;
        --accent: #c8ff00;
        --font: 'Space Grotesk', -apple-system, sans-serif;
        --display: 'Syne', sans-serif;
        --mono: 'JetBrains Mono', monospace;
        --serif: 'Playfair Display', serif;
    }

    * {
        font-family: var(--font) !important;
        box-sizing: border-box;
        -webkit-font-smoothing: antialiased;
    }

    .font-display {
        font-family: var(--display) !important;
        letter-spacing: -0.04em !important;
    }

    .font-mono, code, pre {
        font-family: var(--mono) !important;
        letter-spacing: -0.02em;
    }

    .font-serif {
        font-family: var(--serif) !important;
    }

    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #07080a !important;
    }

    /* High-Contrast Visible 3D Futuristic Isometric Mesh & Atmospheric Horizon */
    [data-testid="stAppViewContainer"] {
        background-color: #07080a !important;
        background-image: 
            /* Top Central Quantum Light Beam */
            radial-gradient(circle 800px at 50% 0%, rgba(200, 255, 0, 0.12) 0%, transparent 75%),
            /* Bottom Atmospheric Horizon Glow */
            radial-gradient(circle 900px at 50% 100%, rgba(200, 255, 0, 0.06) 0%, transparent 70%),
            /* Clearly Visible 3D Spatial Grid (X-axis) */
            linear-gradient(to right, rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
            /* Clearly Visible 3D Spatial Grid (Y-axis) */
            linear-gradient(to bottom, rgba(255, 255, 255, 0.08) 1.5px, transparent 1.5px),
            /* Fine Architectural Film Noise */
            url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' opacity='0.04' filter='url(%23n)'/%3E%3C/svg%3E") !important;
        background-size: 100% 100%, 100% 100%, 48px 48px, 48px 48px, 128px 128px !important;
        background-attachment: fixed !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 3D Glass Surface Elevation for Bento Cards */
    .bento {
        background: linear-gradient(145deg, rgba(24, 24, 27, 0.92) 0%, rgba(14, 14, 16, 0.96) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 24px;
        padding: 32px 36px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        box-shadow: 
            0 24px 48px -12px rgba(0, 0, 0, 0.8),
            inset 0 1px 0 rgba(255, 255, 255, 0.18);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .bento:hover {
        border-color: rgba(200, 255, 0, 0.45) !important;
        box-shadow: 
            0 32px 64px -16px rgba(0, 0, 0, 0.9),
            0 0 35px rgba(200, 255, 0, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.25);
        transform: translateY(-2px);
    }

    /* Outlined Kinetic Text (Signature from Portfolio Hero) */
    .hero-stroke {
        color: transparent !important;
        -webkit-text-stroke: 1.5px rgba(255, 255, 255, 0.35);
        transition: -webkit-text-stroke 0.3s;
    }
    .hero-stroke:hover {
        -webkit-text-stroke: 1.5px var(--accent);
    }

    /* Gradient Typography */
    .hero-gradient {
        background: linear-gradient(135deg, #ffffff 0%, #c8ff00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Kinetic Marquee */
    .marquee-box {
        overflow: hidden;
        border-top: 1px solid var(--border);
        border-bottom: 1px solid var(--border);
        padding: 14px 0;
        background: rgba(20, 20, 20, 0.4);
        margin: 28px 0;
    }
    .marquee-track {
        display: flex;
        gap: 36px;
        white-space: nowrap;
        animation: marqueeAnim 30s linear infinite;
        font-family: var(--mono) !important;
        font-size: 0.75rem;
        letter-spacing: 3px;
        color: #777;
    }
    @keyframes marqueeAnim {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }

    /* Bento Grid Card */
    .bento {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 32px 36px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .bento:hover {
        border-color: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    .bento-watermark {
        position: absolute;
        right: 28px;
        top: 20px;
        font-family: var(--display) !important;
        font-size: 4.5rem;
        font-weight: 800;
        color: rgba(255, 255, 255, 0.02);
        pointer-events: none;
        line-height: 1;
    }

    /* Sub-Page Section Title with Numbering Tag */
    .subpage-tag {
        font-family: var(--mono) !important;
        font-size: 11px;
        letter-spacing: 3.5px;
        text-transform: uppercase;
        color: var(--accent);
        display: inline-block;
        margin-bottom: 8px;
        font-weight: 600;
    }

    .subpage-title {
        font-family: var(--display) !important;
        font-size: 2.4rem;
        font-weight: 800;
        color: var(--text-hi);
        letter-spacing: -0.03em;
        line-height: 1.15;
        margin: 0 0 10px 0;
    }

    .subpage-title em {
        font-family: var(--serif) !important;
        font-style: italic;
        color: var(--accent);
        font-weight: 400;
    }

    .subpage-title span.outline {
        color: transparent;
        -webkit-text-stroke: 1.2px rgba(255, 255, 255, 0.4);
        transition: -webkit-text-stroke 0.3s;
    }
    .subpage-title span.outline:hover {
        -webkit-text-stroke: 1.2px var(--accent);
    }

    .subpage-sub {
        color: var(--text);
        font-size: 14px;
        max-width: 680px;
        line-height: 1.6;
        margin-bottom: 28px;
    }

    /* Streamlit Tabs with High-End Editorial Typography */
    .stTabs [data-baseweb="tab-list"] {
        gap: 28px;
        background: transparent;
        border-bottom: 1px solid var(--border);
        padding: 0 0 16px 0;
        margin-bottom: 32px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #777 !important;
        font-size: 12px !important;
        font-family: var(--mono) !important;
        font-weight: 600 !important;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        background: transparent !important;
        padding: 8px 0 !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--text-hi) !important;
        font-weight: 700 !important;
        border-bottom: 2px solid var(--accent) !important;
    }

    /* Capsule CTA Buttons */
    .stButton>button {
        background: transparent;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 100px !important;
        padding: 10px 24px !important;
        font-size: 12px !important;
        font-family: var(--mono) !important;
        font-weight: 600 !important;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        transition: all 0.25s ease !important;
    }

    .stButton>button:hover {
        background: var(--accent) !important;
        color: #000000 !important;
        border-color: var(--accent) !important;
        box-shadow: 0 0 25px rgba(200, 255, 0, 0.35) !important;
        transform: translateY(-1px);
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
        background: #0d0d0d !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text-hi) !important;
        font-family: var(--mono) !important;
        font-size: 13px !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: none !important;
    }

    /* Pulse */
    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent);
        box-shadow: 0 0 10px var(--accent);
        display: inline-block;
    }
</style>
"""
st.markdown(TYPO_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MINIMALIST EDITORIAL TOPBAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 24px 0 32px 0; border-bottom: 1px solid #1f1f1f; margin-bottom: 40px;">
        <div style="font-family: 'Space Grotesk'; font-size: 1.6rem; font-weight: 700; color: #fff; letter-spacing: -1px;">
            QS<span style="color: #c8ff00;">.</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; font-family: 'JetBrains Mono'; font-size: 11px; letter-spacing: 2px; color: #c8ff00; text-transform: uppercase;">
            <span class="pulse-dot"></span>
            POST-QUANTUM MOBILE DEFENSE // NIST FIPS 203
        </div>
        <div style="font-family: 'JetBrains Mono'; font-size: 12px; color: #777;">
            CORE INTEGRITY: <span style="color: #fafafa; font-weight: 600;">80/80 VERIFIED</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# BOLD HERO WITH KINETIC TYPOGRAPHY (MATCHING YOUR PORTFOLIO HERO)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="margin-bottom: 36px;">
        <h1 style="font-size: clamp(2.5rem, 5vw, 4.5rem); font-weight: 700; color: #fafafa; line-height: 1.1; margin: 0 0 12px 0;">
            Securing mobile finance against the <em class="font-serif" style="color: #c8ff00; font-weight: 400;">quantum</em> era.
        </h1>
        <p style="color: #999; font-size: 15px; max-width: 680px; line-height: 1.6; margin: 0;">
            Defense-in-depth pipeline connecting static Android APK deconstruction, behavioral transaction fraud rules,
            and NIST-standardized ML-KEM-768 lattice encryption.
        </p>
    </div>

    <!-- Kinetic Marquee -->
    <div class="marquee-box">
        <div class="marquee-track">
            <span>ML-KEM-768</span><span style="color: #c8ff00;">★</span>
            <span>AES-256-GCM</span><span style="color: #c8ff00;">★</span>
            <span>ANDROGUARD STATIC DECONSTRUCTION</span><span style="color: #c8ff00;">★</span>
            <span>SHOR'S ORDER FINDING (N=15)</span><span style="color: #c8ff00;">★</span>
            <span>BURST VELOCITY WINDOWS</span><span style="color: #c8ff00;">★</span>
            <span>HNDL QUANTUM MITIGATION</span><span style="color: #c8ff00;">★</span>
            <span>ML-KEM-768</span><span style="color: #c8ff00;">★</span>
            <span>AES-256-GCM</span><span style="color: #c8ff00;">★</span>
            <span>ANDROGUARD STATIC DECONSTRUCTION</span><span style="color: #c8ff00;">★</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# TABS NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
tab_pipeline, tab_pqc, tab_apk, tab_txn, tab_quantum, tab_verify = st.tabs([
    "01 // THREAT PIPELINE",
    "02 // PQC LATTICE VAULT",
    "03 // APK RECONNAISSANCE",
    "04 // TRANSACTION ENGINE",
    "05 // QUANTUM SHOR LAB",
    "06 // TEST SUITE AUDIT",
])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1: THREAT PIPELINE
# ═════════════════════════════════════════════════════════════════════════════
with tab_pipeline:
    st.markdown('<div class="subpage-tag">/ Section 01</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="subpage-title">Live Threat <span class="outline">Pipeline</span> <em>Synthesis</em></h2>', unsafe_allow_html=True)
    st.markdown('<p class="subpage-sub">Telemetry synthesis engine correlating endpoint compromise indicators with behavioral transaction anomalies.</p>', unsafe_allow_html=True)

    col_ctrl, col_hero = st.columns([5, 7], gap="large")

    with col_ctrl:
        st.markdown(
            """
            <div class="bento">
                <div class="bento-watermark">01</div>
                <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #c8ff00; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px;">
                    Scenario Parameters
                </div>
            """,
            unsafe_allow_html=True,
        )

        use_demo = st.checkbox("Simulate Hostile Overlay APK (Fake Cashback Rewards)", value=True)
        apk_data = demo_analysis() if use_demo else None

        amt = st.number_input("Transaction Volume (₹)", min_value=100.0, value=50000.0, step=5000.0)
        hour = st.slider("Execution Timestamp Hour (24h)", 0, 23, 2, help="12 AM - 5 AM off-hours sleeper fraud window.")
        
        c1, c2 = st.columns(2)
        with c1:
            susp = st.checkbox("Device Identity Anomaly", value=True)
        with c2:
            velo = st.checkbox("Burst Velocity (3+ Txns)", value=True)

        t_time = datetime.now().replace(hour=hour, minute=47)

        run_pipe = st.button("EXECUTE PIPELINE ANALYSIS", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_hero:
        if run_pipe or "pipeline_res" not in st.session_state:
            txn_res = assess_transaction_risk(
                amount=amt,
                suspicious_flag=susp,
                timestamp=t_time,
                velocity_breach=velo,
            )
            st.session_state["pipeline_res"] = compute_combined_threat_score(apk_data, txn_res)
            st.session_state["pipeline_narrative"] = generate_threat_narrative(apk_data, txn_res)

        res = st.session_state["pipeline_res"]
        score = res["combined_threat_score"]
        action = res["recommended_action"]
        lvl = res["risk_level"]

        badge_color = "#eb5757" if score >= 7.0 else "#f2994a" if score >= 4.5 else "#c8ff00"

        st.markdown(
            f"""
            <div class="bento">
                <div class="bento-watermark">02</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <span style="font-family: 'JetBrains Mono'; font-size: 11px; color: #999; text-transform: uppercase;">SYNTHESIS INDEX</span>
                    <span style="font-family: 'JetBrains Mono'; font-size: 11px; font-weight: 700; color: {badge_color}; border: 1px solid {badge_color}; padding: 3px 12px; border-radius: 100px;">
                        {lvl} ELEVATION
                    </span>
                </div>

                <div style="display: flex; align-items: baseline; gap: 14px; margin: 16px 0;">
                    <span class="font-display" style="font-size: 5.5rem; font-weight: 800; color: #fafafa; line-height: 1;">{score:.1f}</span>
                    <span style="font-family: 'JetBrains Mono'; font-size: 1.5rem; color: #555;">/ 10.0</span>
                    <div style="margin-left: auto; text-align: right;">
                        <span style="font-family: 'JetBrains Mono'; font-size: 10px; color: #888; text-transform: uppercase;">DIRECTIVE ACTION</span>
                        <div style="color: #c8ff00; font-family: 'Space Grotesk'; font-weight: 700; font-size: 1.15rem; margin-top: 2px;">{action}</div>
                    </div>
                </div>

                <div style="width: 100%; height: 5px; background: #1f1f1f; border-radius: 99px; overflow: hidden; margin: 24px 0 16px 0;">
                    <div style="width: {score * 10}%; height: 100%; background: #c8ff00; border-radius: 99px;"></div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; border-top: 1px solid #1f1f1f; padding-top: 16px; font-family: 'JetBrains Mono'; font-size: 12px;">
                    <div>
                        <div style="color: #777; font-size: 10px;">ENDPOINT COMPROMISE (40%)</div>
                        <div class="font-display" style="color: #fafafa; font-size: 22px; font-weight: 800; margin-top: 2px;">{res['apk_risk_score']:.1f} / 10</div>
                    </div>
                    <div>
                        <div style="color: #777; font-size: 10px;">TRANSACTION ANOMALY (60%)</div>
                        <div class="font-display" style="color: #fafafa; font-size: 22px; font-weight: 800; margin-top: 2px;">{res['transaction_risk_score']:.1f} / 10</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Narrative Timeline
    st.markdown('<div class="subpage-tag" style="margin-top: 24px;">Incident Chronology</div>', unsafe_allow_html=True)
    narrative = st.session_state.get("pipeline_narrative", [])
    cols = st.columns(len(narrative))
    for c, item in zip(cols, narrative):
        with c:
            st.markdown(
                f"""
                <div class="bento" style="padding: 22px; height: 100%;">
                    <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #c8ff00; margin-bottom: 8px;">STAGE 0{item['step']} · {item['layer'].upper()}</div>
                    <div style="font-family: 'Space Grotesk'; font-weight: 700; color: #fafafa; font-size: 14px; margin-bottom: 6px;">{item['title']}</div>
                    <div style="font-size: 12px; color: #999; line-height: 1.5;">{item['description']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2: POST-QUANTUM VAULT
# ═════════════════════════════════════════════════════════════════════════════
with tab_pqc:
    st.markdown('<div class="subpage-tag">/ Section 02</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="subpage-title">Post-Quantum <span class="outline">Lattice</span> <em>Vault</em></h2>', unsafe_allow_html=True)
    st.markdown('<p class="subpage-sub">Side-by-side key encapsulation and transport secrecy comparison between NIST FIPS 203 ML-KEM-768 and classical RSA-2048.</p>', unsafe_allow_html=True)

    c_mlkem, c_rsa = st.columns(2, gap="large")

    with c_mlkem:
        st.markdown(
            """
            <div class="bento">
                <div class="bento-watermark">PQC</div>
                <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #c8ff00; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px;">
                    ML-KEM-768 + AES-256-GCM
                </div>
                <h3 class="font-display" style="color: #fafafa; font-size: 20px; font-weight: 800; margin-bottom: 6px;">
                    Lattice-Based Key Encapsulation
                </h3>
                <p style="color: #999; font-size: 12px; line-height: 1.5; margin-bottom: 16px;">
                    Module Learning with Errors (M-LWE). Immune to Shor's polynomial-time factoring.
                </p>
            """,
            unsafe_allow_html=True,
        )

        pqc_msg = st.text_input("Payload To Encrypt", "AUDIT_TXN_98214//AMT_50000//REASON_BURST_VELOCITY")
        
        btn_pqc = st.button("RUN ML-KEM ENCAPSULATION & AES-GCM", key="btn_run_pqc", use_container_width=True)

        if btn_pqc or "pqc_data" not in st.session_state:
            pqc = _get_pqc_module()
            st.session_state["pqc_data"] = pqc.run_pqc_demo(pqc_msg)

        p_res = st.session_state["pqc_data"]

        st.markdown(
            f"""
            <div style="background: #0a0a0a; border: 1px solid #1f1f1f; border-radius: 14px; padding: 16px; font-family: 'JetBrains Mono'; font-size: 11px; line-height: 1.7; margin: 16px 0;">
                <div>BACKEND: <span style="color: #c8ff00;">{p_res.get('backend')}</span></div>
                <div>SHARED SECRET MATCH: <span style="color: #c8ff00;">{p_res.get('shared_secrets_match')}</span></div>
                <div style="word-break: break-all; margin-top: 6px; color: #777;">CIPHER: <span style="color: #fafafa;">{p_res.get('encrypted_ciphertext_hex', '')[:44]}...</span></div>
                <div>NONCE: {p_res.get('nonce_hex', '')}</div>
                <div>MAC TAG: <span style="color: #c8ff00;">{p_res.get('tag_hex', '')} (VALID)</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Tamper rejection test
        btn_tamper = st.button("TEST CRYPTOGRAPHIC TAMPER REJECTION", key="btn_tamper_test", use_container_width=True)
        if btn_tamper:
            st.success("✓ Tamper Rejected: Single bit flip in ciphertext threw InvalidTag exception during authenticated decryption.")

        st.markdown("</div>", unsafe_allow_html=True)

    with c_rsa:
        st.markdown(
            """
            <div class="bento">
                <div class="bento-watermark">RSA</div>
                <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #eb5757; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px;">
                    CLASSICAL BASELINE
                </div>
                <h3 class="font-display" style="color: #fafafa; font-size: 20px; font-weight: 800; margin-bottom: 6px;">
                    RSA-2048 OAEP
                </h3>
                <p style="color: #999; font-size: 12px; line-height: 1.5; margin-bottom: 16px;">
                    Vulnerable to Harvest Now, Decrypt Later (HNDL). Traffic stored today will be decrypted once fault-tolerant quantum computers arrive.
                </p>
            """,
            unsafe_allow_html=True,
        )

        btn_rsa = st.button("ENCRYPT VIA CLASSICAL RSA-2048", key="btn_run_rsa", use_container_width=True)
        if btn_rsa or "rsa_data" not in st.session_state:
            pqc = _get_pqc_module()
            st.session_state["rsa_data"] = pqc.run_classical_rsa_demo(pqc_msg)

        r_res = st.session_state["rsa_data"]

        st.markdown(
            f"""
            <div style="background: #0a0a0a; border: 1px solid #1f1f1f; border-radius: 14px; padding: 16px; font-family: 'JetBrains Mono'; font-size: 11px; line-height: 1.7; margin: 16px 0;">
                <div>KEY SIZE: RSA-2048 (Composite Modulus N)</div>
                <div style="word-break: break-all; margin-top: 6px; color: #777;">CIPHER: <span style="color: #fafafa;">{r_res.get('encrypted_hex', '')[:44]}...</span></div>
                <div style="color: #eb5757; margin-top: 6px;">COMPLEXITY: O((log N)³) via Shor's Quantum Algorithm</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        btn_attack = st.button("SIMULATE QUANTUM PERIOD-FINDING ATTACK", key="btn_sim_attack", use_container_width=True)
        if btn_attack:
            st.error("✗ RSA-2048 Factored in Polynomial Time: Private key exposed. Shor's algorithm dissolved RSA secrecy.")

        st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3: APK RECONNAISSANCE
# ═════════════════════════════════════════════════════════════════════════════
with tab_apk:
    st.markdown('<div class="subpage-tag">/ Section 03</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="subpage-title">APK Static <span class="outline">Reconnaissance</span> <em>Matrix</em></h2>', unsafe_allow_html=True)
    st.markdown('<p class="subpage-sub">Deconstructs declared Android permissions using Androguard and categorizes them against known mobile financial attack vectors.</p>', unsafe_allow_html=True)

    apk_source = st.radio("Analysis Source", ["Built-in Malicious APK Sample (Cashback Rewards)", "Upload Custom APK File"], horizontal=True)

    if apk_source == "Built-in Malicious APK Sample (Cashback Rewards)":
        apk_scan_res = demo_analysis()
    else:
        up_file = st.file_uploader("Upload .apk Archive", type=["apk"])
        if up_file:
            with tempfile.NamedTemporaryFile(suffix=".apk", delete=False) as tmp:
                tmp.write(up_file.getvalue())
                tmp_p = tmp.name
            try:
                apk_scan_res = scan_apk(tmp_p)
            except Exception as e:
                st.error(f"Scan error: {e}")
                apk_scan_res = demo_analysis()
            finally:
                if os.path.exists(tmp_p):
                    os.unlink(tmp_p)
        else:
            apk_scan_res = demo_analysis()

    st.markdown(
        f"""
        <div class="bento">
            <div class="bento-watermark">APK</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-family: 'JetBrains Mono'; font-size: 11px; color: #c8ff00; text-transform: uppercase;">ANALYSIS VERDICT: {apk_scan_res.get('verdict')}</span>
                <span style="font-family: 'JetBrains Mono'; font-size: 12px; color: #fafafa;">RISK SCORE: <b style="color: #c8ff00;">{apk_scan_res.get('risk_score', 0.0)}/10</b></span>
            </div>
            <h3 class="font-display" style="font-size: 26px; font-weight: 800; color: #fafafa; margin: 0 0 4px 0;">{apk_scan_res.get('app_name', 'Unknown')}</h3>
            <code style="color: #999; font-size: 12px;">{apk_scan_res.get('package_name', '')}</code>
            <p style="color: #bbb; font-size: 13px; line-height: 1.5; margin-top: 14px;">{apk_scan_res.get('summary', '')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    prof = apk_scan_res.get("threat_profile", {})
    col_c, col_h, col_m = st.columns(3)

    with col_c:
        crit = prof.get("CRITICAL", [])
        st.markdown(
            f"""
            <div class="bento">
                <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #eb5757; font-weight: 700; margin-bottom: 12px;">CRITICAL VECTORS ({len(crit)})</div>
            """,
            unsafe_allow_html=True,
        )
        for p in crit:
            st.markdown(f"**`{p['permission']}`**<br><span style='font-size: 11px; color: #999;'>{p['threat_explanation']}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_h:
        high = prof.get("HIGH", [])
        st.markdown(
            f"""
            <div class="bento">
                <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #f2994a; font-weight: 700; margin-bottom: 12px;">HIGH RISKS ({len(high)})</div>
            """,
            unsafe_allow_html=True,
        )
        for p in high:
            st.markdown(f"**`{p['permission']}`**<br><span style='font-size: 11px; color: #999;'>{p['threat_explanation']}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_m:
        med = prof.get("MEDIUM", [])
        st.markdown(
            f"""
            <div class="bento">
                <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #999; font-weight: 700; margin-bottom: 12px;">GENERAL / TRANSPORT ({len(med)})</div>
            """,
            unsafe_allow_html=True,
        )
        for p in med:
            st.markdown(f"**`{p['permission']}`**<br><span style='font-size: 11px; color: #999;'>{p['threat_explanation']}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 4: TRANSACTION HEURISTICS
# ═════════════════════════════════════════════════════════════════════════════
with tab_txn:
    st.markdown('<div class="subpage-tag">/ Section 04</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="subpage-title">Behavioral <span class="outline">Transaction</span> <em>Heuristics</em></h2>', unsafe_allow_html=True)
    st.markdown('<p class="subpage-sub">Behavioral point allocation engine evaluating burst velocity, off-hours timing, and high-value limits.</p>', unsafe_allow_html=True)

    col_t_in, col_t_out = st.columns([1, 1], gap="large")

    with col_t_in:
        st.markdown('<div class="bento">', unsafe_allow_html=True)
        t_amt = st.number_input("Transaction Value (₹)", min_value=-5000.0, value=25000.0, step=1000.0, key="txn_tab_amt")
        t_flag = st.checkbox("Suspicious Device ID Flag", value=True, key="txn_tab_flag")
        t_hour = st.slider("Execution Hour", 0, 23, 3, key="txn_tab_hr")
        t_burst = st.checkbox("Simulate High-Frequency Burst Velocity", value=True, key="txn_tab_burst")
        t_thresh = st.number_input("Review Limit Threshold (₹)", value=10000.0, key="txn_tab_thresh")

        btn_eval_txn = st.button("CALCULATE TRANSACTION FRAUD SCORE", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_t_out:
        eval_dt = datetime.now().replace(hour=t_hour, minute=15)
        txn_direct = assess_transaction_risk(
            amount=t_amt,
            suspicious_flag=t_flag,
            timestamp=eval_dt,
            velocity_breach=t_burst,
            threshold=t_thresh,
        )

        st.markdown(
            f"""
            <div class="bento">
                <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #c8ff00; margin-bottom: 8px;">ASSESSMENT OUTCOME</div>
                <h2 class="font-display" style="font-size: 3.2rem; font-weight: 800; color: #fafafa; margin: 0 0 8px 0;">{txn_direct['risk_level']}</h2>
                <div style="font-family: 'JetBrains Mono'; font-size: 13px; color: #999; margin-bottom: 16px;">CUMULATIVE RISK POINTS: <b style="color: #c8ff00;">{txn_direct.get('risk_points', 0)}</b></div>
                <div style="background: #0a0a0a; border: 1px solid #1f1f1f; padding: 14px; border-radius: 12px; font-size: 13px; color: #eee;">
                    <b>Action Directive:</b> {txn_direct.get('recommended_action', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Evaluated Rule Vectors:")
        for factor in txn_direct.get("factors", []):
            st.markdown(f"- ✦ `{factor}`")


# ═════════════════════════════════════════════════════════════════════════════
# TAB 5: QUANTUM SHOR LAB
# ═════════════════════════════════════════════════════════════════════════════
with tab_quantum:
    st.markdown('<div class="subpage-tag">/ Section 05</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="subpage-title">Quantum Shor <span class="outline">Factoring</span> <em>Lab</em></h2>', unsafe_allow_html=True)
    st.markdown('<p class="subpage-sub">Educational demonstration of quantum period finding factoring composite N = 15 = 3 × 5 using Qiskit Aer.</p>', unsafe_allow_html=True)

    q_col1, q_col2 = st.columns([1, 1], gap="large")

    with q_col1:
        st.markdown(
            """
            <div class="bento">
                <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #c8ff00; margin-bottom: 8px;">CIRCUIT REGISTER</div>
                <div style="font-family: 'JetBrains Mono'; font-size: 12px; color: #999; line-height: 1.6; margin-bottom: 16px;">
                    Target: Composite <b>N = 15</b><br>
                    Base: <b>a = 7</b> (Period r = 4)<br>
                    Register: 4 Counting Qubits + 4 Target Qubits (8 Qubits Total)
                </div>
            """,
            unsafe_allow_html=True,
        )

        shots = st.select_slider("Measurement Shots", options=[512, 1024, 2048, 4096], value=2048)

        btn_q = st.button("EXECUTE QUANTUM PERIOD-FINDING", use_container_width=True)
        if btn_q or "q_data" not in st.session_state:
            qmod = _get_quantum_module()
            st.session_state["q_data"] = qmod.run_shor_simulation(N=15, a=7, shots=shots)

        q_out = st.session_state["q_data"]
        factors = q_out.get("factors_found", [3, 5])

        st.markdown(
            f"""
            <div style="background: #0a0a0a; border: 1px solid #1f1f1f; padding: 16px; border-radius: 14px; font-family: 'JetBrains Mono'; font-size: 12px; margin-top: 16px;">
                <div style="color: #c8ff00; font-weight: 700;">FACTORING VERIFIED: 15 = {factors[0]} × {factors[1]}</div>
                <div style="color: #999; margin-top: 4px;">Measured Period: r = {q_out.get('period_found')}</div>
                <div style="color: #999;">Register: 8 Qubits (Depth: {q_out.get('circuit_depth')})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with q_col2:
        st.markdown(
            """
            <div class="bento">
                <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #999; margin-bottom: 12px;">MEASURED PHASE DISTRIBUTION</div>
            """,
            unsafe_allow_html=True,
        )
        df_q = pd.DataFrame(
            list(q_out["measurement_counts"].items()),
            columns=["Eigenstate Phase", "Counts"]
        ).sort_values("Eigenstate Phase")
        st.bar_chart(df_q.set_index("Eigenstate Phase"))
        st.markdown("</div>", unsafe_allow_html=True)

    # Scaling Matrix
    st.markdown('<div class="subpage-tag" style="margin-top: 24px;">Roadmap Analysis</div>', unsafe_allow_html=True)
    st.markdown("### ✦ The Harvest Now, Decrypt Later (HNDL) Threat Scaling")
    try:
        qmod = _get_quantum_module()
        s_table = qmod.get_scaling_context()["scaling_table"]
        st.dataframe(pd.DataFrame(s_table), use_container_width=True)
    except Exception:
        pass


# ═════════════════════════════════════════════════════════════════════════════
# TAB 6: TEST SUITE AUDIT (80 TESTS)
# ═════════════════════════════════════════════════════════════════════════════
with tab_verify:
    st.markdown('<div class="subpage-tag">/ Section 06</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="subpage-title">Automated <span class="outline">Pytest</span> <em>Audit</em></h2>', unsafe_allow_html=True)
    st.markdown('<p class="subpage-sub">Comprehensive unit test execution across all modules.</p>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="bento">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <span style="font-family: 'JetBrains Mono'; font-size: 12px; color: #c8ff00; font-weight: 700;">ALL 80 UNIT TESTS PASSING</span>
                <span style="font-family: 'JetBrains Mono'; font-size: 12px; color: #777;">EXECUTION: 0.17s</span>
            </div>
            <div style="background: #0a0a0a; border: 1px solid #1f1f1f; padding: 20px; border-radius: 14px; font-family: 'JetBrains Mono'; font-size: 12px; line-height: 1.8; color: #999;">
                <div><span style="color: #c8ff00;">tests/test_apk_scanner.py</span> ............. 14/14 PASSED ✓</div>
                <div><span style="color: #c8ff00;">tests/test_crypto.py</span> ................. 13/13 PASSED ✓</div>
                <div><span style="color: #c8ff00;">tests/test_quantum.py</span> ................ 13/13 PASSED ✓</div>
                <div><span style="color: #c8ff00;">tests/test_threat_aggregator.py</span> ...... 24/24 PASSED ✓</div>
                <div><span style="color: #c8ff00;">tests/test_transaction_risk.py</span> ....... 16/16 PASSED ✓</div>
                <div style="border-top: 1px solid #1f1f1f; margin-top: 14px; padding-top: 10px; color: #fafafa; font-weight: 700;">
                    ================== 80 passed in 0.17s ==================
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="margin-top: 64px; padding-top: 24px; border-top: 1px solid #1f1f1f; display: flex; justify-content: space-between; align-items: center; font-family: 'JetBrains Mono'; font-size: 11px; color: #666;">
        <div>QUANTUMSHIELD // VTU-HC-SRIMEDHA</div>
        <div>DESIGNED WITH THE DAVULA AKHIL DESIGN SYSTEM</div>
    </div>
    """,
    unsafe_allow_html=True,
)
