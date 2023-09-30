import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

import ILAMB.Variable as v
import ILAMB.Post as Post
import ILAMB.ilamblib as ilib

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
# import pandas as pd

from utils import ymax, ymin, xmax, xmin


## BIOMASS
bm_all = v.Variable(filename="../benchmark/biomass/SAATCHI/biomass_0.5x0.5.nc", variable_name="biomass")
biomass = v.Variable(filename="../benchmark/biomass/SAATCHI/biomass_Saa_masked.nc", variable_name="biomass")
bm2= v.Variable(filename="../benchmark/biomass/SAATCHI/biomass_amz_basin2000TCT.nc", variable_name="biomass")

# biomass = np.flipud(biomass.data[0,:,:])
biomass_L07wp =v.Variable(filename="./cf_outputs/biomass_amz_L07_t0.nc", variable_name="biomass")
biomass_L07 =v.Variable(filename="./cf_outputs/biomass_amz_L07.nc", variable_name="biomass")
biomass_L09 =v.Variable(filename="./cf_outputs/biomass_amz_L09.nc", variable_name="biomass")
biomass_L07_std =v.Variable(filename="./cf_outputs/biomass_amz_L07_std.nc", variable_name="biomass")
biomass_L09_std =v.Variable(filename="./cf_outputs/biomass_amz_L09_std.nc", variable_name="biomass")

mask_bool = np.ones(shape=(360, 720), dtype=bool)
msk_amz = np.flipud(biomass_L07.data.mask[0,:,:])

mask_bool[ymin:ymax, xmin:xmax] = msk_amz

b07wp = biomass.bias(biomass_L07wp)
b07 = biomass.bias(biomass_L07)
b09 = biomass.bias(biomass_L09)
b07_std = biomass.bias(biomass_L07_std)
b09_std = biomass.bias(biomass_L09_std)

biases = (b07wp, b07, b09, b07_std, b09_std)

# PLot maps
shape_feature = ShapelyFeature(Reader("../benchmark/GIS/amz_basin_poly_corr.shp").geometries(),
                                ccrs.PlateCarree(), facecolor='none')

def plot_bias():
    vmax,vmin = 30, -30
    grdsp_args = {"bottom":0.03,
                  "left":0.048,
                  "right":0.987,
                  "hspace":0.2,
                  "wspace":0.055}
    bias_arrs = []
    titles = ["0.7wp", "0.7", "0.9", "0.7 std", "0.9 std"]
    img_proj = ccrs.PlateCarree()
    img_extent = [biomass.lon[0], biomass.lon[-1], biomass.lat[0], biomass.lat[-1]]

    fig = plt.figure(figsize=(17, 5))
    gs = gridspec.GridSpec(1, 5, **grdsp_args)

    for n, bias in enumerate(biases):
        img = np.ma.masked_array(np.flipud(bias.data), mask=mask_bool)
        bias_arrs.append(img)
        ax = fig.add_subplot(gs[0, n], projection=ccrs.PlateCarree())
        ax.set_xticks([-75, -55], crs=ccrs.PlateCarree())
        lon_formatter = LongitudeFormatter(
            zero_direction_label=True, number_format='g')
        ax.xaxis.set_major_formatter(lon_formatter)
        if n == 0:
            ax.set_yticks([-20, 0], crs=ccrs.PlateCarree())
            lat_formatter = LatitudeFormatter()
            ax.yaxis.set_major_formatter(lat_formatter)

        ax.set_title(titles[n])
        ax.set_extent([-80., -49.8, -20.5, 5.5], crs=ccrs.PlateCarree())

        imsh = plt.imshow(img, transform=img_proj,
                        extent=img_extent, cmap="bwr", vmax=vmax, vmin=vmin)
        ax.add_feature(cfeature.BORDERS, color="gray")
        ax.add_feature(shape_feature, edgecolor="k")
        ax.coastlines(resolution='110m', linewidth=1, color="gray")
    # plt.show()
    plt.savefig("./bias_biomass.png")
    plt.clf()
    plt.close(fig)

    fig, ax = plt.subplots(1,1, figsize=(10,1), layout="tight")
    Post.ColorBar(ax=ax, vmin=vmin, vmax=vmax, cmap="bwr", label="Biomass bias (Kg/m2) Model - Benchmark")
    plt.savefig("./bias_biomass_colorbar.png")
    plt.clf()
    plt.close(fig)
    return bias_arrs

def get_biomass(var:v.Variable):
    return var.integrateInSpace().convert("Pg").data[0]

def bplot():
    titles = ["Benchmark",  "0.7wp", "0.7", "0.9", "0.7 std", "0.9 std"]
    bm_int = [get_biomass(bm2), get_biomass(biomass_L07wp), get_biomass(biomass_L07),get_biomass(biomass_L09),
              get_biomass(biomass_L07_std),get_biomass(biomass_L09_std)]
    bar_colors = ['tab:red', 'tab:blue', 'tab:blue', 'tab:blue', 'tab:blue', 'tab:blue']
    fig, ax = plt.subplots()
    ax.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.5)
    ax.bar(titles, bm_int, color=bar_colors)
    ax.set_ylabel("Pg (Biomass)")

    plt.savefig("biomass_integrated.png")
    plt.clf()
    plt.close(fig)
