from __future__ import annotations
import hashlib, time
from dataclasses import dataclass, field
from ..crypto import aes_gcm, rsa_oaep, pki, ecdsa_consent
from .triggers import TriggerWindow

@dataclass
class EvidenceRecord:
    device_id: str
    kind: str
    payload: bytes
    ts: float = field(default_factory=time.time)
    pseudonyms: dict[str, str] = field(default_factory=dict)

def pseudonymize(text: str, mapping: dict[str, str]) -> str:
    for real, pseud in mapping.items():
        text = text.replace(real, pseud)
    return text

class DCM:
    def __init__(self, device_id: str, ca: pki.TestCA, gateway_pub,
                 pseudonym_map: dict[str, str], consent_state: dict[str, bool]):
        if not device_id: raise ValueError("device_id required")
        self.device_id = device_id
        self.cert, self.dev_key = ca.issue_device_cert(device_id)
        self.sign_key = ecdsa_consent.generate_device_key()
        self.gateway_pub = gateway_pub
        self.map = pseudonym_map
        self.consent = consent_state

    def collect(self, kind: str, raw: bytes, window: TriggerWindow | None = None) -> EvidenceRecord:
        if self.consent.get(self.device_id) is False:
            raise PermissionError(f"consent withdrawn for {self.device_id}")
        if kind not in ("text", "location", "audio_metadata", "audio_blob"):
            raise ValueError(f"unsupported evidence kind: {kind}")
        if window and not window.contains(time.time()):
            raise ValueError("collection outside authorized window")
        if kind == "text":
            raw = pseudonymize(raw.decode("utf-8", "replace"), self.map).encode()
        return EvidenceRecord(self.device_id, kind, raw)

    def encrypt_and_package(self, rec: EvidenceRecord) -> dict:
        sym = aes_gcm.new_key()
        ct = aes_gcm.encrypt_aes256(sym, rec.payload, aad=rec.device_id.encode())
        wrapped = rsa_oaep.wrap_key(self.gateway_pub, sym)
        h = hashlib.sha256(ct).hexdigest()
        payload_bytes = ct + wrapped + rec.device_id.encode() + b"|" + str(rec.ts).encode()
        sig = ecdsa_consent.sign_consent(self.sign_key, payload_bytes)
        return {
            "device_id": rec.device_id,
            "kind": rec.kind,
            "ciphertext": ct,
            "wrapped_key": wrapped,
            "sha256": h,
            "ts": rec.ts,
            "ecdsa_sig": sig,
        }

    def transmit(self, package: dict, gateway) -> dict:
        return gateway.ingest(package)