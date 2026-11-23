# Reproducibility

`python experiments/reproduce_all.py` regenerates every figure and table in `results/`.
Running `pytest -q` exercises the crypto, consensus, RBAC, DCM, and end-to-end paths.

The Hyperledger Fabric deployment artifacts live under `configs/fabric/`; they are
included for completeness and require a Docker + Fabric v2.5 + Caliper v0.5.0 environment
to execute. The Python pipeline under `src/` and `experiments/` is self-contained.