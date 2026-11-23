from __future__ import annotations
from ..sim.attacks import ddos_scenario, sybil_scenario
from ..config import Config

ATTACK_MATRIX = [
    ("Sybil",               "fake identities",   "PoS+PBFT + PKI + stake weighting"),
    ("DDoS",                "traffic flood",     "rate limiting + firewalls + redundancy"),
    ("Replay",              "resend tx",         "timestamps + nonces + contract checks"),
    ("51%",                 "majority control",  "permissioned + hybrid consensus"),
    ("Data tampering",      "modify data",       "SHA-256 on-chain hash"),
    ("Unauthorized access", "no clearance",      "RBAC + PKI + signatures"),
    ("MITM",                "intercept",         "TLS 1.3 + MQTT/CoAP"),
    ("IoT compromise",      "device vuln",       "secure boot + PKI"),
    ("Smart contract exploit", "code vuln",      "audits + multi-sig"),
]

def run_security_eval(cfg: Config) -> dict:
    d_def = ddos_scenario(cfg, defended=True)
    d_und = ddos_scenario(cfg, defended=False)
    s = sybil_scenario(cfg)
    return {"table6_rows": len(ATTACK_MATRIX),
            "table6": ATTACK_MATRIX,
            "ddos_defended": d_def.__dict__,
            "ddos_undefended": d_und.__dict__,
            "sybil": s.__dict__}