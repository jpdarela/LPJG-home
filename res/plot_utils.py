from pathlib import Path
from typing import List, Union, Callable

import matplotlib.axes
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from post_processing import reader, guess_data
from utils import find_coord

# bounding box for amazon basin / pan amazon at 0.5 degrees of resolution (360 x 720 grid)
xmin, xmax = 201, 260  #/xmax = 272
ymin, ymax = 170, 221  #/ymin = 160


def make_reader(dset:str="sio_reader", time_int:str="Monthly", exp:str="t1"):
    """Create a reader object for LPJ-GUESS output

    Args:
        dset (str, optional): Reader type: "FLUXNET2015" or "sio_reader". Defaults to "sio_reader".
        time_int (str, optional): time integration: "Daily", "Monthly", or "Annually". Defaults to "Monthly".
        exp (str, optional): folder name with SMARTIO output. Defaults to "t1".

    Returns:
        _type_: an instantiated reader based on the guess_data class defined in the post_processing module
    """

    res = Path(f"./").resolve()
    fname = Path(f"{time_int}Out.nc")
    experiment = res/Path(exp)
    assert experiment.exists(), f"No experiment results ins {str(experiment)}"

    return reader[dset](experiment/fname)


def get_data(reader:guess_data, variable:str, pft:int)->np.ndarray:
    """Use a guess_data reader to extract data from LPJ-GUESS smartio output
    for a given variable and PFT, and return the data (an maked array of rank
    (time, lat, lon), with fill_value/no_data=1e+20), variable name, PFT number, and reader object

    Args:
        reader (guess_data): a guess_data object
        variable (str): a string with a valid variable name
        pft (int): int PFT number (-1) for total

    Returns:
        (np.ma.masked_array, str, int, guess_data): a tuple with the data,
        variable name, pft number, and reader object
    """

    data = np.ma.masked_all((reader.periods, 360, 720), dtype=np.float32)

    for gridcell, lonlat in enumerate(reader.GRIDLIST):
        y, x = find_coord(float(lonlat[1]), float(lonlat[0]))
        data[:, y, x] = reader.make_df(variable, gridcell, pft_number=pft).__array__()

    return data[:, ymin:ymax, xmin:xmax], variable, pft, reader


def make_func(reader:guess_data, var:str, pft:int):
    return lambda x: reader.make_df(var, x, pft)


def read_grid(reader: guess_data, var: str, pft: int) -> Callable[[int], pd.DataFrame]:
    return lambda x: reader.make_df(var, x, pft)


def read_pft(reader: guess_data, var: str, grd: int) -> Callable[[int], pd.DataFrame]:
    return lambda x: reader.make_df(var, grd, x)


def mapit(func, iter):
    return pd.DataFrame(list(map(func, iter))).T


def extract_var_grid(exp, ti, var, pft, dset="FLUXNET2015"):
    """_summary_

    Args:
        exp (str): folder name with SMARTIO output
        ti (str): time integration: "Daily", "Monthly" or "Annually"
        var (str): LPJ-GUESS variable name
        pft (int): PFT number
        dset (str): dataset name: "FLUXNET2015" or "sio_reader"

    Returns:
        _type_: pandas DataFrame with the variable values for each gridcell
    """
    rd = make_reader(dset=dset, exp=exp, time_int=ti)
    df =  mapit(read_grid(rd, var, pft), rd.ngrd_range)
    rd.close()
    return df


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

