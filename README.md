# Predicting World Cup Success

## A SQL and Python Analysis of What Makes National Teams Win

This project investigates which measurable factors are most associated with deep FIFA Men's World Cup runs. It is not built to pretend that football can be predicted perfectly. The goal is more practical: use public data, SQL, Python, and clear visual evidence to understand the patterns behind teams that reach the knockout rounds, semifinals, finals, and title.

## Links

- Live portfolio report: https://world-cup-success-analysis.vercel.app
- GitHub repository: https://github.com/ymbawa26/world-cup-success-analysis

## Research Question

Which factors are most associated with World Cup success: goal difference, defensive strength, attacking output, host advantage, tournament experience, confederation/region, knockout-stage efficiency, or pre-tournament form?

## Why This Matters

World Cup analysis often relies on reputation, star players, or vague narratives. A data analyst's job is to separate what the data supports from what it cannot prove. This project turns historical match records into team-level tournament features and tests whether the common explanations for success actually show up in the data.

## Tools Used

- Python: pandas, numpy
- SQL: DuckDB
- Visualization: matplotlib, Plotly
- Dashboard: Streamlit
- Testing: pytest
- Reproducibility: Makefile, requirements.txt

## Data Sources

- Fjelstul World Cup Database: https://github.com/jfjelstul/worldcup
- Mart Jurriaans international results dataset: https://github.com/martj42/international_results
- OpenFootball 2026 groups: https://github.com/openfootball/worldcup/blob/master/2026--usa/cup.txt
- FIFA 2026 group and qualified-team verification:
  - https://www.fifa.com/en/articles/groups-how-teams-qualify-tie-breakers
  - https://www.fifa.com/de/articles/wm-2026-qualifizierte-teams
- Secondary 2026 cross-check: https://www.china.org.cn/2026-04/01/content_118413831.shtml

The 2026 field is included as a preview table only. No 2026 World Cup match results are used because the tournament has not been played yet.

## Project Structure

```text
world-cup-success-analysis/
├── data/
│   ├── raw/
│   └── processed/
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_cleaning_queries.sql
│   ├── 03_feature_engineering.sql
│   └── 04_analysis_queries.sql
├── notebooks/
│   └── world_cup_analysis.ipynb
├── src/
│   ├── load_data.py
│   ├── clean_data.py
│   ├── run_sql_analysis.py
│   ├── visualize.py
│   └── app.py
├── tests/
├── charts/
├── app/
│   ├── assets/
│   └── dashboard.py
├── README.md
├── portfolio_summary.md
├── requirements.txt
├── .gitignore
└── Makefile
```

## Methodology

The pipeline starts with raw World Cup match and team-appearance data, then standardizes team names, parses dates, validates goals and outcomes, and aggregates each team in each tournament. SQL then creates analysis-ready views for team performance, host advantage, historical experience, 2026 preview rankings, stage summaries, and confederation comparisons.

Pre-tournament form is calculated from international matches in the 365 days before each World Cup start date. FIFA World Cup matches are explicitly excluded from this calculation so the feature does not leak tournament results into a pre-tournament signal.

Historical experience is calculated with cumulative features by team, using only tournaments that happened before the current tournament.

## SQL Analysis Summary

The SQL files create clean tables, validation views, and analysis views for:

- wins, losses, draws, goals for, goals against, and goal difference
- champions, finalists, semifinalists, and knockout-stage teams
- host advantage
- historical World Cup experience before each tournament
- pre-tournament form
- country, stage, and confederation summaries
- a verified 48-team 2026 preview table

## Key Findings

Goal difference is the strongest descriptive factor in this dataset. The correlation between stage score and goal difference is about `0.73`, higher than attacking output, defensive goals conceded, historical experience, or recent form.

Deeper runs are associated with a clear goal-difference ladder. Group-stage teams average about `-2.90` goal difference, finalists average about `6.32`, and champions average about `9.73`.

Defense matters. Champions concede about `0.78` goals per match on average, compared with `1.93` for group-stage teams. This suggests title-winning teams usually combine attacking separation with a strong defensive floor.

Host teams have historically performed better, but this is association, not causation. Hosts average a stage score of `3.87` versus `2.10` for non-hosts, with a much higher semifinal rate. That pattern can reflect crowd support, travel, familiarity, and team quality.

