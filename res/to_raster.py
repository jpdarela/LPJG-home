#!/home/jpdarela/.pyenv/shims/python

import os
from pathlib import Path

import cftime
from netCDF4 import Dataset

import numpy as np

from post_processing import reader, guess_data
from utils import find_coord


# functionality to convert smartio to CF netcdf4 files
# good format for post processing (cdo, nco) and analysis


# Set an output folder
nc_out = "./cf_outputs"
os.makedirs(nc_out, exist_ok=True)

# bounding box for amazon basin / pan amazon at 0.5 degrees of resolution (360 x 720 grid)
xmin, xmax = 201, 260  #/xmax = 272
ymin, ymax = 170, 221  #/ymin = 160

# Smartio reader
def make_reader(dset:str, monthly:bool, exp:str):
    """
    :param dset:str: one of "GLDAS", "FLUXNET2015", "ISIMIP_SA", "generic_reader"
    :param monthly:bool: Is the dataset in monthly timesteps? If false, annually data.
    :param exp:str: string with the experient name (a folder containing the netcdf files )

    """
    res = Path(f"./").resolve()
    fname = Path(f"{'Monthly' if monthly else 'Annually'}Out.nc")
    experiment = Path(exp)

    return reader[dset](res/experiment/fname)

def get_data(reader:guess_data, variable:str, pft:int)->np.ndarray:
    """use a guess_data reader to extract data from sio

    :param reader: a guess_data object
    :param variable:str: a string with a valid variable name
    :param pft:int: int PFT number (-1) for total

    """
    data = np.zeros(shape=(reader.periods, 360, 720)) - 9999.0

    for gridcell, lonlat in enumerate(reader.GRIDLIST):
        y, x = find_coord(float(lonlat[1]), float(lonlat[0]))
        data[:, y, x] = reader.make_df(variable, gridcell, pft_number=pft).__array__()

    return data[:, ymin:ymax, xmin:xmax], variable, pft, reader

def create_lband(res=0.5):
    """

    :param res: Resolution in degrees (Default value = 0.5)

    """
    lon = np.arange(-179.75, 180, res, dtype=np.float64)[xmin:xmax]
    lat = np.arange(89.75, -90, -res, dtype=np.float64)[ymin:ymax][::-1]
    half = res / 2.0
    latbnd = np.array([[l - half, l + half] for l in lat])
    lonbnd = np.array([[l - half, l + half] for l in lon])

    return lat, latbnd, lon, lonbnd

def cf_date2str(cftime_in):
    """

    :param cftime_in:

    """
    return ''.join(cftime_in.strftime("%Y%m%d")[:10].split('-')).strip()

def write_nc(arr, var, pft, reader, nc_out=nc_out):
    """

    :param arr:
    :param var:
    :param pft:
    :param reader:
    :param nc_out:  (Default value = nc_out)

    """

    NO_DATA = [-9999.0, -9999.0]
    time_index = reader.time_index
    time_units = reader.time_unit
    calendar = reader.calendar

    geo_v = create_lband()
    lat = geo_v[0]
    lat_bnds = geo_v[1]
    lon = geo_v[2]
    lon_bnds = geo_v[3]

    t0 = cf_date2str(cftime.num2date(time_index[0], time_units, calendar))[:4]
    tf = cf_date2str(cftime.num2date(time_index[-1], time_units, calendar))[:4]

    nc_filename = os.path.join(nc_out, Path(f'{var}_{reader.pft_list[pft]}_{reader.freq}_{t0}-{tf}_{reader.filepath.parent.name}.nc4'))
    with Dataset(nc_filename, mode='w', format='NETCDF4', ) as rootgrp:
        # dimensions  & variables
        rootgrp.createDimension("latitude", lat.size)
        rootgrp.createDimension("longitude", lon.size)
        rootgrp.createDimension("bnds", size=2)
        rootgrp.createDimension("time", None)

        # BOUNDS
        YB = rootgrp.createVariable(
            "lat_bnds", lat_bnds.dtype, ("latitude", "bnds"))
        XB = rootgrp.createVariable(
            "lon_bnds", lon_bnds.dtype, ("longitude", "bnds"))

        time = rootgrp.createVariable("time", np.float64, ("time",))

        latitude = rootgrp.createVariable(
            "latitude", lat.dtype, ("latitude",))
        longitude = rootgrp.createVariable(
            "longitude", lon.dtype, ("longitude",))
        var_ = rootgrp.createVariable(varname=var, datatype=np.float32,
                                        dimensions=(
                                            "time", "latitude", "longitude",),
                                        zlib=True, fill_value=NO_DATA[0],fletcher32=True)

        # attributes
        rootgrp.description = f"{var} - PFT={reader.pft_list[pft]} from LPJ-GUESS(v4.1) SMARTIO output module "
        rootgrp.source = "LPJ-GUESS model outputs - darelafilho@gmail.com"
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
        # var
        var_.units = reader.var_units[var]
        var_.missing_value = NO_DATA[0]

        # WRITING DATA
        out_arr = np.fliplr(arr)
        var_[:, :, :] = np.ma.masked_array(
            out_arr, mask=out_arr == NO_DATA[0])

def sio_to_cf(reader, var, pft):
    """

    :param reader:
    :param var:
    :param pft:

    """
    write_nc(*get_data(reader, var, pft))

if __name__ == "__main__":

    # # Multile ins run
    # ins_res = [f"Hyd_{x}" for x in range(37)]
    # exps = [f"out230914_i37g500_b_jp/{i}" for i in ins_res]
    # for exp in exps:
    #     rm = make_reader(False, exp)
    #     for x in [0,]:
    #         sio_to_cf(rm, "cmass_loss_cav", x)

    exps = ["test_TrBR",]
    dset = "GLDAS"
    pfts = [0,1,-1]

    for exp in exps:
        rm = make_reader(dset, False, exp)
        for x in pfts:
            # sio_to_cf(rm, "cmass_loss_bg", x)
            # sio_to_cf(rm, "cmass_loss_greff", x)
            sio_to_cf(rm, "cmass_leaves", x)
            sio_to_cf(rm, "cveg", x)
            sio_to_cf(rm, "cmass_loss_cav", x)
            sio_to_cf(rm, "et", x)
            sio_to_cf(rm, "npp", x)
            sio_to_cf(rm, "gpp", x)
            sio_to_cf(rm, "ar", x)
            sio_to_cf(rm, "fpc", x)
            sio_to_cf(rm, "lai", x)

    for exp in exps:
        rm = make_reader(dset, True, exp)
        for x in pfts:

            sio_to_cf(rm, "et", x)
            sio_to_cf(rm, "npp", x)
            sio_to_cf(rm, "gpp", x)
            sio_to_cf(rm, "ar", x)
