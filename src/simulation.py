import numpy as np
from scipy.stats import norm


def simulate_repeated_tests(
    number_of_experiments: int,
    sample_size: int,
    rate_a: float,
    rate_b: float,
    seed: int = 42,
) -> dict[str, np.ndarray]:
    """Simulate independent A/B tests and calculate two-proportion z-test p-values."""
    if number_of_experiments < 1:
        raise ValueError("number_of_experiments must be at least 1.")
    if sample_size < 1:
        raise ValueError("sample_size must be at least 1.")
    if not 0 <= rate_a <= 1 or not 0 <= rate_b <= 1:
        raise ValueError("Conversion rates must be between 0 and 1.")

    rng = np.random.default_rng(seed)
    conversions_a = rng.binomial(sample_size, rate_a, size=number_of_experiments)
    conversions_b = rng.binomial(sample_size, rate_b, size=number_of_experiments)
    differences = conversions_b / sample_size - conversions_a / sample_size

    pooled_rate = (conversions_a + conversions_b) / (2 * sample_size)
    standard_error = np.sqrt(
        pooled_rate * (1 - pooled_rate) * (2 / sample_size)
    )
    z_scores = np.divide(
        differences,
        standard_error,
        out=np.zeros_like(differences, dtype=float),
        where=standard_error > 0,
    )
    p_values = 2 * norm.sf(np.abs(z_scores))

    return {
        "conversions_a": conversions_a,
        "conversions_b": conversions_b,
        "differences": differences,
        "p_values": p_values,
    }


def repeat_experiments(
    number_of_experiments: int,
    sample_size: int,
    rate_a: float,
    rate_b: float,
    seed: int = 42,
) -> np.ndarray:
    """Return observed B − A differences for the requested simulated tests."""
    return simulate_repeated_tests(
        number_of_experiments=number_of_experiments,
        sample_size=sample_size,
        rate_a=rate_a,
        rate_b=rate_b,
        seed=seed,
    )["differences"]


def run_experiment(
    n_users: int,
    p_a: float,
    p_b: float,
    seed: int = 42,
):
    """
    Simulate one A/B experiment.

    Parameters
    ----------
    n_users:
        Number of users assigned to each version.

    p_a:
        True conversion probability of Version A.

    p_b:
        True conversion probability of Version B.

    seed:
        Random seed used to make the simulation reproducible.

    Returns
    -------
    dict
        Experiment results for A and B.
    """

    # Create our random-number generator.
    rng = np.random.default_rng(seed)

    # Number of successful conversions for Version A.
    conversions_a = rng.binomial(
        n=n_users,
        p=p_a,
    )

    # Number of successful conversions for Version B.
    conversions_b = rng.binomial(
        n=n_users,
        p=p_b,
    )

    # Observed conversion rates.
    rate_a = conversions_a / n_users
    rate_b = conversions_b / n_users

    # Observed difference.
    difference = rate_b - rate_a

    return {
        "conversions_a": conversions_a,
        "conversions_b": conversions_b,
        "rate_a": rate_a,
        "rate_b": rate_b,
        "difference": difference,
    }