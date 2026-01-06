# Premier League Situation DNA Report

## Overview
This project explores how Premier League teams score, not only how many goals they score.  
Instead of treating goals as one bucket, I split team output by situation and built a visual package that highlights different scoring profiles across the league.

Situations included:
- Open play
- Set pieces (corners + indirect set pieces)
- Penalties
- Direct free kicks

Data source: Understat  
Coverage: up to Matchday 21

## Data and Pipeline
The workflow is simple and reproducible.

1) Raw CSVs (per team)  
Each club has a CSV file placed in `data/`.

2) Build tables (`src/01_build_tables.py`)  
All team CSVs are cleaned, standardized, and merged into:
- `outputs/tables/team_totals.csv` (team totals)
- `outputs/tables/team_by_situation_long.csv` (long-format situation table used for charts)

3) Visual outputs (`src/*.py`)  
Each chart reads the long-format table and exports images to `outputs/figures/`.

## Visual Outputs

### 1) League Map: Open Play vs Set Pieces
File: `outputs/figures/league_map_openplay_vs_setpieces_final.png`

A league-level overview of scoring styles:
- x-axis: Open-play goals
- y-axis: Set-piece goals (corners + set pieces)
- bubble size: total goals (open play + set pieces)

Interpretation:
- Teams far to the right are open-play heavy.
- Teams higher up are set-piece heavy.
- The map makes it easy to compare style differences quickly.

### 2) Open Play Top 5 (xG vs Goals plus conversion context)
File: `outputs/figures/open_play_top5_clean.png`

Highlights the strongest open-play attacking teams:
- bar: open-play xG
- dot: open-play goals
- text: conversion context (example: 1 goal per N shots) and finishing vs expectation (Goals minus xG)

Interpretation:
- High xG teams are consistently creating chances.
- The gap between goals and xG helps spot over or under finishing runs.

### 3) Set Pieces Top 5 Scored
File: `outputs/figures/setpiece_corners_top5_scored.png`

Shows which teams produce the most output from dead balls:
- bar: set-piece goals
- dot: xG reference (context only)

Interpretation:
- Set pieces are a major advantage this season.
- Teams strong in this area often appear near the top of the table.

### 4) Set Pieces Top 5 Conceded
File: `outputs/figures/setpiece_corners_top5_conceded.png`

Identifies weaknesses:
- bar: set-piece goals conceded
- dot: xGA reference

Interpretation:
- Set-piece defending is a separator and poor teams here tend to struggle overall.

### 5) Penalties: Top 5 Scorers
File: `outputs/figures/penalties_top5_scorers_stacked.png`

Shows penalty volume and efficiency:
- stacked bar: attempts = goals + misses
- right text: goals/attempts and conversion percentage

Interpretation:
- Some teams generate more penalty volume.
- The split makes it clear whether they are efficient or wasting attempts.

### 6) Direct Free Kicks: Most Wasteful Teams (Worst 5)
File: `outputs/figures/direct_freekicks_worst5_wasteful.png`

Designed to highlight extreme cases like many shots with zero goals:
- bar: direct free-kick shots
- dot: direct free-kick goals
- ranking: lowest goals-per-shot first, with high-shot 0-goal teams rising to the top

Interpretation:
- Direct free kicks are low-yield for most teams.
- High shot volume with low output is a clear inefficiency signal.

### 7) Team Situation DNA Cards
Folder: `outputs/figures/team_dna/`

One card per team:
- two stacked bars: Goals For and Goals Against
- colors represent situations (open play, set pieces, penalties, direct free kicks)

Interpretation:
- These cards act like a quick scouting snapshot.
- You can instantly see if a team is open-play heavy, set-piece dependent, or leaking goals in specific situations.

## Key Takeaways
- Set pieces are a real separator this season. Teams that consistently perform well on dead balls often trend toward the top, while teams that struggle on them tend to suffer overall.
- Open-play creation does not always match results. Some teams generate strong xG but convert poorly, showing how finishing variance can distort narratives.
- Direct free kicks are low-yield for most teams. The wasteful chart shows how frequently teams take many attempts with almost no return.
- Team DNA cards are the best single summary because they combine attacking and defensive situation splits into one snapshot.

## How to Reproduce
From the project root:

```bash
pip install -r requirements.txt
python src/01_build_tables.py
python src/02_open_play.py
python src/03_set_piece_corners_top5.py
python src/04_pens_dfk.py
python src/05_dna.py
python src/06_league_map.py
