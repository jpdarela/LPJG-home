import math

soiltype = {"clay_frac": 0.2,
            "sand_frac": 0.7,
            "WILTING_POINT": -1.5,
            "shapeA": 0,
            "shapeB": 0,
            "PWPVWC": 0}

def water_pot_parameters(soiltype):
    # Saxton et al. 1986 (eq. 5 & 6)
    # 10 to transform into MPa
    clay_percent = soiltype['clay_frac'] * 100.0
    sand_percent = soiltype['sand_frac'] * 100.0
    soiltype['shapeA'] = -math.exp(-4.396 - 0.0715*clay_percent - 4.88*0.0001\
        *math.pow(sand_percent, 2) - 4.285*0.00001*math.pow(sand_percent, 2)*clay_percent) / 10.0
    soiltype['shapeB'] = -3.14 - 0.00222*math.pow(clay_percent, 2) - 3.484*0.00001\
        *math.pow(sand_percent, 2)*clay_percent

    soiltype['PWPVWC'] = math.pow(soiltype["WILTING_POINT"] / soiltype['shapeA'], 1.0 / soiltype['shapeB'])

def psi_soil(soiltype, wcont):
        psi_s = soiltype["shapeA"] * (wcont ** soiltype["shapeB"])
        print(f"psi_s = {psi_s}")

def r(soiltype, w):
    water_pot_parameters(soiltype)
    psi_soil(soiltype, w)