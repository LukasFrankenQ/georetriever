import numpy as np
import logging


def get_mean_variance(
    means,
    vars,
    alphas,
    betas,
    n_samples=10_000,
):
    """
    Returns estimated mean and variance of random variable

    Z = \sum_{i=1}^n X_i * Y_i

    where X_i ~ N(\mu_i, \sigma_i^2) (with mus, and sigmas given) and
    {Y_1, ... , Y_{n-1}} is sampled uniformly from the (n-1)-simplex with lower
                         bounds alphas and upper bounds betas. Then we set
                         Y_n = 1 - \sum_{i=1}^{n-1} Y_i

    Since n is small (between 2 and 5, otherwise there will be a warning)
    we uniformly sample from the (n-1)-hyperrectangle (constrained by alphas
    and betas) and discard points outside the simplex.

    From this, mean and variance of the Y_i are computed. Using these
    we obtain

    E[Z] = \sum_{i=1}^n E[X_i] E[Y_i] and
    Var[Z] = \sum_{i=1}^n ( Var[X] Var[Y] + Var[X] E[Y]^2 + Var[Y] E[X]^2 )

    Args:
        means(np.ndarray[float]): means of X
        vars(np.ndarray[float]): variances of X
        alphas(np.ndarray[float]): lower bounds of Y
        betas(np.ndarray[float]): uppers bounds of Y
        n_samples(int): number of MC samples

    Returns:
        [float, float]: estimated mean and variance of Z
    """

    assert len(means) == len(vars) == len(alphas) == len(betas)
    assert (alphas.sum() <= 1.0) & (betas.sum() >= 1.0)

    if len(means.flatten()) == 1:
        return means.mean(), variances.mean()

    if len(means) > 6:
        logging.warning("Too many dimensions, estimates maybe inprecise")

    samples = np.random.uniform(
        low=alphas[:-1], high=betas[:-1], size=(n_samples, len(alphas) - 1)
    )

    mask = (1 - betas[-1] < samples.sum(axis=1)) & (
        samples.sum(axis=1) < 1.0 - alphas[-1]
    )

    samples = samples[mask]

    samples = np.vstack(
        [
            samples.T,
            1 - samples.sum(axis=1),
        ]
    ).T

    EYi = np.mean(samples, axis=0)
    VYi = np.var(samples, axis=0)

    mean = (means * EYi).sum()
    variance = (vars * VYi + vars * EYi**2 + means**2 * VYi).sum()

    return mean, variance


if __name__ == "__main__":

    import matplotlib.pyplot as plt

    plt.style.use("bmh")

    means = np.array([1, 2, 3])
    variances = np.ones(3) * 0.1

    alphas = np.array([0.0, 0.0, 0.5])
    betas = np.array([0.5, 0.5, 1.0])

    from scipy import stats

    colors = ["b", "r", "gold"]

    fig, axs = plt.subplots(1, 3, figsize=(16, 4))

    for i, (mean, std, c) in enumerate(zip(means, np.sqrt(variances), colors)):
        x = np.linspace(mean - 3 * std, mean + 3 * std, 300)

        axs[0].fill_between(
            x,
            np.zeros_like(x),
            stats.norm.pdf(x, loc=mean, scale=std),
            label=i + 1,
            linewidth=1.0,
            color=c,
            edgecolor="k",
            alpha=0.3,
        )

    for i, (lower, upper, c) in enumerate(zip(alphas, betas, colors)):

        axs[1].plot(
            [lower, lower], [0, 1], linewidth=1.5, alpha=0.7, label=i + 1, color=c
        )
        axs[1].plot([upper, upper], [0, 1], linewidth=1.5, alpha=0.7, color=c)

    axs[1].set_xlim(-0.05, 1.05)

    mean, var = get_mean_variance(means, variances, alphas, betas)
    std = np.sqrt(var)

    x = np.linspace(mean - 3 * std, mean + 3 * std, 300)

    axs[2].fill_between(
        x,
        np.zeros_like(x),
        stats.norm.pdf(x, loc=mean, scale=std),
        label="Result",
        linewidth=1.0,
        color="g",
        edgecolor="k",
        alpha=0.3,
    )
    axs[2].set_xlim(0, 4)

    for ax in axs:
        ax.legend()
        ax.set_axisbelow(True)

    plt.show()
