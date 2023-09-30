from os import listdir, makedirs
from sys import argv
from pathlib import Path

INPUT_FILES = ["GLDAS", "ISIMIP_SA"]
assert argv[1] in INPUT_FILES, f"input files must be one of: {INPUT_FILES}"

dataset = argv[1]

## Folder containing the folders: grd, env and %GLDAS% <-- This one can vary. We are using GLDAS for now
root = Path("./").resolve()
# root = "/dss/dssfs02/lwp-dss-0001/pr48va/pr48va-dss-0000/ge83bol2/"

#Folder to write the insfile(s)
scratch = "./ins"

clim_root = f"{root}/{dataset}"
env_root = f"{root}/env/"
grd = f"{root}/grd/{dataset}.grd"

with open("./PWS.tsv", "r") as fh:
    PWS_data = fh.readlines()

def get_filename(var):
    """need to rename input files to match input variable names:
    swdown, prec, temp, windspeed, vpd"""
    data = Path(clim_root)
    files = listdir(data)
    return [f for f in files if var in f][0]

def delta_psi_max(isohydricity):
    return 1.067 * isohydricity + 1.049

def make_par(id):
    assert id > 0 and id < 38, "invalid PWS ID"
    data = list(map(float, PWS_data[id].strip().split("\t")))
    return {"psi50": data[2],
            "cav_slope": data[3],
            "isohyd": data[6],
            "delta_psi_max": delta_psi_max(data[6])}

def make_TrBE(n, par):
    base_pft=f"""
pft "TrBE_{n}" (

	alphar 3
	cav_slope {par["cav_slope"]}
	psi50_xylem {par["psi50"]}
	kl_max 7.5
	kr_max 0.0004
	ks_max 1.5
	delta_psi_max {par["delta_psi_max"]}
	isohydricity {par["isohyd"]}

    lambda_max 0.7
	fireresist 0.1
	longevity 600

	crownarea_max 1000
	cton_root 29
	cton_sap 330

	drought_tolerance 0.0001
	emax 5
	eps_iso 24
	eps_mon 0.48 0.19 0.67 0.14 0.12 0.13 0.14 0.29 0.24
	est_max 0.05

	fnstorage 0.05
	ga 0.005
	gdd5min_est 0
	gmin 0.75
	greff_min 0.04
	harv_eff 0
	harvest_slow_frac 0.33
	include 1
	intc 0.02
	k_allom1 250
	k_allom2 36
	k_allom3 0.58
	k_chilla 0
	k_chillb 100
	k_chillk 0.05
	k_latosa 10000
	k_rp 1.6
	kest_bg 0.1
	kest_pres 1
	kest_repr 200
	km_volume 1.477E-06
	landcover "natural"
	leaflong 2
	leafphysiognomy "broadleaf"
	lifeform "tree"
	litterme 0.3

	ltor_max 1
	nuptoroot 0.0028
	parff_min 350000
	pathway "c3"
	phengdd5ramp 0
	phenology "evergreen"

	pstemp_high 30
	pstemp_low 25
	pstemp_max 55
	pstemp_min 2
	reprfrac 0.1
	res_outtake 0
	respcoeff 0.2

	rootdist 0.12 0.12 0.12 0.12 0.12 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04
	root_beta 0.982
	seas_iso 0
	storfrac_mon 0.4 0.8 0.8 0.4 0.4 0.5 0.8 0.2 0.5
	tcmax_est 1000
	tcmin_est 15.5
	tcmin_surv 15.5
	turnover_harv_prod 0.04
	turnover_leaf 0.5
	turnover_root 0.7
	turnover_sap 0.05
	twmin_est -1000
	twminusc 0
	wooddens 200
	wscal_min 0.35
)


"""
    return base_pft

