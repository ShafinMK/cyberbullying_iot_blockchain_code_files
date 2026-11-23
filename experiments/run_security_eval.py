from __future__ import annotations
import json, pathlib
from src.config import load_config
from src.evaluation.security import run_security_eval

def main(out: pathlib.Path):
    cfg = load_config()
    res = run_security_eval(cfg)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2, default=str))
    print(f"[security] DDoS defended={res['ddos_defended']['degradation_pct']}% "
          f"undefended={res['ddos_undefended']['degradation_pct']}% "
          f"Sybil rejected={res['sybil']['nodes_rejected']}/{res['sybil']['nodes_total']}")

if __name__ == "__main__":
    main(pathlib.Path("results/raw/security_eval.json"))