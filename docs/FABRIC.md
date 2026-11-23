# Running the Fabric benchmark (optional)

1. Install Docker 24, Fabric v2.5 binaries, Caliper v0.5.0, Go 1.19.
2. `cd configs/fabric && docker compose up -d`
3. `cd configs/fabric/caliper && npx caliper launch manager --caliper-workspace . \
   --caliper-networkconfig networkconfig.yaml --caliper-benchconfig benchmark.yaml`