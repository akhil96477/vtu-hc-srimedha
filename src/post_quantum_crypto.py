"""QuantumShield - Post-Quantum Cryptography (PQC) & Hybrid Encryption Engine.

This module provides a production-grade cryptographic pipeline combining:
1. Post-Quantum Key Encapsulation Mechanism (ML-KEM / Kyber-768, NIST FIPS 203)
2. Robust Key Derivation via HKDF-SHA256 (RFC 5869)
3. Authenticated Symmetric Encryption with AES-256-GCM (NIST SP 800-38D)
4. Classical RSA-2048 OAEP baseline for side-by-side quantum vulnerability comparison.

Post-Quantum Cryptography Architecture:
- Problem: Classical public-key schemes (RSA, ECC, Diffie-Hellman) rely on integer
  factorization or discrete logarithms, which can be solved in polynomial time by Shor's
  algorithm on a Cryptanalytically Relevant Quantum Computer (CRQC).
- Solution: ML-KEM (Module Learning With Errors, formerly Kyber) relies on the hardness
  of finding short vectors in high-dimensional polynomial lattices. No known quantum
  or classical algorithm solves M-LWE in polynomial time.
- Threat Vector: "Harvest Now, Decrypt Later" (HNDL). Adversaries intercept and store
  encrypted financial communications today, waiting for quantum computers to decrypt them.
  Implementing ML-KEM immediately neutralizes future HNDL exploitation.

Graceful Multi-Tier Architecture:
1. Primary: Real post-quantum ML-KEM-768 via `oqs` (liboqs-python).
2. Fallback Tier 1: Simulated KEM using X25519 ECDH via `cryptography` hazmat.
3. Fallback Tier 2: Simulated KEM + OpenSSL 3 native AES-GCM via standard library `ctypes`.
4. Fallback Tier 3: Pure-Python cryptographic simulation ensuring zero crash on any platform.
"""

from __future__ import annotations

import ctypes
import ctypes.util
from ctypes import byref, c_char_p, c_int, c_size_t, c_void_p, cast, create_string_buffer
import hashlib
import hmac
import os
import secrets
from typing import Any, Optional, Tuple

# ==============================================================================
# Dependency Detection & Backend Selection
# ==============================================================================

# Priority 1: liboqs (real post-quantum ML-KEM / Kyber)
try:
    import oqs  # type: ignore

    _HAVE_OQS = True
except ImportError:
    oqs = None
    _HAVE_OQS = False

# Priority 2: cryptography library
try:
    from cryptography.exceptions import InvalidTag as CryptoInvalidTag
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa, x25519
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF

    _HAVE_CRYPTOGRAPHY = True
except ImportError:
    CryptoInvalidTag = None
    _HAVE_CRYPTOGRAPHY = False


# Authentication Tag Exception
class InvalidTag(Exception):
    """Raised when authenticated decryption fails due to ciphertext tampering or wrong key."""

    pass


# If cryptography is installed, alias or subclass its InvalidTag for uniform exception catching
if CryptoInvalidTag is not None and issubclass(CryptoInvalidTag, Exception):
    _BaseInvalidTag = CryptoInvalidTag
else:
    _BaseInvalidTag = InvalidTag

# Post-Quantum Status Flag
USING_REAL_PQC: bool = _HAVE_OQS


# ==============================================================================
# Native OpenSSL Ctypes Loader (Zero External Dependencies)
# ==============================================================================

def _load_system_libcrypto() -> Optional[ctypes.CDLL]:
    """Attempt to load the native OpenSSL libcrypto shared library.
    
    Searches standard macOS, Homebrew, and Linux locations to enable hardware-accelerated
    AES-256-GCM and EVP functions without needing external Python wheels.
    """
    candidate_paths = [
        ctypes.util.find_library("crypto"),
        "/opt/homebrew/opt/openssl@3/lib/libcrypto.dylib",
        "/opt/homebrew/lib/libcrypto.dylib",
        "/usr/local/opt/openssl@3/lib/libcrypto.dylib",
        "/usr/lib/libcrypto.dylib",
        "libcrypto.so.3",
        "libcrypto.so.1.1",
        "libcrypto.so",
    ]
    for path in candidate_paths:
        if not path:
            continue
        try:
            lib = ctypes.CDLL(path)
            # Verify minimum essential EVP symbol exists
            if hasattr(lib, "EVP_aes_256_gcm"):
                return lib
        except Exception:
            continue
    return None


_SYSTEM_LIBCRYPTO = _load_system_libcrypto()

