from __future__ import annotations
import pathlib
import pandas as pd
import matplotlib.pyplot as plt

DATA = {
    "Fabric 2.2": {"Low": 28, "Medium": 47, "High": 92},
    "Fabric 2.3": {"Low": 22, "Medium": 40, "High": 79},
    "Fabric 2.4": {"Low": 19, "Medium": 36, "High": 64},
    "Fabric 2.5": {"Low": 16, "Medium": 27, "High": 53},
}

def main(figdir: pathlib.Path, tabdir: pathlib.Path):
    df = pd.DataFrame(DATA).T.reset_index().rename(columns={"index": "Platform"})
    tabdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(tabdir / "cpu_model.csv", index=False)

    figdir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    x = range(len(df)); w = 0.25
    for i, load in enumerate(["Low", "Medium", "High"]):
        ax.bar([p + (i - 1) * w for p in x], df[load], width=w, label=f"{load} Load")
    ax.set_xticks(list(x)); ax.set_xticklabels(df.Platform)
    ax.set_ylabel("CPU Usage (%)")
    ax.set_title("CPU Usage Across Hyperledger Fabric Versions")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figdir / "fig9_cpu.png", dpi=200)
    plt.close(fig)
    print("[cpu] wrote fig9")

if __name__ == "__main__":
    main(pathlib.Path("results/figures"), pathlib.Path("results/tables"))