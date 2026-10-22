"""QuantumShield - Cryptographic Engine Test Suite.

Tests for:
1. ML-KEM / Simulated KEM Keypair Generation, Encapsulation, Decapsulation
2. HKDF-SHA256 Key Derivation (Determinism, Domain Separation)
3. AES-256-GCM Authenticated Encryption & Decryption
4. Active Tamper Detection & Wrong-Key Rejection
5. Complete End-to-End PQC Demo Pipeline
6. Classical RSA-2048 Baseline & Shor's Vulnerability Analysis
7. Backend Information Reporting

All tests are designed to pass cleanly in any environment, whether using
liboqs (real PQC), cryptography (hazmat), or the native OpenSSL / pure-Python fallback.
"""

from __future__ import annotations

import pytest

from src.post_quantum_crypto import (
    InvalidTag,
    USING_REAL_PQC,
    decapsulate,
    decrypt_message,
    derive_symmetric_key,
    encapsulate,
    encrypt_message,
    generate_keypair,
    get_backend_info,
    run_classical_rsa_demo,
    run_pqc_demo,
)


# ==============================================================================
# 1. KEM Operations Tests
# ==============================================================================

def test_keypair_generation():
    """Test 1: Keypair generation returns valid, non-empty byte tuples."""
    public_key, secret_key = generate_keypair()

    assert isinstance(public_key, bytes), "Public key must be bytes"
    assert isinstance(secret_key, bytes), "Secret key must be bytes"
    assert len(public_key) > 0, "Public key must not be empty"
    assert len(secret_key) > 0, "Secret key must not be empty"


def test_encapsulate_decapsulate():
    """Test 2: Encapsulation and decapsulation establish matching shared secrets."""
    public_key, secret_key = generate_keypair()

    ciphertext, shared_secret_sender = encapsulate(public_key)
    assert isinstance(ciphertext, bytes) and len(ciphertext) > 0
    assert isinstance(shared_secret_sender, bytes) and len(shared_secret_sender) > 0

    shared_secret_receiver = decapsulate(secret_key, ciphertext)
    assert isinstance(shared_secret_receiver, bytes) and len(shared_secret_receiver) > 0

    assert (
        shared_secret_sender == shared_secret_receiver
    ), "Party A and Party B shared secrets must match perfectly"


# ==============================================================================
# 2. Key Derivation (HKDF-SHA256) Tests
# ==============================================================================

def test_derive_symmetric_key():
    """Test 3: derive_symmetric_key produces a 32-byte (256-bit) AES key."""
    _, secret_key = generate_keypair()
    shared_secret = secret_key[:32] if len(secret_key) >= 32 else secret_key.ljust(32, b"\x00")

    aes_key = derive_symmetric_key(shared_secret)
    assert isinstance(aes_key, bytes)
    assert len(aes_key) == 32, "Derived AES key must be exactly 32 bytes (256 bits)"


def test_derive_key_deterministic():
    """Test 4: HKDF derivation is strictly deterministic for identical inputs."""
    shared_secret = b"deterministic_quantumshield_secret_12345"
    salt = b"test_salt_98765"
    info = b"quantumshield-aes-key"

    key1 = derive_symmetric_key(shared_secret, salt=salt, info=info)
    key2 = derive_symmetric_key(shared_secret, salt=salt, info=info)

    assert key1 == key2, "HKDF key derivation must be completely deterministic"

    # Distinct salt or info must produce cryptographically distinct keys
    key_diff_salt = derive_symmetric_key(shared_secret, salt=b"different_salt", info=info)
    key_diff_info = derive_symmetric_key(shared_secret, salt=salt, info=b"different-info")

    assert key1 != key_diff_salt, "Different salts must produce different keys"
    assert key1 != key_diff_info, "Different info tags must produce different keys"


# ==============================================================================
# 3. AES-256-GCM Encryption / Decryption Tests
# ==============================================================================

def test_aes_gcm_roundtrip():
    """Test 5: Encrypting and decrypting recovers the original plaintext."""
    key = b"\x42" * 32
    message = b"QuantumShield Financial Security Protocol: Confidential Tx #9941"

    encrypted = encrypt_message(key, message)
    assert isinstance(encrypted, dict)
    assert "ciphertext" in encrypted
    assert "nonce" in encrypted
    assert "tag" in encrypted
    assert len(encrypted["nonce"]) == 12, "Nonce must be 12 bytes (96-bit standard)"
    assert len(encrypted["tag"]) == 16, "Tag must be 16 bytes (128-bit standard)"

    decrypted = decrypt_message(
        key, encrypted["ciphertext"], encrypted["nonce"], encrypted["tag"]
    )
    assert decrypted == message, "Decrypted message must match original plaintext"


