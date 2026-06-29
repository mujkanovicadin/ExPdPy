---
title: Convergence for Whom
emoji: 📊
colorFrom: blue
colorTo: teal
sdk: streamlit
sdk_version: 1.35.0
app_file: app.py
pinned: false
---

# Convergence for Whom?
### Club Formation and Persistent Inequality in the Post-Yugoslav Space

**Adin Mujkanovic · Nagoya University GSID · Supervised by Prof. Carlos Mendez**

This app visualises regional economic convergence across 71 subnational regions
of the seven ex-Yugoslav successor states (Slovenia, Croatia, Bosnia and
Herzegovina, Serbia, Montenegro, North Macedonia, and Kosovo) over 2000–2022.

## Features
- **Beta convergence** — scatter of initial GDP vs. growth with OLS fit, speed λ, and half-life
- **Sigma convergence** — cross-sectional standard deviation and Gini index over time
- **Club convergence** — Phillips-Sul transition paths per club
- **Club membership** — summary table and region list per club

## Data
Place `panel_club_convergence.csv` in the repo root. Required columns:
- `year` — time identifier
- `region_num` — region identifier
- `ln_gdp_pc` — log GDP per capita
- `club` (or any column containing "club") — club assignment from Phillips-Sul

## Reference
Phillips, P. C. B., & Sul, D. (2007). Transition modeling and econometric convergence tests.
*Econometrica*, 75(6), 1771–1855.
