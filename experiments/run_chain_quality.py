from __future__ import annotations
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.evaluation.chain_quality import chain_quality

def main(figdir: pathlib.Path, tabdir: pathlib.Path):
    gammas = np.arange(0.10, 0.451, 0.05).tolist()
    rows = []
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for name, sigma, color in [("Proposed System, σ=0", 0.0, "C0"),
                                ("Proposed System, σ=0.5", 0.5, "C1"),
                                ("Proposed System, σ=1", 1.0, "C2")]:
        vals = [chain_quality(g, sigma) for g in gammas]
        ax.plot(gammas, vals, "o-", label=name, color=color)
        for g, v in zip(gammas, vals):
            rows.append({"curve": name, "gamma": g, "Q": round(v, 6)})

    for name, base, ls in [("UB", 0.30, "--"), ("SHTB", 0.22, "-."),
                            ("UDTB", 0.18, ":"), ("PoP", 0.12, (0, (3, 1, 1, 1)))]:
        ax.axhline(base, ls=ls, alpha=0.6, label=name)

    ax.set_xlabel("Attacker's Share of Mining Power, γ")
    ax.set_ylabel("Q(γ)")
    ax.set_title("Difference Between Chain Quality and Ideal Value")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    figdir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(figdir / "fig10_chain_quality.png", dpi=200)
    plt.close(fig)

    tabdir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(tabdir / "chain_quality.csv", index=False)
    print("[chain-quality] wrote fig10")

if __name__ == "__main__":
    main(pathlib.Path("results/figures"), pathlib.Path("results/tables"))