"""QuantumShield Transaction Risk Engine.

This module provides a multi-factor risk assessment system for financial transactions
on mobile devices. It combines temporal heuristics (time-of-day), behavioural metrics
(velocity tracking / burst detection), value thresholds, and external threat signals
into a quantified risk scoring model.

Key Components:
    - Time-of-day risk factor evaluation (elevated risk during overnight hours: 12 AM - 5 AM)
    - Transaction velocity tracker (burst attack / carding attack detection via sliding deque)
    - Multi-factor risk scoring engine (`assess_transaction_risk`)
    - Legacy backward-compatible checker (`simple_risk_check`)

Design Principles:
    - Fail-Safe Security: Malformed or unparseable inputs fail conservatively (safe/cautious outputs).
    - Defense-in-Depth: Multi-layered point accumulation ensures balanced sensitivity.
    - Zero External Dependencies: Built purely on standard library primitives for maximum portability.
"""

from collections import deque
from datetime import datetime, time
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Constants for Risk Thresholds and Level Categorization
DEFAULT_HIGH_VALUE_THRESHOLD: float = 10_000.0
HIGH_RISK_POINT_THRESHOLD: int = 4
MEDIUM_RISK_POINT_THRESHOLD: int = 2

# Operational Risk Action Directives
ACTION_INVALID: str = "REJECT: Invalid transaction amount. Transaction amounts must be strictly greater than zero."
ACTION_HIGH: str = "BLOCK: High risk detected. Transaction held for manual security review and quantum-safe biometric step-up verification."
ACTION_MEDIUM: str = "CHALLENGE: Medium risk detected. Transaction requires quantum-resistant second-factor authentication (PQC OTP) before approval."
ACTION_LOW: str = "APPROVE: Low risk detected. Transaction cleared for immediate automated processing."


def _time_risk_factor(timestamp: Optional[Union[datetime, time]] = None) -> str:
    """Assess whether a transaction timestamp falls within elevated risk hours (12 AM - 5 AM).

    Educational Context:
        In financial cybersecurity and mobile fraud analytics, the "graveyard hours"
        (midnight to 05:00 local time) exhibit a disproportionately high incidence of
        unauthorized account takeovers, SIM-swap exploitations, and automated malware drains.
        During this window, legitimate account holders are typically asleep and unable to
        respond to instant SMS/push notifications or challenge authentication prompts.
        Therefore, transactions executed in this window are assigned elevated risk points.

    Time Window Definition:
        12:00:00 AM (00:00) through 04:59:59 (04:59), i.e., 0 <= hour < 5.
        Hour 5 (05:00:00 AM) marks the start of normal early-morning banking hours.

    Args:
        timestamp: The datetime or time of the transaction. If None, the current
                   local datetime is evaluated.

    Returns:
        'ELEVATED' if the transaction falls between 12 AM and 5 AM (00:00 - 04:59:59),
        'NORMAL' otherwise.
    """
    try:
        if timestamp is None:
            dt = datetime.now()
            hour = dt.hour
        elif isinstance(timestamp, datetime):
            hour = timestamp.hour
        elif isinstance(timestamp, time):
            hour = timestamp.hour
        else:
            # Fail-safe principle: if an unrecognized timestamp object is passed,
            # we log a warning and return ELEVATED to prevent false-safe evasion.
            logger.warning(
                "Unrecognized timestamp type %s; applying fail-safe ELEVATED risk",
                type(timestamp).__name__,
            )
            return "ELEVATED"

        # Check if the hour falls in the [00:00, 05:00) range (midnight through 4:59:59 AM)
        if 0 <= hour < 5:
            return "ELEVATED"
        return "NORMAL"

    except Exception as err:
        # Conservative fail-safe: never crash, flag suspicious anomaly
        logger.error("Error evaluating time-of-day risk: %s; failing safe to ELEVATED", err)
        return "ELEVATED"


