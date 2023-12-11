import ILAMB.Variable as v
import ILAMB.Post as Post
import ILAMB.ilamblib as ilib

import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt


idx = pd.date_range("19480101", "20101231", freq='Y')


def bm():
    experiment = "amz_trbrbe"
    experiment_rm = "add_resp"
    pft = "Total"

    biomass_geoC = v.Variable(filename=r"C:\Users\darel\OneDrive\Desktop\GUESS_data\LPJG-home\benchmark\biomass\GEOCARBON\biomass_Geo_masked.nc", variable_name="biomass")
    biomass_saatchi = v.Variable(filename=r"C:\Users\darel\OneDrive\Desktop\GUESS_data\LPJG-home\benchmark\biomass\SAATCHI\biomass_Saa_masked.nc", variable_name="biomass")


    mod_biomass =v.Variable(filename=f"./cf_outputs/biomass_{pft}_{experiment}.nc", variable_name="biomass")
    mod_biomass_mr =v.Variable(filename=f"./cf_outputs/biomass_{pft}_{experiment_rm}.nc", variable_name="biomass")

def ferti_effect():
    with_resp = v.Variable(filename="./cf_outputs/cveg_Total_Y_1948-2010_add_resp.nc4", variable_name="cveg")
    without_resp = v.Variable(filename="./cf_outputs/cveg_Total_Y_1948-2010_amz_trbrbe.nc4", variable_name="cveg")
    return with_resp, without_resp

a, b = ferti_effect()

r = pd.Series(a.integrateInSpace().convert("Pg").data, index=idx)
nr = pd.Series(b.integrateInSpace().convert("Pg").data, index=idx)

r_res = sm.tsa.seasonal_decompose(r, model='additive')
nr_res = sm.tsa.seasonal_decompose(nr, model='additive')