import numpy as np

from statsmodels.stats.proportion import (
    proportion_confint,
    proportions_ztest,
)


def analyse_experiment(
    conversions_a: int,
    conversions_b: int,
    n_users: int,
    alpha: float = 0.05,
):
    """
    Statistically compare Version A and Version B.
    """

    # Successful conversions.
    counts = np.array(
        [
            conversions_a,
            conversions_b,
        ]
    )

    # Number of users in each experiment group.
    observations = np.array(
        [
            n_users,
            n_users,
        ]
    )

    # -----------------------------------------------------
    # TWO-PROPORTION Z-TEST
    # -----------------------------------------------------

    z_stat, p_value = proportions_ztest(
        count=counts,
        nobs=observations,
        alternative="two-sided",
    )

    # -----------------------------------------------------
    # CONFIDENCE INTERVAL FOR VERSION A
    # -----------------------------------------------------

    ci_a = proportion_confint(
        count=conversions_a,
        nobs=n_users,
        alpha=alpha,
        method="wilson",
    )

    # -----------------------------------------------------
    # CONFIDENCE INTERVAL FOR VERSION B
    # -----------------------------------------------------

    ci_b = proportion_confint(
        count=conversions_b,
        nobs=n_users,
        alpha=alpha,
        method="wilson",
    )

    # Significant when p-value is below alpha.
    significant = p_value < alpha

    return {
        "z_stat": z_stat,
        "p_value": p_value,
        "significant": significant,
        "ci_a": ci_a,
        "ci_b": ci_b,
    }