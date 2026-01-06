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

def fmt_team(name: str) -> str:
    name = str(name)
    if name.lower() == "bournemouth":
        return "BOURNEMOUTH"
    return name

bg = "#0b0f14"
fg = "#e8eef5"
grid = "#1f2a37"
red = "#ff8389"
purple = "#be95ff"
cyan = "#33b1ff"
teal = "#4aa3a3"

need = ["team", "Situation", "Sh", "G", "ShA", "GA"]
missing = [c for c in need if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns in team_by_situation_long.csv: {missing}")

# -------------------- PENALTIES (Top 5 scored) — stacked goals + misses --------------------
pen = df[df["Situation"].str.lower().eq("penalty")].copy()
if pen.empty:
    raise ValueError("No rows found for Situation == 'Penalty'")

pen["team_fmt"] = pen["team"].map(fmt_team)
pen["misses"] = (pen["Sh"] - pen["G"]).clip(lower=0)
pen["conv_pct"] = np.where(pen["Sh"] > 0, 100 * pen["G"] / pen["Sh"], np.nan)

top5 = (
    pen.sort_values(["G", "Sh"], ascending=[False, False])
    .head(5)
    .copy()
    .reset_index(drop=True)
)

top5["rank_label"] = (top5.index + 1).astype(str) + ". " + top5["team_fmt"]

y = np.arange(len(top5))

fig = plt.figure(figsize=(11, 6.5), facecolor=bg)
ax = fig.add_subplot(111, facecolor=bg)

ax.barh(y, top5["G"], color=cyan, height=0.55, label="Goals")
ax.barh(y, top5["misses"], left=top5["G"], color=purple, height=0.55, label="Misses")

for i, (g, sh, miss, pct) in enumerate(zip(top5["G"], top5["Sh"], top5["misses"], top5["conv_pct"])):
    ax.text(sh + 0.12, i, f"{int(g)}/{int(sh)}  ({pct:.0f}%)", va="center", ha="left", color=fg, fontsize=10)
    if miss > 0 and miss >= 1:
        ax.text(g + miss / 2, i, f"{int(miss)}", va="center", ha="center", color=bg, fontsize=10, fontweight="bold")

ax.set_yticks(y)
ax.set_yticklabels(top5["rank_label"], color=fg, fontsize=12)
ax.invert_yaxis()

ax.grid(axis="x", color=grid, linewidth=1, alpha=0.7)
ax.set_axisbelow(True)
ax.tick_params(axis="x", colors=fg)
for s in ax.spines.values():
    s.set_color(grid)

title = "Penalties: Top 5 Scorers"
desc = "Stacked bar = attempts (goals + misses). Right text shows goals/attempts and conversion."
fig.text(0.08, 0.94, title, color=fg, fontsize=17, fontweight="bold")
fig.text(0.08, 0.905, desc, color=teal, fontsize=10)

ax.set_xlabel("Penalty attempts", color=fg, fontsize=11)

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

out_path = FIG_DIR / "penalties_top5_scorers_stacked.png"
fig.savefig(out_path, dpi=220, facecolor=bg, bbox_inches="tight")
plt.close(fig)

print(out_path)

# -------------------- DIRECT FREE KICKS (keep same as before) --------------------
dfk = df[df["Situation"].str.lower().eq("direct freekick")].copy()
if dfk.empty:
    raise ValueError("No rows found for Situation == 'Direct Freekick'")

dfk["team_fmt"] = dfk["team"].map(fmt_team)
dfk["conv"] = np.where(dfk["Sh"] > 0, dfk["G"] / dfk["Sh"], np.nan)

dfk_ranked = dfk.sort_values(
    ["conv", "G", "Sh"],
    ascending=[True, True, False]
).head(5).copy().reset_index(drop=True)

dfk_ranked["rank_label"] = (dfk_ranked.index + 1).astype(str) + ". " + dfk_ranked["team_fmt"]

y = np.arange(len(dfk_ranked))

fig = plt.figure(figsize=(11, 6.5), facecolor=bg)
ax = fig.add_subplot(111, facecolor=bg)

ax.barh(y, dfk_ranked["Sh"], color=cyan, height=0.55, label="Direct free-kick shots")
ax.scatter(
    dfk_ranked["G"],
    y,
    s=90,
    color=red,
    edgecolors=bg,
    linewidths=1.5,
    zorder=3,
    label="Direct free-kick goals",
)

for i, (sh, g) in enumerate(zip(dfk_ranked["Sh"], dfk_ranked["G"])):
    if g > 0:
        n = int(np.rint(sh / g))
        txt = f"{int(g)} goals from {int(sh)} shots  •  1 goal per {n} shots"
    else:
        txt = f"0 goals from {int(sh)} shots"
    ax.text(max(sh, g) + 0.15, i, txt, va="center", ha="left", color=fg, fontsize=10)

ax.set_yticks(y)
ax.set_yticklabels(dfk_ranked["rank_label"], color=fg, fontsize=12)
ax.invert_yaxis()

ax.grid(axis="x", color=grid, linewidth=1, alpha=0.7)
ax.set_axisbelow(True)
ax.tick_params(axis="x", colors=fg)
for s in ax.spines.values():
    s.set_color(grid)

title = "Direct Free Kicks: Most Wasteful Teams (Worst 5)"
desc = "Ranked by goals-per-shot (lowest first). Big shot volume with 0 goals rises to the top."
fig.text(0.08, 0.94, title, color=fg, fontsize=17, fontweight="bold")
fig.text(0.08, 0.905, desc, color=teal, fontsize=10)

ax.set_xlabel("Shots (bar) and goals (dot)", color=fg, fontsize=11)

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

out_path = FIG_DIR / "direct_freekicks_worst5_wasteful.png"
fig.savefig(out_path, dpi=220, facecolor=bg, bbox_inches="tight")
plt.close(fig)

print(out_path)
