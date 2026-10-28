"""
Tests for visual_components library.
"""
import pytest
from src.visual_components import (
    render_threat_dial_gauge,
    render_3d_threat_sphere,
    render_pqc_pipeline_diagram,
    render_quantum_circuit_schematic,
)


def test_threat_dial_gauge_normal():
    svg = render_threat_dial_gauge(score=9.2, level="CRITICAL", action="BLOCK")
    assert "<svg" in svg
    assert "9.2" in svg
    assert "SEVERE RISK" in svg
    assert "</svg>" in svg


def test_threat_dial_gauge_boundary_clamping():
    svg_low = render_threat_dial_gauge(score=-5.0)
    assert "0.0" in svg_low
    assert "SECURE" in svg_low

    svg_high = render_threat_dial_gauge(score=15.0)
    assert "10.0" in svg_high
    assert "SEVERE RISK" in svg_high


def test_3d_threat_sphere_structure():
    html = render_3d_threat_sphere(height=300)
    assert "three.min.js" in html
    assert "THREE.Scene" in html
    assert "QUANTUM RADAR" in html
    assert "ML-KEM-768" in html


def test_pqc_pipeline_diagram():
    svg = render_pqc_pipeline_diagram()
    assert "ML-KEM-768" in svg
    assert "1,184 Bytes" in svg
    assert "1,088 Bytes" in svg
    assert "AES-256-GCM" in svg


def test_quantum_circuit_schematic():
    svg = render_quantum_circuit_schematic(base=7, composite_n=15)
    assert "SHOR ORDER-FINDING (N=15, a=7)" in svg
    assert "QFT †" in svg
    assert "|q₀⟩" in svg
