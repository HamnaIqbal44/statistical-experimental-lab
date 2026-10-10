from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import mannwhitneyu, norm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint, proportions_ztest
from textwrap import dedent

from src.simulation import run_experiment, simulate_repeated_tests
from src.statistics import analyse_experiment


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Statistical Experimentation Lab",
    page_icon="📊",
    layout="wide",
)


# =========================================================
# SESSION STATE
# =========================================================

DEFAULT_VALUES = {
    "p_a": 0.10,
    "p_b": 0.10,
    "n_users": 1000,
    "alpha": 0.05,
    "seed": 42,
}

COOKIE_CATS_PATH = Path(__file__).resolve().parent / "data" / "cookie_cats.csv"


@st.cache_data
def load_cookie_cats():
    if not COOKIE_CATS_PATH.is_file():
        raise FileNotFoundError(
            f"Cookie Cats dataset was not found at {COOKIE_CATS_PATH}."
        )

    data = pd.read_csv(COOKIE_CATS_PATH)
    required_columns = {
        "userid",
        "version",
        "sum_gamerounds",
        "retention_1",
        "retention_7",
    }
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(
            "Cookie Cats dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )
    if data.empty:
        raise ValueError("Cookie Cats dataset contains no rows.")
    return data


def p_values_for_counts(conversions_a, conversions_b, users_per_group):
    rate_a = conversions_a / users_per_group
    rate_b = conversions_b / users_per_group
    pooled_rate = (conversions_a + conversions_b) / (2 * users_per_group)
    standard_error = np.sqrt(
        pooled_rate * (1 - pooled_rate) * (2 / users_per_group)
    )
    z_scores = np.divide(
        rate_b - rate_a,
        standard_error,
        out=np.zeros_like(rate_a, dtype=float),
        where=standard_error > 0,
    )
    return 2 * norm.sf(np.abs(z_scores))


for key, value in DEFAULT_VALUES.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CALLBACKS
# =========================================================

def generate_new_sample():
    """
    Create another random sample.

    This callback executes BEFORE Streamlit recreates
    the widgets, so modifying session_state is allowed.
    """

    st.session_state.seed += 1


def reset_experiment():
    """
    Reset all experiment settings.
    """

    for key, value in DEFAULT_VALUES.items():
        st.session_state[key] = value


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1450px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128,128,128,.15);
    }

    [data-testid="stMetric"] {
        background: rgba(127,127,127,.055);
        border: 1px solid rgba(127,127,127,.15);
        border-radius: 16px;
        padding: 16px;
    }

    .hero {
        padding: 1.5rem 1.7rem;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;

        border-radius: 20px;
        border: 1px solid rgba(127, 127, 127, 0.15);

        background: linear-gradient(
            135deg,
            rgba(99, 102, 241, 0.10),
            rgba(14, 165, 233, 0.05)
        );
    }

    .hero h1 {
        margin: 0;
        padding: 0;
        font-size: 2rem;
        line-height: 1.25;
    }

    .hero p {
        margin: 0.6rem 0 0 0;
        padding: 0;
        opacity: 0.75;
        font-size: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    dedent(
        """
        <div class="hero">
            <h1>📊 Statistical Experimentation Lab</h1>
            <p>
                Explore how randomness, sample size and statistical
                evidence influence an A/B experiment.
            </p>
        </div>
        """
    ),
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("Experiment Setup")

    st.caption(
        "Change the experiment assumptions and observe "
        "how the statistical result changes."
    )


    st.slider(
        "True conversion probability — A",
        min_value=0.01,
        max_value=0.50,
        step=0.01,
        key="p_a",
    )


    st.slider(
        "True conversion probability — B",
        min_value=0.01,
        max_value=0.50,
        step=0.01,
        key="p_b",
    )


    st.slider(
        "Users per group",
        min_value=100,
        max_value=10000,
        step=100,
        key="n_users",
    )


    st.select_slider(
        "Significance level (α)",
        options=[
            0.01,
            0.05,
            0.10,
        ],
        key="alpha",
    )


    st.number_input(
        "Random seed",
        min_value=0,
        step=1,
        key="seed",
    )


    # -----------------------------------------------------
    # BUTTONS
    # -----------------------------------------------------

    button1, button2 = st.columns(2)


    with button1:

        st.button(
            "🎲 New Sample",
            width="stretch",
            on_click=generate_new_sample,
        )


    with button2:

        st.button(
            "↺ Reset",
            width="stretch",
            on_click=reset_experiment,
        )


    st.divider()


    st.caption(
        "Tip: set A and B to the same probability and "
        "press **New Sample** repeatedly."
    )


# =========================================================
# GET CURRENT SETTINGS
# =========================================================

p_a = st.session_state.p_a
p_b = st.session_state.p_b

n_users = st.session_state.n_users

alpha = st.session_state.alpha

seed = int(
    st.session_state.seed
)


# =========================================================
# RUN EXPERIMENT
# =========================================================

result = run_experiment(
    n_users=n_users,
    p_a=p_a,
    p_b=p_b,
    seed=seed,
)


# =========================================================
# STATISTICAL ANALYSIS
# =========================================================

analysis = analyse_experiment(
    conversions_a=result["conversions_a"],
    conversions_b=result["conversions_b"],
    n_users=n_users,
    alpha=alpha,
)


# =========================================================
# EXTRA CALCULATIONS
# =========================================================

true_difference = (
    p_b - p_a
)


if result["rate_a"] > 0:

    relative_lift = (
        result["rate_b"]
        / result["rate_a"]
        - 1
    )

else:

    relative_lift = 0


# =========================================================
# METRICS
# =========================================================

m1, m2, m3, m4, m5 = st.columns(5)


m1.metric(
    "Observed A",
    f'{result["rate_a"]:.2%}',
    delta=(
        f'{result["rate_a"] - p_a:+.2%} '
        "vs truth"
    ),
)


m2.metric(
    "Observed B",
    f'{result["rate_b"]:.2%}',
    delta=(
        f'{result["rate_b"] - p_b:+.2%} '
        "vs truth"
    ),
)


m3.metric(
    "Observed B − A",
    f'{result["difference"]:+.2%}',
    delta=f'True {true_difference:+.2%}',
)


m4.metric(
    "Relative Lift",
    f'{relative_lift:+.2%}',
)


m5.metric(
    "p-value",
    f'{analysis["p_value"]:.4f}',
    delta=(
        "Significant"
        if analysis["significant"]
        else "Not significant"
    ),
)


st.write("")


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📈 Overview",
        "🎯 Uncertainty",
        "🧪 Evidence",
        "🗂 Data Summary",
        "🔁 Simulation Lab",
        "🍪 Cookie Cats",
    ]
)


