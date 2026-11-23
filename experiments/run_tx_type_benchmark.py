from __future__ import annotations
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
from src.config import load_config
from src.sim.engine import tx_type_benchmark

def main(figdir: pathlib.Path, tabdir: pathlib.Path):
    load_config()
    rows = tx_type_benchmark(load_config())
    df = pd.DataFrame(rows)
    tabdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(tabdir / "tx_type_benchmark.csv", index=False)

    figdir.mkdir(parents=True, exist_ok=True)

    # Fig. 4 — TPS by transaction type
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(df.tx_type, df.tps, color="C0")
    ax.set_ylabel("Sustained TPS")
    ax.set_title("TPS by Transaction Type")
    plt.xticks(rotation=35, ha="right")
    fig.tight_layout()
    fig.savefig(figdir / "fig4_tps_by_tx.png", dpi=200)
    plt.close(fig)

    # Fig. 5 — max/min/avg latency by transaction type
    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = range(len(df))
    ax.plot(x, df.lat_max, "o-", label="Max Latency (ms)")
    ax.plot(x, df.lat_min, "s-", label="Min Latency (ms)")
    ax.plot(x, df.lat_avg, "^-", label="Average Latency (ms)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(df.tx_type, rotation=35, ha="right")
    ax.set_ylabel("Latency (ms)")
    ax.legend()
    ax.set_title("Latency by Transaction Type")
    fig.tight_layout()
    fig.savefig(figdir / "fig5_latency_by_tx.png", dpi=200)
    plt.close(fig)
    print(f"[tx-bench] wrote {len(df)} rows")

if __name__ == "__main__":
    main(pathlib.Path("results/figures"), pathlib.Path("results/tables"))