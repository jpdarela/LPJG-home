# plot_utils.py

from pathlib import Path
from typing import List, Union

import matplotlib.axes
import matplotlib.pyplot as plt

import pandas as pd

from post_processing import reader, guess_data

def make_reader(dset:str="sio_reader", time_int:str="Monthly", exp:str="t1"):
    """
    :param dset:str: one of "GLDAS", "FLUXNET2015", "ISIMIP_SA", "sio_reader"
    :param monthly:bool: Is the dataset in monthly timesteps? If false, annually data.
    :param exp:str: string with the experient name (a folder containing the netcdf files )

    """
    res = Path(f"./").resolve()
    fname = Path(f"{time_int}Out.nc")
    experiment = res/Path(exp)
    assert experiment.exists(), f"No experiment results ins {str(experiment)}"

    return reader[dset](experiment/fname)

def getNvars(v1, exp, ti, grd, pft):
    rd = make_reader(exp=exp, time_int=ti)
    return rd.make_df(v1, grd, pft)

def make_func(reader:guess_data, var:str, pft:int):
    return lambda x: reader.make_df(var, x, pft)

def mapit(func, iter):
    return pd.DataFrame(list(map(func, iter))).T

def extract_var(exp, ti, var, pft):
    rd = make_reader(exp=exp, time_int=ti)
    return mapit(make_func(rd, var, pft), rd.ngrd_range)

def plot_multi(
    data: pd.DataFrame,
    x: Union[str, None] = None,
    y: Union[List[str], None] = None,
    spacing: float = 0.1,
    **kwargs
) -> matplotlib.axes.Axes:
    """Plot multiple Y axes on the same chart with same x axis.

    Args:
        data: dataframe which contains x and y columns
        x: column to use as x axis. If None, use index.
        y: list of columns to use as Y axes. If None, all columns are used
            except x column.
        spacing: spacing between the plots
        **kwargs: keyword arguments to pass to data.plot()

    Returns:
        a matplotlib.axes.Axes object returned from data.plot()

    Example:
    >>> plot_multi(df, figsize=(22, 10))
    >>> plot_multi(df, x='time', figsize=(22, 10))
    >>> plot_multi(df, y='price qty value'.split(), figsize=(22, 10))
    >>> plot_multi(df, x='time', y='price qty value'.split(), figsize=(22, 10))
    >>> plot_multi(df[['time price qty'.split()]], x='time', figsize=(22, 10))

    See Also:
        This code is mentioned in https://stackoverflow.com/q/11640243/2593810
    """
    from pandas.plotting._matplotlib.style import get_standard_colors

    # Get default color style from pandas - can be changed to any other color list
    if y is None:
        y = data.columns

    # remove x_col from y_cols
    if x:
        y = [col for col in y if col != x]

    if len(y) == 0:
        return
    colors = get_standard_colors(num_colors=len(y))

    if "legend" not in kwargs:
        kwargs["legend"] = False  # prevent multiple legends

    # First axis
    ax = data.plot(x=x, y=y[0], color=colors[0], **kwargs)
    ax.set_ylabel(ylabel=y[0])
    lines, labels = ax.get_legend_handles_labels()

    for i in range(1, len(y)):
        # Multiple y-axes
        ax_new = ax.twinx()
        ax_new.spines["right"].set_position(("axes", 1 + spacing * (i - 1)))
        data.plot(
            ax=ax_new, x=x, y=y[i], color=colors[i % len(colors)], **kwargs
        )
        ax_new.set_ylabel(ylabel=y[i])

        # Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label

    ax.legend(lines, labels, loc=0)
    return ax

