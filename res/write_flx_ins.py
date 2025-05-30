from pathlib import Path
import sys

ROOT = str(Path("./").resolve().parent)

sep = "\\" if sys.platform == "win32" else "/"

def write_insfile(insfile_name, hyd_sys, pr_path, vpd_path, root=ROOT):

    file = f"""
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !
    ! LPJ-GUESS instruction file created on 10/25/2019 with INSParser v1.0.1.
    !
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    title 'LPJ-GUESS cohort mode - European species FLUXNET'

    import "european_pfts.ins"

    hydraulic_system "{hyd_sys}" !"VPD_BASED_GC" ! "STANDARD", "MONTEITH_SUP_DEM", "VPD_BASED_GC"

    param "file_gridlist" (str "{root}{sep}grd{sep}FLUXNET2015.grd")

    param "file_mip_noy" (str "{root}{sep}env{sep}ndep_NOy_2011_1x1deg.nc")
    param "file_mip_nhx" (str "{root}{sep}env{sep}ndep_NHx_2011_1x1deg.nc")

    !param "file_ndep"     (str "{root}{sep}env{sep}GlobalNitrogenDeposition.bin")

    param "file_co2"      (str "{root}{sep}env{sep}co2_1764_2021_observed.dat")
    param "file_soildata" (str "{root}{sep}env{sep}soils_lpj.dat")

    param "file_temp"     (str "{root}{sep}FLUXNET2015{sep}tas_FLUXNET2015.nc")
    param "variable_temp" (str "tas")

    param "file_prec"     (str "{pr_path}")
    param "variable_prec" (str "pr")

    param "file_insol"      (str "{root}{sep}FLUXNET2015{sep}rsds_FLUXNET2015.nc")
    param "variable_insol"  (str "rsds")

    param "file_wind"     (str "{root}{sep}FLUXNET2015{sep}wind_FLUXNET2015.nc")
    param "variable_wind" (str "wind")

    param "file_vpd"     (str "{vpd_path}")
    param "variable_vpd" (str "vpd")

    param "file_hurs"     (str "")
    param "variable_hurs" (str "hurs")


    ! str "tas", str "pre", and str "swd" before change

    !param "file_specifichum"      (str "")
    !param "variable_specifichum"  (str "Qair")

    !TODO these two are only needed for BVOC I think
    param "file_min_temp"      (str "")
    !param "variable_min_temp"  (str "tasmin")
    param "file_max_temp"      (str "")
    !param "variable_max_temp"  (str "tasmax")

    ! only needed for BLAZE
    param "file_pres"     (str "{root}{sep}FLUXNET2015{sep}ps_FLUXNET2015.nc")
    param "variable_pres" (str "ps")


    param "file_specifichum"     (str "")
    param "file_pres"     (str "")
    param "file_wetdays"     (str "")

    param "file_relhum" (str "")
    !param "file_relhum"     (str "")
    !param "variable_relhum" (str "hurs")

    !param "file_windspeed"     (str "")

"""

    with open(insfile_name, mode='w') as fh:
        fh.write(file)

if __name__ == "__main__":

    assert len(sys.argv) == 4

    write_insfile("../ins/hyd_ins_craft.ins", sys.argv[1], sys.argv[2], sys.argv[3])
