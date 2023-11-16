import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

dav = Path("./results_Dav")
tha = Path("./results_Tha")

species = ['Pic_abi',  'Pin_syl']
cpools = ['LitterC','SoilC']


def pj(a:Path, b:str)->Path:
    return Path(os.path.join(a, b))


def line_cleaner(a_list):
    return [float(x) for x in a_list.strip().split(' ') if x != '']


def header_cleaner(a_list):
    return [x for x in a_list.strip().split(' ') if x != '']


def prep_idx(s, e, FREQ):
    return pd.date_range(f"{s}0101", f"{e}-12-31", freq=FREQ)


def prep_idxm(s, a, b, FREQ):
    return pd.date_range(f"{s}0101", periods= a * b, freq=FREQ)


def read_a_file(base_path:Path, file:str)->pd.DataFrame:
    
    with open(pj(base_path, file), mode='r') as dt:
        dat_list = dt.readlines()
    
    y = len(dat_list) - 1
    x = len(line_cleaner(dat_list[-1]))
    arr = np.zeros(shape=(y, x))
    header = header_cleaner(dat_list.pop(0))
    for i in range(y):
        arr[i, :] = line_cleaner(dat_list[i])

    ds = pd.DataFrame(arr, columns=header)

    TIMESPAN = ds["Year"].__array__()
    s = str(int(TIMESPAN[0]))
    e = str(int(TIMESPAN[-1]))

    ds.index = prep_idx(s, e, "Y")
    return ds


def read_m_file(base_path:Path, file:str)->pd.Series:
    
    with open(pj(base_path, file), mode='r') as dt:
        dat_list = dt.readlines()
    
    y = dat_list.pop(0)
    y = len(dat_list)
    arr = np.array([])
    for x in range(y):
        data = np.array(line_cleaner(dat_list[x]))
        print(data[3:])
        arr = np.hstack((arr, np.array(data[3:])))

    ds = pd.Series(arr)
    ds2 = read_a_file(base_path, file)

    TIMESPAN = ds2["Year"].__array__()
    s = str(int(TIMESPAN[0]))

    ds.index=prep_idxm(s, y, 12, "M")

    return ds


def plot_series(dt, var, vname, units, title, site):
    # plt.figure(figsize=(8, 4)) 
    if type(dt) == pd.DataFrame:
        dt[var].plot(ylabel = f"{vname} ({units})", xlabel=title)
        if type(var) == str:
            x = "total"
        else:
            x = "group"

        plt.savefig(f"{vname}_{x}_{site}.png", dpi=300)
        plt.clf()
        
    elif type(dt) == pd.Series:

        dt.plot(ylabel = f"{vname} ({units})", xlabel=title)
        plt.savefig(f"{vname}_monthly_{site}.png", dpi=300)
        plt.clf()


def plot_fluxes():
    dt = read_a_file(dav, 'anpp.out')
    plot_series(dt, "Total", "NPP", "kg m-2 y-1", "Davos", 'dav')
    plot_series(dt, species, 'NPP' , "kg m-2 y-1", "Davos", 'dav')

    dt = read_a_file(dav, 'agpp.out')
    plot_series(dt, "Total", "GPP", "kg m-2 y-1", "Davos", 'dav')
    plot_series(dt, species, 'GPP' , "kg m-2 y-1", "Davos", 'dav')

    dt = read_a_file(dav, 'aaet.out')
    plot_series(dt, "Total", "AET", "mm month-1", "Davos", 'dav')
    plot_series(dt, species, 'AET' , "mm month-1", "Davos", 'dav')

    dt = read_a_file(tha, 'anpp.out')
    plot_series(dt, "Total", "NPP", "kg m-2 y-1", "Tharand", 'tha')
    plot_series(dt, species, 'NPP' , "kg m-2 y-1", "Tharand", 'tha')

    dt = read_a_file(tha, 'agpp.out')
    plot_series(dt, "Total", "GPP", "kg m-2 y-1", "Tharand", 'tha')
    plot_series(dt, species, 'GPP' , "kg m-2 y-1", "Tharand", 'tha')

    dt = read_a_file(tha, 'aaet.out')
    plot_series(dt, "Total", "AET", "mm month-1", "Tharand", 'tha')
    plot_series(dt, species, 'AET' , "mm month-1", "Tharand", 'tha')

def plot_pools():
    dt = read_a_file(dav, 'cmass.out')
    plot_series(dt, "Total", "CMASS", "kg m-2", "Davos", 'dav')
    plot_series(dt, species, 'CMASS' , "kg m-2", "Davos", 'dav')

    dt = read_a_file(tha, 'cmass.out')
    plot_series(dt, "Total", "CMASS", "kg m-2", "Tharand", 'tha')
    plot_series(dt, species, 'CMASS' , "kg m-2", "Tharand", 'tha')

    dt = read_a_file(dav, 'cpool.out')
    # plot_series(dt, "LitterC", "LitterC", "kg m-2", "Davos", 'dav')
    plot_series(dt, cpools, 'SoilC' , "kg m-2", "Davos", 'dav')

    dt = read_a_file(tha, 'cpool.out')
    # plot_series(dt, "LitterC", "LitterC", "kg m-2", "Tharand", 'tha')
    plot_series(dt, cpools, 'SoilC' , "kg m-2", "Tharand", 'tha')

    dt = read_a_file(dav, 'lai.out')
    plot_series(dt, "Total", "LAI", "m2 m-2", "Davos", 'dav')
    plot_series(dt, species, 'LAI' , "' m-2", "Davos", 'dav')

    dt = read_a_file(tha, 'lai.out')
    plot_series(dt, "Total", "LAI", "m2 'm-2", "Tharand", 'tha')
    plot_series(dt, species, 'LAI' , "m2 m-2", "Tharand", 'tha')

def plot_m():
    dt = read_m_file(dav, 'mgpp.out')
    plot_series(dt, None,  "GPP", "kg m-2 y-1", "Davos", 'dav')

    dt = read_m_file(tha, 'mgpp.out')
    plot_series(dt, None,  "GPP", "kg m-2 y-1", "Tharand", 'tha')

    dt = read_m_file(dav, 'mnpp.out')
    plot_series(dt, None,  "NPP", "kg m-2 y-1", "Davos", 'dav')

    dt = read_m_file(tha, 'mnpp.out')
    plot_series(dt, None,  "NPP", "kg m-2 y-1", "Tharand", 'tha')

    dt = read_m_file(dav, 'maet.out')
    plot_series(dt, None,  "AET", "kg m-2 month-1", "Davos", 'dav')

    dt = read_m_file(tha, 'maet.out')
    plot_series(dt, None,  "AET", "kg m-2 month-1", "Tharand", 'tha')

    dt = read_m_file(dav, 'mnee.out')
    plot_series(dt, None,  "NEE", "kg m-2 y-1", "Davos", 'dav')

    dt = read_m_file(tha, 'mnee.out')
    plot_series(dt, None,  "NEE", "kg m-2 y-1", "Tharand", 'tha')

    dt = read_m_file(dav, 'mlai.out')
    plot_series(dt, None,  "LAI", " m2 m-2", "Davos", 'dav')

    dt = read_m_file(tha, 'mlai.out')
    plot_series(dt, None,  "LAI", "m2 m-2", "Tharand", 'tha')


plot_fluxes()
plot_pools()
plot_m()