# =========================================================
# TAB 1
# =========================================================

with tab1:

    left, right = st.columns(
        [1.4, 1]
    )


    # -----------------------------------------------------
    # TRUE VS OBSERVED
    # -----------------------------------------------------

    with left:

        fig_rates = go.Figure()


        fig_rates.add_trace(
            go.Bar(
                name="True Rate",

                x=[
                    "Version A",
                    "Version B",
                ],

                y=[
                    p_a,
                    p_b,
                ],

                text=[
                    f"{p_a:.1%}",
                    f"{p_b:.1%}",
                ],

                textposition="outside",

                opacity=0.50,

                hovertemplate=(
                    "%{x}"
                    "<br>True probability: %{y:.2%}"
                    "<extra></extra>"
                ),
            )
        )


        fig_rates.add_trace(
            go.Bar(
                name="Observed Rate",

                x=[
                    "Version A",
                    "Version B",
                ],

                y=[
                    result["rate_a"],
                    result["rate_b"],
                ],

                text=[
                    f'{result["rate_a"]:.1%}',
                    f'{result["rate_b"]:.1%}',
                ],

                textposition="outside",

                hovertemplate=(
                    "%{x}"
                    "<br>Observed: %{y:.2%}"
                    "<extra></extra>"
                ),
            )
        )


        max_rate = max(
            p_a,
            p_b,
            result["rate_a"],
            result["rate_b"],
        )


        fig_rates.update_layout(
            title="True Probability vs Observed Sample",

            barmode="group",

            yaxis=dict(
                tickformat=".0%",
                title="Conversion Rate",

                range=[
                    0,
                    max(
                        0.15,
                        max_rate * 1.35,
                    ),
                ],
            ),

            xaxis_title="",

            legend=dict(
                orientation="h",

                yanchor="bottom",
                y=1.02,

                xanchor="right",
                x=1,
            ),

            margin=dict(
                l=25,
                r=25,
                t=70,
                b=30,
            ),
        )


        st.plotly_chart(
            fig_rates,
            width="stretch",
            alt="True and observed conversion rates for A and B.",
        )


    # -----------------------------------------------------
    # USER OUTCOMES
    # -----------------------------------------------------

    with right:

        converted_a = (
            result["conversions_a"]
        )

        converted_b = (
            result["conversions_b"]
        )


        fig_users = go.Figure()


        fig_users.add_trace(
            go.Bar(
                name="Converted",

                x=[
                    "Version A",
                    "Version B",
                ],

                y=[
                    converted_a,
                    converted_b,
                ],

                hovertemplate=(
                    "%{x}"
                    "<br>Converted: %{y:,}"
                    "<extra></extra>"
                ),
            )
        )


        fig_users.add_trace(
            go.Bar(
                name="Did Not Convert",

                x=[
                    "Version A",
                    "Version B",
                ],

                y=[
                    n_users - converted_a,
                    n_users - converted_b,
                ],

                hovertemplate=(
                    "%{x}"
                    "<br>Did not convert: %{y:,}"
                    "<extra></extra>"
                ),
            )
        )


        fig_users.update_layout(
            title="User Outcomes",

            barmode="stack",

            yaxis_title="Users",

            legend=dict(
                orientation="h",

                yanchor="bottom",
                y=1.02,

                xanchor="right",
                x=1,
            ),

            margin=dict(
                l=25,
                r=25,
                t=70,
                b=30,
            ),
        )


        st.plotly_chart(
            fig_users,
            width="stretch",
            alt="Observed conversion rates by version and sample size.",
        )


    st.caption(
        "Click New Sample and watch the observed "
        "values move while the true probabilities remain fixed."
    )


