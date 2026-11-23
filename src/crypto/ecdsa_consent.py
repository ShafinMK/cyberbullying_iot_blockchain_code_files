from __future__ import annotations
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

def generate_device_key() -> ec.EllipticCurvePrivateKey:
    return ec.generate_private_key(ec.SECP256R1())

def sign_consent(priv: ec.EllipticCurvePrivateKey, message: bytes) -> bytes:
    return priv.sign(message, ec.ECDSA(hashes.SHA256()))

def verify_consent(pub: ec.EllipticCurvePublicKey, message: bytes, sig: bytes) -> bool:
    try:
        pub.verify(sig, message, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False