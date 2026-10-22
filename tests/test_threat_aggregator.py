"""
Tests for the QuantumShield Threat Aggregator.

Tests the unified scoring pipeline that combines APK and transaction
risk assessments into a single threat score.
"""

import pytest
from src.threat_aggregator import (
    compute_combined_threat_score,
    generate_threat_narrative,
    _compute_apk_score,
    _compute_txn_score,
)


# ─────────────────────── APK Score Computation ────────────────────────


class TestAPKScoreComputation:
    """Tests for the internal APK risk score calculation."""

    def test_none_apk_result(self):
        """No APK result should contribute 0 risk."""
        assert _compute_apk_score(None) == 0.0

    def test_precomputed_risk_score(self):
        """If the scanner already computed a risk_score, use it."""
        result = {"risk_score": 7.5}
        assert _compute_apk_score(result) == 7.5

    def test_risk_score_capped_at_10(self):
        """Risk score should never exceed 10."""
        result = {"risk_score": 15.0}
        assert _compute_apk_score(result) == 10.0

    def test_manual_scoring_critical(self):
        """CRITICAL permissions should each contribute 2.5 points."""
        result = {
            "threat_profile": {
                "CRITICAL": [
                    {"permission": "READ_SMS"},
                    {"permission": "RECEIVE_SMS"},
                ],
                "HIGH": [],
                "MEDIUM": [],
                "LOW": [],
            }
        }
        assert _compute_apk_score(result) == 5.0  # 2 × 2.5

    def test_manual_scoring_mixed(self):
        """Mixed permission categories should sum correctly."""
        result = {
            "threat_profile": {
                "CRITICAL": [{"permission": "READ_SMS"}],       # 2.5
                "HIGH": [{"permission": "CAMERA"}],              # 1.5
                "MEDIUM": [{"permission": "INTERNET"}],          # 0.5
                "LOW": [{"permission": "VIBRATE"}],              # 0.0
            }
        }
        assert _compute_apk_score(result) == 4.5  # 2.5 + 1.5 + 0.5


# ─────────────────────── Transaction Score Computation ────────────────


class TestTxnScoreComputation:
    """Tests for the internal transaction risk score calculation."""

    def test_none_txn_result(self):
        """No transaction result should contribute 0 risk."""
        assert _compute_txn_score(None) == 0.0

    def test_risk_points_scaling(self):
        """risk_points should be scaled to 0-10 (max 8 → 10)."""
        result = {"risk_points": 4}
        assert _compute_txn_score(result) == 5.0  # 4 × (10/8) = 5.0

    def test_risk_points_max(self):
        """Maximum risk_points (8) should map to 10."""
        result = {"risk_points": 8}
        assert _compute_txn_score(result) == 10.0

    def test_simple_level_mapping_low(self):
        """Simple LOW risk level should map to 2.0."""
        result = {"risk_level": "LOW"}
        assert _compute_txn_score(result) == 2.0

    def test_simple_level_mapping_high(self):
        """Simple HIGH risk level should map to 8.0."""
        result = {"risk_level": "HIGH"}
        assert _compute_txn_score(result) == 8.0

    def test_simple_level_mapping_invalid(self):
        """INVALID should map to maximum risk (10.0)."""
        result = {"risk_level": "INVALID"}
        assert _compute_txn_score(result) == 10.0


# ─────────────────────── Combined Threat Score ────────────────────────


