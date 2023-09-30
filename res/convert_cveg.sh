#!/bin/sh
cd cf_outputs
cdo selyear,2000 cveg_TrBE_1_19481231-20101231_$1.nc4 cveg_2000_$1.nc
cdo -expr,'biomass=cveg * 2.0' cveg_2000_$1.nc out_$1.nc
cdo setattribute,biomass@units="kg m-2" out_$1.nc biomass_$1.nc
rm -rf out* cveg_2000*
cd ..