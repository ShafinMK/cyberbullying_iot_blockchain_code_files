from __future__ import annotations
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

def generate_rsa_keypair(bits: int = 2048) -> rsa.RSAPrivateKey:
    if bits < 2048: raise ValueError("RSA-2048 minimum for forensic use")
    return rsa.generate_private_key(public_exponent=65537, key_size=bits)

def public_pem(priv: rsa.RSAPrivateKey) -> bytes:
    return priv.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)

def load_public_pem(pem: bytes) -> rsa.RSAPublicKey:
    return serialization.load_pem_public_key(pem)

def wrap_key(pub: rsa.RSAPublicKey, sym_key: bytes) -> bytes:
    return pub.encrypt(sym_key,
        padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                     algorithm=hashes.SHA256(), label=None))

def unwrap_key(priv: rsa.RSAPrivateKey, wrapped: bytes) -> bytes:
    return priv.decrypt(wrapped,
        padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                     algorithm=hashes.SHA256(), label=None))