# Configure ctypes signatures if libcrypto was loaded
if _SYSTEM_LIBCRYPTO is not None:
    try:
        _SYSTEM_LIBCRYPTO.EVP_CIPHER_CTX_new.restype = c_void_p
        _SYSTEM_LIBCRYPTO.EVP_CIPHER_CTX_free.argtypes = [c_void_p]
        _SYSTEM_LIBCRYPTO.EVP_aes_256_gcm.restype = c_void_p

        _SYSTEM_LIBCRYPTO.EVP_EncryptInit_ex.argtypes = [c_void_p, c_void_p, c_void_p, c_char_p, c_char_p]
        _SYSTEM_LIBCRYPTO.EVP_EncryptInit_ex.restype = c_int

        _SYSTEM_LIBCRYPTO.EVP_CIPHER_CTX_ctrl.argtypes = [c_void_p, c_int, c_int, c_void_p]
        _SYSTEM_LIBCRYPTO.EVP_CIPHER_CTX_ctrl.restype = c_int

        _SYSTEM_LIBCRYPTO.EVP_EncryptUpdate.argtypes = [c_void_p, c_void_p, ctypes.POINTER(c_int), c_char_p, c_int]
        _SYSTEM_LIBCRYPTO.EVP_EncryptUpdate.restype = c_int

        _SYSTEM_LIBCRYPTO.EVP_EncryptFinal_ex.argtypes = [c_void_p, c_void_p, ctypes.POINTER(c_int)]
        _SYSTEM_LIBCRYPTO.EVP_EncryptFinal_ex.restype = c_int

        _SYSTEM_LIBCRYPTO.EVP_DecryptInit_ex.argtypes = [c_void_p, c_void_p, c_void_p, c_char_p, c_char_p]
        _SYSTEM_LIBCRYPTO.EVP_DecryptInit_ex.restype = c_int

        _SYSTEM_LIBCRYPTO.EVP_DecryptUpdate.argtypes = [c_void_p, c_void_p, ctypes.POINTER(c_int), c_char_p, c_int]
        _SYSTEM_LIBCRYPTO.EVP_DecryptUpdate.restype = c_int

        _SYSTEM_LIBCRYPTO.EVP_DecryptFinal_ex.argtypes = [c_void_p, c_void_p, ctypes.POINTER(c_int)]
        _SYSTEM_LIBCRYPTO.EVP_DecryptFinal_ex.restype = c_int
    except Exception:
        _SYSTEM_LIBCRYPTO = None


def get_backend_info() -> str:
    """Return a descriptive human-readable string of the active cryptographic backend.
    
    Returns:
        str: Description indicating whether real PQC (liboqs) or a classical simulation
             (cryptography hazmat or native OpenSSL ctypes) is active.
    """
    if USING_REAL_PQC and oqs is not None:
        version = getattr(oqs, "__version__", "unknown")
        return f"Post-Quantum Hardware/C Engine: ML-KEM-768 (liboqs-python v{version}, NIST FIPS 203)"
    elif _HAVE_CRYPTOGRAPHY:
        return "Simulated KEM (ECDH X25519 via cryptography.hazmat — Classical Simulation)"
    elif _SYSTEM_LIBCRYPTO is not None:
        return "Simulated KEM (Diffie-Hellman RFC 3526 MODP + Native OpenSSL 3 AES-256-GCM — Simulation)"
    else:
        return "Simulated KEM (Pure-Python Diffie-Hellman + Authenticated Encryption Simulation)"


# ==============================================================================
# Mathematical Parameters for Fallback Simulated KEM & Classical RSA
# ==============================================================================

# RFC 3526 2048-bit MODP Diffie-Hellman Group (Group 14) prime
_DH2048_P = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
    "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
    "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF",
    16,
)
_DH2048_G = 2

# Standard verified RSA-2048 parameters for classical vulnerability comparison
_RSA_N = int(
    "632d6326e0abe76092b54281f7599c9a02732b0fc6ab35b74805ae0b3587d773cd9385fe53a18af37b57923d"
    "9a925da75a1ced625c95410d6fe12cf6683a67082b074e8b606d6e22b7d1df426f07a4a1d318caf4d8f8bb20"
    "981d7b14f9385b6c630c8722c8d715fea07f2167bfbc5f81f707cf92fce04a279be3bb86c13d4efa130cb4f0"
    "f09ec885aec91b7d8365f656a8c02a51b4436bb92156d227b5345c82797aab5c50576903ae003479515c5c55"
    "db4e7dfc3b351fd0ff81b8a153c81be4fd370bec44382687c9c739687def28d7b8eb5aeeb2df9d3dad7c7dfa"
    "d4295e0cea9cbd704e1c467aa009fd86695bd4e96510ef74af5a6fbae2822c29eaca6e17",
    16,
)
_RSA_E = 65537
_RSA_D = int(
    "208870effddf26051ddaebb82a6570e36c4e4f1fdbb1a9eb376af58ea3beadc444f95188fdf20ddc94e74307"
    "863ee10dd6978a9f2b73a26540000379c8f2ef7d54700f29d535d05cff238f3301ace62a574ed8b4bcbfcad2"
    "8453975e67ea3ec32d329cd9a23c3bf0ccc1273a1b4135ab32579395c9f1e1216117b11a2125755454714b55"
    "a9d1915f9d79c3b88dc3115b9b5705422bd5cb6164c640ae9cefa179a0991b926bf25d68999d221786ba0d8c"
    "8faa021b434b4acd895907e02497ec6b8ae698e01926e97b7607915304fba88b2d525fdf14f1e776908b8bbb"
    "be8773e635fcb81c2a75c442692bde5b282483e9c7ea97e5a19ea082664552ca53a3a321",
    16,
)


