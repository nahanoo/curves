import pandas as pd
import numpy as np
import scipy.optimize as optimize
import numba
from matplotlib import pyplot as plt
from scipy.integrate import odeint
from scipy.stats import linregress


def get_df(path):
    return pd.read_csv(path)


def mask_df(df, wells):
    return df[["time"] + wells]


def get_n0(series):
    for value in series:
        if value > 0:
            return value


def get_yield(series, c0):
    return (max(series) - get_n0(series)) / c0


def get_max_growth_rate(series, intervals):
    return max(np.gradient(series) / series) * intervals


def lin_regression(t, series):
    slope, intercept, r_value, p_value, std_err = linregress(t, np.log(series))
    return slope


def monod(y, t, v, Km, q):
    n, c = y
    dndt = v * c / (Km + c) * n
    dcdt = -v * c / (Km + c) * n / q
    return np.array([dndt, dcdt])


def simulate_monod(Km, v, t, q, n, c0, n0):
    y = odeint(monod, [n0, c0], t, args=(v, Km[0], q))
    return np.sum((n - y[:, 0]) ** 2)


def fit_yield(df, c0):
    qs = []
    for c in df.columns[1:]:
        qs.append(get_yield(df[c], c0))
    return np.average(qs)


def fit_n0(df):
    n0s = []
    for c in df.columns[1:]:
        n0s.append(get_n0(df[c]))
    return np.average(n0s)


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


def plot_OD(df, t1=None, t2=None):
    if (t1 is not None) | (t2 is not None):
        df = df[(df["time"] > t1) & (df["time"] < t2)]
    for c in df.columns[1:]:
        plt.plot(df["time"], df[c], label=c)
    plt.legend()
    plt.show()


def fit_max_growth_rate(df, t1, t2, n0, plot=True):
    vs = []
    df = df[(df["time"] > t1) & (df["time"] < t2)]
    for c in df.columns[1:]:
        vs.append(lin_regression(df["time"], df[c].to_numpy()))
    v = np.average(vs)
    fit = [n0 * np.exp(v * t) for t in df["time"]]
    if plot:
        for c in df.columns[1:]:
            plt.plot(df["time"], df[c], label=c)
        plt.plot(df["time"], fit)
        plt.legend()
        plt.show()
    return v


def plot_fit(df, Km, v, n0, q, c0):
    # Plotting
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


meta = pd.read_csv(
    "~/ChiBioFlow/data/at_oa/240808_ct_oa_plate_reader/metadata.csv", index_col=0
)
raw = pd.read_csv("~/ChiBioFlow/data/at_oa/240808_ct_oa_plate_reader/measurements.csv")
df = pd.DataFrame(columns=["time", "OD", "well"])


def ct():
    species = "Comamonas testosteroni"
    conc = 15
    mask = (meta["species"] == species) & (meta["cs_conc"] == 15)
    columns = list(set(meta[mask]["linegroup"]))
    ct15 = raw[["time"] + columns]
    ct15 = ct15.dropna()
    ct15 = ct15[ct15["time"] < 30]
    n0 = fit_n0(ct15)
    q = fit_yield(ct15, 15)
    v = fit_max_growth_rate(ct15, 0, 6, n0)
    Km = get_Km(ct15["time"].to_numpy(), ct15[ct15.columns[2]], 15, 0.01, v, q)
    plot_fit(ct15, Km, v, n0, q, 15)


species = "Ochrobactrum anthropi"
conc = 15
mask = (meta["species"] == species) & (meta["cs_conc"] == 15)
columns = list(set(meta[mask]["linegroup"]))
ct15 = raw[["time"] + columns]
ct15 = ct15.dropna()
ct15 = ct15[(ct15["time"] < 30) & (ct15["time"] > 13)]
n0 = fit_n0(ct15)
q = fit_yield(ct15, 15)
v = fit_max_growth_rate(ct15, 13, 18, n0, plot=False)
Km = get_Km(ct15["time"].to_numpy(), ct15[ct15.columns[2]], 15, 0.01, v, q)
plot_fit(ct15, Km, v, n0, q, 15)


# Km, n0, q = fit_params(ct15, 15, v)
# plot_max_growth_rate(ct15, 6, vline=3.5)
