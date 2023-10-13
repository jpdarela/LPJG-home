from os import makedirs, linesep
from sys import argv, platform
from netCDF4 import Dataset
import numpy as np
from numba import jit

INPUT_FILES = ["GLDAS", "ISIMIP_SA"]
assert argv[1] in INPUT_FILES, f"input files must be one of: {INPUT_FILES}"

input_dataset = argv[1]

mask_ds = Dataset("./msk/amz_basin.nc")
mask = np.flipud(mask_ds.variables["Band1"][...].mask)
mask_ds.close()

input_files = dict(
    GLDAS = "./GLDAS/GLDAS_1948_2010_prec_daily_half.nc",
    ISIMIP_SA = "./ISIMIP_SA/pr_sa_1979_2016_watch-wfdei.nc")


makedirs("./grd", exist_ok=True)


@jit(nopython=True)
def find_coord(N, W, RES=0.5):

    Yc = round(N, 2)
    Xc = round(W, 2)

    Ymax = 90 - RES/2
    Ymin = Ymax * (-1)
    Xmax = 180 - RES/2
    Xmin = Xmax * (-1)

    # snap --- hook invalid values to the borders
    if abs(Yc) > Ymax:
        if Yc < 0:
            Yc = Ymin
        else:
            Yc = Ymax

    if abs(Xc) > Xmax:
        if Xc < 0:
            Xc = Xmin
        else:
            Xc = Xmax

    Yind = 0
    Xind = 0

    lon = np.arange(Xmin, 180, RES)
    lat = np.arange(Ymax, -90, RES * (-1))

    while Yc < lat[Yind]:
        Yind += 1

    if Xc <= 0:
        while Xc > lon[Xind]:
            Xind += 1
    else:
        Xind += lon.size // 2
        while Xc > lon[Xind]:
            Xind += 1

    return Yind, Xind


def read_crs():
    dt = Dataset(input_files[input_dataset])
    names = dt.variables["station"][:]
    lat = dt.variables["lat"][:]
    lon = dt.variables["lon"][:]
    station_names = [f"station_{str(n)}" for n in names]
    dt.close()
    return input_dataset, lon, lat, station_names


def write_gridlist(fname, lon , lat, names):
    if platform == "win32":
        endline = "\n"
    else:
       endline = "\r\n"
    with open(f"./grd/{fname}.grd", 'w', encoding="utf-8") as fh:
        for i, nm in enumerate(names):
            y, x = find_coord(lat[i], lon[i])
            if not mask[y, x]:
                fh.write(f"{str(round(lon[i], 2))}\t{str(round(lat[i], 2))}\t{nm}{endline}")

def main():
    write_gridlist(*read_crs())

if __name__ == "__main__":
    main()
