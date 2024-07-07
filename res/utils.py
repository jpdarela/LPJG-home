from pathlib import Path
from netCDF4 import Dataset
import cftime
import numpy as np
from numba import jit
import pandas as pd


def read_gridlist(gridlist_filemane):
    """

    :param gridlist_filemane:

    """
    with open(gridlist_filemane, mode="r") as gridfile:
        gridlist = []
        for line in gridfile.readlines():
            gridlist.append(line.strip().split("\t"))
        gridlist = list(map(lambda P:[np.array(float(P[0]), "f4"), np.array(float(P[1]), "f4"), P[2]], gridlist))

    sites_coordinates =  dict(list(map(lambda P:(P[2].split("-")[-1], P[:3]), gridlist)))
    return gridlist, sites_coordinates


def make_gridlist(filename):
    """Create a gridlist from a SMARTIO out file

    :param filename:

    """
    assert Path(filename).exists(), "need a smartIO out file to extract the metadata for the grdlist"
    with Dataset(filename) as ds:
        lon = ds.groups["Base"].variables["Longitude"][:]
        lat = ds.groups["Base"].variables["Latitude"][:]
        st = ds.groups["Base"].variables["Station"][:]
    coord = []
    s = 0
    for x, y in zip(lon,lat):
        coord.append([np.array([x,]), np.array([y,]), str(st[s])])
        s += 1
    sites_coordinates =  dict(list(map(lambda P:(P[2].split("-")[-1], P[:3]), coord)))
    return coord, sites_coordinates


def mask_gridlist(outfile, gridlist, mask_file, variable="mask"):
    """Mask a gridlist file using a geographiic mask

    Args:
        outfile (str): gridlist file name without extension. The file is writen in the ../grd/ folder
        gridlist (str): gridlist file path
        mask_file (str): mask file path
        variable (str, optional): variable with mask data in the mask_file netCDF. Defaults to "mask".
    """

    with Dataset(mask_file, "r") as ds:
        mask = np.flipud(ds.variables[variable][:].mask)

    data = pd.read_csv(gridlist, sep='\t', names=['longitude', 'latitude', 'site_name'])

    data['mask'] = data.apply(lambda row: mask[find_coord(row['latitude'], row['longitude'])], axis=1)

    np.savetxt(f"../grd/{outfile}.grd",
               data[data.apply(lambda x: x['mask'] == False, axis=1)].__array__()[:,:3],
               fmt="%.2f\t%.2f\t%s",
               delimiter="\t")


@jit(nopython=True)
def find_coord(N: float, W: float, res: float = 0.5, rounding: int = 2) -> tuple[int, int]:
    """It finds the indices for a given latitude and longitude in a <res> degree resolution grid

    Args:
        N (float): latitude in decimal degrees north
        W (float): longitude in decimal degrees west
        res (float, optional): grid resolution. Defaults to 0.5 degrees.
        rounding (int, optional): decimal significant digits. Defaults to 2.

    Returns:
        tuple[int, int]: (y, x) indices for the given latitude and longitude
        in the grid (0,0) is the upper left corner. Feeding the function with
        lat/long outside the boundaries(-180 - 180; -90 - 90) geographic coordinates
        will cause the function to return invalid indices in the grid.
    """

    Yc:float = round(N, rounding)
    Xc:float = round(W, rounding)

    half_res:float = res / 2
    Ymin:float = -90 + half_res
    Xmin:float = -180 + half_res

    # Generate longitude and latitude arrays (cell center coordinates)
    lon = np.arange(Xmin, 180, res)
    lat = np.arange(Ymin, 90, res)

    # Find indices for Yc and Xc using searchsorted
    # Yc is negative because our origin (-90 degrees north) is in the upper left corner.
    Yind = np.searchsorted(lat, -Yc - half_res, side='left')
    Xind = np.searchsorted(lon, Xc - half_res, side='left')

    if Yc > 90:
        Yind = -1
    if Xc < -180:
        Xind = -1

    return Yind, Xind


def rm_leapday_idx(date_range:pd.date_range):

    """xclude leap days from a pandas date_range> Return a new index object

    :param date_range:pd.date_range:

    """
    to_exclude = []
    for n, i in enumerate(date_range):
        if i.day == 29 and i.month == 2:
            to_exclude.append(n)

    return list(map(lambda P: cftime.datetime(P.year, P.month, P.day, calendar="noleap"), date_range.delete(to_exclude)))


def cf_date2str(cftime_in):
    """

    :param cftime_in:

    """
    return ''.join(cftime_in.strftime("%Y%m%d")[:10].split('-')).strip()


