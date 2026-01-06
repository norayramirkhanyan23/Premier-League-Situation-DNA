import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
FIG_DIR = PROJECT_ROOT / "outputs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

bg = "#0b0f14"
fg = "#e8eef5"
grid = "#1f2a37"
cyan = "#33b1ff"
purple = "#be95ff"
teal = "#4aa3a3"

df = pd.read_csv(TABLES_DIR / "team_by_situation_long.csv")
df["Situation"] = df["Situation"].astype(str).str.strip()
df["team"] = df["team"].astype(str).str.strip()

need = ["team", "Situation", "G", "Sh"]
missing = [c for c in need if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns in team_by_situation_long.csv: {missing}")

def fmt_team(name: str) -> str:
    name = str(name).strip()
    if name.lower() == "bournemouth":
        return "BOURNEMOUTH"
    return name.title()

def norm_situation(s: str) -> str:
    s = str(s).strip().lower()
    if s == "open play":
        return "Open play"
    if s in {"from corner", "set piece"}:
        return "Set pieces"
    return s.title()

df["SituationGroup"] = df["Situation"].map(norm_situation)

agg = df.groupby(["team", "SituationGroup"], as_index=False).agg(
    G=("G", "sum"),
    Sh=("Sh", "sum"),
)

pivot_g = agg.pivot_table(index="team", columns="SituationGroup", values="G", fill_value=0.0)
pivot_sh = agg.pivot_table(index="team", columns="SituationGroup", values="Sh", fill_value=0.0)

for col in ["Open play", "Set pieces"]:
    if col not in pivot_g.columns:
        pivot_g[col] = 0.0
    if col not in pivot_sh.columns:
        pivot_sh[col] = 0.0

out = pd.DataFrame({
    "team": pivot_g.index,
    "open_play_goals": pivot_g["Open play"].astype(float).values,
    "set_piece_goals": pivot_g["Set pieces"].astype(float).values,
    "open_play_shots": pivot_sh["Open play"].astype(float).values,
    "set_piece_shots": pivot_sh["Set pieces"].astype(float).values,
})
out["total_goals"] = out["open_play_goals"] + out["set_piece_goals"]
out["team_fmt"] = out["team"].map(fmt_team)

# bubble sizes
sizes = 180 + 55 * out["total_goals"].to_numpy()
sizes = np.clip(sizes, 200, 650)

# axis limits
xmax = max(out["open_play_goals"].max(), 1) * 1.12
ymax = 25

# label selection: always include these clubs + a few extremes
must_label = {
    "Arsenal",
    "Aston Villa",
    "Liverpool",
    "Manchester City",
    "Manchester United",
}

out["ratio_sp"] = np.where(out["total_goals"] > 0, out["set_piece_goals"] / out["total_goals"], 0.0)
out["skew"] = (out["open_play_goals"] - out["set_piece_goals"]).abs()

label_idx = set()

# forced clubs
for i, t in enumerate(out["team_fmt"].tolist()):
    if t in must_label:
        label_idx.add(i)

# add a few extremes so it stays informative
label_idx.update(out.sort_values("open_play_goals", ascending=False).head(2).index.tolist())
label_idx.update(out.sort_values("set_piece_goals", ascending=False).head(2).index.tolist())
label_idx.update(out.sort_values("ratio_sp", ascending=False).head(1).index.tolist())
label_idx.update(out.sort_values("skew", ascending=False).head(1).index.tolist())

label_df = out.loc[sorted(label_idx)].copy()

fig = plt.figure(figsize=(11.8, 7.2), facecolor=bg)
ax = fig.add_subplot(111, facecolor=bg)

ax.scatter(
    out["open_play_goals"],
    out["set_piece_goals"],
    s=sizes,
    color=cyan,
    edgecolors=purple,
    linewidths=1.8,
    alpha=0.95,
    zorder=3,
)

# balanced reference line
m = min(xmax, ymax)
x = np.linspace(0, m, 200)
ax.plot(x, x, color=grid, linewidth=1.2, alpha=0.9)

# mean guides
ax.axvline(out["open_play_goals"].mean(), color=grid, linewidth=1, alpha=0.55)
ax.axhline(out["set_piece_goals"].mean(), color=grid, linewidth=1, alpha=0.55)

# labels
for _, r in label_df.iterrows():
    ax.text(
        r["open_play_goals"] + 0.35,
        r["set_piece_goals"] + 0.20,
        r["team_fmt"],
        color=fg,
        fontsize=10.5,
        ha="left",
        va="bottom",
        zorder=4,
    )

ax.set_xlim(0, xmax)
ax.set_ylim(0, ymax)
ax.set_yticks([0, 5, 10, 15, 20, 25])

ax.grid(color=grid, linewidth=1, alpha=0.65)
ax.set_axisbelow(True)
ax.tick_params(axis="both", colors=fg)
for s in ax.spines.values():
    s.set_color(grid)

title = "Open Play vs Set Pieces"
desc = "Dots = teams. Bubble size = total goals (open play + set pieces). Labels include key clubs + extremes."
fig.text(0.07, 0.95, title, color=fg, fontsize=20, fontweight="bold")
fig.text(0.07, 0.915, desc, color=teal, fontsize=10)

ax.set_xlabel("Open-play goals", color=fg, fontsize=12)
ax.set_ylabel("Set-piece goals (corners + set pieces)", color=fg, fontsize=12)

ax.text(0.02, 0.98, "↑ More set-piece dependent", transform=ax.transAxes, color=teal, fontsize=10, va="top")
ax.text(0.98, 0.03, "→ More open-play dependent", transform=ax.transAxes, color=teal, fontsize=10, ha="right")

plt.tight_layout(rect=[0.05, 0.06, 0.98, 0.88])

out_path = FIG_DIR / "league_map_openplay_vs_setpieces_final.png"
fig.savefig(out_path, dpi=220, facecolor=bg, bbox_inches="tight")
plt.close(fig)

print(out_path)
