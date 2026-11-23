from __future__ import annotations
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_LEN = 32
NONCE_LEN = 12
TAG_LEN = 16

def new_key() -> bytes:
    return AESGCM.generate_key(bit_length=256)

def encrypt_aes256(key: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
    if len(key) != KEY_LEN: raise ValueError(f"AES-256 key must be {KEY_LEN} bytes")
    if not isinstance(plaintext, (bytes, bytearray)): raise TypeError("plaintext must be bytes")
    nonce = os.urandom(NONCE_LEN)
    ct = AESGCM(key).encrypt(nonce, bytes(plaintext), aad or None)
    return nonce + ct

def decrypt_aes256(key: bytes, blob: bytes, aad: bytes = b"") -> bytes:
    if len(key) != KEY_LEN: raise ValueError("bad key length")
    if len(blob) < NONCE_LEN + TAG_LEN: raise ValueError("ciphertext too short")
    nonce, ct = blob[:NONCE_LEN], blob[NONCE_LEN:]
    return AESGCM(key).decrypt(nonce, ct, aad or None)

def padded_len(nbytes: int) -> int:
    block = 16
    return ((nbytes // block) + 1) * block