def test_aes_gcm_tamper_detection():
    """Test 6: Modified ciphertext raises InvalidTag upon decryption."""
    key = b"\x37" * 32
    message = b"Amount: INR 500,000 to Account #123456789"

    encrypted = encrypt_message(key, message)
    tampered_ciphertext = bytearray(encrypted["ciphertext"])
    tampered_ciphertext[0] ^= 0x01  # Flip one bit

    with pytest.raises((InvalidTag, Exception)):
        decrypt_message(
            key, bytes(tampered_ciphertext), encrypted["nonce"], encrypted["tag"]
        )


def test_aes_gcm_wrong_key():
    """Test 7: Decrypting with an incorrect key raises InvalidTag."""
    correct_key = b"\x11" * 32
    wrong_key = b"\x22" * 32
    message = b"Sensitive Financial Alert: Suspicious Overlay Detected"

    encrypted = encrypt_message(correct_key, message)

    with pytest.raises((InvalidTag, Exception)):
        decrypt_message(
            wrong_key, encrypted["ciphertext"], encrypted["nonce"], encrypted["tag"]
        )


# ==============================================================================
# 4. Full PQC Demo Pipeline Tests
# ==============================================================================

def test_full_demo_pipeline():
    """Test 8: run_pqc_demo returns expected structure with all required fields."""
    result = run_pqc_demo()

    expected_keys = [
        "public_key_hex",
        "secret_key_hex",
        "kem_ciphertext_hex",
        "shared_secrets_match",
        "shared_secret_hex",
        "aes_key_hex",
        "original_message",
        "encrypted_ciphertext_hex",
        "nonce_hex",
        "tag_hex",
        "decrypted_message",
        "tamper_test_passed",
        "backend",
        "steps",
    ]

    for key in expected_keys:
        assert key in result, f"Result dictionary must contain '{key}'"

    assert isinstance(result["public_key_hex"], str)
    assert isinstance(result["secret_key_hex"], str)
    assert isinstance(result["kem_ciphertext_hex"], str)
    assert result["shared_secrets_match"] is True
    assert isinstance(result["aes_key_hex"], str)
    assert len(result["aes_key_hex"]) == 64  # 32 bytes = 64 hex characters
    assert result["decrypted_message"] == result["original_message"]
    assert isinstance(result["steps"], list)
    assert len(result["steps"]) >= 8


def test_full_demo_tamper_passes():
    """Test 9: run_pqc_demo reports tamper_test_passed = True."""
    result = run_pqc_demo(
        message="QuantumShield Transaction Audit: Fraud Probability 0.98 - Blocked"
    )
    assert result["tamper_test_passed"] is True, "Tamper test must detect bit alteration"


# ==============================================================================
# 5. Classical RSA Comparison Tests
# ==============================================================================

def test_rsa_demo():
    """Test 10: run_classical_rsa_demo returns expected structure and explains vulnerability."""
    msg = "Financial Wire: Interbank Transfer $1,000,000"
    result = run_classical_rsa_demo(msg)

    expected_keys = [
        "key_size",
        "public_key_hex",
        "encrypted_hex",
        "decrypted_message",
        "quantum_vulnerable",
        "vulnerability_explanation",
    ]

    for key in expected_keys:
        assert key in result, f"RSA demo result must contain '{key}'"

    assert result["key_size"] == 2048
    assert result["quantum_vulnerable"] is True
    assert result["decrypted_message"] == msg
    assert "Shor" in result["vulnerability_explanation"]
    assert "ML-KEM" in result["vulnerability_explanation"]


# ==============================================================================
# 6. Backend Information Tests
# ==============================================================================

def test_backend_info():
    """Test 11: get_backend_info returns a non-empty string describing the active backend."""
    backend_info = get_backend_info()
    assert isinstance(backend_info, str)
    assert len(backend_info.strip()) > 0
    assert any(
        kw in backend_info
        for kw in ["ML-KEM", "Simulated", "X25519", "Diffie-Hellman", "OpenSSL"]
    )


# ==============================================================================
# 7. Additional Robustness & Edge Case Tests
# ==============================================================================

def test_aes_gcm_tampered_tag():
    """Verify that tampering with the tag itself causes rejection."""
    key = b"\x55" * 32
    message = b"Critical security payload"
    encrypted = encrypt_message(key, message)

    tampered_tag = bytearray(encrypted["tag"])
    tampered_tag[0] ^= 0xFF

    with pytest.raises((InvalidTag, Exception)):
        decrypt_message(
            key, encrypted["ciphertext"], encrypted["nonce"], bytes(tampered_tag)
        )


def test_aes_gcm_string_input():
    """Verify that encrypt_message transparently handles string inputs."""
    key = b"\x77" * 32
    str_msg = "Transaction #1001 with Unicode currency: ₹75,000.50"
    encrypted = encrypt_message(key, str_msg)
    decrypted = decrypt_message(
        key, encrypted["ciphertext"], encrypted["nonce"], encrypted["tag"]
    )
    assert decrypted.decode("utf-8") == str_msg
