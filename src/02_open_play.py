import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
FIG_DIR = PROJECT_ROOT / "outputs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(TABLES_DIR / "team_by_situation_long.csv")
df["Situation"] = df["Situation"].astype(str).str.strip()

open_play = df[df["Situation"].str.lower().eq("open play")].copy()

need = ["team", "Sh", "G", "xG"]
missing = [c for c in need if c not in open_play.columns]
if missing:
    raise ValueError(f"Missing columns in open-play data: {missing}")

open_play["G_minus_xG"] = open_play["G"] - open_play["xG"]
open_play["every_n_shots"] = np.where(
    open_play["G"] > 0,
    np.rint(open_play["Sh"] / open_play["G"]).astype(int),
    np.nan,
)

top5 = (
    open_play.sort_values("xG", ascending=False)
    .head(5)
    .copy()
    .reset_index(drop=True)
)
top5["rank_label"] = (top5.index + 1).astype(str) + ". " + top5["team"].astype(str)

bg = "#0b0f14"
fg = "#e8eef5"
grid = "#1f2a37"
red = "#ff8389"
cyan = "#33b1ff"
teal = "#4aa3a3"

y = np.arange(len(top5))

fig = plt.figure(figsize=(11, 6.5), facecolor=bg)
ax = fig.add_subplot(111, facecolor=bg)

ax.barh(y, top5["xG"], color=cyan, height=0.55, label="Open-play xG")

ax.scatter(
    top5["G"],
    y,
    s=90,
    color=red,
    edgecolors=bg,
    linewidths=1.5,
    zorder=3,
    label="Open-play Goals",
)

for i, (g, xg, nshots, diff) in enumerate(
    zip(top5["G"], top5["xG"], top5["every_n_shots"], top5["G_minus_xG"])
):
    if np.isfinite(nshots):
        txt = f"1 goal per {int(nshots)} shots"
    else:
        txt = "no goals yet"
    sign = "+" if diff >= 0 else ""
    ax.text(
        max(g, xg) + 0.15,
        i,
        f"{txt}   ({sign}{diff:.2f})",
        va="center",
        ha="left",
        color=fg,
        fontsize=10,
    )

ax.set_yticks(y)
ax.set_yticklabels(top5["rank_label"], color=fg, fontsize=12)
ax.invert_yaxis()

ax.grid(axis="x", color=grid, linewidth=1, alpha=0.7)
ax.set_axisbelow(True)
ax.tick_params(axis="x", colors=fg)
for spine in ax.spines.values():
    spine.set_color(grid)

title = "Top 5 Open-Play Goalscoring (ranked by xG)"
desc = "Cyan bar = open-play xG. Red dot = open-play goals. Right text shows conversion and finishing (G−xG)."
fig.text(0.08, 0.94, title, color=fg, fontsize=17, fontweight="bold")
fig.text(0.08, 0.905, desc, color=teal, fontsize=10)

ax.set_xlabel("Open-play output", color=fg, fontsize=11)

out_path = FIG_DIR / "open_play_top5_clean.png"

plt.tight_layout(rect=[0.06, 0.06, 0.98, 0.88])

leg = ax.legend(
    loc="lower right",
    bbox_to_anchor=(1.0, 0.0),
    bbox_transform=ax.transAxes,
    borderaxespad=0.0,
    facecolor=bg,
    edgecolor=grid,
    framealpha=0.9,
)
for t in leg.get_texts():
    t.set_color(fg)

fig.savefig(out_path, dpi=220, facecolor=bg, bbox_inches="tight")
plt.close(fig)

print(out_path)
