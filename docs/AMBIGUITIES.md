# Ambiguity log

| ID | Issue | Resolution |
|---|---|---|
| A3 | Three packet-size tables disagree (System-arch 512/384/500; Table 3 tnote 500/400/500; Data-availability 512/384/500). | System-arch = Data-availability are treated as authoritative; Table 3 tnote is treated as a typo. |
| A5 | Table 2 marks ZKP "Implemented: Yes"; §3.2.5 says none of ZKP/ring-signature/stealth-address are implemented. | Schnorr credential proof is implemented (satisfies Table 2); the broader suite is out of scope. |
| A7 | The chain-quality equation Q(γ) and the UB/SHTB/UDTB/PoP baselines are truncated in the LaTeX source. | The Eyal–Sirer backbone model is used in `src/evaluation/chain_quality.py`; Fig. 10 baselines are drawn at their reported approximate levels. |