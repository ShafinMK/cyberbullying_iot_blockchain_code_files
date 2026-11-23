import pytest
from src.config import load_config
from src.crypto import pki, rsa_oaep
from src.dcm.device import DCM
from src.dcm.gateway import Gateway
from src.storage.ipfs_client import LocalIPFSStub

def _make(consent=True):
    ca = pki.TestCA()
    gw_priv = rsa_oaep.generate_rsa_keypair()
    ipfs = LocalIPFSStub()

    class ChainStub:
        def __init__(self): self.records = []
        def submit(self, rec): self.records.append(rec); return {"ok": True, "sha256": rec["sha256"]}

    chain = ChainStub()
    gw = Gateway(ca, chain, ipfs)
    dcm = DCM("dev1", ca, gw_priv.public_key(),
              {"a@x.com": "user_a3f2"}, {"dev1": consent})
    return dcm, gw, chain

def test_consent_withdrawn_blocks_collection():
    dcm, _, _ = _make(consent=False)
    with pytest.raises(PermissionError): dcm.collect("text", b"hi")

def test_pseudonymize_on_collect():
    dcm, _, _ = _make()
    rec = dcm.collect("text", b"from a@x.com")
    assert b"user_a3f2" in rec.payload and b"a@x.com" not in rec.payload

def test_gateway_submits_and_hashes():
    dcm, gw, chain = _make()
    rec = dcm.collect("text", b"hello")
    pkg = dcm.encrypt_and_package(rec)
    receipt = gw.ingest(pkg)
    assert receipt["ok"] and len(chain.records) == 1

def test_tampered_packet_rejected():
    dcm, gw, _ = _make()
    pkg = dcm.encrypt_and_package(dcm.collect("text", b"x"))
    pkg["sha256"] = "0" * 64
    with pytest.raises(ValueError): gw.ingest(pkg)