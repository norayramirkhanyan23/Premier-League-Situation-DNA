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

SITUATIONS = {"From corner", "Set piece"}
sp = df[df["Situation"].isin(SITUATIONS)].copy()

need = ["team", "Sh", "G", "ShA", "GA", "xG", "xGA"]
missing = [c for c in need if c not in sp.columns]
if missing:
    raise ValueError(f"Missing columns in team_by_situation_long.csv: {missing}")

def fmt_team(name: str) -> str:
    name = str(name)
    if name.lower() == "bournemouth":
        return "BOURNEMOUTH"
    return name

bg = "#0b0f14"
fg = "#e8eef5"
grid = "#1f2a37"
red = "#ff8389"
cyan = "#33b1ff"
teal = "#4aa3a3"

attack = sp.groupby("team", as_index=False).agg(
    Sh=("Sh", "sum"),
    G=("G", "sum"),
    xG=("xG", "sum"),
)

defense = sp.groupby("team", as_index=False).agg(
    ShA=("ShA", "sum"),
    GA=("GA", "sum"),
    xGA=("xGA", "sum"),
)

def add_rate_cols_attack(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["shots_per_goal"] = np.where(d["G"] > 0, d["Sh"] / d["G"], np.inf)
    d["every_n_shots"] = np.where(
        np.isfinite(d["shots_per_goal"]),
        np.rint(d["shots_per_goal"]).astype(int),
        np.nan,
    )
    return d

def add_rate_cols_defense(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["shotsA_per_goalA"] = np.where(d["GA"] > 0, d["ShA"] / d["GA"], np.inf)
    d["every_n_shotsA"] = np.where(
        np.isfinite(d["shotsA_per_goalA"]),
        np.rint(d["shotsA_per_goalA"]).astype(int),
        np.nan,
    )
    return d

attack = add_rate_cols_attack(attack)
defense = add_rate_cols_defense(defense)

def make_chart_top5(
    data: pd.DataFrame,
    rank_col: str,
    bar_col: str,
    dot_col: str,
    title: str,
    desc: str,
    bar_label: str,
    dot_label: str,
    right_text_fn,
    out_name: str,
    xlabel: str,
):
    top5 = (
        data.sort_values(rank_col, ascending=False)
        .head(5)
        .copy()
        .reset_index(drop=True)
    )
    top5["team_fmt"] = top5["team"].map(fmt_team)
    top5["rank_label"] = (top5.index + 1).astype(str) + ". " + top5["team_fmt"].astype(str)

    y = np.arange(len(top5))

    fig = plt.figure(figsize=(11, 6.5), facecolor=bg)
    ax = fig.add_subplot(111, facecolor=bg)

    ax.barh(y, top5[bar_col], color=cyan, height=0.55, label=bar_label)

    ax.scatter(
        top5[dot_col],
        y,
        s=90,
        color=red,
        edgecolors=bg,
        linewidths=1.5,
        zorder=3,
        label=dot_label,
    )

    for i in range(len(top5)):
        b = float(top5.iloc[i][bar_col])
        d = float(top5.iloc[i][dot_col])
        txt = right_text_fn(top5.iloc[i])
        ax.text(
            max(b, d) + 0.15,
            i,
            txt,
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

    fig.text(0.08, 0.94, title, color=fg, fontsize=17, fontweight="bold")
    fig.text(0.08, 0.905, desc, color=teal, fontsize=10)

    ax.set_xlabel(xlabel, color=fg, fontsize=11)

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

    out_path = FIG_DIR / out_name
    fig.savefig(out_path, dpi=220, facecolor=bg, bbox_inches="tight")
    plt.close(fig)

    print(out_path)

def right_text_scored(row):
    n = row["every_n_shots"]
    if np.isfinite(n):
        rate = f"1 goal per {int(n)} shots"
    else:
        rate = "no goals yet"
    return f"{rate}   xG {row['xG']:.2f}"

def right_text_conceded(row):
    n = row["every_n_shotsA"]
    if np.isfinite(n):
        rate = f"1 conceded per {int(n)} shots"
    else:
        rate = "no goals conceded"
    return f"{rate}   xGA {row['xGA']:.2f}"

make_chart_top5(
    data=attack,
    rank_col="G",
    bar_col="G",
    dot_col="xG",
    title="Corners + Set Pieces: Goals Scored",
    desc="Cyan bar = goals. Red dot = xG (reference). Right text shows goals per shot.",
    bar_label="Goals",
    dot_label="xG",
    right_text_fn=right_text_scored,
    out_name="setpiece_corners_top5_scored.png",
    xlabel="Goals (bar) and xG (dot)",
)

make_chart_top5(
    data=defense,
    rank_col="GA",
    bar_col="GA",
    dot_col="xGA",
    title="Corners + Set Pieces: Goals Conceded",
    desc="Cyan bar = goals conceded. Red dot = xGA (reference). Right text shows conceded per shot.",
    bar_label="Goals Conceded",
    dot_label="xGA",
    right_text_fn=right_text_conceded,
    out_name="setpiece_corners_top5_conceded.png",
    xlabel="Goals conceded (bar) and xGA (dot)",
)