# ==============================================================================
# 1. KEM Operations (Key Generation, Encapsulation, Decapsulation)
# ==============================================================================

def generate_keypair() -> Tuple[bytes, bytes]:
    """Generate a KEM keypair.
    
    If liboqs is installed, generates a true NIST FIPS 203 ML-KEM-768 lattice keypair.
    Otherwise, generates an ephemeral public/secret keypair using X25519 or RFC 3526 MODP.
    
    Returns:
        tuple[bytes, bytes]: (public_key, secret_key)
    """
    if USING_REAL_PQC and oqs is not None:
        kem_alg = "ML-KEM-768" if "ML-KEM-768" in oqs.get_enabled_KEM_mechanisms() else "Kyber768"
        with oqs.KeyEncapsulation(kem_alg) as kem:
            public_key = kem.generate_keypair()
            secret_key = kem.export_secret_key()
            return public_key, secret_key

    if _HAVE_CRYPTOGRAPHY:
        # X25519 ECDH KEM simulation
        priv = x25519.X25519PrivateKey.generate()
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.Format.Raw)
        priv_bytes = priv.private_bytes(
            serialization.Encoding.Raw,
            serialization.Format.Raw,
            serialization.NoEncryption(),
        )
        return pub_bytes, priv_bytes

    # Self-contained pure-Python fallback (RFC 3526 MODP-2048)
    priv_int = secrets.randbits(256)
    pub_int = pow(_DH2048_G, priv_int, _DH2048_P)
    return pub_int.to_bytes(256, "big"), priv_int.to_bytes(32, "big")


def encapsulate(public_key: bytes) -> Tuple[bytes, bytes]:
    """Encapsulate a freshly generated symmetric shared secret against a public key.
    
    In a Key Encapsulation Mechanism (KEM):
    - Party A takes Party B's public key.
    - Party A encapsulates: generates a random symmetric shared secret and an encapsulation
      ciphertext that only Party B's secret key can invert.
      
    Args:
        public_key: The recipient's public key bytes.
        
    Returns:
        tuple[bytes, bytes]: (ciphertext, shared_secret)
    """
    if not isinstance(public_key, (bytes, bytearray)):
        raise TypeError("public_key must be bytes")

    if USING_REAL_PQC and oqs is not None:
        kem_alg = "ML-KEM-768" if "ML-KEM-768" in oqs.get_enabled_KEM_mechanisms() else "Kyber768"
        with oqs.KeyEncapsulation(kem_alg) as kem:
            ciphertext, shared_secret = kem.encap_secret(public_key)
            return ciphertext, shared_secret

    if _HAVE_CRYPTOGRAPHY:
        # Ephemeral X25519 key generation
        peer_pub = x25519.X25519PublicKey.from_public_bytes(public_key)
        ephem_priv = x25519.X25519PrivateKey.generate()
        ephem_pub_bytes = ephem_priv.public_key().public_bytes(
            serialization.Encoding.Raw,
            serialization.Format.Raw,
        )
        shared_secret = ephem_priv.exchange(peer_pub)
        return ephem_pub_bytes, shared_secret

    # Self-contained pure-Python fallback
    peer_pub_int = int.from_bytes(public_key, "big")
    ephem_priv_int = secrets.randbits(256)
    ephem_pub_int = pow(_DH2048_G, ephem_priv_int, _DH2048_P)
    raw_secret_int = pow(peer_pub_int, ephem_priv_int, _DH2048_P)
    # Digest raw group element to 32 bytes to mirror standard KEM output
    shared_secret = hashlib.sha256(raw_secret_int.to_bytes(256, "big")).digest()
    ciphertext = ephem_pub_int.to_bytes(256, "big")
    return ciphertext, shared_secret


