"""Comprehensive test suite for QuantumShield Transaction Risk Engine.

Tests the multi-factor risk assessment logic, sliding-window velocity tracker,
time-of-day heuristic factors, and legacy backward-compatible checker.

All tests operate on real application logic without mocking to guarantee
end-to-end correctness of the security risk engine.
"""

from datetime import datetime, time, timedelta
import inspect
from pathlib import Path
import sys

# Ensure src/ and root are in sys.path for direct execution and pytest discovery
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from transaction_risk import (  # noqa: E402
    DEFAULT_HIGH_VALUE_THRESHOLD,
    TransactionVelocityTracker,
    _time_risk_factor,
    assess_transaction_risk,
    simple_risk_check,
)


# ============================================================================
# 1. Low Risk Assessment
# ============================================================================
def test_low_risk() -> None:
    """Test 1: Normal small transaction amount with no risk flags results in LOW risk."""
    daytime = datetime(2026, 10, 21, 14, 30)  # 2:30 PM (normal daytime)
    result = assess_transaction_risk(
        amount=50.0,
        suspicious_flag=False,
        timestamp=daytime,
        velocity_breach=False,
        threshold=10_000.0,
    )

    assert result["risk_level"] == "LOW"
    assert result["risk_points"] == 0
    assert result["factors"] == []
    assert "APPROVE" in result["recommended_action"]
    assert result["amount"] == 50.0
    assert result["timestamp_used"] == daytime


# ============================================================================
# 2. Medium Risk Assessment
# ============================================================================
def test_medium_risk() -> None:
    """Test 2: Amount >= threshold ($10,000) with no other flags results in MEDIUM risk (2 points)."""
    daytime = datetime(2026, 10, 21, 15, 0)  # 3:00 PM
    result = assess_transaction_risk(
        amount=10_000.0,
        suspicious_flag=False,
        timestamp=daytime,
        velocity_breach=False,
        threshold=10_000.0,
    )

    assert result["risk_level"] == "MEDIUM"
    assert result["risk_points"] == 2
    assert len(result["factors"]) == 1
    assert "10,000.00" in result["factors"][0]
    assert "CHALLENGE" in result["recommended_action"]


# ============================================================================
# 3. High Risk with Suspicious Flag
# ============================================================================
def test_high_risk_suspicious() -> None:
    """Test 3: Suspicious flag set (+3 points) combined with secondary risk factors triggers HIGH risk."""
    # Scenario A: Suspicious flag (+3) + elevated night-time hour (+1) = 4 points -> HIGH
    night_time = datetime(2026, 10, 21, 2, 30)  # 2:30 AM
    result_night = assess_transaction_risk(
        amount=250.0,
        suspicious_flag=True,
        timestamp=night_time,
        velocity_breach=False,
    )

    assert result_night["risk_level"] == "HIGH"
    assert result_night["risk_points"] == 4
    assert any("suspicious" in f.lower() for f in result_night["factors"])
    assert any("12 am - 5 am" in f.lower() for f in result_night["factors"])
    assert "BLOCK" in result_night["recommended_action"]

    # Scenario B: Suspicious flag (+3) + high-value threshold (+2) = 5 points -> HIGH
    daytime = datetime(2026, 10, 21, 11, 0)
    result_large = assess_transaction_risk(
        amount=15_000.0,
        suspicious_flag=True,
        timestamp=daytime,
        velocity_breach=False,
    )
    assert result_large["risk_level"] == "HIGH"
    assert result_large["risk_points"] == 5

    # Scenario C: Suspicious flag (+3) + velocity breach (+2) = 5 points -> HIGH
    result_velocity = assess_transaction_risk(
        amount=100.0,
        suspicious_flag=True,
        timestamp=daytime,
        velocity_breach=True,
    )
    assert result_velocity["risk_level"] == "HIGH"
    assert result_velocity["risk_points"] == 5

    # Scenario D: In legacy simple check, suspicious_flag alone directly returns HIGH
    assert simple_risk_check(100.0, suspicious_flag=True) == "HIGH"


# ============================================================================
# 4. Invalid Zero Amount
# ============================================================================
def test_invalid_zero() -> None:
    """Test 4: Zero transaction amount (amount = 0) returns INVALID immediately."""
    result = assess_transaction_risk(amount=0.0)

    assert result["risk_level"] == "INVALID"
    assert result["risk_points"] == 0
    assert len(result["factors"]) == 1
    assert "strictly greater than zero" in result["factors"][0]
    assert "REJECT" in result["recommended_action"]
    assert result["amount"] == 0.0

    # Also verify legacy simple check returns INVALID
    assert simple_risk_check(0.0) == "INVALID"


