from __future__ import annotations
import datetime as dt
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

class TestCA:
    def __init__(self):
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.cert = self._self_signed()

    def _self_signed(self) -> x509.Certificate:
        n = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "TestCA")])
        return (x509.CertificateBuilder()
                .subject_name(n).issuer_name(n)
                .public_key(self.key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(dt.datetime.utcnow())
                .not_valid_after(dt.datetime.utcnow() + dt.timedelta(days=365))
                .sign(self.key, hashes.SHA256()))

    def issue_device_cert(self, device_id: str):
        dev_key = ec.generate_private_key(ec.SECP256R1())
        n = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, device_id)])
        cert = (x509.CertificateBuilder()
                .subject_name(n).issuer_name(self.cert.subject)
                .public_key(dev_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(dt.datetime.utcnow())
                .not_valid_after(dt.datetime.utcnow() + dt.timedelta(days=90))
                .sign(self.key, hashes.SHA256()))
        return cert, dev_key

    def verify_device_cert(self, cert: x509.Certificate) -> bool:
        try:
            self.cert.public_key().verify(
                cert.signature, cert.tbs_certificate_bytes,
                ec.ECDSA(cert.signature_hash_algorithm))
            return True
        except Exception:
            return False

    def cert_pem(self, cert: x509.Certificate) -> bytes:
        return cert.public_bytes(serialization.Encoding.PEM)