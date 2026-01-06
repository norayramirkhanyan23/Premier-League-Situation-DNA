# Premier League Situation DNA

A visual breakdown of how Premier League teams score across different situations.

Instead of only looking at total goals, this project splits scoring into:
- Open play
- Set pieces (corners + indirect)
- Penalties
- Direct free kicks

Source: Understat (data up to Matchday 21).

## What’s inside

### Core outputs
- League map: Open-play goals vs set-piece goals (bubble size = total goals)
- Open play Top 5: xG vs goals + conversion context
- Set pieces Top 5: scored and conceded
- Penalties Top 5: attempts split into goals vs misses
- Direct free kicks: most wasteful teams (high shots, low goals)
- Team DNA cards: one chart per team (Goals For vs Goals Against split by situation)

All generated figures are saved to `outputs/figures/`.

## Repo structure
```text
data/                     # raw team CSVs
outputs/
  tables/                 # cleaned tables
  figures/                # generated charts
src/                      # scripts