class TransactionVelocityTracker:
    """Sliding-window transaction velocity tracker for burst attack detection.

    Educational Context:
        Automated fraud campaigns (such as credential stuffing, automated bots, and
        card testing / carding attacks) characteristically execute transactions in
        rapid succession to drain funds before bank fraud detection triggers a killswitch.
        Human financial behaviour is inherently rate-limited by cognitive and physical interaction
        speed. An unexpected cluster of transactions within a short timeframe strongly
        indicates script-driven or malware-automated execution.

    Mechanism:
        Uses a double-ended queue (`collections.deque`) to store timestamps of recent transactions.
        On every evaluation, timestamps older than `(current_time - window_seconds)` are evicted
        from the left end in O(k) amortized time, maintaining a lean rolling window. If the remaining
        count exceeds `max_count`, a velocity breach is flagged.

    Attributes:
        max_count: Maximum permissible transactions within the rolling window before triggering a breach.
        window_seconds: Duration of the rolling observation window in seconds.
    """

    def __init__(self, max_count: int = 3, window_seconds: float = 60.0) -> None:
        """Initialize the velocity tracker with configurable burst limits.

        Args:
            max_count: The maximum allowed transaction count within the sliding window (default: 3).
                       A breach occurs when count exceeds this limit.
            window_seconds: The duration of the sliding window in seconds (default: 60.0).
        """
        if max_count < 0:
            raise ValueError(f"max_count must be non-negative, got {max_count}")
        if window_seconds <= 0:
            raise ValueError(f"window_seconds must be positive, got {window_seconds}")

        self.max_count: int = int(max_count)
        self.window_seconds: float = float(window_seconds)
        self._timestamps: deque[float] = deque()

    @staticmethod
    def _normalize_timestamp(ts: Optional[Union[datetime, float, int]]) -> float:
        """Convert a datetime or numeric epoch into uniform Unix epoch seconds (float).

        Args:
            ts: Optional timestamp (datetime, int, float, or None).

        Returns:
            Epoch timestamp as a float.
        """
        if ts is None:
            return datetime.now().timestamp()
        if isinstance(ts, datetime):
            return ts.timestamp()
        if isinstance(ts, (int, float)):
            return float(ts)
        raise TypeError(
            f"Unsupported timestamp type {type(ts).__name__}; expected datetime, int, or float."
        )

    def record_and_check(self, timestamp: Optional[Union[datetime, float, int]] = None) -> bool:
        """Record a transaction timestamp and evaluate whether the velocity threshold is breached.

        Args:
            timestamp: The transaction timestamp to record. If None, current time is used.

        Returns:
            True if the velocity threshold is breached (transaction count in window > max_count),
            False otherwise.
        """
        try:
            ts_sec = self._normalize_timestamp(timestamp)
        except Exception as err:
            logger.error("Failed to parse timestamp in velocity tracker: %s; failing safe to True", err)
            # Fail-safe principle: unparseable timestamp during a rate check treated as breach
            return True

        cutoff = ts_sec - self.window_seconds

        # Prune expired transactions outside the rolling window
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

        # Handle potentially out-of-order timestamps gracefully
        if self._timestamps and ts_sec < self._timestamps[-1]:
            # Insertion out-of-order: re-sort deque to preserve monotonicity
            self._timestamps.append(ts_sec)
            sorted_ts = sorted(self._timestamps)
            self._timestamps = deque(sorted_ts)
            # Re-prune in case older timestamps shifted to front
            while self._timestamps and self._timestamps[0] < cutoff:
                self._timestamps.popleft()
        else:
            self._timestamps.append(ts_sec)

        # Breach condition: count in the current window exceeds max allowed count
        return len(self._timestamps) > self.max_count

    def reset(self) -> None:
        """Clear all recorded timestamps, resetting the velocity tracker to initial state."""
        self._timestamps.clear()

    @property
    def current_count(self) -> int:
        """Return the number of transactions currently tracked in the active window."""
        return len(self._timestamps)

    def get_history(self) -> List[float]:
        """Return a snapshot list of active epoch timestamps currently in the window."""
        return list(self._timestamps)


