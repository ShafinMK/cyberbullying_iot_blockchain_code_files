from __future__ import annotations
import hashlib
from ..crypto import aes_gcm, rsa_oaep

def store_evidence(ipfs, plaintext: bytes, authorized_pubs: dict) -> dict:
    sym = aes_gcm.new_key()
    ct = aes_gcm.encrypt_aes256(sym, plaintext)
    cid = ipfs.put(ct)
    wrapped = {uid: rsa_oaep.wrap_key(pub, sym).hex() for uid, pub in authorized_pubs.items()}
    return {"cid": cid, "sha256": hashlib.sha256(ct).hexdigest(), "wrapped_keys": wrapped}

def retrieve_evidence(ipfs, cid: str, uid: str, priv, wrapped_hex: str) -> bytes:
    ct = ipfs.get(cid)
    sym = rsa_oaep.unwrap_key(priv, bytes.fromhex(wrapped_hex))
    return aes_gcm.decrypt_aes256(sym, ct)