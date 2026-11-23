# A Blockchain-Driven Forensic Framework for Secure Cyberbullying Evidence Collection in IoT Environments

**Reproducibility companion** to Shafin & Reno, *Scientific Reports* (2026) 16:34038.

[![Paper](https://img.shields.io/badge/paper-10.1038%2Fs41598--026--64205--4-blue)](https://doi.org/10.1038/s41598-026-64205-4)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

---

## Table of Contents

1. [What This Repository Is](#1-what-this-repository-is)
2. [Repository Structure](#2-repository-structure)
3. [Requirements](#3-requirements)
4. [Quick Start (5 minutes)](#4-quick-start-5-minutes)
5. [Reproducing the Full Paper](#5-reproducing-the-full-paper)
6. [Reproducing Individual Figures and Tables](#6-reproducing-individual-figures-and-tables)
7. [Running the Unit Tests](#7-running-the-unit-tests)
8. [Running the Real Hyperledger Fabric Benchmark (Optional)](#8-running-the-real-hyperledger-fabric-benchmark-optional)
9. [Understanding the Code](#9-understanding-the-code)
10. [Troubleshooting](#10-troubleshooting)
11. [Citation](#11-citation)
12. [License](#12-license)

---

## 1. What This Repository Is

This repository contains a complete, executable reconstruction of the computational methodology described in the paper:

- **Evidence collection** — Data Collection Module (DCM) that pseudonymizes, encrypts with AES-256-GCM, and packages evidence from IoT devices.
- **Transport** — IoT gateway with PKI certificate verification, SHA-256 integrity check, and consent-withdrawal blacklist.
- **Consensus** — Hybrid **PoS + PBFT** with stake-weighted committee selection (`s_i = 0.3·U_i + 0.3·V_i + 0.4·R_i`, committee size `k = ⌈m/3⌉ + 1`).
- **Blockchain layer** — Hyperledger Fabric v2.5 chaincode in Go (Algorithms 1, 2, and 3 from the paper).
- **Off-chain storage** — IPFS envelope with AES-256 file encryption and RSA-2048-OAEP key wrapping.
- **Access control** — Flat RBAC with five roles (LE, FE, JU, EM, SA), time-bound expiry, and an immutable audit log.
- **Evaluation** — Throughput, latency, CPU usage, DDoS and Sybil resilience, and chain-quality analysis.

Everything runs with **Python 3.11+** alone. The Hyperledger Fabric deployment (Docker + Caliper) is optional and included under `configs/fabric/`.

---

## 2. Repository Structure

# Project Structure: cyberbullying-iot-blockchain

- **cyberbullying-iot-blockchain/**
  - **configs/**
    - Master config + Fabric artifacts
  - **chaincode/**
    - Go smart contracts (Algorithms 1–3)
  - **src/**
    - Python library (crypto, DCM, consensus, RBAC, storage, sim)
  - **experiments/**
    - Drivers for every figure and table
  - **tests/**
    - Pytest suite (15 tests)
  - **results/**
    - figures/
    - tables/
    - raw/
  - **notebooks/**
    - reproduction.ipynb
  - **docs/**
    - METHODOLOGY
    - REPRODUCIBILITY
    - AMBIGUITIES
    - FABRIC

## Requirements

- **Mandatory**: Python 3.11+, pip 23+
- **Optional** (Fabric path only): Docker 24+, Hyperledger Fabric 2.5, Caliper 0.5.0, Go 1.19, IPFS 0.18.1

If you only need figures and tables, Python is sufficient.

---

## Quick start

```bash
git clone https://github.com/<your-org>/cyberbullying-iot-blockchain.git
cd cyberbullying-iot-blockchain
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
python experiments/reproduce_all.py

Here is the properly formatted Markdown for your `README.md` file:

```

# How to Reproduce the Work

## 1. Full Pipeline (One Command)

Run the following command to reproduce the complete pipeline:

```bash
python experiments/reproduce_all.py
```

## 2. Step-by-Step Verification

Run the following commands in order and verify the expected outputs.

| Step | Command | Verification / Expected Results |
|---|---|---|
| 1 | `pytest -q` | All 15 tests pass |
| 2 | `python experiments/run_consensus_validation.py` | `k = 4`, `f_max = 1`, `pearson_r = 0.94`, `finality = 380.0 ms` |
| 3 | `python experiments/run_tx_type_benchmark.py` | `tx_type_benchmark.csv`: Add Evidence = 156 TPS / 255 ms; Get Data = 363 TPS / 89 ms |
| 4 | `python experiments/run_workload_scaling.py` | `scaling_all.csv`: Uploading = 153 → 95 TPS; Updating = 129 → 66 TPS; Retrieval = 251 → 145 TPS |
| 5 | `python experiments/run_cpu_model.py` | `cpu_model.csv`: Fabric 2.5 = 16% / 27% / 53% (Low / Medium / High) |
| 6 | `python experiments/run_security_eval.py` | DDoS = 9% defended, 85% undefended; Sybil = 100/100 rejected; Table 6 = 9 rows |
| 7 | `python experiments/run_chain_quality.py` | `fig10_chain_quality.png` shows three σ-curves over γ ∈ [0.10, 0.45] |

## 3. Individual Artifact Generation

The following commands can be executed independently to generate specific figures, tables, and validation results.

| Artifact | Command |
|---|---|
| Figures 4 & 5 | `python experiments/run_tx_type_benchmark.py` |
| Figures 6–8 | `python experiments/run_workload_scaling.py` |
| Figure 9 | `python experiments/run_cpu_model.py` |
| Figure 10 | `python experiments/run_chain_quality.py` |
| Table 6 + DDoS/Sybil Evaluation | `python experiments/run_security_eval.py` |
| Consensus Validation | `python experiments/run_consensus_validation.py` |


# 4. Optional: Real Fabric Benchmark

This step is only required if you want to obtain performance measurements from a live Hyperledger Fabric cluster rather than the Python simulation model.

## 4.1. Install Fabric Binaries

```bash
curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.5.0 1.5.7
export PATH=$PWD/bin:$PATH
```

## 4.2. Start the Fabric Network

```bash
cd configs/fabric && docker compose up -d
```

## 4.3. Package and Deploy Chaincode

```bash
peer lifecycle chaincode package evidence.tar.gz \
    --path ../../chaincode --lang golang --label evidence_1.0
```

**Note:** Full installation, approval, and commit commands are provided in `docs/FABRIC.md`.

## 4.4. Run Hyperledger Caliper

```bash
cd caliper && npx caliper launch manager \
    --caliper-workspace . \
    --caliper-networkconfig networkconfig.yaml \
    --caliper-benchconfig benchmark.yaml
```

## 4.5. Stop the Fabric Network

```bash
cd .. && docker compose down -v
```

---

# 5. Where the Paper's Equations Live

The following table maps the mathematical equations, algorithms, and components presented in the paper to their corresponding implementation files.

| Paper Component | Implementation File |
|---|---|
| AES-256 (`C = E_AES256(P)`) | `src/crypto/aes_gcm.py` |
| RSA-OAEP Key Wrap | `src/crypto/rsa_oaep.py` |
| ECDSA Consent Signature | `src/crypto/ecdsa_consent.py` |
| X.509 PKI | `src/crypto/pki.py` |
| ZKP (`C = g^K mod p`) | `src/crypto/zkp_schnorr.py` |
| Algorithm 3 — IoTDeviceClient | `src/dcm/device.py` |
| Gateway Delegation / Blacklist | `src/dcm/gateway.py` |
| Algorithm 1 — SubmitEvidence | `chaincode/evidence.go` |
| Algorithm 2 — RetrieveEvidence | `chaincode/rbac.go` |
| Stake (`s_i = 0.3U + 0.3V + 0.4R`) | `src/consensus/stake.py` |
| Committee (`k = ⌈m/3⌉ + 1`) | `src/consensus/committee.py` |
| PBFT Quorum (`⌊2k/3⌋ + 1`) | `src/consensus/pbft.py` |
| Hybrid PoS → PBFT | `src/consensus/hybrid.py` |
| RBAC Model and Engine | `src/rbac/` |
| TPS / Latency / Pearson r | `src/evaluation/metrics.py` |
| DDoS / Sybil | `src/sim/attacks.py` |
| Chain Quality `Q(γ)` | `src/evaluation/chain_quality.py` |

**Complete mapping:** See `docs/METHODOLOGY.md`.

---

# 6. Interactive Exploration

The project also supports interactive exploration through Python.

## 6.1. Explore the Consensus Model

```python
>>> from src.config import load_config
>>> from src.consensus.stake import random_validators
>>> cfg = load_config()
>>> vals = random_validators(cfg, 10)
>>> [round(v.stake, 4) for v in vals]  # Sums to 1.0
```

## 6.2. Explore AES-256 Encryption and Decryption

```python
>>> from src.crypto import aes_gcm
>>> k = aes_gcm.new_key()
>>> ct = aes_gcm.encrypt_aes256(k, b"evidence")
>>> aes_gcm.decrypt_aes256(k, ct)
b'evidence'
```

## 6.3. Guided Notebook

Alternatively, open the following Jupyter notebook for a guided walkthrough:

```text
notebooks/reproduction.ipynb
```

---

# 7. Troubleshooting

The following table describes common problems and their corresponding solutions.

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'src'` | Run commands from the repository root, not from `experiments/`. |
| Config not found | Change directory to the repository root. |
| Cryptography installation fails on Windows | Run `pip install cryptography --only-binary=:all:` |
| Matplotlib display error | Set the environment variable: `export MPLBACKEND=Agg` |
| Results differ slightly | Check that the random seed is set to `42` in `configs/config.yaml`. |
| Real Fabric numbers differ from the paper | This is expected because hardware and network configurations differ. See `docs/REPRODUCIBILITY.md`. |

---

**Additional Documentation**

- `docs/METHODOLOGY.md` — Complete mapping of equations, algorithms, and implementation.
- `docs/REPRODUCIBILITY.md` — Reproduction instructions and experimental details.
- `docs/FABRIC.md` — Hyperledger Fabric deployment and benchmarking instructions.
- `notebooks/reproduction.ipynb` — Interactive project walkthrough.