# =========================================================
# TAB 2 — CONFIDENCE INTERVALS
# =========================================================

with tab2:

    st.subheader(
        "Confidence Intervals"
    )


    st.write(
        """
        The observed conversion rate is only an estimate.

        A confidence interval shows the uncertainty
        around that estimate.
        """
    )


    rates = [
        result["rate_a"],
        result["rate_b"],
    ]


    lower = [
        analysis["ci_a"][0],
        analysis["ci_b"][0],
    ]


    upper = [
        analysis["ci_a"][1],
        analysis["ci_b"][1],
    ]


    error_plus = [
        upper[i] - rates[i]
        for i in range(2)
    ]


    error_minus = [
        rates[i] - lower[i]
        for i in range(2)
    ]


    fig_ci = go.Figure()


    fig_ci.add_trace(
        go.Scatter(
            x=rates,

            y=[
                "Version A",
                "Version B",
            ],

            mode="markers",

            marker=dict(
                size=18
            ),

            error_x=dict(
                type="data",

                symmetric=False,

                array=error_plus,

                arrayminus=error_minus,

                thickness=2,

                width=7,
            ),

            customdata=[
                [
                    lower[0],
                    upper[0],
                ],

                [
                    lower[1],
                    upper[1],
                ],
            ],

            hovertemplate=(
                "%{y}"
                "<br>Observed: %{x:.2%}"
                "<br>Lower: %{customdata[0]:.2%}"
                "<br>Upper: %{customdata[1]:.2%}"
                "<extra></extra>"
            ),
        )
    )


    fig_ci.add_vline(
        x=p_a,
        line_dash="dot",
        annotation_text="True A",
    )


    if p_b != p_a:

        fig_ci.add_vline(
            x=p_b,
            line_dash="dot",
            annotation_text="True B",
        )


    minimum = max(
        0,
        min(
            lower + [p_a, p_b]
        ) - 0.03,
    )


    maximum = min(
        1,
        max(
            upper + [p_a, p_b]
        ) + 0.03,
    )


    fig_ci.update_layout(
        title=(
            f"{(1-alpha):.0%} Confidence Intervals"
        ),

        xaxis=dict(
            tickformat=".0%",

            range=[
                minimum,
                maximum,
            ],

            title="Conversion Rate",
        ),

        yaxis_title="",

        height=430,

        margin=dict(
            l=40,
            r=40,
            t=70,
            b=50,
        ),
    )


    st.plotly_chart(
        fig_ci,
        width="stretch",
        alt="Observed conversion rates with confidence intervals for both versions.",
    )


    c1, c2 = st.columns(2)


    c1.info(
        f"""
        **Version A**

        Observed: {result["rate_a"]:.2%}

        Interval:

        **{analysis["ci_a"][0]:.2%}
        → {analysis["ci_a"][1]:.2%}**
        """
    )


    c2.info(
        f"""
        **Version B**

        Observed: {result["rate_b"]:.2%}

        Interval:

        **{analysis["ci_b"][0]:.2%}
        → {analysis["ci_b"][1]:.2%}**
        """
    )


# =========================================================
# TAB 3 — P-VALUE
# =========================================================

