import pandas as pd
import numpy as np
import scipy.optimize as optimize
from os.path import join
from matplotlib import pyplot as plt
from scipy.integrate import odeint
from scipy.stats import linregress


def get_dfs(path):
    meta = pd.read_csv(join(path, "metadata.csv"))
    raw = pd.read_csv(join(path, "measurements.csv"))
    return meta, raw


def mask_df(df, t1, t2):
    for i, row in df.iterrows():
        if row["time"] >= t1:
            t0 = row["time"]
            break
    df = df[(df["time"] >= t1) & (df["time"] <= t2)]
    df.loc[:, "time"] = df.loc[:, "time"] - t0
    return df


def plot_OD(df, t1=None, t2=None):
    if (t1 is not None) | (t2 is not None):
        df = df[(df["time"] > t1) & (df["time"] < t2)]
    for c in df.columns[1:]:
        plt.plot(df["time"], df[c], label=c)
    plt.xlabel("Time [h]"), plt.ylabel("OD")
    plt.legend()
    plt.show()


def get_n0_series(series):
    for value in series:
        if value > 0:
            return value


def get_n0(df):
    n0s = []
    for c in df.columns[1:]:
        n0s.append(get_n0_series(df[c]))
    return np.average(n0s)


def get_yield_series(series, c0):
    return (max(series) - get_n0_series(series)) / c0


def get_yield(df, c0):
    qs = []
    for c in df.columns[1:]:
        qs.append(get_yield_series(df[c], c0))
    return np.average(qs)


def fit_max_growth_rate(df, t1, t2, plot=True):
    vs = []
    df = df[(df["time"] >= t1) & (df["time"] <= t2)]
    for c in df.columns[1:]:
        slope, intercept, r_value, p_value, std_err = linregress(
            df["time"].to_numpy(), np.log(df[c].to_numpy())
        )
        vs.append(slope)
    v = np.average(vs)
    if plot:
        n0 = get_n0(df)
        fit = [n0 * np.exp(v * t) for t in df["time"]]
        for c in df.columns[1:]:
            plt.plot(df["time"], df[c], label=c)
        plt.plot(df["time"], fit, label="Model", linestyle="--")
        plt.legend()
        plt.show()
    return v


def monod(y, t, v, Km, q):
    n, c = y
    dndt = v * c / (Km + c) * n
    dcdt = -v * c / (Km + c) * n / q
    return np.array([dndt, dcdt])


def simulate_monod(Km, v, t, q, n, c0, n0):
    y = odeint(monod, [n0, c0], t, args=(v, Km[0], q))
    return np.sum((n - y[:, 0]) ** 2)


def get_Km(t, series, c0, n0, v, q):
    Km = optimize.minimize(
        simulate_monod,
        [0.1],
        args=(
            v,
            t,
            q,
            series,
            c0,
            n0,
        ),
        bounds=((0, 100),),
    ).x
    return Km[0]


def fit_Km(df, v, c0):
    Kms = []
    for c in df.columns[1:]:
        n0, q = get_n0_series(df[c]), get_yield_series(df[c], c0)
        Kms.append(get_Km(df["time"].to_numpy(), df[c].to_numpy(), c0, n0, v, q))
    return np.average(Kms)


def plot_fit(df, Km, v, n0, q, c0):
    plt.figure(figsize=(10, 6))
    for c in df.columns[1:]:
        plt.plot(df["time"].to_numpy(), df[c], label=c)

    y = odeint(
        monod,
        [n0, c0],
        df["time"].to_numpy(),
        args=(v, Km, q),
    )
    plt.plot(df["time"].to_numpy(), y[:, 0], label="Model", linestyle="--")

    plt.xlabel("Time")
    plt.ylabel("OD")
    plt.legend()
    plt.show()