def assess_transaction_risk(
    amount: float,
    suspicious_flag: bool = False,
    timestamp: Optional[datetime] = None,
    velocity_breach: bool = False,
    threshold: float = DEFAULT_HIGH_VALUE_THRESHOLD,
) -> Dict[str, Any]:
    """Perform a multi-factor risk assessment on a financial transaction.

    Educational Context:
        Single-factor fraud heuristics (such as only looking at amount) suffer from high
        false-positive and false-negative rates. QuantumShield applies a defense-in-depth,
        multi-factor scoring model that aggregates orthogonal risk vectors:
        1. Threat intelligence / security signals (suspicious_flag: +3 pts)
        2. High-value exposure (amount >= threshold: +2 pts)
        3. Burst velocity anomalies (velocity_breach: +2 pts)
        4. Temporal risk heuristics (12 AM - 5 AM: +1 pt)

    Scoring System:
        - `amount <= 0`: Immediately categorized as INVALID (0 points, transaction rejected).
        - `suspicious_flag`: +3 points (indicates anomalous device, known bad actor, or compromised state).
        - `amount >= threshold`: +2 points (large capital movement increases potential impact).
        - `velocity_breach`: +2 points (burst attack pattern detected by velocity tracker).
        - `time is ELEVATED`: +1 point (overnight transaction during vulnerable sleeper hours).

    Risk Level Mapping:
        - points >= 4: HIGH (Immediate block, manual review, and PQC biometric step-up)
        - points >= 2: MEDIUM (Step-up PQC authentication required)
        - else (0 or 1): LOW (Approved for standard execution)

    Args:
        amount: Transaction amount in currency units. Must be strictly positive.
        suspicious_flag: External security flag indicating suspicious account/device activity.
        timestamp: Transaction timestamp. If None, current datetime is used.
        velocity_breach: Boolean indicating whether velocity rate limits were breached.
        threshold: High-value transaction threshold amount (default: 10,000.0).

    Returns:
        A dictionary containing:
            - `risk_level`: 'INVALID', 'HIGH', 'MEDIUM', or 'LOW'
            - `risk_points`: Total accumulated risk points (int)
            - `factors`: List of human-readable factor explanations (List[str])
            - `recommended_action`: Action directive string tailored to the risk level (str)
            - `amount`: Numeric transaction amount (float)
            - `timestamp_used`: The datetime object used for the assessment (datetime)
    """
    # Establish canonical timestamp
    if timestamp is None:
        timestamp_used: datetime = datetime.now()
    elif isinstance(timestamp, datetime):
        timestamp_used = timestamp
    else:
        # Fallback if non-datetime passed
        try:
            timestamp_used = datetime.now()
        except Exception:
            timestamp_used = datetime.now()

    # Fail-safe validation of amount: non-numeric or non-positive amounts are strictly INVALID
    try:
        numeric_amount = float(amount)
    except (TypeError, ValueError):
        return {
            "risk_level": "INVALID",
            "risk_points": 0,
            "factors": [f"Invalid amount value: {amount!r}. Amount must be a valid positive number."],
            "recommended_action": ACTION_INVALID,
            "amount": amount,
            "timestamp_used": timestamp_used,
        }

    # Amount <= 0 is immediately INVALID per specification
    if numeric_amount <= 0:
        return {
            "risk_level": "INVALID",
            "risk_points": 0,
            "factors": [
                f"Transaction amount must be strictly greater than zero (received ${numeric_amount:,.2f})."
            ],
            "recommended_action": ACTION_INVALID,
            "amount": numeric_amount,
            "timestamp_used": timestamp_used,
        }

    # Multi-factor point accumulation
    points: int = 0
    factors: List[str] = []

    # 1. Suspicious Account / Device Threat Flag (+3 points)
    if bool(suspicious_flag):
        points += 3
        factors.append(
            "Suspicious activity flag detected: anomalous device or account threat signal (+3 points)"
        )

    # 2. High-Value Amount Threshold (+2 points)
    try:
        numeric_threshold = float(threshold)
    except (TypeError, ValueError):
        numeric_threshold = DEFAULT_HIGH_VALUE_THRESHOLD

    if numeric_amount >= numeric_threshold:
        points += 2
        factors.append(
            f"Transaction amount (${numeric_amount:,.2f}) meets or exceeds high-value threshold (${numeric_threshold:,.2f}) (+2 points)"
        )

    # 3. Velocity Breach / Burst Detection (+2 points)
    if bool(velocity_breach):
        points += 2
        factors.append(
            "Transaction velocity breach detected: rapid successive transactions exceed allowable limits (+2 points)"
        )

    # 4. Time-of-Day Risk Factor (+1 point)
    time_status = _time_risk_factor(timestamp_used)
    if time_status == "ELEVATED":
        points += 1
        formatted_time = timestamp_used.strftime("%I:%M %p")
        factors.append(
            f"Transaction occurred during elevated risk overnight hours (12 AM - 5 AM): {formatted_time} (+1 point)"
        )

    # Risk level mapping and recommendation assignment
    if points >= HIGH_RISK_POINT_THRESHOLD:
        risk_level = "HIGH"
        recommended_action = ACTION_HIGH
    elif points >= MEDIUM_RISK_POINT_THRESHOLD:
        risk_level = "MEDIUM"
        recommended_action = ACTION_MEDIUM
    else:
        risk_level = "LOW"
        recommended_action = ACTION_LOW

    return {
        "risk_level": risk_level,
        "risk_points": points,
        "factors": factors,
        "recommended_action": recommended_action,
        "amount": numeric_amount,
        "timestamp_used": timestamp_used,
    }


def simple_risk_check(amount: float, suspicious_flag: bool = False) -> str:
    """Evaluate transaction risk level using legacy heuristic rules.

    Maintained for backward compatibility with early QuantumShield integrations
    that require a simple, fast string result based purely on amount and threat flag.

    Legacy Rules:
        - `amount <= 0`: 'INVALID'
        - `suspicious_flag == True`: 'HIGH'
        - `amount >= 10,000.0`: 'MEDIUM'
        - otherwise: 'LOW'

    Args:
        amount: Transaction amount.
        suspicious_flag: Boolean flag indicating suspicious threat activity.

    Returns:
        One of the risk level strings: 'INVALID', 'HIGH', 'MEDIUM', or 'LOW'.
    """
    try:
        numeric_amount = float(amount)
    except (TypeError, ValueError):
        return "INVALID"

    if numeric_amount <= 0:
        return "INVALID"
    if suspicious_flag:
        return "HIGH"
    if numeric_amount >= DEFAULT_HIGH_VALUE_THRESHOLD:
        return "MEDIUM"
    return "LOW"
