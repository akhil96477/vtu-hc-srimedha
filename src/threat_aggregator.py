"""
QuantumShield Threat Aggregator
================================
Combines APK permission risk and transaction risk into a single
weighted threat score, creating a unified security assessment pipeline.

This is the connective tissue that transforms QuantumShield from
"4 separate demos" into "1 integrated security platform."

Architecture:
    APK Scanner → threat_profile → ─┐
                                     ├─→ Combined Threat Score (0-10)
    Transaction Engine → risk_result ─┘

Weights reflect real-world threat modeling:
    - APK permission risk:  40% (attack surface / device compromise)
    - Transaction anomaly:  60% (direct financial impact)
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional


def compute_combined_threat_score(
    apk_result: Optional[dict] = None,
    txn_result: Optional[dict] = None,
) -> dict:
    """
    Combine APK permission risk and transaction risk into a single
    weighted threat score on a 0–10 scale.

    Parameters
    ----------
    apk_result : dict, optional
        Output from ``apk_scanner.generate_threat_profile()`` — must contain
        'threat_profile' (dict with CRITICAL/HIGH/MEDIUM/LOW lists) and
        'risk_score' (float 0–10).  If None, APK contribution is 0.
    txn_result : dict, optional
        Output from ``transaction_risk.assess_transaction_risk()`` — must
        contain 'risk_level' (str) and optionally 'risk_points' (int).
        If None, transaction contribution is 0.

    Returns
    -------
    dict
        Combined assessment with keys:
        - apk_risk_score (float)
        - transaction_risk_score (float)
        - combined_threat_score (float, 0–10)
        - recommended_action (str)
        - risk_level (str: CRITICAL / HIGH / MEDIUM / LOW)
        - explanation (str)
        - factors (list[str])
        - timestamp (str, ISO format)
    """
    apk_score = _compute_apk_score(apk_result)
    txn_score = _compute_txn_score(txn_result)

    # Weighted combination: APK 40%, Transaction 60%
    # These weights reflect that a transaction anomaly has more immediate
    # financial impact, while APK risk represents the attack surface.
    APK_WEIGHT = 0.4
    TXN_WEIGHT = 0.6
    combined = (APK_WEIGHT * apk_score) + (TXN_WEIGHT * txn_score)
    combined = round(min(combined, 10.0), 1)

    # Determine action and risk level
    if combined >= 7.5:
        action = "BLOCK_AND_ALERT"
        risk_level = "CRITICAL"
    elif combined >= 5.0:
        action = "BLOCK_AND_REVIEW"
        risk_level = "HIGH"
    elif combined >= 3.0:
        action = "FLAG_FOR_REVIEW"
        risk_level = "MEDIUM"
    else:
        action = "ALLOW"
        risk_level = "LOW"

    # Gather explanation factors
    factors = _gather_factors(apk_result, txn_result, apk_score, txn_score)
    explanation = _generate_explanation(
        apk_score, txn_score, combined, action, factors
    )

    return {
        "apk_risk_score": round(apk_score, 1),
        "transaction_risk_score": round(txn_score, 1),
        "combined_threat_score": combined,
        "recommended_action": action,
        "risk_level": risk_level,
        "explanation": explanation,
        "factors": factors,
        "timestamp": datetime.now().isoformat(),
    }


# ──────────────────────────── Internal Helpers ────────────────────────────


def _compute_apk_score(apk_result: Optional[dict]) -> float:
    """
    Derive a 0–10 risk score from the APK threat profile.

    Scoring logic:
    - If apk_result has a pre-computed 'risk_score', use it directly.
    - Otherwise, score based on permission categories:
        • Each CRITICAL permission: +2.5 points
        • Each HIGH permission:     +1.5 points
        • Each MEDIUM permission:   +0.5 points
        • LOW permissions:          +0   points
      Capped at 10.
    """
    if apk_result is None:
        return 0.0

    # If the scanner already computed a risk_score, use it
    if "risk_score" in apk_result:
        return min(float(apk_result["risk_score"]), 10.0)

    # Manual scoring from threat_profile categories
    profile = apk_result.get("threat_profile", {})
    score = 0.0
    score += len(profile.get("CRITICAL", [])) * 2.5
    score += len(profile.get("HIGH", [])) * 1.5
    score += len(profile.get("MEDIUM", [])) * 0.5
    return min(score, 10.0)


def _compute_txn_score(txn_result: Optional[dict]) -> float:
    """
    Derive a 0–10 risk score from the transaction assessment.

    Uses risk_points if available (from the multi-factor engine),
    otherwise maps the simple risk_level string.
    """
    if txn_result is None:
        return 0.0

    # If the enhanced engine provided risk_points, scale to 0-10
    if "risk_points" in txn_result:
        # Max risk_points is typically 8 (3+2+2+1), scale to 10
        raw = float(txn_result["risk_points"])
        return min(raw * (10.0 / 8.0), 10.0)

    # Fallback: map the simple risk level string
    level_map = {
        "LOW": 2.0,
        "MEDIUM": 5.0,
        "HIGH": 8.0,
        "INVALID": 10.0,
    }
    level = txn_result.get("risk_level", "LOW")
    return level_map.get(level, 2.0)


def _gather_factors(
    apk_result: Optional[dict],
    txn_result: Optional[dict],
    apk_score: float,
    txn_score: float,
) -> list[str]:
    """Collect human-readable risk factors from both modules."""
    factors = []

    # APK factors
    if apk_result:
        verdict = apk_result.get("verdict", "UNKNOWN")
        if verdict == "DANGEROUS":
            critical_perms = apk_result.get("threat_profile", {}).get("CRITICAL", [])
            perm_names = [p.get("permission", "?") for p in critical_perms]
            factors.append(
                f"APK flagged as DANGEROUS — critical permissions detected: "
                f"{', '.join(perm_names)}"
            )
        elif verdict == "SUSPICIOUS":
            factors.append("APK flagged as SUSPICIOUS — high-risk permissions detected")
        if apk_score >= 5.0:
            factors.append(f"APK risk score is elevated: {apk_score:.1f}/10")

    # Transaction factors
    if txn_result:
        txn_factors = txn_result.get("factors", [])
        factors.extend(txn_factors)

        risk_level = txn_result.get("risk_level", "")
        if risk_level == "INVALID":
            factors.append("Transaction amount is invalid (zero or negative)")

    if not factors:
        factors.append("No significant risk factors identified")

    return factors


def _generate_explanation(
    apk_score: float,
    txn_score: float,
    combined: float,
    action: str,
    factors: list[str],
) -> str:
    """Generate a human-readable explanation of the combined assessment."""
    action_descriptions = {
        "BLOCK_AND_ALERT": (
            "Immediately block this transaction and alert the user. "
            "Multiple high-severity indicators suggest active compromise or fraud."
        ),
        "BLOCK_AND_REVIEW": (
            "Block this transaction pending manual security review. "
            "Significant risk indicators require human investigation."
        ),
        "FLAG_FOR_REVIEW": (
            "Flag this transaction for review. Proceed with additional "
            "verification (e.g., 2FA re-confirmation)."
        ),
        "ALLOW": (
            "Transaction appears normal. Allow with standard monitoring."
        ),
    }

    lines = [
        f"Combined Threat Score: {combined}/10",
        f"  • Device (APK) Risk:      {apk_score:.1f}/10 (weight: 40%)",
        f"  • Transaction Risk:       {txn_score:.1f}/10 (weight: 60%)",
        f"",
        f"Recommended Action: {action}",
        action_descriptions.get(action, ""),
        f"",
        f"Contributing Factors:",
    ]
    for i, factor in enumerate(factors, 1):
        lines.append(f"  {i}. {factor}")

    return "\n".join(lines)


# ──────────────────────────── Threat Timeline ─────────────────────────────


def generate_threat_narrative(
    apk_result: Optional[dict] = None,
    txn_result: Optional[dict] = None,
) -> list[dict]:
    """
    Generate a step-by-step threat narrative connecting the modules.

    This is used by the Streamlit dashboard to tell a coherent story
    rather than presenting disconnected module outputs.

    Returns a list of narrative steps, each with:
    - step (int)
    - layer (str)
    - title (str)
    - description (str)
    - status (str: 'danger', 'warning', 'safe', 'info')
    - icon (str: emoji)
    """
    steps = []

    # Layer 1: Device Compromise
    if apk_result:
        verdict = apk_result.get("verdict", "UNKNOWN")
        if verdict == "DANGEROUS":
            steps.append({
                "step": 1,
                "layer": "Device",
                "title": "Malicious App Detected",
                "description": (
                    f"A third-party app was found requesting critical permissions "
                    f"that enable financial attacks (OTP interception, overlay attacks). "
                    f"APK risk score: {apk_result.get('risk_score', '?')}/10."
                ),
                "status": "danger",
                "icon": "🔴",
            })
        elif verdict == "SUSPICIOUS":
            steps.append({
                "step": 1,
                "layer": "Device",
                "title": "Suspicious App Detected",
                "description": (
                    "An app with surveillance-capable permissions was found. "
                    "While not definitively malicious, these permissions enable "
                    "location tracking, audio recording, and contact exfiltration."
                ),
                "status": "warning",
                "icon": "🟠",
            })
        else:
            steps.append({
                "step": 1,
                "layer": "Device",
                "title": "App Permissions Appear Normal",
                "description": (
                    "No critical or high-risk permissions detected in the analyzed app. "
                    "Note: this does not guarantee the app is safe."
                ),
                "status": "safe",
                "icon": "🟢",
            })
    else:
        steps.append({
            "step": 1,
            "layer": "Device",
            "title": "No APK Analyzed",
            "description": "Upload an APK to assess device-layer risk.",
            "status": "info",
            "icon": "ℹ️",
        })

    # Layer 2: Transaction Anomaly
    if txn_result:
        risk_level = txn_result.get("risk_level", "LOW")
        risk_map = {
            "HIGH": ("danger", "🔴", "High-Risk Transaction Detected"),
            "MEDIUM": ("warning", "🟠", "Elevated Transaction Risk"),
            "LOW": ("safe", "🟢", "Transaction Appears Normal"),
            "INVALID": ("danger", "🔴", "Invalid Transaction Detected"),
        }
        status, icon, title = risk_map.get(
            risk_level, ("info", "ℹ️", "Transaction Assessed")
        )
        factors_text = "; ".join(txn_result.get("factors", ["No specific factors"]))
        steps.append({
            "step": 2,
            "layer": "Transaction",
            "title": title,
            "description": (
                f"Risk level: {risk_level}. Factors: {factors_text}. "
                f"{txn_result.get('recommended_action', '')}"
            ),
            "status": status,
            "icon": icon,
        })
    else:
        steps.append({
            "step": 2,
            "layer": "Transaction",
            "title": "No Transaction Analyzed",
            "description": "Submit a transaction to assess financial risk.",
            "status": "info",
            "icon": "ℹ️",
        })

    # Layer 3: Transport Security
    steps.append({
        "step": 3,
        "layer": "Transport",
        "title": "Quantum-Safe Encryption Available",
        "description": (
            "Transaction data can be encrypted using ML-KEM (FIPS 203) + "
            "AES-256-GCM, providing quantum-resistant confidentiality. "
            "This protects against 'Harvest Now, Decrypt Later' attacks."
        ),
        "status": "safe",
        "icon": "🔐",
    })

    # Layer 4: Why It Matters
    steps.append({
        "step": 4,
        "layer": "Quantum Threat",
        "title": "The Quantum Threat Is Real",
        "description": (
            "Shor's algorithm can factor large integers in polynomial time. "
            "While current quantum hardware cannot break RSA-2048, adversaries "
            "are recording encrypted traffic today to decrypt when quantum "
            "computers mature. This is why NIST standardized ML-KEM in 2024."
        ),
        "status": "warning",
        "icon": "⚛️",
    })

    return steps
