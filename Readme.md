# Statistical Experimentation Lab

**Statistical Experimentation Lab** is an interactive statistics application for learning, simulating, and analysing controlled experiments such as A/B tests.

The project combines **probability, statistical inference, confidence intervals, hypothesis testing, simulation, power analysis, repeated experimentation, and real-world A/B testing** in an interactive Streamlit application.

Instead of only calculating statistical formulas, the application helps users understand **why experimental results change, how uncertainty behaves, and when an observed difference provides convincing statistical evidence**.

---

## 🎯 Project Objective

Suppose two versions of a website are tested:

```text
Variant A → Existing version
Variant B → New version
```

Users are randomly assigned to one of the two variants.

Each user either:

```text
Converts     → 1
Doesn't      → 0
```

The main question is:

> **If Variant B has a higher observed conversion rate than Variant A, is the difference real or could it simply be random variation?**

The Statistical Experimentation Lab explores this question using simulation and statistical inference.

---

# ✨ Main Features

## 🧪 A/B Experiment Simulation

Users can configure an artificial experiment by controlling:

- True conversion probability for Variant A
- True conversion probability for Variant B
- Sample size
- Significance level
- Random seed

The application then simulates the observed experiment using binomial random variables.

Example:

```text
True conversion rate A = 10%
True conversion rate B = 11%

Sample size per group = 5,000
```

The observed result may be:

```text
Observed A = 10.34%
Observed B = 10.82%
```

Even though the true probabilities are fixed, the observed results vary because of sampling randomness.

---

## 📊 Experiment Overview

The Overview workspace answers:

> **What happened in this experiment?**

It presents:

- Number of users in Variant A
- Number of users in Variant B
- Observed conversions
- Observed conversion rates
- Absolute difference
- Relative lift
- Statistical result summary

---

# 📈 Absolute Difference

The absolute difference between variants is calculated as:

```text
Difference = Conversion Rate B - Conversion Rate A
```

Example:

```text
A = 10%
B = 12%

Absolute Difference = 2 percentage points
```

---

# 📈 Relative Lift

Relative lift measures the improvement relative to the baseline conversion rate.

```text
Relative Lift =
(B - A) / A
```

Example:

```text
A = 10%
B = 12%
```

Then:

```text
Relative Lift = 20%
```

This means Variant B converts approximately 20% more users relative to Variant A.

---

# 🎯 Confidence Intervals

The **Uncertainty** workspace investigates:

> **How precise are the observed conversion rates?**

The application calculates **Wilson confidence intervals** for conversion proportions.

A confidence interval expresses uncertainty around an observed rate.

For example:

```text
Observed Conversion Rate = 10.5%

95% Confidence Interval:
9.7% – 11.3%
```

The interval becomes narrower as sample size increases.

This demonstrates an important statistical principle:

```text
Larger Sample
      ↓
Lower Sampling Uncertainty
      ↓
Narrower Confidence Interval
```

---

# 🧠 Hypothesis Testing

The **Evidence** workspace evaluates whether the difference between variants is statistically persuasive.

The project uses a:

```text
Two-Sided Two-Proportion Z-Test
```

---

## Null Hypothesis

```text
H₀: pA = pB
```

This means there is no real difference between the two conversion probabilities.

---

## Alternative Hypothesis

```text
H₁: pA ≠ pB
```

This means the conversion probabilities are different.

---

# 📉 P-Value

The hypothesis test produces a **p-value**.

The p-value measures how surprising the observed difference would be if the null hypothesis were true.

The decision rule is:

```text
if p-value < α:
    Reject H₀
else:
    Do not reject H₀
```

For example:

```text
α = 0.05
p-value = 0.013
```

Since:

```text
0.013 < 0.05
```

the experiment is considered statistically significant at the 5% significance level.

---

# ⚠️ Statistical Significance

Statistical significance does **not** automatically mean that a result is practically important.

For example:

```text
A = 10.00%
B = 10.10%
```

With a very large sample, this tiny difference could become statistically significant.

Therefore, an experiment should consider both:

```text
Statistical Evidence
+
Practical Effect Size
```

---

# 🔬 Simulation Lab

One experiment can produce a misleading result because of sampling randomness.

The **Simulation Lab** therefore allows the same experiment to be repeated many times.

For example:

```text
True A = 10%
True B = 10%

Repeat experiment 1,000 times
```

Even though both variants have identical true conversion rates, some individual experiments may still appear statistically significant.

This demonstrates the concept of:

```text
Type I Error
```

and why the significance level matters.

---

# 📊 Sampling Distribution

Repeated experiments produce a distribution of observed effects.

Example:

```text
Experiment 1 → +0.3%
Experiment 2 → -0.2%
Experiment 3 → +0.8%
Experiment 4 → -0.1%
...
```

Together these results form a **sampling distribution**.

The application visualizes how experimental outcomes fluctuate around the true underlying effect.

---

# ⚠️ False Positives

Suppose:

