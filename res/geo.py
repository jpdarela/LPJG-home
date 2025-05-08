import numpy as np
from utils import find_coord


# Regions defined in the end of the file

def define_region(north:float, south:float, west:float, east:float, res:float=0.5, rounding:float=2):
    """define a bounding box for a given region of interest

    Args:
        north (float): Northernmost latitude. Units: degrees north.
        south (float): Southernmost latitude. Units: degrees north.
        west (float): Westernmost longitude. Units: degrees east.
        east (float): Easternmost longitude. Units: degrees east.
        res (float, optional): grid resolution. Defaults to 0.5 decimal degrees.
        rounding (int, optional): by default, coordinates are rounded.
        This sets the number of decimal digits. Defaults to 2.

    Returns:
        dict: bbox dictionary with keys ymin, ymax, xmin, xmax
    """
    ymin, xmin = find_coord(north, west, res, rounding)
    ymax, xmax = find_coord(south, east, res, rounding)

    return {"ymin": ymin, "ymax": ymax, "xmin": xmin, "xmax": xmax}


def get_region(region):
    """
    Get bounding box for a region of interest
    """
    return region["ymin"], region["ymax"], region["xmin"], region["xmax"]


def create_latlon_bands(ymin, ymax, xmin, xmax, res=0.5):
    """

    :param res: Resolution in degrees (Default value = 0.5)

    """
    half_res:float = res / 2
    Ymax:float = 90 - half_res
    Xmin:float = -180 + half_res

    lon = np.arange(Xmin, 180, res, dtype=np.float64)[xmin:xmax]
    lat = np.arange(Ymax, -90, -res, dtype=np.float64)[ymin:ymax][::-1]

    latbnd = np.array([[l - half_res, l + half_res] for l in lat])
    lonbnd = np.array([[l - half_res, l + half_res] for l in lon])

    return lat, latbnd, lon, lonbnd


# Bbox
pan_amazon_bbox = {"north":4.75, "south":-20.75, "west":-79.25, "east":-49.75}
global_bbox = {"north":90, "south":-90, "west":-180, "east":180}

germany_bbox = {"north":55.1, "south":47.3, "west":5.9, "east":15.2}

# Regions
global_region = define_region(**global_bbox)
pan_amazon_region = define_region(**pan_amazon_bbox)