with tab3:

    left, right = st.columns(
        [1.1, 1]
    )


    with left:

        gauge_max = min(
            1.0,

            max(
                0.10,
                alpha * 2,
                analysis["p_value"] * 1.10,
            ),
        )


        fig_p = go.Figure(
            go.Indicator(
                mode="gauge+number",

                value=analysis["p_value"],

                number=dict(
                    valueformat=".4f"
                ),

                title=dict(
                    text="p-value"
                ),

                gauge=dict(
                    axis=dict(
                        range=[
                            0,
                            gauge_max,
                        ],
                    ),

                    threshold=dict(
                        line=dict(
                            width=4
                        ),

                        thickness=0.8,

                        value=alpha,
                    ),
                ),
            )
        )


        fig_p.update_layout(
            height=340,

            margin=dict(
                l=35,
                r=35,
                t=50,
                b=20,
            ),
        )


        st.plotly_chart(
            fig_p,
            width="stretch",
            alt="Gauge showing the experiment p-value and significance threshold.",
        )


        st.caption(
            f"Threshold α = {alpha:.2f}"
        )


    with right:


        if analysis["significant"]:

            st.success(
                "### Statistically Significant"
            )

            st.write(
                f"""
                **p = {analysis["p_value"]:.4f}**

                is smaller than

                **α = {alpha:.2f}**

                This experiment provides enough
                statistical evidence to reject the
                equal-proportions null hypothesis.
                """
            )


        else:

            st.info(
                "### Not Statistically Significant"
            )

            st.write(
                f"""
                **p = {analysis["p_value"]:.4f}**

                is greater than or equal to

                **α = {alpha:.2f}**

                We do not currently have enough
                evidence to reject the equal-proportions
                null hypothesis.
                """
            )


        st.warning(
            """
            **Important**

            Statistical significance does not automatically
            mean that an effect is large or practically useful.
            """
        )


# =========================================================
# TAB 4 — DATA
# =========================================================

with tab4:


    summary = pd.DataFrame(
        {
            "Version": [
                "A",
                "B",
            ],

            "True Probability": [
                p_a,
                p_b,
            ],

            "Users": [
                n_users,
                n_users,
            ],

            "Conversions": [
                result["conversions_a"],
                result["conversions_b"],
            ],

            "Non-Conversions": [
                n_users - result["conversions_a"],
                n_users - result["conversions_b"],
            ],

            "Observed Rate": [
                result["rate_a"],
                result["rate_b"],
            ],

            "CI Lower": [
                analysis["ci_a"][0],
                analysis["ci_b"][0],
            ],

            "CI Upper": [
                analysis["ci_a"][1],
                analysis["ci_b"][1],
            ],
        }
    )


    display = summary.copy()


    percentage_columns = [
        "True Probability",
        "Observed Rate",
        "CI Lower",
        "CI Upper",
    ]


    for column in percentage_columns:

        display[column] = (
            display[column]
            .map(
                lambda value:
                f"{value:.2%}"
            )
        )


    st.dataframe(
        display,

        width="stretch",

        hide_index=True,
        alt="Experiment inputs, conversions, observed rates, and confidence intervals.",
    )


    csv = (
        summary
        .to_csv(index=False)
        .encode("utf-8")
    )


    st.download_button(
        "⬇ Download Experiment Data",

        data=csv,

        file_name="ab_experiment_summary.csv",

        mime="text/csv",
    )