```text
A and B are truly identical
α = 0.05
```

If the experiment is repeated many times, approximately 5% of experiments may still be statistically significant purely due to chance.

This illustrates why:

```text
p < 0.05
```

does not mean that the probability of the null hypothesis being true is 5%.

---

# 🔁 Optional Stopping

The project also demonstrates the danger of repeatedly checking an experiment and stopping as soon as:

```text
p < 0.05
```

Repeatedly testing the same experiment without an appropriate sequential-testing framework can increase the false-positive rate.

This demonstrates why experiment duration and stopping rules should ideally be decided before examining the result.

---

# 🧪 Multiple Testing

Running many statistical tests increases the probability of finding at least one significant result by chance.

For example:

```text
1 test      → relatively low false-positive opportunity
20 tests    → much greater chance of at least one false positive
```

The project uses simulation to make this problem easier to understand.

---

# 🎮 Real-World Experiment — Cookie Cats

In addition to simulated A/B tests, the project includes analysis of the **Cookie Cats** mobile-game experiment.

The experiment compares two versions:

```text
gate_30
gate_40
```

The purpose is to investigate whether changing the location of a game gate affects player behaviour and retention.

---

## Experiment Groups

The dataset contains approximately:

```text
gate_30 → 44,700 players
gate_40 → 45,489 players
```

---

## Metrics Analysed

The project examines:

```text
Game Engagement
Day-1 Retention
Day-7 Retention
```

This transfers the statistical ideas learned in simulation to a real experimental dataset.

---

# 🧠 Why Simulation Is Important

A statistical formula gives a result for one dataset.

Simulation allows us to investigate:

```text
What happens if the experiment is repeated?
```

This makes abstract concepts such as:

- Sampling variability
- Confidence intervals
- Type I errors
- Statistical power
- False positives
- Multiple testing

much easier to understand.

---

# 🏗️ Project Architecture

The application follows a modular architecture.

```text
                   ┌──────────────────────────┐
                   │      User Controls       │
                   │        app.py            │
                   └────────────┬─────────────┘
                                │
                                ▼
                   ┌──────────────────────────┐
                   │    Simulation Layer      │
                   │ src/simulation.py        │
                   │                          │
                   │ Binomial experiments     │
                   │ Seeded random generator  │
                   │ Repeated simulation      │
                   └────────────┬─────────────┘
                                │
                                ▼
                   ┌──────────────────────────┐
                   │ Statistical Layer        │
                   │ src/statistics.py        │
                   │                          │
                   │ Conversion rates         │
                   │ Wilson intervals         │
                   │ Two-proportion Z-test    │
                   │ P-values                 │
                   │ Statistical decisions    │
                   └────────────┬─────────────┘
                                │
                                ▼
          ┌──────────────────────────────────────┐
          │       Presentation Layer             │
          │             app.py                   │
          │                                      │
          │ Overview                             │
          │ Uncertainty                          │
          │ Evidence                             │
          │ Data Summary                         │
          │ Simulation Lab                       │
          │ Cookie Cats                          │
          └──────────────────────────────────────┘
```

The simulation layer generates data, while the statistical layer receives observed experiment results and performs inference.

This separation keeps statistical logic independent from the frontend.

---

# 📄 Module Responsibilities

| File | Responsibility |
|---|---|
| `app.py` | Streamlit interface, experiment controls, dashboard and visualizations |
| `src/simulation.py` | Generates A/B experiments and repeated simulations |
| `src/statistics.py` | Confidence intervals, hypothesis tests and statistical summaries |
| `data/cookie_cats.csv` | Real A/B experiment dataset |

---

# 🎲 Reproducibility

Simulation uses NumPy's seeded random-number generator:

```python
np.random.default_rng(seed)
```

A fixed seed makes the experiment reproducible.

For example:

```text
Seed = 42
```

will reproduce the same simulated experiment when the same parameters are used.

---

# 💻 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive statistical dashboard |
| NumPy | Simulation and numerical computation |
| Pandas | Data manipulation |
| SciPy | Statistical computation |
| Statsmodels | Confidence intervals and hypothesis testing |
| Plotly | Interactive visualizations |
| Git / GitHub | Version control |

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd statistical_experimentation_lab
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Typical dependencies include:

```text
streamlit
numpy
pandas
scipy
statsmodels
plotly
```

---

# ▶️ Run the Application

```bash
streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

---

# 🧭 Typical Workflow

```text
Choose experiment probabilities
        ↓
Choose sample size and α
        ↓
Simulate Variant A and Variant B
        ↓
Observe conversion rates
        ↓
Measure effect size
        ↓
Calculate confidence intervals
        ↓
Run hypothesis test
        ↓
Inspect p-value
        ↓
Repeat experiment in Simulation Lab
        ↓
Apply concepts to Cookie Cats
```

---

# 👤 Author

**Hamna Iqbal**

**Statistical Experimentation Lab — Interactive A/B Testing & Statistical Inference**