from pathlib import Path
import os

import cftime
from netCDF4 import Dataset
import numpy as np

from utils import cf_date2str
from geo import create_latlon_bands, global_bbox
from post_processing import guess_data
from reader import get_data

#TODO docstring
def write_nc(arr:np.ndarray[np.float32],
             var:str,
             pft:int,
             reader:guess_data,
             nc_out:str,
             bbox:dict[str, int]=global_bbox)->None:
    """_summary_

    Args:
        arr (np.array[float]): _description_
        var (str): _description_
        pft (int): _description_
        reader (guess_data): _description_
        nc_out (str): _description_
        bbox (dict[str, int], optional): _description_. Defaults to global_bbox.
    """

    NO_DATA = [1e+20, 1e+20,]
    time_index = reader.time_index
    time_units = reader.time_unit
    calendar = reader.calendar

    geo_v = create_latlon_bands(**bbox)
    lat = geo_v[0]
    lat_bnds = geo_v[1]
    lon = geo_v[2]
    lon_bnds = geo_v[3]

    t0 = cf_date2str(cftime.num2date(time_index[0], time_units, calendar))[:4]
    tf = cf_date2str(cftime.num2date(time_index[-1], time_units, calendar))[:4]

    nc_filename = os.path.join(nc_out,
        Path(f'{var}_{reader.pft_list[pft]}_{reader.freq}_{t0}-{tf}_{reader.filepath.parent.name}.nc4'))

    with Dataset(nc_filename, mode='w', format='NETCDF4', ) as rootgrp:
        rootgrp.createDimension("latitude", lat.size)
        rootgrp.createDimension("longitude", lon.size)
        rootgrp.createDimension("bnds", size=2)
        rootgrp.createDimension("time", None)
        YB = rootgrp.createVariable(
            "lat_bnds", lat_bnds.dtype, ("latitude", "bnds"))
        XB = rootgrp.createVariable(
            "lon_bnds", lon_bnds.dtype, ("longitude", "bnds"))
        time = rootgrp.createVariable("time", np.float64, ("time",))
        latitude = rootgrp.createVariable(
            "latitude", lat.dtype, ("latitude",))
        longitude = rootgrp.createVariable(
            "longitude", lon.dtype, ("longitude",))
        var_ = rootgrp.createVariable(varname=var,
                                      datatype=np.float32,
                                      dimensions=("time", "latitude", "longitude",),
                                      fill_value=NO_DATA[0],
                                      compression="zlib",
                                      complevel=9,
                                      shuffle=True,
                                      least_significant_digit=4,
                                      fletcher32=True)

        # attributes
        rootgrp.description = f"{var} - PFT={reader.pft_list[pft]} from LPJ-GUESS-HYD(v4.1) SMARTIO output module "
        rootgrp.source = "LPyJ-GUESS"
        rootgrp.experiment = "TEST"

        # time
        time.units = time_units
        time.calendar = calendar
        time.axis = 'T'
        time[...] = time_index

        # lat
        latitude.units = u"degrees_north"
        latitude.long_name = u"latitude"
        latitude.standart_name = u"latitude"
        latitude.axis = u'Y'
        latitude[...] = lat
        YB[...] = lat_bnds

        # lon
        longitude.units = "degrees_east"
        longitude.long_name = "longitude"
        longitude.standart_name = "longitude"
        longitude.axis = u'X'
        longitude[...] = lon
        XB[...] = lon_bnds

        var_.units = reader.var_units[var]

        # WRITING DATA
        var_[:, :, :] = np.fliplr(arr)

#TODO docstring
def sio_to_cf(reader:guess_data, var:str, pft:int, ncout:str, bbox:dict[str, int])->None:
    """_summary_

    Args:
        reader (guess_data): _description_
        var (str): _description_
        pft (int): _description_
        ncout (str): _description_
        bbox (dict[str, int]): _description_
    """
    write_nc(*get_data(reader, var, pft, bbox=bbox), nc_out=ncout, bbox=bbox)
