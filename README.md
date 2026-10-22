<div align="center">

# Srimedha — QuantumShield

**VTU-QFF-HC-0151** &nbsp;|&nbsp; Tier: **Online** &nbsp;|&nbsp; Event: **VTU-Qiskit Fall Fest 2026**

[![Tests](https://img.shields.io/badge/pytest-80%20passed-brightgreen.svg)]()
[![PQC Standard](https://img.shields.io/badge/NIST-FIPS%20203%20(ML--KEM)--blue.svg)]()
[![Quantum](https://img.shields.io/badge/Qiskit-Shor's%20N=15-purple.svg)]()
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)]()

</div>

---

<div align="center">

| | |
| :--- | :--- |
| **Team** | Srimedha |
| **Team ID** | VTU-QFF-HC-0151 |
| **Tier** | Online |
| **Repository** | [vtu-hc-srimedha](https://github.com/vtu-qiskit-fall-fest-2026/vtu-hc-srimedha.git) |
| **Organisation** | [vtu-qiskit-fall-fest-2026](https://github.com/vtu-qiskit-fall-fest-2026) |
| **Event** | VTU-QFF Hackathon — VTU-Qiskit Fall Fest 2026 |

</div>

---

## 🛡️ Executive Summary

**QuantumShield** is a defense-in-depth security intelligence platform engineered for mobile banking and financial transactions. It addresses threat vectors across three interconnected operational layers while demonstrating post-quantum cryptographic defenses:

1. **Endpoint Layer (APK Reconnaissance):** Static Android manifest deconstruction mapping permissions to critical financial attack surfaces (OTP theft, screen overlay phishing, and accessibility taps).
2. **Behavioral Layer (Transaction Integrity Engine):** Multi-factor anomaly scoring using sliding-window burst velocity checks (deque window), sleeper-hour temporal risk heuristics (12 AM – 5 AM), and high-value exposure limits.
3. **Transport Layer (Post-Quantum Cryptography):** NIST FIPS 203 **ML-KEM-768 (Kyber)** key encapsulation mechanism paired with **AES-256-GCM** authenticated encryption and active tamper rejection.
4. **Quantum Threat Proof (Qiskit Circuit Lab):** Educational implementation of Shor's algorithm factoring composite $N=15 = 3 \times 5$ via Quantum Phase Estimation, demonstrating why classical RSA/ECC traffic is vulnerable to Harvest Now, Decrypt Later (HNDL) attacks.
5. **Unified Threat Synthesis:** A cross-module pipeline weighting endpoint risk (40%) and transaction anomaly (60%) into an explainable 0–10 risk score with automated directives (`BLOCK_AND_ALERT`, `FLAG_FOR_REVIEW`, `ALLOW`).

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE QUANTUMSHIELD THREAT PIPELINE                    │
│                                                                         │
│  LAYER 1: DEVICE         LAYER 2: TRANSACTION      LAYER 3: TRANSPORT  │
│  ─────────────────       ──────────────────────     ─────────────────── │
│  User installs APK  ──▶  App triggers a ₹50K   ──▶  Transaction audit  │
│  with READ_SMS,          transfer at 2:47 AM        payload encrypted   │
│  RECEIVE_SMS,            with burst anomaly         via ML-KEM-768      │
│  SYSTEM_ALERT_WINDOW            │                   + AES-256-GCM       │
│         │                       │                         │             │
│         ▼                       ▼                         ▼             │
│  ┌──────────────┐      ┌─────────────────┐       ┌─────────────────┐    │
│  │ APK Scanner  │      │  Risk Engine    │       │ PQC Vault       │    │
│  │ (Androguard) │      │  (Heuristics)   │       │ (NIST FIPS 203) │    │
│  └──────┬───────┘      └────────┬────────┘       └────────┬────────┘    │
│         │                       │                         │             │
│         └───────────┬───────────┘                         │             │
│                     ▼                                     │             │
│         ┌──────────────────────┐                          │             │
│         │   THREAT AGGREGATOR  │◀─────────────────────────┘             │
│         │   Combined Score     │    (Audit payload transport secured    │
│         │   40% APK + 60% Txn  │     against HNDL quantum threat)       │
│         └──────────────────────┘                                        │
│                                                                         │
│  LAYER 4: QUANTUM DEMO (Qiskit Circuit)                                │
│  Shor's Algorithm factoring N=15 proves RSA-2048 vulnerability.         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
vtu-hc-srimedha/
├── app.py                           # 6-Tab Streamlit Dashboard (Portfolio-themed)
├── dashboard_3d.html                # Standalone Three.js 3D WebGL Interface
├── requirements.txt                 # Dependencies
├── README.md                        # Project documentation
├── .gitignore                       # Clean Python ignore rules
├── src/
│   ├── __init__.py
│   ├── threat_aggregator.py         # Cross-module unified 0-10 scorer & narrative
│   ├── transaction_risk.py          # Multi-factor risk engine (velocity, time-of-day)
│   ├── apk_scanner.py               # Androguard static analyzer + threat matrix
│   ├── post_quantum_crypto.py       # ML-KEM-768 / X25519 fallback + AES-256-GCM
│   └── quantum_demo.py              # Shor's Algorithm (N=15) circuit & HNDL context
├── tests/
│   ├── test_threat_aggregator.py    # 24 tests
│   ├── test_transaction_risk.py     # 16 tests
│   ├── test_apk_scanner.py          # 14 tests
│   ├── test_crypto.py               # 13 tests
│   └── test_quantum.py              # 13 tests
└── docs/
    ├── presentation_guide.md        # 5-minute timed judge pitch script & Q&A
    └── CONVERSATION_EXPORT.md       # Full design & implementation transcript
```

---

## ⚡ Quick Start

### 1. Installation
```bash
git clone https://github.com/vtu-qiskit-fall-fest-2026/vtu-hc-srimedha.git
cd vtu-hc-srimedha
pip install -r requirements.txt
```

### 2. Run Automated Verification Tests
```bash
pytest tests/ -v
# Output: 80 passed in ~0.20s
```

### 3. Launch Dashboard
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 🧪 Automated Test Suite (80 / 80 Passing)

| Test Module | Tests | Focus Area | Status |
| :--- | :---: | :--- | :---: |
| `tests/test_threat_aggregator.py` | 24 | Cross-module weighting, narrative generation, scoring edge cases | ✅ Passing |
| `tests/test_transaction_risk.py` | 16 | Burst velocity tracker, sleeper hour limits, point accumulation | ✅ Passing |
| `tests/test_apk_scanner.py` | 14 | Manifest parsing, threat category mapping, fail-safe error handling | ✅ Passing |
| `tests/test_crypto.py` | 13 | ML-KEM key exchange, AES-GCM encryption, active bit-flip tamper rejection | ✅ Passing |
| `tests/test_quantum.py` | 13 | Shor circuit period finding ($N=15$), eigenstate measurement, HNDL context | ✅ Passing |
| **Total** | **80** | **Comprehensive zero-mock system integrity** | **100% Pass** |

---

## 🎯 Educational Boundaries & Honest Scoping

| Claim | Reality |
| :--- | :--- |
| **"Breaks RSA-2048 with Quantum Computers"** | **No.** Shor's algorithm is demonstrated as an educational proof-of-concept simulation on $N = 15 = 3 \times 5$. Breaking RSA-2048 requires $\sim 4,096$ logical fault-tolerant qubits ($\sim 20$ million physical qubits). |
| **"Full Dynamic Malware Sandbox"** | **No.** The APK scanner performs static manifest inspection of permissions using Androguard. |
| **"End-to-End Production PKI"** | **No.** ML-KEM provides confidential key encapsulation; entity authentication requires digital signatures (e.g., ML-DSA) within a complete public key infrastructure. |

---

## 📄 License

Released under the [MIT License](LICENSE). See `LICENSE` for details.

---

<div align="center">

**Srimedha** · Team ID `VTU-QFF-HC-0151` · Tier `Online`
· Built with ⚛️ Qiskit for the VTU-QFF Hackathon

[⬆ Back to Top](#srimedha---quantumshield)

</div>
