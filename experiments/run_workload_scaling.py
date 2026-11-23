from __future__ import annotations
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
from src.config import load_config
from src.sim.engine import scale_sweep, SCALING

def main(figdir: pathlib.Path, tabdir: pathlib.Path):
    cfg = load_config()
    rows = []
    for tx_type in SCALING:
        for r in scale_sweep(cfg, tx_type):
            rows.append({"tx_type": tx_type, "label": SCALING[tx_type]["label"],
                         "volume": r.volume, "tps": r.tps,
                         "lat_avg": r.lat_avg_ms, "lat_max": r.lat_max_ms,
                         "lat_min": r.lat_min_ms})
    df = pd.DataFrame(rows)
    tabdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(tabdir / "scaling_all.csv", index=False)

    figdir.mkdir(parents=True, exist_ok=True)
    for tx_type, fname in [("add_evidence", "fig6_uploading.png"),
                            ("update_evidence", "fig7_updating.png"),
                            ("get_data", "fig8_retrieval.png")]:
        d = df[df.tx_type == tx_type]
        label = SCALING[tx_type]["label"]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
        ax1.plot(d.volume, d.tps, "o-", color="C0")
        ax1.set_xlabel("Transaction Volume")
        ax1.set_ylabel("Throughput (TPS)")
        ax1.set_title(f"Throughput vs Volume ({label})")
        ax1.grid(alpha=0.3)
        ax2.plot(d.volume, d.lat_avg, "s-", color="C1")
        ax2.set_xlabel("Transaction Volume")
        ax2.set_ylabel("Average Latency (ms)")
        ax2.set_title(f"Latency vs Volume ({label})")
        ax2.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(figdir / fname, dpi=200)
        plt.close(fig)
    print(f"[scaling] wrote {len(df)} rows -> {tabdir/'scaling_all.csv'}")

if __name__ == "__main__":
    main(pathlib.Path("results/figures"), pathlib.Path("results/tables"))