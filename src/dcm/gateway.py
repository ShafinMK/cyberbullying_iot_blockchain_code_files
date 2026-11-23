from __future__ import annotations
import hashlib
from ..crypto import rsa_oaep, pki

class Gateway:
    def __init__(self, ca: pki.TestCA, chain_client, ipfs_client):
        self.ca = ca
        self.priv = rsa_oaep.generate_rsa_keypair()
        self.pub = self.priv.public_key()
        self.chain = chain_client
        self.ipfs = ipfs_client
        self.blacklist: set[str] = set()

    def ingest(self, pkg: dict) -> dict:
        dev = pkg["device_id"]
        if dev in self.blacklist:
            raise PermissionError(f"device {dev} on consent-withdrawal blacklist")
        h = hashlib.sha256(pkg["ciphertext"]).hexdigest()
        if h != pkg["sha256"]:
            raise ValueError("gateway integrity check failed (hash mismatch)")
        if pkg["kind"] == "audio_blob":
            cid = self.ipfs.put(pkg["ciphertext"])
            onchain = {"device_id": dev, "kind": pkg["kind"], "cid": cid,
                       "sha256": h, "wrapped_key": pkg["wrapped_key"].hex(),
                       "ts": pkg["ts"]}
        else:
            onchain = {"device_id": dev, "kind": pkg["kind"],
                       "sha256": h, "wrapped_key": pkg["wrapped_key"].hex(),
                       "ts": pkg["ts"], "inline_len": len(pkg["ciphertext"])}
        return self.chain.submit(onchain)

    def add_to_blacklist(self, device_id: str) -> None:
        self.blacklist.add(device_id)