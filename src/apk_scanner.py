"""QuantumShield - Static Android APK Permission Analyzer.

This module inspects Android application permissions declared in the AndroidManifest.xml
and evaluates potential threat vectors targeting mobile banking and financial transactions.

Threat Modeling Context:
- Mobile banking trojans (e.g., TeaBot, Anatsa, SharkBot) often exploit a small set of
  high-privilege permissions to intercept one-time passwords (OTPs), launch overlay attacks,
  or perform automated unauthorized fund transfers via accessibility abuse.
- This module categorizes requested permissions into CRITICAL, HIGH, MEDIUM, and LOW risk
  categories and computes a weighted composite risk score (0-10) with a verdict.

Fail-Safe Principle:
- Any file reading, parsing, or integrity failure produces an ERROR verdict.
- An analyzer must NEVER fall back to 'SAFE' or 'LOW_CONCERN' on corrupt or unreadable APKs.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Graceful import of Androguard:
# The module must import cleanly even when Androguard is not yet installed in the environment.
try:
    from androguard.core.bytecodes.apk import APK  # type: ignore

    ANDROGUARD_AVAILABLE = True
except ImportError:
    try:
        # Fallback import path supported by some Androguard versions
        from androguard.misc import AnalyzeAPK  # type: ignore

        ANDROGUARD_AVAILABLE = True
    except ImportError:
        ANDROGUARD_AVAILABLE = False


# ==============================================================================
# Permission Threat Classification Map
# ==============================================================================
# Mappings represent financial security attack vectors:
# - CRITICAL: Direct financial theft vectors (OTP interception, screen overlays, ATS automation)
# - HIGH: Surveillance, reconnaissance, and social engineering vectors
# - MEDIUM: Data exfiltration channels and background persistence mechanisms
# ==============================================================================

PERMISSION_THREAT_MAP: dict[str, dict[str, str]] = {
    "CRITICAL": {
        "READ_SMS": "Can intercept OTP codes sent by banks",
        "RECEIVE_SMS": "Can silently receive and hide SMS messages",
        "SEND_SMS": "Can send premium-rate SMS or forward OTPs to attacker",
        "SYSTEM_ALERT_WINDOW": "Can draw fake login screens over banking apps (overlay attack)",
        "BIND_ACCESSIBILITY_SERVICE": "Can read screen content and simulate user taps",
        "READ_PHONE_STATE": "Can access device IMEI and phone number for tracking",
    },
    "HIGH": {
        "ACCESS_FINE_LOCATION": "Tracks precise GPS location",
        "CAMERA": "Can silently capture photos/video",
        "RECORD_AUDIO": "Can record conversations and surroundings",
        "READ_CONTACTS": "Can exfiltrate contact list for social engineering",
        "READ_CALL_LOG": "Can monitor call patterns",
        "GET_ACCOUNTS": "Can enumerate user accounts on the device",
    },
    "MEDIUM": {
        "INTERNET": "Can transmit collected data to external servers",
        "READ_EXTERNAL_STORAGE": "Can access files, photos, documents",
        "WRITE_EXTERNAL_STORAGE": "Can modify or plant files",
        "INSTALL_PACKAGES": "Can silently install additional malicious apps",
        "WAKE_LOCK": "Can prevent device from sleeping to maintain background activity",
    },
}

# Educational caveat on static analysis constraints
STATIC_ANALYSIS_CAVEAT: str = (
    "Static manifest analysis inspects declared permissions but cannot verify runtime behavior. "
    "Malware may conceal activity through dynamic class loading, reflection, or native payloads. "
    "Full assurance requires multi-layered defense combining static inspection, behavioral "
    "heuristics, and post-quantum encrypted transport."
)


def extract_permission_short_name(permission: str) -> str:
    """Extract the normalized permission short name from a qualified Android permission string.

    Android permissions are usually fully qualified strings such as
    'android.permission.READ_SMS' or 'com.android.launcher.permission.INSTALL_SHORTCUT'.
    This helper normalizes and strips namespaces to obtain the core token (e.g., 'READ_SMS').

    Args:
        permission: Raw permission string (e.g. 'android.permission.READ_SMS').

    Returns:
        Short permission name (e.g. 'READ_SMS'), stripped of leading/trailing spaces.
    """
    if not permission:
        return ""
    cleaned = str(permission).strip()
    return cleaned.split(".")[-1]


def classify_permission(permission: str) -> tuple[str, str]:
    """Classify an individual permission into a threat category and explanation.

    Args:
        permission: Full or short Android permission name.

    Returns:
        Tuple of (category, threat_explanation) where category is one of
        'CRITICAL', 'HIGH', 'MEDIUM', or 'LOW'.
    """
    short_name = extract_permission_short_name(permission)

    for category, perms_dict in PERMISSION_THREAT_MAP.items():
        if short_name in perms_dict:
            return category, perms_dict[short_name]
        if permission in perms_dict:
            return category, perms_dict[permission]

    return "LOW", "Standard Android application permission with low direct security/financial risk."


def analyze_apk(file_path: str) -> dict[str, Any]:
    """Perform static inspection of an Android APK file using Androguard.

    Extracts application package metadata and the complete list of declared
    permissions from the embedded AndroidManifest.xml.

    Educational Note on APK Parsing Security:
    - Attackers frequently construct malformed APK archives (manipulated zip headers,
      duplicate central directory records) to crash or evade standard antivirus scanners.
    - To adhere to the fail-safe principle, any parsing anomaly immediately returns
      status='ERROR' rather than assuming benign behavior.

    Args:
        file_path: Filesystem path to the APK package.

    Returns:
        Dict containing:
            - status: 'SUCCESS' or 'ERROR'
            - package_name: App package identifier (or None on error)
            - app_name: Display name of the application (or None)
            - version_code: Internal build version number (or None)
            - version_name: User-visible version string (or None)
            - permissions: List of permission string identifiers
            - error: Human-readable error description if status == 'ERROR', else None

    Raises:
        ImportError: If Androguard is not installed and an existing .apk file is analyzed.
    """
    # 1. Parameter Validation: empty or non-string check
    if not file_path or not isinstance(file_path, (str, Path)):
        return {
            "status": "ERROR",
            "package_name": None,
            "app_name": None,
            "version_code": None,
            "version_name": None,
            "permissions": [],
            "error": "Validation error: Valid file path must be provided.",
        }

    target_path = Path(file_path)

    # 2. Extension Validation: Reject non-APK files early
    if target_path.suffix.lower() != ".apk":
        return {
            "status": "ERROR",
            "package_name": None,
            "app_name": None,
            "version_code": None,
            "version_name": None,
            "permissions": [],
            "error": (
                f"Validation error: Expected .apk file extension, but received '{target_path.suffix}'."
            ),
        }

    # 3. File Existence Validation
    if not target_path.is_file():
        return {
            "status": "ERROR",
            "package_name": None,
            "app_name": None,
            "version_code": None,
            "version_name": None,
            "permissions": [],
            "error": f"File does not exist: {file_path}",
        }

    # 4. Dependency Validation: Verify Androguard is installed
    if not ANDROGUARD_AVAILABLE:
        raise ImportError(
            "Androguard is required for APK static analysis but is not installed. "
            "Please install it using 'pip install androguard'."
        )

    # 5. APK Archive Parsing
    try:
        apk_obj = APK(str(target_path))

        # Check APK integrity if method is provided by Androguard version
        if hasattr(apk_obj, "is_valid_APK") and not apk_obj.is_valid_APK():
            return {
                "status": "ERROR",
                "package_name": None,
                "app_name": None,
                "version_code": None,
                "version_name": None,
                "permissions": [],
                "error": "Malformed APK: File archive is corrupt or invalid Android package.",
            }

        package_name = apk_obj.get_package()
        app_name = apk_obj.get_app_name()
        version_code = apk_obj.get_androidversion_code()
        version_name = apk_obj.get_androidversion_name()
        raw_permissions = apk_obj.get_permissions() or []

        return {
            "status": "SUCCESS",
            "package_name": str(package_name) if package_name is not None else None,
            "app_name": str(app_name) if app_name is not None else None,
            "version_code": str(version_code) if version_code is not None else None,
            "version_name": str(version_name) if version_name is not None else None,
            "permissions": [str(p) for p in raw_permissions],
            "error": None,
        }

    except Exception as exc:
        # Conservative fail-safe handling: Never return 'SAFE' or default permissions on failure
        return {
            "status": "ERROR",
            "package_name": None,
            "app_name": None,
            "version_code": None,
            "version_name": None,
            "permissions": [],
            "error": f"Malformed APK parsing error: {exc}",
        }


def generate_threat_profile(permissions: list[str] | None) -> dict[str, Any]:
    """Evaluate permissions list against threat vectors to generate a security profile.

    Risk Scoring Algorithm:
    - CRITICAL permissions = +2.5 points each (Direct financial attack vectors)
    - HIGH permissions = +1.5 points each (Surveillance & reconnaissance)
    - MEDIUM permissions = +0.5 points each (Potential abuse / exfiltration)
    - LOW permissions = +0.0 points each (Standard benign application functions)
    - Total score is capped at 10.0 (maximum risk).

    Verdict Determination:
    - 'DANGEROUS': Any CRITICAL permission detected (immediate financial threat)
    - 'SUSPICIOUS': No CRITICAL, but at least one HIGH permission detected
    - 'MODERATE': No CRITICAL or HIGH, but at least one MEDIUM permission detected
    - 'LOW_CONCERN': Only LOW permissions (or empty permission list)

    Args:
        permissions: List of permission string identifiers from APK manifest.

    Returns:
        Dict containing:
            - verdict: 'DANGEROUS' | 'SUSPICIOUS' | 'MODERATE' | 'LOW_CONCERN'
            - summary: Human-readable assessment of the permission risk
            - risk_score: Float between 0.0 and 10.0
            - threat_profile: Dict with lists of categorized threat entries
            - total_permissions: Count of total unique permissions evaluated
            - caveat: Educational notice regarding static analysis limitations
    """
    threat_profile: dict[str, list[dict[str, str]]] = {
        "CRITICAL": [],
        "HIGH": [],
        "MEDIUM": [],
        "LOW": [],
    }

    if not permissions:
        return {
            "verdict": "LOW_CONCERN",
            "summary": "No permissions declared in application manifest.",
            "risk_score": 0.0,
            "threat_profile": threat_profile,
            "total_permissions": 0,
            "caveat": STATIC_ANALYSIS_CAVEAT,
        }

    # Normalize and deduplicate permissions while preserving declaration order
    seen_permissions: set[str] = set()
    normalized_permissions: list[str] = []

    for raw_p in permissions:
        if raw_p is None:
            continue
        p_str = str(raw_p).strip()
        if not p_str:
            continue
        if p_str not in seen_permissions:
            seen_permissions.add(p_str)
            normalized_permissions.append(p_str)

    # Classify each unique permission
    score = 0.0
    for perm in normalized_permissions:
        category, explanation = classify_permission(perm)
        short_name = extract_permission_short_name(perm)

        entry = {
            "permission": perm,
            "short_name": short_name,
            "threat_explanation": explanation,
        }
        threat_profile[category].append(entry)

        # Weight calculation
        if category == "CRITICAL":
            score += 2.5
        elif category == "HIGH":
            score += 1.5
        elif category == "MEDIUM":
            score += 0.5
        elif category == "LOW":
            score += 0.0

    risk_score = min(10.0, round(score, 2))

    # Verdict hierarchy
    crit_count = len(threat_profile["CRITICAL"])
    high_count = len(threat_profile["HIGH"])
    med_count = len(threat_profile["MEDIUM"])
    low_count = len(threat_profile["LOW"])
    total_perms = len(normalized_permissions)

    if crit_count > 0:
        verdict = "DANGEROUS"
        summary = (
            f"High-risk alert: Application requests {crit_count} CRITICAL permission(s) "
            f"associated with direct financial fraud and credential theft."
        )
    elif high_count > 0:
        verdict = "SUSPICIOUS"
        summary = (
            f"Elevated risk: Application requests {high_count} HIGH threat permission(s) "
            f"enabling device surveillance and data exfiltration."
        )
    elif med_count > 0:
        verdict = "MODERATE"
        summary = (
            f"Moderate risk: Application requests {med_count} MEDIUM threat permission(s) "
            f"with potential for background abuse or data transmission."
        )
    else:
        verdict = "LOW_CONCERN"
        summary = (
            f"Low risk: Application requests {low_count} standard low-risk permission(s) "
            f"with no direct banking attack vectors detected."
        )

    return {
        "verdict": verdict,
        "summary": summary,
        "risk_score": risk_score,
        "threat_profile": threat_profile,
        "total_permissions": total_perms,
        "caveat": STATIC_ANALYSIS_CAVEAT,
    }


def scan_apk(file_path: str) -> dict[str, Any]:
    """Execute complete APK static security inspection pipeline.

    Chains APK manifest parsing with threat vector profiling. In accordance with
    defensive engineering principles, errors during APK parsing propagate as
    an explicit ERROR verdict rather than defaulting to safe statuses.

    Args:
        file_path: Path to the target APK file.

    Returns:
        Unified dictionary combining package metadata and threat assessment.
    """
    analysis = analyze_apk(file_path)

    if analysis.get("status") == "ERROR":
        return {
            "status": "ERROR",
            "package_name": analysis.get("package_name"),
            "app_name": analysis.get("app_name"),
            "version_code": analysis.get("version_code"),
            "version_name": analysis.get("version_name"),
            "permissions": [],
            "error": analysis.get("error", "Unknown error during APK analysis"),
            "verdict": "ERROR",
            "summary": f"Security scan failed: {analysis.get('error')}",
            "risk_score": None,
            "threat_profile": {
                "CRITICAL": [],
                "HIGH": [],
                "MEDIUM": [],
                "LOW": [],
            },
            "total_permissions": 0,
            "caveat": STATIC_ANALYSIS_CAVEAT,
        }

    threat_profile = generate_threat_profile(analysis.get("permissions", []))

    # Combine analysis metadata and threat profile
    return {
        **analysis,
        **threat_profile,
    }


def demo_analysis() -> dict[str, Any]:
    """Generate a realistic mock analysis for demonstration and offline testing.

    Simulates the scan of a malicious banking overlay trojan disguised as a
    rewards application ('com.fake.cashback.rewards'). The fake application
    requests critical OTP interception and overlay permissions.

    This ensures interactive demos (e.g., Streamlit UI) can showcase threat
    breakdowns, radar scores, and mitigations even without sample APKs uploaded.

    Returns:
        Dict adhering to the scan_apk return structure with high-threat indicators.
    """
    demo_permissions = [
        "android.permission.READ_SMS",
        "android.permission.RECEIVE_SMS",
        "android.permission.SYSTEM_ALERT_WINDOW",
        "android.permission.CAMERA",
        "android.permission.INTERNET",
        "android.permission.ACCESS_FINE_LOCATION",
    ]

    threat_info = generate_threat_profile(demo_permissions)

    return {
        "status": "SUCCESS",
        "package_name": "com.fake.cashback.rewards",
        "app_name": "SuperCashback Rewards",
        "version_code": "104",
        "version_name": "1.4.2",
        "permissions": demo_permissions,
        "error": None,
        **threat_info,
    }