# ============================================================================
# 5. Invalid Negative Amount
# ============================================================================
def test_invalid_negative() -> None:
    """Test 5: Negative transaction amount (amount = -100) returns INVALID immediately."""
    result = assess_transaction_risk(amount=-100.0)

    assert result["risk_level"] == "INVALID"
    assert result["risk_points"] == 0
    assert len(result["factors"]) == 1
    assert "strictly greater than zero" in result["factors"][0]
    assert "REJECT" in result["recommended_action"]
    assert result["amount"] == -100.0

    # Also verify legacy simple check returns INVALID
    assert simple_risk_check(-100.0) == "INVALID"


# ============================================================================
# 6. Night-Time Elevated Risk Factor
# ============================================================================
def test_night_time_elevated() -> None:
    """Test 6: Transaction at 2 AM triggers ELEVATED time-of-day risk factor (+1 point)."""
    night_time = datetime(2026, 10, 21, 2, 0)  # 2:00 AM

    # Direct time risk factor evaluation
    assert _time_risk_factor(night_time) == "ELEVATED"

    # Multi-factor assessment evaluation
    result = assess_transaction_risk(
        amount=150.0,
        suspicious_flag=False,
        timestamp=night_time,
        velocity_breach=False,
    )

    assert result["risk_points"] == 1
    assert result["risk_level"] == "LOW"  # 1 point is LOW (not blocked without corroborating signals)
    assert len(result["factors"]) == 1
    assert "02:00 AM" in result["factors"][0]
    assert "12 AM - 5 AM" in result["factors"][0]


# ============================================================================
# 7. Daytime Normal Risk Factor
# ============================================================================
def test_daytime_normal() -> None:
    """Test 7: Transaction at 2 PM falls within NORMAL hours (0 time risk points)."""
    daytime = datetime(2026, 10, 21, 14, 0)  # 2:00 PM (14:00)

    # Direct time risk factor evaluation
    assert _time_risk_factor(daytime) == "NORMAL"

    # Multi-factor assessment evaluation
    result = assess_transaction_risk(
        amount=150.0,
        suspicious_flag=False,
        timestamp=daytime,
        velocity_breach=False,
    )

    assert result["risk_points"] == 0
    assert result["risk_level"] == "LOW"
    assert result["factors"] == []


# ============================================================================
# 8. Velocity Breach (Rapid Burst Transactions)
# ============================================================================
def test_velocity_breach() -> None:
    """Test 8: Rapid transactions within sliding window trigger velocity breach."""
    tracker = TransactionVelocityTracker(max_count=3, window_seconds=60.0)
    base_time = datetime(2026, 10, 21, 12, 0, 0)

    # 1st transaction at t=0s -> 1 in window <= 3 -> False
    assert not tracker.record_and_check(base_time + timedelta(seconds=0))
    # 2nd transaction at t=10s -> 2 in window <= 3 -> False
    assert not tracker.record_and_check(base_time + timedelta(seconds=10))
    # 3rd transaction at t=20s -> 3 in window <= 3 -> False (threshold limit)
    assert not tracker.record_and_check(base_time + timedelta(seconds=20))
    # 4th transaction at t=25s -> 4 in window > 3 -> True (BREACH!)
    breached = tracker.record_and_check(base_time + timedelta(seconds=25))
    assert breached is True
    assert tracker.current_count == 4

    # Now assess risk with velocity breach flag
    risk_result = assess_transaction_risk(
        amount=200.0,
        suspicious_flag=False,
        timestamp=base_time,
        velocity_breach=breached,
    )
    assert risk_result["risk_points"] == 2
    assert risk_result["risk_level"] == "MEDIUM"
    assert any("velocity" in f.lower() for f in risk_result["factors"])


# ============================================================================
# 9. Velocity No Breach (Transactions Spread Apart)
# ============================================================================
def test_velocity_no_breach() -> None:
    """Test 9: Transactions spaced further than window_seconds do not trigger a breach."""
    tracker = TransactionVelocityTracker(max_count=3, window_seconds=60.0)
    base_time = datetime(2026, 10, 21, 12, 0, 0)

    # Transactions spaced 70 seconds apart (window is 60 seconds)
    t1 = base_time + timedelta(seconds=0)
    t2 = base_time + timedelta(seconds=70)
    t3 = base_time + timedelta(seconds=140)
    t4 = base_time + timedelta(seconds=210)

    assert not tracker.record_and_check(t1)
    assert not tracker.record_and_check(t2)
    assert not tracker.record_and_check(t3)
    assert not tracker.record_and_check(t4)
    # Only 1 transaction currently in active window
    assert tracker.current_count == 1


