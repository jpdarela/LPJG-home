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

## BIOMASS

biomass = v.Variable(filename="../benchmark/biomass/SAATCHI/biomass_Saa_masked.nc", variable_name="biomass")
bm2= v.Variable(filename="../benchmark/biomass/SAATCHI/biomass_amz_basin2000TCT.nc", variable_name="biomass")

biomass_L07 =v.Variable(filename="./cf_outputs/biomass_amz_L07.nc", variable_name="biomass")
biomass_gc_water =v.Variable(filename="./cf_outputs/biomass_amz_gc_water2.nc", variable_name="biomass")



b07 = biomass.bias(biomass_L07)
bgc = biomass.bias(biomass_gc_water)

biases = (b07, bgc)

# PLot maps
shape_feature = ShapelyFeature(Reader("../benchmark/GIS/amz_basin_poly_corr.shp").geometries(),
                                ccrs.PlateCarree())

def plot_bias():
    vmax,vmin = 30, -30
    # grdsp_args = {"top":0.97,
    #               "bottom":0.03,
    #               "left":0.049,
    #               "right":0.987,
    #               "hspace":0.2,
    #               "wspace":0.058}

    titles = ["L0.7", "gc_water"]
    img_proj = ccrs.PlateCarree()
    img_extent = [b07.lon[0], b07.lon[-1], b07.lat[0], b07.lat[-1]]

    fig = plt.figure(figsize=(12, 5))
    gs = gridspec.GridSpec(1, 2)#, **grdsp_args)

    for n, bias in enumerate(biases):
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

        imsh = plt.imshow(np.flipud(bias.data), transform=img_proj,
                        extent=img_extent, cmap="bwr", vmax=vmax, vmin=vmin)
        ax.add_feature(cfeature.BORDERS, color="gray")
        ax.add_feature(shape_feature, facecolor='none', edgecolor="k")
        ax.coastlines(resolution='110m', linewidth=1, color="gray")

    plt.savefig("./bias_biomass2.png")
    plt.clf()
    plt.close(fig)
    fig, ax = plt.subplots(1,1, figsize=(10,1), layout="tight")
    Post.ColorBar(ax=ax, vmin=vmin, vmax=vmax, cmap="bwr", label="Biomass bias (Kg/m2) Model - Benchmark")
    plt.savefig("./bias_biomass_colorbar2.png")
    plt.clf()
    plt.close(fig)

def get_biomass(var:v.Variable):
    return var.integrateInSpace().convert("Pg").data[0]

def bplot():
    titles = ["Benchmark", "0.7", "gc_water"]
    bm_int = [get_biomass(bm2),get_biomass(biomass_L07),get_biomass(biomass_gc_water)]
    bar_colors = ['tab:red', 'tab:blue', 'tab:blue']
    fig, ax = plt.subplots()
    ax.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.5)
    ax.bar(titles, bm_int, color=bar_colors)
    ax.set_ylabel("Pg (Biomass)")
    plt.savefig("biomass_integrated2.png")
    plt.clf()
    plt.close(fig)