Pre-tournament form is useful context but not a clean predictor. Its correlation with stage score is about `0.22`, which suggests a positive but noisy relationship.

Confederation differences are visible. CONMEBOL and UEFA have the highest average stage scores in the historical dataset. This pattern should be interpreted carefully because tournament formats, qualification paths, and global football depth have changed over time.

## 2026 World Cup Preview

The project includes a verified 2026 field table with `48` teams across `12` groups. The dashboard compares qualified teams using only historical results and pre-tournament form available before the tournament.

The 2026 preview is not a prediction of the winner. It is a context layer for the expanded tournament field.

## Baseline Model

The project includes a simple leakage-safe logistic regression baseline for estimating whether a team reaches the semifinals/top four. The model trains on tournaments from `1966-2006` and tests on `2010-2022`.

Features are limited to information available before or during the team-tournament context without using future tournaments:

- host flag
- historical World Cup experience before the tournament
- historical best stage before the tournament
- pre-tournament form
- confederation

Current held-out accuracy is about `0.719`. This is not presented as a betting model or a winner predictor. It is a baseline for showing how engineered features can be evaluated without data leakage.

Model outputs are exported to:

- `data/processed/baseline_model_predictions.csv`
- `data/processed/baseline_model_feature_importance.csv`
- `data/processed/baseline_model_confusion_matrix.csv`
- `data/processed/baseline_model_summary.csv`

## Visualizations

Generated chart outputs are saved in `charts/`:

- World Cup titles by country
- Finals reached by country
- Average goal difference by tournament stage reached
- Host country performance compared to non-host performance
- Goals scored vs goals conceded for successful teams
- Defensive strength of champions vs non-champions
- Pre-tournament form vs World Cup performance
- Top overperforming team-tournament runs
- Team performance over time
- Confederation performance comparison
- 2026 qualified-team historical title comparison

Each chart is tied to a specific analytical question rather than being decorative.

## Dashboard

Run the dashboard with:

```bash
make app
```

The Streamlit app includes:

- Overview KPIs
- Team explorer
- Factor analysis
- Side-by-side country comparison
- 2026 qualified-team preview
- Leakage-safe baseline model page
- Written insights and limitations

## Testing

Run:

```bash
pytest
```

or:

```bash
make test
```

The tests cover:

- data loading and required columns
- duplicate handling
- team-name standardization
- date parsing
- numeric goal fields
- missing-score handling
- match outcome calculations
- SQL table/view creation
- aggregate win/loss/draw/goal calculations
- impossible records such as negative goals
- host advantage flags
- champion/finalist/semifinalist labels
- historical experience without future leakage
- pre-tournament form without World Cup result leakage
- 2026 field size validation

Current test status: `11 passed`.

## How To Run Locally

```bash
make setup
make run
make test
make app
```

If you prefer to run steps manually:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/clean_data.py
.venv/bin/python src/run_sql_analysis.py
.venv/bin/python src/visualize.py
.venv/bin/python -m pytest
.venv/bin/python -m streamlit run app/dashboard.py
```

## Limitations

World Cup formats have changed across eras, so stage labels are normalized into a stage-score scale. This makes long-run comparison possible but imperfect.

The analysis does not include player-level quality, injuries, tactics, squad age, Elo ratings, betting markets, or draw difficulty. Those would improve a predictive model but are outside the core public datasets used here.

Pre-tournament form depends on available international match records and does not adjust for opponent strength. It is useful context, not a complete rating system.

Some country names changed over time. The pipeline standardizes common naming differences, but historical national-team continuity is analytically complicated.

## What This Does Not Prove

This project does not prove that any single factor causes World Cup success. It shows associations in historical data. It also does not claim to predict the 2026 winner. Football tournaments are short, high-variance events, and team-level historical features cannot fully capture matchups, tactics, player availability, or chance.

## Future Improvements

- Add Elo ratings or FIFA rankings as pre-tournament strength features
- Adjust pre-tournament form for opponent quality
- Add calibrated probabilities and compare the baseline model with Elo/FIFA-ranking baselines
- Add player-level squad features such as age, minutes, and club strength
- Add draw difficulty and travel distance for 2026

## Portfolio Summary

See `portfolio_summary.md` for a concise case-study version and resume bullet.