with tab5:

    st.subheader("Repeated experiments")
    st.write(
        "Choose a simulation to explore sampling variation, false positives, "
        "power, optional stopping, or multiple testing."
    )
    simulation_topic = st.selectbox(
        "Simulation",
        [
            "Sampling distribution",
            "False positives and power",
            "Optional stopping",
            "Multiple testing",
        ],
        key="simulation_topic",
    )

    if simulation_topic == "Sampling distribution":
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        with sim_col1:
            sim_rate_a = st.slider(
                "True rate A",
                0.01,
                0.50,
                0.10,
                0.01,
                key="sampling_rate_a",
            )
            sim_rate_b = st.slider(
                "True rate B",
                0.01,
                0.50,
                0.11,
                0.01,
                key="sampling_rate_b",
            )
        with sim_col2:
            sim_users = st.slider(
                "Users per group",
                100,
                10000,
                1000,
                100,
                key="sampling_users",
            )
            sim_runs = st.slider(
                "Experiments",
                100,
                10000,
                1000,
                100,
                key="sampling_runs",
            )
        with sim_col3:
            sim_alpha = st.select_slider(
                "Significance level",
                options=[0.01, 0.05, 0.10],
                value=0.05,
                key="sampling_alpha",
            )
            sim_seed = st.number_input(
                "Simulation seed",
                min_value=0,
                value=42,
                step=1,
                key="sampling_seed",
            )

        simulation = simulate_repeated_tests(
            sim_runs,
            sim_users,
            sim_rate_a,
            sim_rate_b,
            seed=int(sim_seed),
        )
        significance_rate = float(
            np.mean(simulation["p_values"] < sim_alpha)
        )
        metric_cols = st.columns(3)
        metric_cols[0].metric(
            "Mean observed B − A",
            f"{simulation['differences'].mean():+.2%}",
        )
        metric_cols[1].metric(
            "Standard deviation",
            f"{simulation['differences'].std():.2%}",
        )
        metric_cols[2].metric(
            "Significant tests",
            f"{significance_rate:.1%}",
        )

        fig_sampling = go.Figure(
            go.Histogram(
                x=simulation["differences"],
                nbinsx=45,
                name="Simulated difference",
            )
        )
        fig_sampling.add_vline(
            x=sim_rate_b - sim_rate_a,
            line_dash="dash",
            annotation_text=f"True difference: {sim_rate_b - sim_rate_a:+.1%}",
        )
        fig_sampling.update_layout(
            title="Sampling distribution of observed B − A differences",
            xaxis_title="Observed conversion-rate difference",
            yaxis_title="Number of experiments",
        )
        st.plotly_chart(
            fig_sampling,
            width="stretch",
            alt="Distribution of simulated observed B minus A conversion differences.",
        )
        st.caption(
            f"The true difference is {sim_rate_b - sim_rate_a:+.2%}; "
            f"{significance_rate:.1%} of simulated tests were significant "
            f"at alpha = {sim_alpha:.2f}."
        )

    elif simulation_topic == "False positives and power":
        scenario = st.radio(
            "Scenario",
            ["False-positive rate (equal versions)", "Power (B is better)"],
            horizontal=True,
            key="power_scenario",
        )
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        with sim_col1:
            sim_rate_a = st.slider(
                "True rate A",
                0.01,
                0.50,
                0.10,
                0.01,
                key="power_rate_a",
            )
            if scenario.startswith("False-positive"):
                sim_rate_b = sim_rate_a
            elif sim_rate_a >= 0.50:
                sim_rate_b = sim_rate_a
                st.info(
                    "Version B cannot be better than a 50% conversion rate. "
                    "Lower the true rate for A to simulate a positive effect."
                )
            else:
                sim_rate_b = st.slider(
                    "True rate B",
                    min_value=float(sim_rate_a),
                    max_value=min(0.50, float(sim_rate_a) + 0.30),
                    value=min(0.11, 0.50, float(sim_rate_a) + 0.30),
                    step=0.01,
                    key="power_rate_b",
                )
        with sim_col2:
            sim_users = st.slider(
                "Users per group",
                100,
                10000,
                1000,
                100,
                key="power_users",
            )
            sim_runs = st.slider(
                "Simulated experiments",
                100,
                10000,
                2000,
                100,
                key="power_runs",
            )
        with sim_col3:
            sim_alpha = st.select_slider(
                "Significance level",
                options=[0.01, 0.05, 0.10],
                value=0.05,
                key="power_alpha",
            )
            sim_seed = st.number_input(
                "Simulation seed",
                min_value=0,
                value=42,
                step=1,
                key="power_seed",
            )

        simulation = simulate_repeated_tests(
            sim_runs,
            sim_users,
            sim_rate_a,
            sim_rate_b,
            seed=int(sim_seed),
        )
        detected_rate = float(np.mean(simulation["p_values"] < sim_alpha))
        result_label = (
            "Estimated false-positive rate"
            if scenario.startswith("False-positive")
            else "Estimated statistical power"
        )
        st.metric(result_label, f"{detected_rate:.1%}")
        st.caption(
            f"{sim_runs:,} tests · {sim_users:,} users per group · true rates "
            f"{sim_rate_a:.1%} (A) and {sim_rate_b:.1%} (B) · alpha "
            f"{sim_alpha:.2f}."
        )
        if scenario.startswith("False-positive"):
            st.info(
                "Under equal true rates, the false-positive rate should be near "
                "alpha over many repetitions. Small differences are expected "
                "from Monte Carlo randomness."
            )
        else:
            st.info(
                "Power estimates the chance of detecting a real effect under "
                "these assumptions. Larger samples and larger effects generally "
                "increase power."
            )

    elif simulation_topic == "Optional stopping":
        st.write(
            "Compare repeatedly checking for significance with testing once at "
            "a pre-planned final sample size."
        )
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        with sim_col1:
            null_rate = st.slider(
                "Shared true conversion rate",
                0.01,
                0.50,
                0.10,
                0.01,
                key="stopping_rate",
            )
            users_per_look = st.slider(
                "New users per group at each check",
                50,
                2000,
                200,
                50,
                key="stopping_users",
            )
        with sim_col2:
            number_of_looks = st.slider(
                "Number of significance checks",
                2,
                30,
                10,
                key="stopping_looks",
            )
            sim_runs = st.slider(
                "Simulated experiments",
                100,
                5000,
                1000,
                100,
                key="stopping_runs",
            )
        with sim_col3:
            sim_alpha = st.select_slider(
                "Significance level",
                options=[0.01, 0.05, 0.10],
                value=0.05,
                key="stopping_alpha",
            )
            sim_seed = st.number_input(
                "Simulation seed",
                min_value=0,
                value=42,
                step=1,
                key="stopping_seed",
            )

        rng = np.random.default_rng(int(sim_seed))
        cumulative_a = np.zeros(sim_runs, dtype=np.int64)
        cumulative_b = np.zeros(sim_runs, dtype=np.int64)
        fixed_sample_a = np.zeros(sim_runs, dtype=np.int64)
        fixed_sample_b = np.zeros(sim_runs, dtype=np.int64)
        stopped = np.zeros(sim_runs, dtype=bool)
        stopping_counts = []
        for look in range(1, number_of_looks + 1):
            batch_a = rng.binomial(users_per_look, null_rate, size=sim_runs)
            batch_b = rng.binomial(users_per_look, null_rate, size=sim_runs)
            fixed_sample_a += batch_a
            fixed_sample_b += batch_b
            active = ~stopped
            cumulative_a[active] += batch_a[active]
            cumulative_b[active] += batch_b[active]
            p_values = p_values_for_counts(
                cumulative_a,
                cumulative_b,
                look * users_per_look,
            )
            stopped |= active & (p_values < sim_alpha)
            stopping_counts.append(int(stopped.sum()))

        peeking_rate = float(stopped.mean())
        fixed_sample_p_values = p_values_for_counts(
            fixed_sample_a,
            fixed_sample_b,
            number_of_looks * users_per_look,
        )
        fixed_sample_rate = float(
            np.mean(fixed_sample_p_values < sim_alpha)
        )
        metric_cols = st.columns(3)
        metric_cols[0].metric(
            "Significant at any check",
            f"{peeking_rate:.1%}",
        )
        metric_cols[1].metric(
            "Significant at final check",
            f"{fixed_sample_rate:.1%}",
        )
        metric_cols[2].metric(
            "Planned final users per group",
            f"{number_of_looks * users_per_look:,}",
        )
        fig_stopping = go.Figure(
            go.Scatter(
                x=np.arange(1, number_of_looks + 1) * users_per_look,
                y=stopping_counts,
                mode="lines+markers",
            )
        )
        fig_stopping.update_layout(
            title="Cumulative experiments flagged while repeatedly checking",
            xaxis_title="Users per group",
            yaxis_title="Experiments flagged as significant",
        )
        st.plotly_chart(
            fig_stopping,
            width="stretch",
            alt="Cumulative null experiments flagged during repeated significance checks.",
        )
        st.warning(
            "Repeatedly checking an ordinary fixed-sample p-value and stopping "
            "when significant inflates false positives. Pre-plan the analysis "
            "time or use a sequential-testing method."
        )

    else:
        st.write(
            "When many independent null hypotheses are tested, the chance of "
            "at least one false positive increases."
        )
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        with sim_col1:
            number_of_tests = st.slider(
                "Independent tests",
                2,
                100,
                20,
                key="multiple_tests",
            )
            null_rate = st.slider(
                "Shared true conversion rate",
                0.01,
                0.50,
                0.10,
                0.01,
                key="multiple_rate",
            )
        with sim_col2:
            sim_users = st.slider(
                "Users per group, per test",
                100,
                5000,
                1000,
                100,
                key="multiple_users",
            )
            sim_runs = st.slider(
                "Simulated test families",
                100,
                5000,
                1000,
                100,
                key="multiple_runs",
            )
        with sim_col3:
            sim_alpha = st.select_slider(
                "Family-wise significance level",
                options=[0.01, 0.05, 0.10],
                value=0.05,
                key="multiple_alpha",
            )
            sim_seed = st.number_input(
                "Simulation seed",
                min_value=0,
                value=42,
                step=1,
                key="multiple_seed",
            )

        rng = np.random.default_rng(int(sim_seed))
        counts_a = rng.binomial(
            sim_users,
            null_rate,
            size=(sim_runs, number_of_tests),
        )
        counts_b = rng.binomial(
            sim_users,
            null_rate,
            size=(sim_runs, number_of_tests),
        )
        p_values = p_values_for_counts(counts_a, counts_b, sim_users)
        unadjusted_family_rate = float(
            np.mean(np.any(p_values < sim_alpha, axis=1))
        )
        bonferroni_family_rate = float(
            np.mean(np.any(p_values < sim_alpha / number_of_tests, axis=1))
        )
        metric_cols = st.columns(3)
        metric_cols[0].metric(
            "At least one raw p < alpha",
            f"{unadjusted_family_rate:.1%}",
        )
        metric_cols[1].metric(
            "At least one Bonferroni result",
            f"{bonferroni_family_rate:.1%}",
        )
        metric_cols[2].metric("Tests per family", f"{number_of_tests}")
        st.caption(
            f"Bonferroni compares each test with alpha / {number_of_tests} = "
            f"{sim_alpha / number_of_tests:.4f}."
        )


