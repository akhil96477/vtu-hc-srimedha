# QuantumShield Demo Presentation Guide

## ⏱️ 5-Minute Pitch Script for Judges

### 0:00 - 0:45 | Problem Setup & Reality Check
> *"Every day, mobile users face sophisticated threats targeting their financial security. Most solutions focus on only one vector. QuantumShield approaches mobile financial threat protection as defense-in-depth across three interconnected layers: the device itself, transaction activity, and future-proof transport security."*
- **Action:** Open Streamlit dashboard, highlight sidebar stats (RBI annual mobile fraud figures, FIPS 203 timeline).

### 0:45 - 1:45 | Layer 1: Device Threat Inspection (APK Analysis)
> *"An attacker begins by compromising the endpoint. We analyze Android APK declarations statically using Androguard."*
- **Action:** Open **📱 APK Analysis** tab.
- Click **Analyze Demo APK** (fake cashback rewards app).
- Show the **Permission Threat Heatmap**:
  - `READ_SMS` & `RECEIVE_SMS` (OTP interception)
  - `SYSTEM_ALERT_WINDOW` (Overlay attack spoofing bank UI)
- Highlight the **Fail-Safe Principle**: Malformed or corrupt APKs trigger `Analysis Error / Insufficient Data`, never defaulting to `SAFE`.

### 1:45 - 2:45 | Layer 2: Behavioral Transaction Assessment
> *"Now the malicious app triggers an illicit transfer. Our risk engine doesn't just check an amount; it evaluates behavioral signals."*
- **Action:** Open **💳 Transaction Risk** tab.
- Input: ₹50,000 at 2:47 AM, check **Velocity breach** and **Suspicious flag**.
- Point out the cumulative point scoring and explainable breakdown:
  - Burst velocity anomaly flagged.
  - Off-hours / sleeper hour risk factor added.
  - Result: **HIGH RISK**, recommending blocking + step-up authentication.

### 2:45 - 3:45 | Layer 3: Post-Quantum Transport Protection
> *"Even if a bank blocks or logs this transaction, that audit payload is transmitted over the wire. Adversaries today execute 'Harvest Now, Decrypt Later' (HNDL) attacks to store encrypted packets and decrypt them once quantum computers mature."*
- **Action:** Open **🔐 PQC Demo** tab.
- Click **Run PQC Demo**:
  - Show NIST FIPS 203 **ML-KEM-768** key encapsulation + **AES-256-GCM** encryption.
  - Emphasize the **Tamper Detection Test**: Byte alteration actively rejected by authenticated decryption.
- Click **Run Classical RSA Demo** $\rightarrow$ click **Simulate Quantum Attack** to visually contrast classical vulnerability with quantum resistance.

### 3:45 - 4:30 | Layer 4: The Quantum Threat Proof (Qiskit Demo)
> *"Why does classical crypto fail? Shor's algorithm solves period finding in polynomial time."*
- **Action:** Open **⚛️ Quantum Threat** tab.
- Run the quantum simulation for $N = 15 = 3 \times 5$.
- Show measurement peaks yielding period $r = 4$ and prime factors $3$ and $5$.
- Display the **Scaling Challenge Table** ($N=15 \rightarrow$ RSA-2048) and articulate the HNDL risk window.

### 4:30 - 5:00 | The Unified Pipeline & Technical Honesty
> *"Everything ties together in our Unified Threat Pipeline."*
- **Action:** Switch to **🔗 Threat Pipeline** tab.
- Show the combined threat score (e.g., $9.2 / 10$) synthesizing APK danger + transaction anomaly.
- **The Honesty Slide:**
  - Prototype scope: Static permission scanning, educational risk thresholds, simulated quantum circuits on classical backends.
  - Verification: Point out the **80 passing unit tests** across the suite.

---

## 💡 Quick Answers to Tough Judge Questions

1. **"Why not use machine learning for the transaction engine?"**
   * *Answer:* Financial regulators and compliance frameworks mandate transparent, auditable, explainable decisions. Rule-based and heuristic engines with clear scoring factors are easy to audit, debug, and configure before feeding into ML ensembles.

2. **"Does ML-KEM authenticate the server/client?"**
   * *Answer:* No, ML-KEM is strictly a Key Encapsulation Mechanism for confidentiality. Entity authentication requires digital signatures (e.g., ML-DSA / SLH-DSA) and a PKI framework. We intentionally highlight this distinction in our architecture documentation.

3. **"Why run Shor's algorithm for $N=15$ if it's already solved?"**
   * *Answer:* Simulating fault-tolerant quantum algorithms beyond toy composites exceeds classical memory and qubit simulation limits ($2^n$ state vectors). The purpose is educational proof-of-concept: validating the quantum phase estimation / period finding circuit structure that breaks the mathematical premise of RSA.
