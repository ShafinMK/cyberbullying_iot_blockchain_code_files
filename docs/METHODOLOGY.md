# Method → module map

| Paper component | Module |
|---|---|
| AES-256 (Eq. C = E_AES256(P)) | `src/crypto/aes_gcm.py` |
| RSA-OAEP key wrap | `src/crypto/rsa_oaep.py` |
| ECDSA consent signature | `src/crypto/ecdsa_consent.py` |
| PKI / X.509 device certs | `src/crypto/pki.py` |
| ZKP (C = g^K mod p) | `src/crypto/zkp_schnorr.py` |
| DCM (Algorithm 3) | `src/dcm/device.py` |
| Gateway delegation / blacklist | `src/dcm/gateway.py` |
| IPFS AES+RSA envelope | `src/storage/envelope.py` |
| Stake s_i = 0.3U+0.3V+0.4R | `src/consensus/stake.py` |
| Committee k = ⌈m/3⌉+1 | `src/consensus/committee.py` |
| PBFT quorum ⌊2k/3⌋+1 | `src/consensus/pbft.py` |
| Hybrid PoS→PBFT | `src/consensus/hybrid.py` |
| RBAC (Algorithm 2) | `src/rbac/` + `chaincode/rbac.go` |
| SubmitEvidence (Algorithm 1) | `chaincode/evidence.go` |
| Consent lifecycle | `chaincode/consent.go` |
| TPS / L_avg | `src/evaluation/metrics.py` |
| DDoS / Sybil | `src/sim/attacks.py` |
| Chain quality Q(γ) | `src/evaluation/chain_quality.py` |