def decapsulate(secret_key: bytes, ciphertext: bytes) -> bytes:
    """Decapsulate an encapsulation ciphertext using the recipient's secret key.
    
    Party B decapsulates: recovers the exact symmetric shared secret generated by Party A.
    
    Args:
        secret_key: The recipient's secret key bytes.
        ciphertext: The encapsulation ciphertext bytes.
        
    Returns:
        bytes: The recovered shared secret.
    """
    if not isinstance(secret_key, (bytes, bytearray)):
        raise TypeError("secret_key must be bytes")
    if not isinstance(ciphertext, (bytes, bytearray)):
        raise TypeError("ciphertext must be bytes")

    if USING_REAL_PQC and oqs is not None:
        kem_alg = "ML-KEM-768" if "ML-KEM-768" in oqs.get_enabled_KEM_mechanisms() else "Kyber768"
        with oqs.KeyEncapsulation(kem_alg, secret_key=secret_key) as kem:
            shared_secret = kem.decap_secret(ciphertext)
            return shared_secret

    if _HAVE_CRYPTOGRAPHY:
        priv = x25519.X25519PrivateKey.from_private_bytes(secret_key)
        ephem_pub = x25519.X25519PublicKey.from_public_bytes(ciphertext)
        shared_secret = priv.exchange(ephem_pub)
        return shared_secret

    # Self-contained pure-Python fallback
    priv_int = int.from_bytes(secret_key, "big")
    ephem_pub_int = int.from_bytes(ciphertext, "big")
    raw_secret_int = pow(ephem_pub_int, priv_int, _DH2048_P)
    shared_secret = hashlib.sha256(raw_secret_int.to_bytes(256, "big")).digest()
    return shared_secret


# ==============================================================================
# 2. Key Derivation (HKDF-SHA256, RFC 5869)
# ==============================================================================

def derive_symmetric_key(
    shared_secret: bytes,
    salt: Optional[bytes] = None,
    info: bytes = b"quantumshield-aes-key",
) -> bytes:
    """Derive a 256-bit (32-byte) AES key from a shared secret using HKDF-SHA256.
    
    HKDF follows the extract-and-expand paradigm:
    1. Extract: PRK = HMAC-Hash(salt, IKM)
       Extracts pseudo-random randomness from the potentially non-uniform shared secret.
    2. Expand: OKM = HMAC-Hash(PRK, info || 0x01)
       Binds the derived key cryptographically to the specific application protocol context ('info').
       
    Args:
        shared_secret: The raw KEM shared secret bytes.
        salt: Optional cryptographic salt bytes. If None, defaults to 32 null bytes per RFC 5869.
        info: Optional domain separation info tag.
        
    Returns:
        bytes: 32-byte (256-bit) cryptographically strong symmetric key.
    """
    if not isinstance(shared_secret, (bytes, bytearray)):
        raise TypeError("shared_secret must be bytes")
    if not isinstance(info, (bytes, bytearray)):
        raise TypeError("info must be bytes")

    if _HAVE_CRYPTOGRAPHY:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=info,
        )
        return hkdf.derive(bytes(shared_secret))

    # Standard RFC 5869 HKDF-SHA256 implemented with Python stdlib hmac/hashlib
    # If salt is None, RFC 5869 sets salt to a string of HashLen zeros (32 bytes for SHA256)
    salt_bytes = bytes(salt) if salt is not None else bytes(32)
    # Step 1: HKDF-Extract
    prk = hmac.new(salt_bytes, bytes(shared_secret), hashlib.sha256).digest()
    # Step 2: HKDF-Expand (for L=32 bytes, N=1 block is sufficient)
    t1 = hmac.new(prk, bytes(info) + b"\x01", hashlib.sha256).digest()
    return t1[:32]


# ==============================================================================
# 3. AES-256-GCM Encryption / Decryption (NIST SP 800-38D)
# ==============================================================================

