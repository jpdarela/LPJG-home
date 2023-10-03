from pathlib import Path
from os import makedirs

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from post_processing import reader, guess_data, GRIDLIST
import pandas as pd

# Date time conversion registration
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


res = Path(f"./").resolve()
fname = Path(f"MonthlyOut.nc")

new = Path("exp1")
std = Path("std")

figs = Path(f"./figures").resolve()

makedirs(figs, exist_ok=True)

dt_new = guess_data(res/new/fname)
# dt_std = guess_data(res/std/fname)

grd_range = range(len(GRIDLIST))
wcont_range = [f"wcont{x + 1}" for x in range(15)]

def mapcar(func, iter):
    return pd.DataFrame(list(map(func, iter))).T

def save_profile(df, name="SoilW", months=120):
    tzero = df.shape[0] - months
    dtime = df.index[tzero:]
    x_lims = mdates.date2num([dtime[0], dtime[-1]])
    y_lims = [1, 15]
    arr = df.__array__()[tzero:,:].T
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(16, 7))
    imx = ax.imshow(arr, cmap="viridis_r",extent=[x_lims[0], x_lims[1],  y_lims[0], y_lims[1]],
                    aspect="auto", vmin=0, vmax=18)
    ax.xaxis_date()
    date_format = mdates.DateFormatter("%Y-%m-%d")
    ax.xaxis.set_major_formatter(date_format)
    ax.set_ylabel("Soil layers")

    cbar = plt.colorbar(imx, ax=ax, orientation='vertical',  spacing='proportional', shrink=0.60, pad=0)
    cbar.ax.set_ylabel("mm m-2")
    fig.autofmt_xdate()
    # plt.show()
    plt.savefig(figs / Path(f"profile_{name}.png"), dpi=300, transparent=True)
    plt.clf()
    plt.close(fig)

def save_png(df, ylab, name):
    df.plot()
    plt.ylabel(ylab)
    plt.savefig(figs / Path(f"{name}.png"), dpi=200)
    plt.clf()
    plt.close()

def plot_ts(df, ylab):
    df.plot()
    plt.ylabel(ylab)
    plt.show()
    plt.clf()
    plt.close()

def plot_soil_prof(guessData:guess_data, grd, pft, name):
    func = lambda x: guessData._make_data_frame(x, grd, pft)
    wp = mapcar(func, wcont_range)
    save_profile(wp, name=name)
    return wp

def plot_cveg(guessData:guess_data, pft=-1):
    get_cvegs = lambda x: guessData._make_data_frame("cveg", x, pft)
    cveg = mapcar(get_cvegs, grd_range)
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15,4))
    ax.set_ylabel("CVEG (kg m-2)")
    ax.set_xlabel("y")
    cveg.plot(ax=ax)
    ax.grid(True)
    plt.savefig(figs / Path(f"cveg_{guessData.pft_list[pft]}"))
    plt.clf()
    plt.close(fig)
    return cveg



if __name__ == "__main__":
    pass
    # get_npp0 = lambda x: dt_new._make_data_frame("npp", x, 0)
    # get_npp1 = lambda x: dt_new._make_data_frame("npp", x, 1)
    # # get_npp2 = lambda x: dt_new._make_data_frame("npp", x, 2)
    # # get_npp3 = lambda x: dt_new._make_data_frame("npp", x, 3)
    # get_npp4 = lambda x: dt_new._make_data_frame("npp", x, -1)
    # get_gpp = lambda x: dt_new._make_data_frame("gpp", x, -1)
    # get_gpph = lambda x: dt_new._make_data_frame("gpp", x, 3)
    # get_w = lambda x: dt_new._make_data_frame("wcont", x, -1)
    # get_w_r = lambda x: dt_new._make_data_frame("wcont", x, 3)
    # get_gcw = lambda x: dt_new._make_data_frame("gc_water", x, -1)
    # get_gc = lambda x: dt_new._make_data_frame("gc", x, -1)
    # get_et = lambda x: dt_new._make_data_frame("et", x, -1)
    # get_cveg = lambda x: dt_new._make_data_frame("cveg", x, -1)
    # get_psi_s = lambda x: dt_new._make_data_frame("psisoil", x, -1)
    # get_water_flow = lambda x: dt_new._make_data_frame("waterflow", x, -1)
    # get_wstress = lambda x: dt_new._make_data_frame("wstress", x, -1)
    # get_ar = lambda x: dt_new._make_data_frame("ar", x, -1)


    # cveg = mapcar(get_cveg, grd_range)
    # npp_iso = mapcar(get_npp0, grd_range)
    # npp_isoh = mapcar(get_npp3, grd_range)
    # water = mapcar(get_w, grd_range)
    # gpp_iso = mapcar(get_gpp, grd_range)
    # gpp_isoh = mapcar(get_gpph, grd_range)