# ============================================================================
# 10. Combined Multiple Factors to High Risk
# ============================================================================
def test_combined_high_risk() -> None:
    """Test 10: Multiple orthogonal risk factors combining to score >= 4 points (HIGH risk)."""
    # Scenario 1: High value (+2) + Velocity breach (+2) = 4 points -> HIGH
    daytime = datetime(2026, 10, 21, 13, 0)
    res1 = assess_transaction_risk(
        amount=12_000.0,
        suspicious_flag=False,
        timestamp=daytime,
        velocity_breach=True,
    )
    assert res1["risk_points"] == 4
    assert res1["risk_level"] == "HIGH"
    assert len(res1["factors"]) == 2

    # Scenario 2: High value (+2) + Velocity breach (+2) + Night time (+1) = 5 points -> HIGH
    night_time = datetime(2026, 10, 21, 3, 15)  # 3:15 AM
    res2 = assess_transaction_risk(
        amount=25_000.0,
        suspicious_flag=False,
        timestamp=night_time,
        velocity_breach=True,
    )
    assert res2["risk_points"] == 5
    assert res2["risk_level"] == "HIGH"
    assert len(res2["factors"]) == 3

    # Scenario 3: All 4 factors present: Suspicious (+3) + Amount (+2) + Velocity (+2) + Time (+1) = 8 points -> HIGH
    res3 = assess_transaction_risk(
        amount=50_000.0,
        suspicious_flag=True,
        timestamp=night_time,
        velocity_breach=True,
    )
    assert res3["risk_points"] == 8
    assert res3["risk_level"] == "HIGH"
    assert len(res3["factors"]) == 4
    assert "BLOCK" in res3["recommended_action"]


# ============================================================================
# 11. Custom High-Value Threshold
# ============================================================================
def test_custom_threshold() -> None:
    """Test 11: Custom threshold value alters point assessment appropriately."""
    daytime = datetime(2026, 10, 21, 12, 0)
    custom_threshold = 5_000.0

    # Amount $6,000 is BELOW the default $10,000 threshold (0 points)
    res_default = assess_transaction_risk(
        amount=6_000.0,
        timestamp=daytime,
        threshold=DEFAULT_HIGH_VALUE_THRESHOLD,
    )
    assert res_default["risk_points"] == 0
    assert res_default["risk_level"] == "LOW"

    # Amount $6,000 meets or EXCEEDS custom $5,000 threshold (+2 points)
    res_custom = assess_transaction_risk(
        amount=6_000.0,
        timestamp=daytime,
        threshold=custom_threshold,
    )
    assert res_custom["risk_points"] == 2
    assert res_custom["risk_level"] == "MEDIUM"
    assert any("5,000.00" in f for f in res_custom["factors"])


# ============================================================================
# 12. Simple Risk Check Backward Compatibility
# ============================================================================
def test_simple_risk_check_backward_compat() -> None:
    """Test 12: Verify full backward compatibility of simple_risk_check with legacy callers."""
    # Invalid amounts
    assert simple_risk_check(0) == "INVALID"
    assert simple_risk_check(0.0) == "INVALID"
    assert simple_risk_check(-10.5) == "INVALID"

    # Suspicious flag -> HIGH
    assert simple_risk_check(100.0, suspicious_flag=True) == "HIGH"
    assert simple_risk_check(50_000.0, suspicious_flag=True) == "HIGH"

    # High amount without suspicious flag -> MEDIUM
    assert simple_risk_check(10_000.0, suspicious_flag=False) == "MEDIUM"
    assert simple_risk_check(15_000.0, suspicious_flag=False) == "MEDIUM"

    # Normal amount without flags -> LOW
    assert simple_risk_check(9_999.99, suspicious_flag=False) == "LOW"
    assert simple_risk_check(50.0, suspicious_flag=False) == "LOW"
    assert simple_risk_check(1.0) == "LOW"