def encrypt_message(key: bytes, plaintext: bytes) -> dict:
    """Encrypt a plaintext byte string using AES-256-GCM authenticated encryption.
    
    AES-GCM combines counter-mode (CTR) confidentiality with Galois field (GHASH)
    message authentication. It guarantees both confidentiality and integrity: any
    bit flip in ciphertext or nonce will cause decryption to be rejected.
    
    Args:
        key: 32-byte (256-bit) AES encryption key.
        plaintext: The message bytes to encrypt. If str is passed, it is UTF-8 encoded.
        
    Returns:
        dict: {
            'ciphertext': bytes,
            'nonce': bytes (12-byte initialization vector),
            'tag': bytes (16-byte authentication tag)
        }
    """
    if isinstance(plaintext, str):
        plaintext = plaintext.encode("utf-8")
    if not isinstance(plaintext, (bytes, bytearray)):
        raise TypeError("plaintext must be bytes or str")
    if len(key) != 32:
        raise ValueError(f"AES-256 requires a 32-byte key, got {len(key)} bytes")

    nonce = os.urandom(12)  # NIST standard 96-bit nonce

    # Path A: cryptography library
    if _HAVE_CRYPTOGRAPHY:
        aesgcm = AESGCM(key)
        ct_with_tag = aesgcm.encrypt(nonce, bytes(plaintext), None)
        ciphertext = ct_with_tag[:-16]
        tag = ct_with_tag[-16:]
        return {"ciphertext": ciphertext, "nonce": nonce, "tag": tag}

    # Path B: Native OpenSSL 3 ctypes (hardware accelerated)
    if _SYSTEM_LIBCRYPTO is not None:
        ctx = _SYSTEM_LIBCRYPTO.EVP_CIPHER_CTX_new()
        try:
            _SYSTEM_LIBCRYPTO.EVP_EncryptInit_ex(ctx, _SYSTEM_LIBCRYPTO.EVP_aes_256_gcm(), None, None, None)
            _SYSTEM_LIBCRYPTO.EVP_CIPHER_CTX_ctrl(ctx, 0x9, len(nonce), None)  # EVP_CTRL_GCM_SET_IVLEN
            _SYSTEM_LIBCRYPTO.EVP_EncryptInit_ex(ctx, None, None, key, nonce)

            out_buf = create_string_buffer(len(plaintext) + 16)
            out_len = c_int(0)
            _SYSTEM_LIBCRYPTO.EVP_EncryptUpdate(
                ctx, cast(out_buf, c_void_p), byref(out_len), bytes(plaintext), len(plaintext)
            )
            ct_len = out_len.value

            _SYSTEM_LIBCRYPTO.EVP_EncryptFinal_ex(
                ctx, cast(byref(out_buf, ct_len), c_void_p), byref(out_len)
            )
            ct_len += out_len.value

            tag_buf = create_string_buffer(16)
            _SYSTEM_LIBCRYPTO.EVP_CIPHER_CTX_ctrl(ctx, 0x10, 16, cast(tag_buf, c_void_p))  # EVP_CTRL_GCM_GET_TAG

            return {
                "ciphertext": out_buf.raw[:ct_len],
                "nonce": nonce,
                "tag": tag_buf.raw[:16],
            }
        finally:
            _SYSTEM_LIBCRYPTO.EVP_CIPHER_CTX_free(ctx)

    # Path C: Pure-Python CTR + HMAC authenticated encryption fallback
    # Encrypt via CTR keystream generated by HMAC-SHA256 counter
    keystream = b""
    blocks_needed = (len(plaintext) + 31) // 32
    for counter in range(blocks_needed):
        keystream += hmac.new(
            key, nonce + counter.to_bytes(4, "big"), hashlib.sha256
        ).digest()
    ciphertext = bytes(p ^ k for p, k in zip(plaintext, keystream[:len(plaintext)]))
    # Compute 16-byte authentication tag over nonce || ciphertext
    tag = hmac.new(key, b"GCM-SIM:" + nonce + ciphertext, hashlib.sha256).digest()[:16]
    return {"ciphertext": ciphertext, "nonce": nonce, "tag": tag}


