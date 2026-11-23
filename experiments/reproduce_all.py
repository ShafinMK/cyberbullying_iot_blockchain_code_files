from __future__ import annotations
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.config import load_config
from experiments import (run_consensus_validation, run_tx_type_benchmark,
                          run_workload_scaling, run_cpu_model,
                          run_security_eval, run_chain_quality)

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIG  = ROOT / "results" / "figures"
TAB  = ROOT / "results" / "tables"
RAW  = ROOT / "results" / "raw"
for d in (FIG, TAB, RAW): d.mkdir(parents=True, exist_ok=True)

def main():
    load_config()
    print("== consensus validation =="); run_consensus_validation.main(RAW / "consensus_validation.json")
    print("== tx-type benchmark ==");   run_tx_type_benchmark.main(FIG, TAB)
    print("== workload scaling ==");     run_workload_scaling.main(FIG, TAB)
    print("== cpu model ==");            run_cpu_model.main(FIG, TAB)
    print("== security eval ==");        run_security_eval.main(RAW / "security_eval.json")
    print("== chain quality ==");        run_chain_quality.main(FIG, TAB)
    print("\nAll outputs written to results/.")

if __name__ == "__main__":
    main()