# ============================================================================
# Additional Comprehensive Tests (Edge Cases & Invariants)
# ============================================================================
def test_velocity_tracker_reset() -> None:
    """Test that reset() clears all history and allows fresh tracking."""
    tracker = TransactionVelocityTracker(max_count=2, window_seconds=30.0)
    now = datetime(2026, 10, 21, 10, 0, 0)

    tracker.record_and_check(now)
    tracker.record_and_check(now + timedelta(seconds=5))
    # 3rd is a breach
    assert tracker.record_and_check(now + timedelta(seconds=10)) is True
    assert tracker.current_count == 3

    # Reset
    tracker.reset()
    assert tracker.current_count == 0
    assert tracker.get_history() == []

    # First transaction after reset should not breach
    assert not tracker.record_and_check(now + timedelta(seconds=15))
    assert tracker.current_count == 1


def test_time_risk_factor_boundaries() -> None:
    """Test exact boundary hours for time-of-day risk factor (00:00, 04:59, 05:00, 23:59)."""
    # Midnight 00:00:00 -> ELEVATED
    assert _time_risk_factor(time(0, 0, 0)) == "ELEVATED"
    assert _time_risk_factor(datetime(2026, 10, 21, 0, 0, 0)) == "ELEVATED"

    # 04:59:59 AM -> ELEVATED
    assert _time_risk_factor(time(4, 59, 59)) == "ELEVATED"

    # 05:00:00 AM -> NORMAL (banking hours begin)
    assert _time_risk_factor(time(5, 0, 0)) == "NORMAL"
    assert _time_risk_factor(datetime(2026, 10, 21, 5, 0, 0)) == "NORMAL"

    # 12:00:00 PM (Noon) -> NORMAL
    assert _time_risk_factor(time(12, 0, 0)) == "NORMAL"

    # 23:59:59 PM (Late night before midnight) -> NORMAL
    assert _time_risk_factor(time(23, 59, 59)) == "NORMAL"


def test_invalid_amount_types_fail_safe() -> None:
    """Test fail-safe handling of unparseable amount types."""
    res_str = assess_transaction_risk(amount="invalid_number")  # type: ignore[arg-type]
    assert res_str["risk_level"] == "INVALID"
    assert res_str["risk_points"] == 0
    assert "REJECT" in res_str["recommended_action"]

    res_none = assess_transaction_risk(amount=None)  # type: ignore[arg-type]
    assert res_none["risk_level"] == "INVALID"

    assert simple_risk_check("invalid") == "INVALID"  # type: ignore[arg-type]


def test_recommended_actions_distinct() -> None:
    """Ensure recommended actions for each risk level are unique and actionable."""
    dt = datetime(2026, 10, 21, 12, 0)
    low_res = assess_transaction_risk(amount=50.0, timestamp=dt)
    med_res = assess_transaction_risk(amount=10_000.0, timestamp=dt)
    high_res = assess_transaction_risk(amount=10_000.0, suspicious_flag=True, timestamp=dt)
    inv_res = assess_transaction_risk(amount=0.0, timestamp=dt)

    actions = {
        low_res["recommended_action"],
        med_res["recommended_action"],
        high_res["recommended_action"],
        inv_res["recommended_action"],
    }
    # All 4 risk levels must produce distinct recommended actions
    assert len(actions) == 4


# ============================================================================
# Embedded Test Runner (permits running directly via python without pytest CLI)
# ============================================================================
if __name__ == "__main__":
    current_module = sys.modules[__name__]
    all_test_functions = [
        obj
        for name, obj in inspect.getmembers(current_module)
        if inspect.isfunction(obj) and name.startswith("test_")
    ]

    print("=== QuantumShield Transaction Risk Engine Test Suite ===")
    print(f"Discovered {len(all_test_functions)} test cases.\n")

    passed_count = 0
    failed_count = 0

    for test_fn in all_test_functions:
        try:
            test_fn()
            print(f"  [PASS] {test_fn.__name__}")
            passed_count += 1
        except AssertionError as exc:
            print(f"  [FAIL] {test_fn.__name__}: Assertion failed: {exc}")
            failed_count += 1
        except Exception as exc:
            print(f"  [FAIL] {test_fn.__name__}: Unexpected error: {exc}")
            failed_count += 1

    print("\n-------------------------------------------------------")
    print(f"Summary: {passed_count} passed, {failed_count} failed out of {len(all_test_functions)} tests.")
    print("-------------------------------------------------------")

    if failed_count > 0:
        sys.exit(1)
    else:
        print("ALL TESTS PASSED SUCCESSFULLY.")
        sys.exit(0)