# @jit(nopython=True)
# def find_coord2(N:float, W:float, RES:float=0.5) -> tuple[int, int]:
#     """

#     not good
#     :param N:float: latitude in decimal degrees
#     :param W:float: Longitude in decimal degrees
#     :param RES:float: Resolution in degrees (Default value = 0.5)

#     """

#     Yc = round(N, 2)
#     Xc = round(W, 2)

#     Ymax = 90 - RES/2
#     Ymin = Ymax * (-1)
#     Xmax = 180 - RES/2
#     Xmin = Xmax * (-1)

#     # snap --- hook invalid values to the borders
#     if abs(Yc) > Ymax:
#         if Yc < 0:
#             Yc = Ymin
#         else:
#             Yc = Ymax

#     if abs(Xc) > Xmax:
#         if Xc < 0:
#             Xc = Xmin
#         else:
#             Xc = Xmax

#     Yind = 0
#     Xind = 0

#     lon = np.arange(Xmin, 180, RES)
#     lat = np.arange(Ymax, -90, RES * (-1))

#     while Yc < lat[Yind]:
#         Yind += 1

#     if Xc <= 0:
#         while Xc > lon[Xind]:
#             Xind += 1
#     else:
#         Xind += lon.size // 2
#         while Xc > lon[Xind]:
#             Xind += 1

#     return Yind, Xind





# Some functions dealing with conversions

# p50 and p88 in MPa
def cav_slope(p50, p88):
    """

    :param p50:
    :param p88:

    """
    return 2 / np.log(p50/p88)

def p50(p88, cav_slope):
    """

    :param p88:
    :param cav_slope:

    """
    return p88 * np.exp(2/cav_slope)

def p88(p50, cav_slope):
    """

    :param p50:
    :param cav_slope:

    """
    return p50 / np.exp(2/cav_slope)

# COnvert conductance from flux (mmol m-2 s-1) to (velocity cm/s)
def mol2vel(mmol):
    """

    :param mmol:

    """
    return mmol / 410 # cm/s

def vel2mol(vel):
    """

    :param vel:

    """
    return vel * 410

def gC(vpd_nonzero, flux, LAMBDA=2477, GAMMA=0.065, CP_AIR=1.005, RHO_WATER=998, RHO_AIR=1.1644):
    """

    :param vpd_nonzero:
    :param flux:
    :param LAMBDA:  (Default value = 2477)
    :param GAMMA:  (Default value = 0.065)
    :param CP_AIR:  (Default value = 1.005)
    :param RHO_WATER:  (Default value = 998)
    :param RHO_AIR:  (Default value = 1.1644)

    """
    return LAMBDA * GAMMA / CP_AIR * RHO_WATER / RHO_AIR * flux / (-vpd_nonzero)

def what_is_x_when_y_is(inpt, x, y):
    """

    :param inpt:
    :param x:
    :param y:

    """
    return x[y.searchsorted(inpt, 'left')]

def interp_x_from_y(inpt, x, y):
    """

    :param inpt:
    :param x:
    :param y:

    """
    return np.interp(inpt, y, x)

def find_max_vpd(gc_target=25):
    """

    :param gc_target:  (Default value = 25)

    """
    vpd = np.linspace(-1e-3, -4, int(1e4))
    deltaPsi = np.linspace(2.5e-7, 9.5e-5, 100)

    fh = open("out.txt", 'w')
    fh.write("VPD_MAX,flux\r\n")
    for i in deltaPsi:
        gc = gC(vpd, float(i))
        order = gc.argsort()
        x = vpd[order]
        y = gc[order]
        fh.write(f"{what_is_x_when_y_is(gc_target, x, y)},{i}\r\n")
        print(f"DeltaPsi = {i} - VPD = {what_is_x_when_y_is(gc_target, x, y)}")
    fh.close()

def convert_PAR_Joules_to_Watts(value_in_Joules):
    """

    :param value_in_Joules:value in Joules/m2/day

    1 joule per second == 1 watt (J m-2 s-1)

    return: value in Watts/m2

    """
    return value_in_Joules * 1.157407407e-5

def convert_PAR_Watts_to_Joules(value_in_Watts):
    """

    :param value_in_Watts:value in Watts/m2

    return: value in Joules/m2/day

    """
    return value_in_Watts * 86400

def convert_PAR_Watts_to_mol(value_in_Watts):
    """

    :param value_in_Watts:value in watts/m2

    return: value in µmol/m2/s

    1 W/m2 == 4.6 µmol/m2/s
    Fraction of PAR in the 400-700 nm range is 0.46


    """
    return value_in_Watts * 2.116