class TestCombinedThreatScore:
    """Tests for the main combined scoring function."""

    def test_both_none(self):
        """No inputs should produce minimal risk."""
        result = compute_combined_threat_score(None, None)
        assert result["combined_threat_score"] == 0.0
        assert result["recommended_action"] == "ALLOW"
        assert result["risk_level"] == "LOW"

    def test_high_apk_low_txn(self):
        """High APK risk with low transaction risk."""
        apk = {"risk_score": 8.0}
        txn = {"risk_level": "LOW"}
        result = compute_combined_threat_score(apk, txn)
        # 0.4 × 8.0 + 0.6 × 2.0 = 3.2 + 1.2 = 4.4
        assert result["combined_threat_score"] == 4.4
        assert result["risk_level"] == "MEDIUM"

    def test_low_apk_high_txn(self):
        """Low APK risk with high transaction risk."""
        apk = {"risk_score": 2.0}
        txn = {"risk_level": "HIGH"}
        result = compute_combined_threat_score(apk, txn)
        # 0.4 × 2.0 + 0.6 × 8.0 = 0.8 + 4.8 = 5.6
        assert result["combined_threat_score"] == 5.6
        assert result["risk_level"] == "HIGH"

    def test_both_critical(self):
        """Both modules flagging critical should produce maximum severity."""
        apk = {"risk_score": 10.0}
        txn = {"risk_level": "INVALID"}
        result = compute_combined_threat_score(apk, txn)
        # 0.4 × 10.0 + 0.6 × 10.0 = 10.0
        assert result["combined_threat_score"] == 10.0
        assert result["recommended_action"] == "BLOCK_AND_ALERT"
        assert result["risk_level"] == "CRITICAL"

    def test_output_structure(self):
        """Output should contain all required keys."""
        result = compute_combined_threat_score(None, None)
        required_keys = {
            "apk_risk_score",
            "transaction_risk_score",
            "combined_threat_score",
            "recommended_action",
            "risk_level",
            "explanation",
            "factors",
            "timestamp",
        }
        assert required_keys.issubset(result.keys())

    def test_explanation_contains_scores(self):
        """Explanation should mention the component scores."""
        apk = {"risk_score": 5.0}
        txn = {"risk_level": "MEDIUM"}
        result = compute_combined_threat_score(apk, txn)
        explanation = result["explanation"]
        assert "5.0" in explanation
        assert "Device" in explanation or "APK" in explanation

    def test_factors_include_apk_dangerous(self):
        """Factors should mention DANGEROUS APK verdict."""
        apk = {
            "verdict": "DANGEROUS",
            "risk_score": 9.0,
            "threat_profile": {
                "CRITICAL": [{"permission": "READ_SMS"}],
                "HIGH": [],
                "MEDIUM": [],
                "LOW": [],
            },
        }
        result = compute_combined_threat_score(apk, None)
        factors_text = " ".join(result["factors"])
        assert "DANGEROUS" in factors_text
        assert "READ_SMS" in factors_text

    def test_factors_include_txn_details(self):
        """Transaction factors should be passed through to combined output."""
        txn = {
            "risk_level": "HIGH",
            "risk_points": 5,
            "factors": ["Suspicious activity flag is set", "High-value transaction"],
        }
        result = compute_combined_threat_score(None, txn)
        assert "Suspicious activity flag is set" in result["factors"]
        assert "High-value transaction" in result["factors"]


# ─────────────────────── Threat Narrative ─────────────────────────────


class TestThreatNarrative:
    """Tests for the narrative generation used by the Streamlit dashboard."""

    def test_empty_narrative(self):
        """No inputs should still produce a 4-step narrative."""
        steps = generate_threat_narrative()
        assert len(steps) == 4
        assert steps[0]["layer"] == "Device"
        assert steps[1]["layer"] == "Transaction"
        assert steps[2]["layer"] == "Transport"
        assert steps[3]["layer"] == "Quantum Threat"

    def test_dangerous_apk_narrative(self):
        """DANGEROUS APK should produce danger status in step 1."""
        apk = {
            "verdict": "DANGEROUS",
            "risk_score": 9.0,
            "threat_profile": {"CRITICAL": [{"permission": "READ_SMS"}]},
        }
        steps = generate_threat_narrative(apk_result=apk)
        assert steps[0]["status"] == "danger"
        assert steps[0]["icon"] == "🔴"

    def test_high_txn_narrative(self):
        """HIGH risk transaction should produce danger status in step 2."""
        txn = {
            "risk_level": "HIGH",
            "factors": ["Suspicious flag"],
            "recommended_action": "Block transaction.",
        }
        steps = generate_threat_narrative(txn_result=txn)
        assert steps[1]["status"] == "danger"

    def test_narrative_step_structure(self):
        """Each narrative step should have the required keys."""
        steps = generate_threat_narrative()
        required_keys = {"step", "layer", "title", "description", "status", "icon"}
        for step in steps:
            assert required_keys.issubset(step.keys())

    def test_transport_always_safe(self):
        """Transport layer (PQC) should always show as available/safe."""
        steps = generate_threat_narrative()
        assert steps[2]["status"] == "safe"
        assert "ML-KEM" in steps[2]["description"]
