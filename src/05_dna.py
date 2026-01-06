import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
FIG_DIR = PROJECT_ROOT / "outputs" / "figures" / "team_dna"
FIG_DIR.mkdir(parents=True, exist_ok=True)

bg = "#0b0f14"
fg = "#e8eef5"
grid = "#1f2a37"
cyan = "#33b1ff"
purple = "#be95ff"
red = "#ff8389"
teal = "#4aa3a3"
gray = "#94a3b8"

df = pd.read_csv(TABLES_DIR / "team_by_situation_long.csv")
df["Situation"] = df["Situation"].astype(str).str.strip()
df["team"] = df["team"].astype(str).str.strip()

need = ["team", "Situation", "G", "GA"]
missing = [c for c in need if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns in team_by_situation_long.csv: {missing}")

def fmt_team(name: str) -> str:
    name = str(name).strip()
    if name.lower() == "bournemouth":
        return "BOURNEMOUTH"
    return name

def norm_situation(s: str) -> str:
    s = str(s).strip().lower()
    if s == "open play":
        return "Open play"
    if s in {"from corner", "set piece"}:
        return "Set pieces"
    if s == "direct freekick":
        return "Direct free kicks"
    if s == "penalty":
        return "Penalties"
    return s.title()

color_map = {
    "Open play": cyan,
    "Set pieces": purple,
    "Direct free kicks": teal,
    "Penalties": red,
}

df["SituationGroup"] = df["Situation"].map(norm_situation)

teams = sorted(df["team"].unique(), key=lambda x: fmt_team(x).lower())

for team in teams:
    d = df[df["team"] == team].copy()

    agg = d.groupby("SituationGroup", as_index=False).agg(
        G=("G", "sum"),
        GA=("GA", "sum"),
    )

    order = ["Open play", "Set pieces", "Direct free kicks", "Penalties"]
    others = [s for s in agg["SituationGroup"].unique() if s not in order]
    order_full = order + sorted(others)

    agg = agg.set_index("SituationGroup").reindex(order_full).fillna(0).reset_index()

    g_vals = agg["G"].astype(float).to_numpy()
    ga_vals = agg["GA"].astype(float).to_numpy()
    labels = agg["SituationGroup"].tolist()
    colors = [color_map.get(l, gray) for l in labels]

    total_g = float(g_vals.sum())
    total_ga = float(ga_vals.sum())
    xmax = max(total_g, total_ga, 1.0) * 1.12

    fig = plt.figure(figsize=(11, 4.8), facecolor=bg)
    ax = fig.add_subplot(111, facecolor=bg)

    y_for = 1.0
    y_against = 0.0
    h = 0.42

    left = 0.0
    for v, c, lab in zip(g_vals, colors, labels):
        ax.barh(y_for, v, left=left, height=h, color=c)
        if v >= 1:
            pct = (v / total_g * 100) if total_g > 0 else 0
            ax.text(left + v / 2, y_for, f"{int(v)}", ha="center", va="center", color=bg, fontsize=10, fontweight="bold")
            if v >= 2.5:
                ax.text(left + v / 2, y_for + 0.22, f"{pct:.0f}%", ha="center", va="center", color=fg, fontsize=9)
        left += v

    left = 0.0
    for v, c, lab in zip(ga_vals, colors, labels):
        ax.barh(y_against, v, left=left, height=h, color=c)
        if v >= 1:
            pct = (v / total_ga * 100) if total_ga > 0 else 0
            ax.text(left + v / 2, y_against, f"{int(v)}", ha="center", va="center", color=bg, fontsize=10, fontweight="bold")
            if v >= 2.5:
                ax.text(left + v / 2, y_against + 0.22, f"{pct:.0f}%", ha="center", va="center", color=fg, fontsize=9)
        left += v

    ax.text(xmax * 0.995, y_for, f"Total: {int(total_g)}", ha="right", va="center", color=fg, fontsize=10)
    ax.text(xmax * 0.995, y_against, f"Total: {int(total_ga)}", ha="right", va="center", color=fg, fontsize=10)

    ax.set_yticks([y_for, y_against])
    ax.set_yticklabels(["Goals For", "Goals Against"], color=fg, fontsize=12)
    ax.set_xlim(0, xmax)

    ax.grid(axis="x", color=grid, linewidth=1, alpha=0.65)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", colors=fg)
    for s in ax.spines.values():
        s.set_color(grid)

    title = f"{fmt_team(team)} Situation DNA"
    desc = "Goals for/against split by situation (Open play, Set pieces, Direct FKs, Penalties)."
    fig.text(0.07, 0.93, title, color=fg, fontsize=18, fontweight="bold")
    fig.text(0.07, 0.895, desc, color=teal, fontsize=10)

    handles = []
    seen = set()
    for lab, c in zip(labels, colors):
        if lab not in seen:
            seen.add(lab)
            handles.append(plt.Rectangle((0, 0), 1, 1, color=c, label=lab))

    leg = ax.legend(
        handles=handles,
        loc="lower right",
        bbox_to_anchor=(1.0, 0.0),
        bbox_transform=ax.transAxes,
        borderaxespad=0.0,
        facecolor=bg,
        edgecolor=grid,
        framealpha=0.9,
        ncol=2,
    )
    for t in leg.get_texts():
        t.set_color(fg)

    ax.set_xlabel("Goals", color=fg, fontsize=11)
    plt.tight_layout(rect=[0.05, 0.08, 0.98, 0.86])

    out_path = FIG_DIR / f"{fmt_team(team).replace(' ', '_')}_situation_dna.png"
    fig.savefig(out_path, dpi=220, facecolor=bg, bbox_inches="tight")
    plt.close(fig)

print(FIG_DIR)
