# Portfolio Case Study: Predicting World Cup Success

## Problem

World Cup debates often jump straight to predictions, but most prediction claims are too confident for the amount of data available. This project asks a narrower and more defensible question: which measurable team-level factors are most associated with deep World Cup runs?

## Data

The analysis combines the Fjelstul World Cup Database for tournament history with international match results from Mart Jurriaans' dataset for pre-tournament form. A separate 2026 preview table verifies the expanded 48-team field and groups from current public sources.

## Method

I built a reproducible SQL and Python pipeline that cleans team names, validates match records, aggregates team-tournament performance, flags hosts, labels champions/finalists/semifinalists, calculates historical experience using only past tournaments, and computes recent form before each tournament starts.

## Tools

Python, pandas, DuckDB SQL, matplotlib, Plotly, Streamlit, pytest, and Make.

## Findings

Goal difference has the strongest descriptive relationship with stage reached. Champions also concede fewer goals per match than the overall field, and host teams have historically advanced deeper on average. Pre-tournament form adds useful context, but it is noisy and should not be treated as a standalone predictor.

## What I Learned

The most important analytics decision was avoiding data leakage. Experience features must use only prior tournaments, and recent form must exclude World Cup matches. This constraint made the analysis more credible even though it made the feature engineering more careful.

## Why This Demonstrates Data Analyst Skills

The project shows end-to-end analytical work: sourcing public data, documenting limitations, designing SQL transformations, engineering defensible features, testing the pipeline, building charts tied to conclusions, and presenting the results in an interactive dashboard.

## Resume Bullet

Built a World Cup performance analytics project using SQL, Python, and Streamlit, engineering team-level features from historical match data to analyze how goal difference, defensive strength, host advantage, tournament experience, and recent form relate to deep tournament runs.
