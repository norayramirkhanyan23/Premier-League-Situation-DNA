import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
OUT_TABLES.mkdir(parents=True, exist_ok=True)

SET_PIECE_SITUATIONS = {"From corner", "Set piece", "Direct Freekick", "Penalty"}

TEAM_NAME_MAP = {
    "arsenal": "Arsenal",
    "mancity": "Manchester City",
    "aston villa": "Aston Villa",
    "liverpool": "Liverpool",
    "chelsea": "Chelsea",
    "mu": "Manchester United",
    "brentford": "Brentford",
    "sunderland": "Sunderland",
    "newcastle": "Newcastle United",
    "brighton": "Brighton",
    "fulham": "Fulham",
    "everton": "Everton",
    "spurs": "Tottenham",
    "crystal palace": "Crystal Palace",
    "bournemouth": "Bournemouth",
    "leeds": "Leeds",
    "nf": "Nottingham Forest",
    "westham": "West Ham",
    "burnley": "Burnley",
    "wolves": "Wolverhampton Wanderers",
}

RENAME_COLS = {
    "statistic": "Situation",
    "shots": "Sh",
    "goals": "G",
    "shots_against": "ShA",
    "goals_against": "GA",
    "xg": "xG",
    "xga": "xGA",
    "xg_diff": "xGD",
    "xgpersh": "xG/Sh",
    "xgapersh": "xGA/Sh",
}

files = sorted(DATA_DIR.glob("*.csv"))
if not files:
    raise FileNotFoundError(f"No CSV files found in: {DATA_DIR}")

dfs = []
for f in files:
    team_key = f.stem.strip().lower()
    team = TEAM_NAME_MAP.get(team_key, f.stem.strip())

    df = pd.read_csv(f, sep=";", quotechar='"', encoding="utf-8-sig")
    df.columns = [str(c).strip() for c in df.columns]

    lower_map = {c: str(c).strip().lower() for c in df.columns}
    df = df.rename(columns={c: lower_map[c] for c in df.columns})
    df = df.rename(columns=RENAME_COLS)

    required = ["Situation", "Sh", "G", "ShA", "GA", "xG", "xGA"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{f.name} missing columns: {missing}. Found: {list(df.columns)}")

    if "number" in df.columns:
        df = df.drop(columns=["number"])

    num_cols = [c for c in df.columns if c not in ["Situation"]]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["team"] = team
    dfs.append(df)

data = pd.concat(dfs, ignore_index=True)

team_totals = data.groupby("team", as_index=False).agg(
    Sh=("Sh", "sum"),
    G=("G", "sum"),
    ShA=("ShA", "sum"),
    GA=("GA", "sum"),
    xG=("xG", "sum"),
    xGA=("xGA", "sum"),
)

team_totals["finishing_G_minus_xG"] = team_totals["G"] - team_totals["xG"]
team_totals["prevention_xGA_minus_GA"] = team_totals["xGA"] - team_totals["GA"]

sp = (
    data[data["Situation"].isin(SET_PIECE_SITUATIONS)]
    .groupby("team", as_index=False)
    .agg(sp_xG=("xG", "sum"), sp_xGA=("xGA", "sum"))
)

team_totals = team_totals.merge(sp, on="team", how="left").fillna({"sp_xG": 0, "sp_xGA": 0})
team_totals["sp_dependency"] = team_totals["sp_xG"] / team_totals["xG"].replace({0: pd.NA})
team_totals["sp_vulnerability"] = team_totals["sp_xGA"] / team_totals["xGA"].replace({0: pd.NA})

data["xG_share"] = data["xG"] / data.groupby("team")["xG"].transform("sum")
data["xGA_share"] = data["xGA"] / data.groupby("team")["xGA"].transform("sum")

team_totals.to_csv(OUT_TABLES / "team_totals.csv", index=False)
data.to_csv(OUT_TABLES / "team_by_situation_long.csv", index=False)

print("outputs/tables/team_totals.csv")
print("outputs/tables/team_by_situation_long.csv")
