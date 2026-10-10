# Statistical Experimentation Lab

An interactive Streamlit app for learning how randomness affects A/B tests and
for analyzing the Cookie Cats mobile-game experiment.

## Run locally

From the project directory:

```bash
python -m venv .venv
```

Activate the environment, then install the project dependencies and start the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## App sections

- **Overview** — project introduction and a quick view of the Cookie Cats data.
- **Single experiment** — simulate an A/B test with configurable conversion
  rates, sample size, significance threshold, and random seed. View observed
  rates, Wilson confidence intervals, and a two-proportion z-test.
- **Simulation lab** — explore sampling distributions, false-positive rates,
  statistical power, optional stopping, and multiple-testing inflation.
- **Cookie Cats study** — compare gate-at-level-30 and gate-at-level-40 players
  on day-1 retention, day-7 retention, and game rounds. Retention uses
  two-proportion z-tests; the skewed game-round counts use a Mann–Whitney U test.
  Holm adjustment is applied across the three outcomes.

The included data is `data/cookie_cats.csv`. The simulation helpers in
`src/simulation.py` can also be imported into notebooks; `repeat_experiments`
returns the simulated B − A differences for each run.

## Research question

How can randomness make two versions with the same true conversion probability
look different in a real A/B experiment?

## Interpretation

Simulation results depend on the configured assumptions. A p-value is not the
probability that a hypothesis is true, and statistical significance alone does
not establish practical importance or causation. Repeatedly checking ordinary
fixed-sample p-values can inflate false positives; the app demonstrates this
with an optional-stopping simulation.
