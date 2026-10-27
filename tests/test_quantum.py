"""
Tests for the QuantumShield Quantum Computing Demo Module
==========================================================
Verifies Shor's algorithm simulation, fallback handling, period finding,
classical factor extraction, scaling context metrics, and educational explanations.

All tests are designed to execute and pass reliably even when Qiskit is not
installed in the runtime environment.
"""

import pytest

from src.quantum_demo import (
    QISKIT_AVAILABLE,
    build_shor_circuit,
    get_qiskit_status,
    get_scaling_context,
    get_shor_explanation,
    run_shor_simulation,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Shor's Simulation Structure & Results
# ─────────────────────────────────────────────────────────────────────────────


def test_run_shor_simulation_structure():
    """Verify run_shor_simulation returns a dictionary with all expected keys."""
    res = run_shor_simulation(N=15, a=7, shots=2048)
    assert isinstance(res, dict)

    expected_keys = {
        "n_value",
        "base_a",
        "n_qubits",
        "n_counting_qubits",
        "shots",
        "measurement_counts",
        "period_found",
        "factors_found",
        "factoring_successful",
        "circuit_depth",
        "using_real_qiskit",
        "explanation",
    }
    assert expected_keys.issubset(res.keys())
    assert res["n_value"] == 15
    assert res["base_a"] == 7
    assert res["n_qubits"] == 8
    assert res["n_counting_qubits"] == 4
    assert res["shots"] == 2048
    assert isinstance(res["circuit_depth"], int)
    assert res["circuit_depth"] > 0
    assert isinstance(res["using_real_qiskit"], bool)


def test_factors_found():
    """Verify that factors_found contains the correct prime factors 3 and 5."""
    res = run_shor_simulation(N=15, a=7, shots=2048)
    factors = res["factors_found"]
    assert isinstance(factors, list)
    assert 3 in factors
    assert 5 in factors
    # Product of factors should equal N
    assert factors[0] * factors[1] == 15


def test_factoring_successful():
    """Verify factoring_successful flag is True."""
    res = run_shor_simulation(N=15, a=7, shots=2048)
    assert res["factoring_successful"] is True


def test_measurement_counts_exist():
    """Verify measurement_counts is a non-empty dictionary of bitstrings."""
    res = run_shor_simulation(N=15, a=7, shots=2048)
    counts = res["measurement_counts"]
    assert isinstance(counts, dict)
    assert len(counts) > 0

    # Ensure all counts are positive integers and keys are binary strings
    for bitstring, count in counts.items():
        assert isinstance(bitstring, str)
        assert set(bitstring).issubset({"0", "1"})
        assert isinstance(count, int)
        assert count > 0

    # Check that counts sum to the total shots
    assert sum(counts.values()) == 2048


def test_period_found_is_correct():
    """Verify that period r=4 is correctly extracted for a=7 mod 15."""
    res = run_shor_simulation(N=15, a=7, shots=2048)
    assert res["period_found"] == 4
    # Verify mathematically: 7^4 mod 15 == 1
    assert pow(7, res["period_found"], 15) == 1


# ─────────────────────────────────────────────────────────────────────────────
# 2. Scaling Context Metrics
# ─────────────────────────────────────────────────────────────────────────────


def test_scaling_context_structure():
    """Verify get_scaling_context returns dictionary with expected keys and types."""
    context = get_scaling_context()
    assert isinstance(context, dict)

    required_keys = {
        "scaling_table",
        "current_state",
        "hndl_explanation",
        "timeline_estimate",
        "why_pqc_now",
    }
    assert required_keys.issubset(context.keys())
    assert isinstance(context["scaling_table"], list)
    assert isinstance(context["current_state"], dict)
    assert isinstance(context["hndl_explanation"], str)
    assert isinstance(context["timeline_estimate"], str)
    assert isinstance(context["why_pqc_now"], str)


def test_scaling_table_entries():
    """Verify scaling table includes entries from N=15 through RSA-2048."""
    context = get_scaling_context()
    table = context["scaling_table"]

    targets = [entry["target"] for entry in table]
    assert any("15" in t for t in targets), "Missing N=15 entry"
    assert any("21" in t for t in targets), "Missing N=21 entry"
    assert any("512" in t for t in targets), "Missing RSA-512 entry"
    assert any("1024" in t for t in targets), "Missing RSA-1024 entry"
    assert any("2048" in t for t in targets), "Missing RSA-2048 entry"

    # Verify each row contains the expected keys
    row_keys = {"target", "bits", "logical_qubits", "physical_qubits_est", "status"}
    for row in table:
        assert row_keys.issubset(row.keys())
        assert isinstance(row["bits"], int)
        assert isinstance(row["status"], str)


def test_scaling_current_state():
    """Verify current_state dictionary has hardware frontier data."""
    context = get_scaling_context()
    state = context["current_state"]
    assert "largest_quantum_computer" in state
    assert "qubit_count" in state
    assert "year" in state
    assert isinstance(state["qubit_count"], int)
    assert state["qubit_count"] >= 1000
    assert isinstance(state["year"], int)


def test_hndl_explanation_exists():
    """Verify HNDL explanation is a non-empty, detailed string."""
    context = get_scaling_context()
    hndl = context["hndl_explanation"]
    assert isinstance(hndl, str)
    assert len(hndl) > 100
    assert "Harvest Now" in hndl or "HNDL" in hndl
    assert "Decrypt" in hndl


# ─────────────────────────────────────────────────────────────────────────────
# 3. Educational Narratives & Status Checks
# ─────────────────────────────────────────────────────────────────────────────


def test_shor_explanation():
    """Verify get_shor_explanation returns comprehensive educational text."""
    explanation = get_shor_explanation()
    assert isinstance(explanation, str)
    assert len(explanation) > 500

    # Ensure key conceptual pillars are covered
    assert "Shor" in explanation
    assert "RSA" in explanation
    assert "ECC" in explanation or "Elliptic Curve" in explanation
    assert "HNDL" in explanation or "Harvest Now" in explanation
    assert "ML-KEM" in explanation
    assert "FIPS 203" in explanation


def test_qiskit_status():
    """Verify get_qiskit_status returns a string with status information."""
    status = get_qiskit_status()
    assert isinstance(status, str)
    assert len(status) > 0
    if QISKIT_AVAILABLE:
        assert "Qiskit" in status
    else:
        assert "not installed" in status or "fallback" in status


def test_build_shor_circuit_fallback_behavior():
    """Verify build_shor_circuit gracefully returns None when Qiskit is absent."""
    circuit = build_shor_circuit(N=15, a=7)
    if not QISKIT_AVAILABLE:
        assert circuit is None
    else:
        assert circuit is not None
        assert circuit.num_qubits == 8


def test_custom_shots_scaling():
    """Verify that run_shor_simulation scales properly for non-default shot counts."""
    res = run_shor_simulation(N=15, a=7, shots=1000)
    assert res["shots"] == 1000
    assert sum(res["measurement_counts"].values()) == 1000
    assert res["factoring_successful"] is True
    assert res["factors_found"] == [3, 5]


def test_solve_modular_period():
    """Verify solve_modular_period accurately determines period and factors for multiple bases."""
    from src.quantum_demo import solve_modular_period

    # Test base a=7 on N=15 (period r=4)
    res7 = solve_modular_period(N=15, a=7)
    assert res7["period_r"] == 4
    assert res7["factoring_successful"] is True
    assert res7["factors_found"] == [3, 5]

    # Test base a=11 on N=15 (period r=2)
    res11 = solve_modular_period(N=15, a=11)
    assert res11["period_r"] == 2
    assert res11["factoring_successful"] is True
    assert res11["factors_found"] == [3, 5]

    # Test non-coprime base a=3 on N=15 (gcd reveals factor immediately)
    res3 = solve_modular_period(N=15, a=3)
    assert res3["is_coprime"] is False
    assert 3 in res3["factors_found"]


def test_get_transpilation_analysis():
    """Verify IBM Quantum hardware transpilation metrics are populated accurately."""
    from src.quantum_demo import get_transpilation_analysis

    analysis = get_transpilation_analysis("IBM Heron")
    assert "Heron" in analysis["target_qpu"]
    assert "cz" in analysis["native_basis_gates"]
    assert analysis["logical_qubits_required"] == 8
    assert analysis["transpiled_circuit_depth_level3"] == 58
    assert "cz (2-qubit entanglers)" in analysis["gate_counts_transpiled"]
    assert "SamplerV2" in analysis["runtime_sampler_v2_snippet"]



if __name__ == "__main__":
    # Allow running directly via `python tests/test_quantum.py`
    import sys

    print("Running quantum demo tests directly...")
    tests = [
        obj
        for name, obj in list(globals().items())
        if name.startswith("test_") and callable(obj)
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  [PASS] {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {t.__name__}: {e}")
            failed += 1

    print(f"\nResult: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