def decrypt_message(key: bytes, ciphertext: bytes, nonce: bytes, tag: bytes) -> bytes:
    """Decrypt an authenticated AES-256-GCM ciphertext and verify its integrity tag.
    
    Fail-Safe Principle:
    If any single bit of ciphertext, nonce, tag, or key is modified or incorrect,
    this function raises InvalidTag immediately and releases NO plaintext bits.
    
    Args:
        key: 32-byte AES decryption key.
        ciphertext: The encrypted ciphertext bytes.
        nonce: The 12-byte initialization vector used during encryption.
        tag: The 16-byte authentication tag.
        
    Returns:
        bytes: The authenticated decrypted plaintext bytes.
        
    Raises:
        InvalidTag: If tag verification fails due to tampering, corruption, or wrong key.
    """
    if not isinstance(ciphertext, (bytes, bytearray)):
        raise TypeError("ciphertext must be bytes")
    if not isinstance(nonce, (bytes, bytearray)):
        raise TypeError("nonce must be bytes")
    if not isinstance(tag, (bytes, bytearray)):
        raise TypeError("tag must be bytes")
    if len(key) != 32:
        raise ValueError(f"AES-256 requires a 32-byte key, got {len(key)} bytes")
    if len(tag) != 16:
        raise InvalidTag(f"Invalid authentication tag length: expected 16 bytes, got {len(tag)}")

    # Path A: cryptography library
    if _HAVE_CRYPTOGRAPHY:
        try:
            aesgcm = AESGCM(key)
            return aesgcm.decrypt(nonce, ciphertext + tag, None)
        except Exception as exc:
            raise InvalidTag("Ciphertext authentication failed: tag mismatch or tampering.") from exc

    # Path B: Native OpenSSL 3 ctypes
    if _SYSTEM_LIBCRYPTO is not None:
        ctx = _SYSTEM_LIBCRYPTO.EVP_CIPHER_CTX_new()
        try:
            _SYSTEM_LIBCRYPTO.EVP_DecryptInit_ex(ctx, _SYSTEM_LIBCRYPTO.EVP_aes_256_gcm(), None, None, None)
            _SYSTEM_LIBCRYPTO.EVP_CIPHER_CTX_ctrl(ctx, 0x9, len(nonce), None)  # EVP_CTRL_GCM_SET_IVLEN
            _SYSTEM_LIBCRYPTO.EVP_DecryptInit_ex(ctx, None, None, key, nonce)

            plain_buf = create_string_buffer(len(ciphertext) + 16)
            p_len = c_int(0)
            _SYSTEM_LIBCRYPTO.EVP_DecryptUpdate(
                ctx, cast(plain_buf, c_void_p), byref(p_len), bytes(ciphertext), len(ciphertext)
            )
            dec_len = p_len.value

            # Set expected authentication tag
            tag_buf = create_string_buffer(bytes(tag), 16)
            _SYSTEM_LIBCRYPTO.EVP_CIPHER_CTX_ctrl(ctx, 0x11, 16, cast(tag_buf, c_void_p))  # EVP_CTRL_GCM_SET_TAG

            ret = _SYSTEM_LIBCRYPTO.EVP_DecryptFinal_ex(
                ctx, cast(byref(plain_buf, dec_len), c_void_p), byref(p_len)
            )
            if ret <= 0:
                raise InvalidTag("Authentication tag verification failed: ciphertext or tag modified.")
            dec_len += p_len.value
            return plain_buf.raw[:dec_len]
        finally:
            _SYSTEM_LIBCRYPTO.EVP_CIPHER_CTX_free(ctx)

    # Path C: Pure-Python CTR + HMAC authenticated decryption fallback
    expected_tag = hmac.new(key, b"GCM-SIM:" + nonce + ciphertext, hashlib.sha256).digest()[:16]
    if not hmac.compare_digest(expected_tag, bytes(tag)):
        raise InvalidTag("Authentication tag mismatch: data corrupted or wrong key.")

    keystream = b""
    blocks_needed = (len(ciphertext) + 31) // 32
    for counter in range(blocks_needed):
        keystream += hmac.new(
            key, nonce + counter.to_bytes(4, "big"), hashlib.sha256
        ).digest()
    plaintext = bytes(c ^ k for c, k in zip(ciphertext, keystream[:len(ciphertext)]))
    return plaintext


# ==============================================================================
# 4. Classical RSA Baseline Comparison (Educational Shor's Analysis)
# ==============================================================================

def _mgf1_sha256(seed: bytes, length: int) -> bytes:
    """Mask Generation Function MGF1 based on SHA-256 (RFC 8017 PKCS#1 v2.2)."""
    t = b""
    counter = 0
    while len(t) < length:
        t += hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
        counter += 1
    return t[:length]


def _oaep_pad_sha256(message: bytes, k: int = 256, label: bytes = b"") -> bytes:
    """Encode message with PKCS#1 v2.2 OAEP padding using SHA-256 and MGF1."""
    h_len = 32
    l_hash = hashlib.sha256(label).digest()
    ps_len = k - len(message) - 2 * h_len - 2
    if ps_len < 0:
        raise ValueError("Message too long for RSA key size with OAEP padding")
    ps = b"\x00" * ps_len
    db = l_hash + ps + b"\x01" + message
    seed = os.urandom(h_len)
    db_mask = _mgf1_sha256(seed, k - h_len - 1)
    masked_db = bytes(x ^ y for x, y in zip(db, db_mask))
    seed_mask = _mgf1_sha256(masked_db, h_len)
    masked_seed = bytes(x ^ y for x, y in zip(seed, seed_mask))
    return b"\x00" + masked_seed + masked_db


def _oaep_unpad_sha256(em: bytes, k: int = 256, label: bytes = b"") -> bytes:
    """Decode and verify PKCS#1 v2.2 OAEP padding using SHA-256 and MGF1."""
    h_len = 32
    if len(em) != k or em[0] != 0:
        raise ValueError("Invalid OAEP encoding")
    masked_seed = em[1 : 1 + h_len]
    masked_db = em[1 + h_len :]
    seed_mask = _mgf1_sha256(masked_db, h_len)
    seed = bytes(x ^ y for x, y in zip(masked_seed, seed_mask))
    db_mask = _mgf1_sha256(seed, len(masked_db))
    db = bytes(x ^ y for x, y in zip(masked_db, db_mask))
    l_hash = hashlib.sha256(label).digest()
    if db[:h_len] != l_hash:
        raise ValueError("OAEP hash mismatch")
    idx = db.find(b"\x01", h_len)
    if idx == -1:
        raise ValueError("OAEP delimiter byte not found")
    return db[idx + 1 :]


