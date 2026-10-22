"""Tests for the QuantumShield APK Security Scanner module.

Ensures that permission mapping, threat scoring, verdict assignment, and error
handling follow fail-safe principles without requiring external dependencies
(such as Androguard) to be installed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to sys.path to allow direct imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.apk_scanner import (
    PERMISSION_THREAT_MAP,
    STATIC_ANALYSIS_CAVEAT,
    analyze_apk,
    classify_permission,
    demo_analysis,
    extract_permission_short_name,
    generate_threat_profile,
    scan_apk,
)


def test_threat_profile_critical() -> None:
    """Permissions containing CRITICAL items must result in a DANGEROUS verdict."""
    perms = [
        "android.permission.READ_SMS",
        "android.permission.INTERNET",
    ]
    result = generate_threat_profile(perms)

    assert result["verdict"] == "DANGEROUS"
    # READ_SMS (2.5) + INTERNET (0.5) = 3.0
    assert result["risk_score"] == 3.0
    assert len(result["threat_profile"]["CRITICAL"]) == 1
    assert result["threat_profile"]["CRITICAL"][0]["short_name"] == "READ_SMS"
    assert (
        result["threat_profile"]["CRITICAL"][0]["threat_explanation"]
        == "Can intercept OTP codes sent by banks"
    )
    assert len(result["threat_profile"]["MEDIUM"]) == 1
    assert result["total_permissions"] == 2
    assert "CRITICAL" in result["summary"]


def test_threat_profile_high_only() -> None:
    """Permissions with only HIGH items must result in a SUSPICIOUS verdict."""
    perms = [
        "android.permission.CAMERA",
        "android.permission.ACCESS_FINE_LOCATION",
    ]
    result = generate_threat_profile(perms)

    assert result["verdict"] == "SUSPICIOUS"
    # CAMERA (1.5) + ACCESS_FINE_LOCATION (1.5) = 3.0
    assert result["risk_score"] == 3.0
    assert len(result["threat_profile"]["CRITICAL"]) == 0
    assert len(result["threat_profile"]["HIGH"]) == 2
    assert result["total_permissions"] == 2
    assert "HIGH" in result["summary"]


def test_threat_profile_low_only() -> None:
    """Permissions with only standard/unmapped items must result in LOW_CONCERN."""
    perms = [
        "android.permission.VIBRATE",
        "android.permission.SET_WALLPAPER",
    ]
    result = generate_threat_profile(perms)

    assert result["verdict"] == "LOW_CONCERN"
    assert result["risk_score"] == 0.0
    assert len(result["threat_profile"]["CRITICAL"]) == 0
    assert len(result["threat_profile"]["HIGH"]) == 0
    assert len(result["threat_profile"]["MEDIUM"]) == 0
    assert len(result["threat_profile"]["LOW"]) == 2
    assert result["total_permissions"] == 2


def test_threat_profile_empty() -> None:
    """Empty or None permissions list must yield LOW_CONCERN with zero score."""
    result_empty = generate_threat_profile([])
    assert result_empty["verdict"] == "LOW_CONCERN"
    assert result_empty["risk_score"] == 0.0
    assert result_empty["total_permissions"] == 0
    assert result_empty["threat_profile"]["CRITICAL"] == []
    assert result_empty["threat_profile"]["HIGH"] == []
    assert result_empty["threat_profile"]["MEDIUM"] == []
    assert result_empty["threat_profile"]["LOW"] == []

    result_none = generate_threat_profile(None)
    assert result_none["verdict"] == "LOW_CONCERN"
    assert result_none["risk_score"] == 0.0
    assert result_none["total_permissions"] == 0


def test_threat_profile_risk_score_cap() -> None:
    """Multiple CRITICAL and HIGH permissions must cap the risk score at 10.0."""
    perms = [
        "READ_SMS",  # 2.5
        "RECEIVE_SMS",  # 2.5
        "SEND_SMS",  # 2.5
        "SYSTEM_ALERT_WINDOW",  # 2.5
        "BIND_ACCESSIBILITY_SERVICE",  # 2.5 (Subtotal = 12.5)
        "CAMERA",  # 1.5
    ]
    result = generate_threat_profile(perms)

    assert result["verdict"] == "DANGEROUS"
    # Uncapped score would be 14.0, but must cap at exactly 10.0
    assert result["risk_score"] == 10.0
    assert len(result["threat_profile"]["CRITICAL"]) == 5
    assert len(result["threat_profile"]["HIGH"]) == 1


def test_analyze_apk_missing_file() -> None:
    """Non-existent APK file must return status='ERROR' and never crash."""
    non_existent = "/Users/akhil/non_existent_app_bundle_12345.apk"
    result = analyze_apk(non_existent)

    assert isinstance(result, dict)
    assert result["status"] == "ERROR"
    assert result["package_name"] is None
    assert result["permissions"] == []
    assert "File does not exist" in result["error"]


def test_analyze_apk_wrong_extension() -> None:
    """File without .apk extension must return status='ERROR' with validation message."""
    wrong_file = "sample_document.txt"
    result = analyze_apk(wrong_file)

    assert isinstance(result, dict)
    assert result["status"] == "ERROR"
    assert result["package_name"] is None
    assert result["permissions"] == []
    assert "Validation error" in result["error"]
    assert ".apk" in result["error"]


def test_demo_analysis_returns_valid() -> None:
    """demo_analysis must return a populated mock result with expected threat profile."""
    result = demo_analysis()

    assert isinstance(result, dict)
    assert result["status"] == "SUCCESS"
    assert result["package_name"] == "com.fake.cashback.rewards"
    assert result["app_name"] == "SuperCashback Rewards"
    assert result["version_code"] == "104"
    assert result["version_name"] == "1.4.2"
    assert result["verdict"] == "DANGEROUS"
    assert result["risk_score"] == 10.0
    assert result["total_permissions"] == 6
    assert result["error"] is None

    # Check key expected permissions
    critical_names = [e["short_name"] for e in result["threat_profile"]["CRITICAL"]]
    assert "READ_SMS" in critical_names
    assert "RECEIVE_SMS" in critical_names
    assert "SYSTEM_ALERT_WINDOW" in critical_names

    high_names = [e["short_name"] for e in result["threat_profile"]["HIGH"]]
    assert "CAMERA" in high_names
    assert "ACCESS_FINE_LOCATION" in high_names

    med_names = [e["short_name"] for e in result["threat_profile"]["MEDIUM"]]
    assert "INTERNET" in med_names

    assert result["caveat"] == STATIC_ANALYSIS_CAVEAT


def test_permission_short_name_extraction() -> None:
    """'android.permission.READ_SMS' must extract as 'READ_SMS' and classify as CRITICAL."""
    # Test short name extraction
    full_name = "android.permission.READ_SMS"
    short_name = extract_permission_short_name(full_name)
    assert short_name == "READ_SMS"

    # Test classification
    category, explanation = classify_permission(full_name)
    assert category == "CRITICAL"
    assert explanation == PERMISSION_THREAT_MAP["CRITICAL"]["READ_SMS"]

    # Test in threat profile context
    profile = generate_threat_profile([full_name])
    assert profile["verdict"] == "DANGEROUS"
    assert len(profile["threat_profile"]["CRITICAL"]) == 1
    assert profile["threat_profile"]["CRITICAL"][0]["permission"] == full_name
    assert profile["threat_profile"]["CRITICAL"][0]["short_name"] == "READ_SMS"


def test_threat_profile_moderate_only() -> None:
    """Permissions with only MEDIUM items must result in MODERATE verdict."""
    perms = [
        "android.permission.INTERNET",  # 0.5
        "android.permission.WAKE_LOCK",  # 0.5
    ]
    result = generate_threat_profile(perms)

    assert result["verdict"] == "MODERATE"
    assert result["risk_score"] == 1.0
    assert len(result["threat_profile"]["MEDIUM"]) == 2
    assert len(result["threat_profile"]["CRITICAL"]) == 0
    assert len(result["threat_profile"]["HIGH"]) == 0


def test_scan_apk_wrapper_error_propagation() -> None:
    """scan_apk must propagate errors as fail-safe ERROR status."""
    result = scan_apk("missing_target.apk")

    assert result["status"] == "ERROR"
    assert result["verdict"] == "ERROR"
    assert result["risk_score"] is None
    assert result["total_permissions"] == 0
    assert "failed" in result["summary"].lower()


def test_threat_profile_deduplication() -> None:
    """Duplicate permissions in input list must not inflate risk score."""
    perms = [
        "android.permission.READ_SMS",
        "android.permission.READ_SMS",
        "android.permission.INTERNET",
    ]
    result = generate_threat_profile(perms)

    # 1 unique CRITICAL (2.5) + 1 unique MEDIUM (0.5) = 3.0
    assert result["total_permissions"] == 2
    assert result["risk_score"] == 3.0
    assert len(result["threat_profile"]["CRITICAL"]) == 1


def test_permission_threat_map_integrity() -> None:
    """Verify that PERMISSION_THREAT_MAP contains all required threat categories and entries."""
    required_critical = {
        "READ_SMS",
        "RECEIVE_SMS",
        "SEND_SMS",
        "SYSTEM_ALERT_WINDOW",
        "BIND_ACCESSIBILITY_SERVICE",
        "READ_PHONE_STATE",
    }
    required_high = {
        "ACCESS_FINE_LOCATION",
        "CAMERA",
        "RECORD_AUDIO",
        "READ_CONTACTS",
        "READ_CALL_LOG",
        "GET_ACCOUNTS",
    }
    required_medium = {
        "INTERNET",
        "READ_EXTERNAL_STORAGE",
        "WRITE_EXTERNAL_STORAGE",
        "INSTALL_PACKAGES",
        "WAKE_LOCK",
    }

    assert required_critical.issubset(set(PERMISSION_THREAT_MAP["CRITICAL"].keys()))
    assert required_high.issubset(set(PERMISSION_THREAT_MAP["HIGH"].keys()))
    assert required_medium.issubset(set(PERMISSION_THREAT_MAP["MEDIUM"].keys()))


def test_analyze_apk_missing_androguard() -> None:
    """When Androguard is not installed and an existing .apk is passed, raise informative ImportError."""
    import tempfile
    import src.apk_scanner as scanner

    with tempfile.NamedTemporaryFile(suffix=".apk") as f:
        if not scanner.ANDROGUARD_AVAILABLE:
            try:
                scanner.analyze_apk(f.name)
                assert False, "Expected ImportError when Androguard is not installed"
            except ImportError as err:
                assert "androguard" in str(err).lower()
                assert "pip install" in str(err).lower()


# Direct test runner support for execution without pytest installed
if __name__ == "__main__":
    import inspect

    current_module = sys.modules[__name__]
    test_functions = [
        obj
        for name, obj in inspect.getmembers(current_module, inspect.isfunction)
        if name.startswith("test_")
    ]

    print(f"Running {len(test_functions)} APK scanner tests...\n")
    passed = 0
    failed = 0

    for test_fn in test_functions:
        test_name = test_fn.__name__
        try:
            test_fn()
            print(f"  [PASS] {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {test_name}: {type(e).__name__}: {e}")
            failed += 1

    print(f"\nTest Summary: {passed} passed, {failed} failed.")
    if failed > 0:
        sys.exit(1)
    else:
        print("All APK scanner tests passed successfully!")