with tab6:

    st.subheader("Cookie Cats experiment")
    st.write(
        "Compare player retention and game rounds between the gate-at-level-30 "
        "and gate-at-level-40 groups in the included dataset."
    )
    cookie_data = load_cookie_cats()
    versions = sorted(cookie_data["version"].dropna().unique().tolist())
    if len(versions) != 2:
        st.error(
            "The Cookie Cats analysis expects exactly two experiment versions; "
            f"found {len(versions)}."
        )
    else:
        groups = {
            version: cookie_data.loc[cookie_data["version"] == version]
            for version in versions
        }
        group_summary = pd.DataFrame(
            [
                {
                    "Version": version,
                    "Players": len(group),
                    "Mean rounds": group["sum_gamerounds"].mean(),
                    "Median rounds": group["sum_gamerounds"].median(),
                    "Day-1 retention": group["retention_1"].mean(),
                    "Day-7 retention": group["retention_7"].mean(),
                }
                for version, group in groups.items()
            ]
        )
        st.dataframe(
            group_summary.style.format(
                {
                    "Mean rounds": "{:.1f}",
                    "Median rounds": "{:.0f}",
                    "Day-1 retention": "{:.2%}",
                    "Day-7 retention": "{:.2%}",
                }
            ),
            hide_index=True,
            alt="Player counts, game rounds, and retention rates by experiment version.",
        )

        outcomes = {}
        raw_p_values = []
        for column, label in [
            ("retention_1", "Day-1 retention"),
            ("retention_7", "Day-7 retention"),
        ]:
            counts = [int(groups[version][column].sum()) for version in versions]
            sizes = [len(groups[version]) for version in versions]
            z_stat, p_value = proportions_ztest(count=counts, nobs=sizes)
            intervals = [
                proportion_confint(
                    count=count,
                    nobs=size,
                    alpha=0.05,
                    method="wilson",
                )
                for count, size in zip(counts, sizes)
            ]
            outcomes[label] = {
                "rates": [count / size for count, size in zip(counts, sizes)],
                "intervals": intervals,
                "p_value": float(p_value),
                "test": "Two-proportion z-test",
            }
            raw_p_values.append(float(p_value))

        rounds_a = groups[versions[0]]["sum_gamerounds"]
        rounds_b = groups[versions[1]]["sum_gamerounds"]
        rounds_test = mannwhitneyu(rounds_a, rounds_b, alternative="two-sided")
        outcomes["Game rounds"] = {
            "p_value": float(rounds_test.pvalue),
            "test": "Mann–Whitney U test",
        }
        raw_p_values.append(float(rounds_test.pvalue))
        adjusted_p_values = multipletests(raw_p_values, method="holm")[1]
        for index, outcome in enumerate(
            ["Day-1 retention", "Day-7 retention", "Game rounds"]
        ):
            outcomes[outcome]["adjusted_p"] = float(adjusted_p_values[index])

        selected_outcome = st.radio(
            "Outcome to inspect",
            ["Day-1 retention", "Day-7 retention", "Game rounds"],
            horizontal=True,
            key="cookie_outcome",
        )
        selected_result = outcomes[selected_outcome]
        if selected_outcome == "Game rounds":
            visible_percentile = st.slider(
                "Show game rounds through percentile",
                min_value=90,
                max_value=100,
                value=99,
                key="cookie_rounds_percentile",
            )
            upper_limit = cookie_data["sum_gamerounds"].quantile(
                visible_percentile / 100
            )
            rounds_data = cookie_data[
                cookie_data["sum_gamerounds"] <= upper_limit
            ]
            fig_cookie = go.Figure()
            for version in versions:
                fig_cookie.add_trace(
                    go.Histogram(
                        x=rounds_data.loc[
                            rounds_data["version"] == version,
                            "sum_gamerounds",
                        ],
                        name=version,
                        opacity=0.65,
                        nbinsx=50,
                    )
                )
            fig_cookie.update_layout(
                barmode="overlay",
                title=f"Game rounds through the {visible_percentile}th percentile",
                xaxis_title="Game rounds",
                yaxis_title="Players",
            )
            st.plotly_chart(
                fig_cookie,
                width="stretch",
                alt="Distribution of game rounds by Cookie Cats experiment version.",
            )
            st.caption(
                f"Values above {upper_limit:,.0f} rounds are hidden from this "
                "chart only. All players are included in the Mann–Whitney test."
            )
            st.write(
                f"Median rounds: {versions[0]} {rounds_a.median():.0f}; "
                f"{versions[1]} {rounds_b.median():.0f}. "
                f"Mean rounds: {versions[0]} {rounds_a.mean():.2f}; "
                f"{versions[1]} {rounds_b.mean():.2f}."
            )
        else:
            retention = selected_result
            rates = retention["rates"]
            intervals = retention["intervals"]
            fig_cookie = go.Figure(
                go.Bar(
                    x=versions,
                    y=rates,
                    error_y={
                        "type": "data",
                        "symmetric": False,
                        "array": [
                            intervals[i][1] - rates[i]
                            for i in range(2)
                        ],
                        "arrayminus": [
                            rates[i] - intervals[i][0]
                            for i in range(2)
                        ],
                    },
                    text=[f"{rate:.2%}" for rate in rates],
                    textposition="outside",
                )
            )
            fig_cookie.update_layout(
                title=f"{selected_outcome} with 95% Wilson intervals",
                xaxis_title="Experiment version",
                yaxis_title="Retention",
                showlegend=False,
            )
            fig_cookie.update_yaxes(tickformat=".0%", rangemode="tozero")
            st.plotly_chart(
                fig_cookie,
                width="stretch",
                alt=f"{selected_outcome} by experiment version with Wilson confidence intervals.",
            )

        st.write(
            f"**{selected_result['test']}** · raw p-value "
            f"`{selected_result['p_value']:.4g}` · Holm-adjusted p-value "
            f"`{selected_result['adjusted_p']:.4g}`."
        )
        if selected_result["adjusted_p"] < 0.05:
            st.success(
                "This outcome is statistically significant after Holm adjustment "
                "at the 5% level. Evaluate effect size and product context before "
                "making a decision."
            )
        else:
            st.info(
                "This outcome is not statistically significant after Holm "
                "adjustment at the 5% level."
            )
        st.caption(
            "Holm adjustment accounts for the three outcomes. Retention uses "
            "two-proportion z-tests; the skewed game-round counts use a "
            "Mann–Whitney U test."
        )
        with st.expander("Preview and download the dataset"):
            st.dataframe(
                cookie_data.head(1000),
                hide_index=True,
                alt="First 1,000 rows of the Cookie Cats experiment dataset.",
            )
            st.caption("Preview limited to the first 1,000 rows.")
            st.download_button(
                "Download full Cookie Cats dataset",
                data=cookie_data.to_csv(index=False).encode("utf-8"),
                file_name="cookie_cats.csv",
                mime="text/csv",
            )


# =========================================================
# LEARNING SECTION
# =========================================================

st.divider()


with st.expander(
    "🧠 Experiment to try"
):

    st.markdown(
        """
        ### Experiment 1

        Set:

        - **A = 10%**
        - **B = 10%**
        - **Users = 1,000**

        Click **New Sample** repeatedly.

        Even though the true probabilities are identical,
        the observed conversion rates usually differ.

        ### Experiment 2

        Increase users to:

        **10,000**

        Now observe how the sample conversion rates usually
        move closer to the true 10%.

        This demonstrates the idea of
        **sampling variation** and begins connecting the
        project to the Law of Large Numbers.
        """
    )