def run_classical_rsa_demo(message: str = "Same financial report") -> dict:
    """Demonstrate classical RSA-2048 encryption and explain its vulnerability to Shor's algorithm.
    
    Generates/executes an RSA-2048 OAEP encryption-decryption cycle to contrast directly
    with the lattice-based post-quantum ML-KEM pipeline.
    
    Args:
        message: Plaintext string to encrypt.
        
    Returns:
        dict: {
            'key_size': int (2048),
            'public_key_hex': str (abbreviated),
            'encrypted_hex': str (abbreviated),
            'decrypted_message': str,
            'quantum_vulnerable': bool (always True),
            'vulnerability_explanation': str
        }
    """
    msg_bytes = message.encode("utf-8") if isinstance(message, str) else message

    if _HAVE_CRYPTOGRAPHY:
        # Standard cryptography hazmat RSA execution
        priv_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pub_key = priv_key.public_key()
        encrypted = pub_key.encrypt(
            msg_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        decrypted = priv_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        pub_der = pub_key.public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        public_key_hex = pub_der.hex()[:64]
    else:
        # Pure-Python PKCS#1 v2.2 OAEP + 2048-bit modular exponentiation
        padded = _oaep_pad_sha256(msg_bytes, 256)
        m_int = int.from_bytes(padded, "big")
        c_int = pow(m_int, _RSA_E, _RSA_N)
        encrypted = c_int.to_bytes(256, "big")

        dec_int = pow(c_int, _RSA_D, _RSA_N)
        dec_padded = dec_int.to_bytes(256, "big")
        decrypted = _oaep_unpad_sha256(dec_padded, 256)
        public_key_hex = hex(_RSA_N)[2:66]

    vulnerability_explanation = (
        "CRITICAL QUANTUM VULNERABILITY (Shor's Algorithm):\n"
        "Classical RSA-2048 security relies strictly on the mathematical hardness of the "
        "Integer Factorization Problem (IFP). Peter Shor's 1994 quantum algorithm solves "
        "order-finding in polynomial time O((log N)^3) on a fault-tolerant quantum computer using "
        "the Quantum Fourier Transform (QFT). While classical Number Field Sieve (GNFS) requires "
        "~10^30 operations to factor N=2048, a quantum computer with ~4,096 logical qubits "
        "can factor the modulus and recover private key d in seconds to minutes. "
        "Any financial transaction secured solely by RSA or classical ECC is subject to "
        "'Harvest Now, Decrypt Later' (HNDL) attacks. In contrast, QuantumShield's ML-KEM relies "
        "on the Module Learning With Errors (M-LWE) lattice problem, which has no known "
        "sub-exponential quantum solution."
    )

    return {
        "key_size": 2048,
        "public_key_hex": public_key_hex,
        "encrypted_hex": encrypted.hex()[:64],
        "decrypted_message": decrypted.decode("utf-8", errors="replace"),
        "quantum_vulnerable": True,
        "vulnerability_explanation": vulnerability_explanation,
    }


# ==============================================================================
# 5. Full PQC End-to-End Demo Pipeline
# ==============================================================================

def run_pqc_demo(
    message: str = "QuantumShield Financial Report: Transaction #4821 — Amount: ₹50,000 — Status: BLOCKED",
) -> dict:
    """Execute the complete post-quantum hybrid cryptographic workflow.
    
    Full Workflow:
    1. Key Generation (Party B / Bank Server): Generates ML-KEM public and secret keypair.
    2. Encapsulation (Party A / Client Device): Encapsulates against Party B's public key,
       producing shared_secret_a and kem_ciphertext.
    3. Decapsulation (Party B / Bank Server): Decapsulates kem_ciphertext using secret key,
       recovering shared_secret_b.
    4. Verification: Asserts shared_secret_a == shared_secret_b.
    5. Key Derivation: Derives a 256-bit symmetric key via HKDF-SHA256 bound to 'quantumshield-aes-key'.
    6. AES-256-GCM Encryption: Encrypts the financial transaction report with nonce and tag.
    7. Decryption & Verification: Authenticates tag and recovers the original financial record.
    8. Active Tamper Rejection Test: Flips a bit in the encrypted ciphertext, attempts decryption,
       and verifies that the cryptographic engine detects the tamper and aborts safely.
       
    Args:
        message: Financial transaction payload to secure.
        
    Returns:
        dict: Complete audit trail containing all intermediate cryptographic artifacts,
              hex-encoded representations, verification statuses, and tamper test results.
    """
    steps: list[dict[str, Any]] = []

    # Step 1: Keypair generation (Party B)
    public_key, secret_key = generate_keypair()
    steps.append({
        "step": 1,
        "name": "KEM Keypair Generation (Party B)",
        "status": "COMPLETED",
        "details": f"Generated public key ({len(public_key)} bytes) and secret key ({len(secret_key)} bytes).",
    })

    # Step 2: Encapsulation (Party A)
    kem_ciphertext, shared_secret_a = encapsulate(public_key)
    steps.append({
        "step": 2,
        "name": "KEM Encapsulation (Party A)",
        "status": "COMPLETED",
        "details": f"Encapsulated against public key -> Ciphertext ({len(kem_ciphertext)} bytes), Shared Secret ({len(shared_secret_a)} bytes).",
    })

    # Step 3: Decapsulation (Party B)
    shared_secret_b = decapsulate(secret_key, kem_ciphertext)
    steps.append({
        "step": 3,
        "name": "KEM Decapsulation (Party B)",
        "status": "COMPLETED",
        "details": f"Decapsulated ciphertext -> Recovered Shared Secret ({len(shared_secret_b)} bytes).",
    })

    # Step 4: Verification of shared secrets
    shared_secrets_match = (shared_secret_a == shared_secret_b)
    if not shared_secrets_match:
        raise RuntimeError("Fatal PQC Error: Encapsulated and decapsulated shared secrets do not match!")
    steps.append({
        "step": 4,
        "name": "Shared Secret Agreement Verification",
        "status": "COMPLETED",
        "details": f"Secrets match perfectly: {shared_secrets_match}.",
    })

    # Step 5: Derive symmetric AES key via HKDF
    aes_key = derive_symmetric_key(shared_secret_a, salt=None, info=b"quantumshield-aes-key")
    steps.append({
        "step": 5,
        "name": "HKDF-SHA256 Key Derivation",
        "status": "COMPLETED",
        "details": f"Derived 256-bit AES symmetric key from shared secret.",
    })

    # Step 6: Encrypt message with AES-256-GCM
    plaintext_bytes = message.encode("utf-8")
    encrypted = encrypt_message(aes_key, plaintext_bytes)
    steps.append({
        "step": 6,
        "name": "AES-256-GCM Authenticated Encryption",
        "status": "COMPLETED",
        "details": f"Encrypted {len(plaintext_bytes)} bytes of financial payload. Nonce: 12 bytes, Tag: 16 bytes.",
    })

    # Step 7: Decrypt and verify
    decrypted_bytes = decrypt_message(
        aes_key, encrypted["ciphertext"], encrypted["nonce"], encrypted["tag"]
    )
    decrypted_message = decrypted_bytes.decode("utf-8", errors="replace")
    if decrypted_message != message:
        raise RuntimeError("Fatal Decryption Error: Recovered message does not match original plaintext!")
    steps.append({
        "step": 7,
        "name": "AES-256-GCM Decryption & Integrity Verification",
        "status": "COMPLETED",
        "details": "Authenticated tag verified; plaintext match confirmed.",
    })

    # Step 8: Active Tamper Injection Test (Fail-Safe Verification)
    tamper_test_passed = False
    tampered_ciphertext = bytearray(encrypted["ciphertext"])
    if len(tampered_ciphertext) > 0:
        tampered_ciphertext[0] ^= 0x01  # Invert a single bit
    else:
        tampered_ciphertext = bytearray(b"\x01")

    try:
        decrypt_message(
            aes_key,
            bytes(tampered_ciphertext),
            encrypted["nonce"],
            encrypted["tag"],
        )
        # If decryption succeeded despite flipped bit, the tamper detection FAILED
        tamper_test_passed = False
    except (InvalidTag, Exception):
        # Tamper was correctly detected and rejected!
        tamper_test_passed = True

    steps.append({
        "step": 8,
        "name": "Tamper Resistance Test",
        "status": "COMPLETED" if tamper_test_passed else "FAILED",
        "details": f"Flipped bit in ciphertext; authentication rejection passed: {tamper_test_passed}.",
    })

    return {
        "public_key_hex": public_key[:32].hex(),
        "secret_key_hex": secret_key[:16].hex(),
        "kem_ciphertext_hex": kem_ciphertext[:32].hex(),
        "shared_secrets_match": shared_secrets_match,
        "shared_secret_hex": shared_secret_a[:32].hex(),
        "aes_key_hex": aes_key.hex(),
        "original_message": message,
        "encrypted_ciphertext_hex": encrypted["ciphertext"][:64].hex(),
        "nonce_hex": encrypted["nonce"].hex(),
        "tag_hex": encrypted["tag"].hex(),
        "decrypted_message": decrypted_message,
        "tamper_test_passed": tamper_test_passed,
        "backend": get_backend_info(),
        "steps": steps,
    }
