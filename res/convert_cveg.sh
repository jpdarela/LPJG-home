#!/bin/sh
cd cf_outputs
cdo selyear,2000 cveg_$1_Y_**_$2.nc4 cveg_2000_$2.nc
cdo -expr,'biomass=cveg * 2.0' cveg_2000_$2.nc out_$2.nc
cdo setattribute,biomass@units="kg m-2" out_$2.nc biomass_$1_$2.nc
rm -rf out* cveg_2000*
cd ..