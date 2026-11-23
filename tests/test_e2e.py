from src.config import load_config
from src.crypto import pki, rsa_oaep
from src.dcm.device import DCM
from src.dcm.gateway import Gateway
from src.storage.ipfs_client import LocalIPFSStub
from src.storage.envelope import store_evidence, retrieve_evidence
from src.rbac.model import Role
from src.rbac.engine import RBACEngine

def test_full_path():
    load_config()
    ca = pki.TestCA()
    officer_priv = rsa_oaep.generate_rsa_keypair()
    ipfs = LocalIPFSStub()

    class ChainStub:
        def __init__(self): self.records = []
        def submit(self, rec): self.records.append(rec); return {"ok": True}

    gw = Gateway(ca, ChainStub(), ipfs)
    dcm = DCM("devX", ca, rsa_oaep.generate_rsa_keypair().public_key(),
              {"v@x": "user_a3f2"}, {"devX": True})

    rec = dcm.collect("audio_blob", b"AUDIODATA" * 1000)
    pkg = dcm.encrypt_and_package(rec)
    assert gw.ingest(pkg)["ok"]

    env = store_evidence(ipfs, b"AUDIODATA" * 1000, {"officer1": officer_priv.public_key()})
    pt = retrieve_evidence(ipfs, env["cid"], "officer1", officer_priv,
                           env["wrapped_keys"]["officer1"])
    assert pt == b"AUDIODATA" * 1000

    e = RBACEngine(); e.assign_role("officer1", Role.LE, by="sa")
    assert e.check_permission("officer1", Role.LE, "RETRIEVE_EVIDENCE")