ins = f"""
title "'LPJ-GUESS-HYD testing'"

param "file_gridlist" (str "{grd}")
param "file_co2"      (str "{env_root}co2_1764_2016_observed.dat")
param "file_mip_nhx"  (str "{env_root}ndep_NHx_2011_1x1deg.nc")
param "file_mip_noy"  (str "{env_root}ndep_NOy_2011_1x1deg.nc")
param "file_soildata" (str "{env_root}soils_lpj.dat")
param "file_insol"    (str "{clim_root}/{get_filename("swdown")}")
param "file_prec"     (str "{clim_root}/{get_filename("prec")}")
param "file_temp"     (str "{clim_root}/{get_filename("temp")}")
param "file_vpd"      (str "{clim_root}/{get_filename("vpd")}")
param "file_wind"     (str "{clim_root}/{get_filename("windspeed")}")
param "file_wetdays"         (str "")
param "file_specifichum"     (str "")
param "file_pres"            (str "")
param "file_relhum"          (str "")
param "file_max_temp"        (str "")
param "file_min_temp"        (str "")
param "file_hurs"            (str "")
param "variable_hurs"        (str "")
param "variable_insol"       (str "insol")
param "variable_max_temp"    (str "tasmax")
param "variable_min_temp"    (str "tasmin")
param "variable_prec"        (str "prec")
param "variable_temp"        (str "temp")
param "variable_vpd"         (str "vpd")
param "variable_wind"        (str "windspeed")

!! SOIL N
f_denitri_gas_max 0.33
f_denitri_max 0.33
f_nitri_gas_max 0.25
f_nitri_max 0.1
k_c 0.017
k_n 0.083


hydraulic_system "VPD_based_GC" ! "standard" !

npatch 100
nyear_spinup 1500
distinterval 500
patcharea 1000

output_time_range "scenario" ! "full" ! "spinup" !
suppress_annually_output 0
suppress_daily_output 1
suppress_monthly_output 0


ifcalccton 1
ifcalcsla 1
ifcarbonfreeze 1
ifcdebt 1
ifcentury 1
ifdetrendspinuptemp 0
ifdisturb 1
ifdroughtlimitedestab 0
ifinundationstress 1
ifmethane 0
ifmultilayersnow 1
ifnlim 1
ifntransform 1
iforganicsoilproperties 0
ifrainonwetdaysonly 1
ifsaturatewetlands 0
ifsme 1
ifsmoothgreffmort 1
iftwolayersoil 0
wetland_runon 0

alphaa_nlim 0.6
disable_mort_greff 0

estinterval 5
firemodel "globfirm"
freenyears 100

ifbgestab 1
ifbvoc 0
ifcalccton 1
ifcalcsla 1
ifcdebt 1
ifcentury 1
ifdisturb 1
ifdroughtlimitedestab 0
ifnlim 1
ifrainonwetdaysonly 1
ifsme 1
ifsmoothgreffmort 1
ifstochestab 1
ifstochmort 1
nfix_a 0.102
nfix_b 0.524

nrelocfrac 0.5

outputdirectory "./"

restart 0
rootdistribution "fixed"
run_landcover 0
save_state 0

textured_soil 1
vegmode "cohort"
wateruptake "rootdist"
weathergenerator "gwgen"
year_begin 1800
year_end 2010


st "Natural" (
	intercrop "nointercrop"
	landcover "natural"
	naturalveg "all"
	restrictpfts 0
	stinclude 1
)


"""

def write_ins(name=""):
    makedirs(scratch, exist_ok=True)
    insfilename = f"{scratch}/{dataset}_{name}.ins"
    with open(insfilename, "w") as fh:
        fh.write(ins)
    return str(Path(insfilename).resolve())

def add_pft(insfile, n, par):
    with open(insfile, "a") as fh:
        fh.write(make_TrBE(n, par))

def multi_ins():
    makedirs(scratch, exist_ok=True)
    with open(f"{scratch}/insfiles.txt", "w") as fh:
        for i in range(len(PWS_data) - 1):
            insfile = write_ins(name=f"TrBe-{i}")
            add_pft(insfile, i, make_par(i + 1))
            fh.write(insfile + "\n")

def multi_pft(pwss=None):
    insfile = write_ins("PWS")
    rg = pwss if pwss is not None else range(len(PWS_data) - 1)
    for i in rg:
        add_pft(insfile, i, make_par(i + 1))


if __name__ == "__main__":
    # multi_ins()
    multi_pft([1,])
