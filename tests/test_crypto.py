import pytest
from src.crypto import aes_gcm, rsa_oaep, ecdsa_consent, zkp_schnorr

def test_aes_roundtrip():
    k = aes_gcm.new_key(); pt = b"hello forensic evidence"
    assert aes_gcm.decrypt_aes256(k, aes_gcm.encrypt_aes256(k, pt)) == pt

def test_aes_tamper_detected():
    k = aes_gcm.new_key(); ct = bytearray(aes_gcm.encrypt_aes256(k, b"x"*40)); ct[-1] ^= 1
    with pytest.raises(Exception): aes_gcm.decrypt_aes256(k, bytes(ct))

def test_rsa_wrap_roundtrip():
    priv = rsa_oaep.generate_rsa_keypair(); sym = aes_gcm.new_key()
    assert rsa_oaep.unwrap_key(priv, rsa_oaep.wrap_key(priv.public_key(), sym)) == sym

def test_consent_sig():
    priv = ecdsa_consent.generate_device_key(); msg = b"consent:v1"
    assert ecdsa_consent.verify_consent(priv.public_key(), msg, ecdsa_consent.sign_consent(priv, msg))

def test_schnorr():
    C, t, s = zkp_schnorr.prove(secret_K=1234567, nonce_r=42)
    assert zkp_schnorr.verify(C, t, s)
    assert not zkp_schnorr.verify(C, t, (s + 1) % zkp_schnorr.P)