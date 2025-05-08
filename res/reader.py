from pathlib import Path
from typing import Callable, Collection, Union

import numpy as np
import pandas as pd

from geo import get_region
from guess_data import reader, guess_data
from utils import find_coord

# bounding box for amazon basin / pan amazon at 0.5 degrees of resolution (360 x 720 grid)


def make_reader(dset:str="sio_reader", time_int:str="Monthly", exp:Union[str, None]=None):
    """Create a reader object for LPJ-GUESS output. The reader object is based on the guess_data
    class defined in the guess_data module. The instance returned here should be closed after
    use in order to properly close the netCDF file. Use the close() method of the reader object.

    Args:
        dset (str, optional): Reader type Defaults to "sio_reader".
        time_int (str, optional): time integration: "Daily", "Monthly", or "Annually". Defaults to "Monthly".
        exp (str, optional): folder name with SMARTIO output. Defaults to None.

    Returns:
        guess_reader: an instantiated reader based on the guess_data class defined in the guess_data module
    """
    assert exp is not None, "Need to provide an experiment folder name to create the reader"

    res = Path(f"./").resolve()
    fname = Path(f"{time_int}Out.nc")
    experiment = res/Path(exp)
    assert experiment.exists(), f"No experiment results ins {str(experiment)}"

    return reader[dset](experiment/fname)


def get_data(reader:guess_data, variable:str, pft:int, region:dict[str, int])->np.ma.MaskedArray[np.float32]:
    """Use a guess_data reader to extract data from LPJ-GUESS smartio output
    for a given variable and PFT, and return the data (a maked array of rank
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
    ymin, ymax, xmin, xmax = get_region(region)
    return data[:, ymin:ymax, xmin:xmax], variable, pft, reader


def read_grid(reader: guess_data, var: str, pft: int) -> Callable[[int], pd.Series]:
    """_summary_

    Args:
        reader (guess_data): _description_
        var (str): _description_
        pft (int): _description_

    Returns:
        Callable[[int], pd.Series]: _description_
    """
    return lambda grd: reader.make_df(var, grd, pft)


def read_pft(reader: guess_data, var: str, grd: int) -> Callable[[int], pd.Series]:
    """_summary_

    Args:
        reader (guess_data): _description_
        var (str): _description_
        grd (int): _description_

    Returns:
        Callable[[int], pd.Series]: _description_
    """
    return lambda pft: reader.make_df(var, grd, pft)


def mapit(func:Callable[[int], pd.Series], iter:Collection[int])-> pd.DataFrame:
    """_summary_

    Args:
        func (Callable[[int], pd.Series]): _description_
        iter (Collection[int]): list of integers reoresenting grid cells or pfts

    Returns:
        DataFrame: A dataframe with the results of the function func applied to each element of iter
    """
    return pd.DataFrame(list(map(func, iter))).T


def extract_var_grid(experiment:str, time_integration:str, var:str, pft:int, dset:str="FLUXNET2015"):
    """_summary_

    Args:
        experiment (str): _description_
        ti (str): _description_
        var (str): _description_
        pft (int): _description_
        dset (str, optional): _description_. Defaults to "FLUXNET2015".

    Returns:
        _type_: _description_
    """
    rd = make_reader(dset=dset, exp=experiment, time_int=time_integration)
    df =  mapit(read_grid(rd, var, pft), rd.ngrd_range)
    rd.close()
    return df

def extract_var_pft(experiment:str, time_integration:str, var:str, grd:int, dset:str="FLUXNET2015"):
    """_summary_

    Args:
        experiment (str): _description_
        ti (str): _description_
        var (str): _description_
        grd (int): _description_
        dset (str, optional): _description_. Defaults to "FLUXNET2015".

    Returns:
        _type_: _description_
    """
    rd:guess_data = make_reader(dset=dset, exp=experiment, time_int=time_integration)
    df =  mapit(read_pft(rd, var, grd), rd.npft_range)
    rd.close()
    return df

