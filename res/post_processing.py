from datetime import datetime
from copy import deepcopy
from pathlib import Path
import os

from netCDF4 import Dataset
import cftime
import pandas as pd

from utils import make_gridlist, read_gridlist, rm_leapday_idx


__author__= "jpdarela"
__descr__ = "reader for SMARTIO outputs"


class guess_data:


    NO_T_UNIT = {"cveg", "cmass_leaves", "clitter_patch", "csoil",
                  "gc", "gc_water", "wcont","cmass_loss_greff",
                  "cmass_loss_bg", "cmass_loss_cav", "fpc", "deltap"} | {f"wcont{x}" for x in range(1, 16)}

    T_UNIT = {"npp", "gpp", "reco", "ar", "hr", "nee",
              "total_transpiration", "canopy_interception", "et"}

    TIME_UNITS = {'Daily'    :('day-1',   'D'),
               'Monthly'  :('month-1', 'MS'),
               'Annually' :('year-1',  'Y')}


    def __init__(self, filepath:Path, end:str, gridlist_filepath:str) -> None:
        """
        filepath: pathlib.Path or string with the path for the smart output file
        """

        self.extra:dict               = {} # stores reco, aet, gpp & nee asked time_series by _get_ref_data method
        self.gridcell_names:list[str] = [] # Gridecell names from the gridlist file
        self.var_units:list[str]      = {} # store standard units for variables
        self.gridlist_filepath = gridlist_filepath
        # identify the required dataset location
        try:
            # We expect an object of type pathlib.Path
            self.filepath = filepath.resolve()
        except:
            # Or a valid string inputable to pathlib.Path
            self.filepath = Path(filepath).resolve()
        finally:
            assert self.filepath.exists(), f"no file in : {self.filepath}"
            assert self.filepath.is_file(), f"{self.filepath} is not a file"
            assert self.filepath.name.split(".")[-1] in {"nc","nc4"}, "not a netcdf4"
            # TODO assert a proper file (smartio)

        # File dataset location and other attributes
        self.base_dir = self.filepath.cwd()
        self.filename = self.filepath.name
        self.time_integration = self.filepath.stem.split("O")[0]
        self.uniT = self.TIME_UNITS[self.time_integration][0]
        self.freq = self.TIME_UNITS[self.time_integration][1]

        # Open the dataset
        try:
            self.GRIDLIST, self.SITES_COORDINATES = make_gridlist(self.filepath)
            # self.GRIDLIST, self.SITES_COORDINATES = read_gridlist(self.gridlist_filepath)
            self.dataset = Dataset(self.filepath, mode='r')

        except:
            print(f"Failed to open {self.filename}")
            raise FileNotFoundError

        # Interface netCDF4 groups
        self.Base = self.dataset.groups["Base"]
        self.Pft = self.dataset.groups["Pft-Out"]
        self.Patch = self.dataset.groups["Patch-Out"]

        # Manage time dim
        self.calendar = "standard"
        self.time_unit_original = self.Base['Time'].units
        self.start = "-".join(self.time_unit_original.split(" ")[-1].split("-")[::-1])

        self.periods = self.Base["Time"].shape[0]
        self.time_unit = f"days since {self.start}"

        if self.time_integration == "Daily":
            self.calendar = self.Base['Time'].calendar
            assert end, "for daily ouputs the end date need to be set (e.g. 'yyyymmdd')"
            self.idx = rm_leapday_idx(pd.date_range(self.start, end, freq="D", unit='s')) # e.g. pd.date_range(start="19890101", periods=self.periods) #
            self.time_index = cftime.date2num(self.idx,
                                        units=self.time_unit,
                                        calendar=self.calendar)
            index = [x.isoformat() for x in self.idx]
            self.idx = pd.to_datetime(index)

        else:
            self.idx = pd.date_range(self.start, periods=self.periods, freq=self.freq, unit='s')
            self.time_index = cftime.date2num(self.idx.to_pydatetime(),
                                            units=self.time_unit,
                                            calendar=self.calendar)

        # Collect other ancillary values
        self.pft_vars = set(self.Pft.variables.keys())
        self.patch_vars = set(self.Patch.variables.keys())
        self.pft_list = self.Base['Pfts'][:]
        return None


    def __set_units(self, var):
        if var in self.pft_vars:
            if var in self.var_units.keys():
                pass
            else:
                if var in self.NO_T_UNIT:
                    self.var_units[var] = self.Pft.variables[var].unit
                else:
                    self.var_units[var] = self.Pft.variables[var].unit + f" {self.TIME_UNITS[self.time_integration][0]}"
        elif var in self.patch_vars:
            if var in self.var_units.keys():
                pass
            else:
                if var in self.NO_T_UNIT:
                    self.var_units[var] = self.Patch.variables[var].unit
                else:
                    self.var_units[var] = self.Patch.variables[var].unit + f" {self.TIME_UNITS[self.time_integration][0]}"
        elif var in ("nee", "reco"):
            if var in self.var_units.keys():
                pass
            else:
                self.var_units[var] = "kg m-2" + f" {self.TIME_UNITS[self.time_integration][0]}"
        elif var == "et":
            if var in self.var_units.keys():
                pass
            else:
                self.var_units[var] = "mm" + f" {self.TIME_UNITS[self.time_integration][0]}"


    def __get_pft_data(self, var:str, gridcell:int,
                      pft_number:int=-1, stand_number:int=0)->pd.Series:

        assert var in self.pft_vars
        gridname = self.GRIDLIST[gridcell][2].split('-')[-1]

        if gridname not in self.gridcell_names:
            self.gridcell_names.append(gridname)

        self.__set_units(var)

        vname = var + "_" + gridname + "_" + self.pft_list[pft_number]

        return pd.Series(self.Pft.variables[var][gridcell, :, pft_number, stand_number],
                         index=self.idx, name=vname)


    def __get_patch_data(self, var:str, gridcell:int, pft_number=-1,
                        stand_number:int=0)->pd.Series:

        assert var in self.patch_vars
        gridname = self.GRIDLIST[gridcell][2].split('-')[-1]

        if gridname not in self.gridcell_names:
            self.gridcell_names.append(gridname)

        self.__set_units(var)

        vname = var + "_" + gridname + "_" + self.pft_list[pft_number]

        return pd.Series(self.Patch.variables[var][gridcell, :, stand_number],
                         index=self.idx, name=vname)


    def __make_reco(self, gridcell, pft=-1, stand=0):

        gridname = self.GRIDLIST[gridcell][2].split('-')[-1]
        vname = "reco_" + gridname + "_" + self.pft_list[pft]

        if vname in self.extra.keys():
            return self.extra[vname]

        ar = self.__get_pft_data(var="ar",
                                gridcell=gridcell, pft_number=pft, stand_number=stand)
        hr = self.__get_patch_data(var="hr",
                                  gridcell=gridcell, stand_number=stand)

        tmp = ar + hr
        tmp.name = vname
        self.__set_units("reco")
        self.extra[vname] = deepcopy(tmp)
        return tmp


    def __make_nee(self, gridcell, pft=-1, stand=0):

        gridname = self.GRIDLIST[gridcell][2].split('-')[-1]
        vname = "nee_" + gridname + "_" + self.pft_list[pft]

        if vname in self.extra.keys():
            return self.extra[vname]

        reco = self.__make_reco(gridcell=gridcell, pft=pft)

        gpp = self.__get_pft_data("gpp", gridcell=gridcell, pft_number=pft, stand_number=stand)

        tmp = reco - gpp
        tmp.name = vname
        self.__set_units("nee")
        self.extra[vname] = deepcopy(tmp)
        return tmp


    def __make_et(self, gridcell, pft=-1, stand=0):

        gridname = self.GRIDLIST[gridcell][2].split('-')[-1]

        vname = "et_" + gridname + "_" + self.pft_list[pft]

        if vname in self.extra.keys():
            return self.extra[vname]

        evap1 = self.__get_patch_data("total_transpiration", gridcell=gridcell, pft_number=pft, stand_number=stand)
        evap2 = self.__get_patch_data("canopy_interception", gridcell=gridcell, pft_number=pft, stand_number=stand)

        tmp = evap1 + evap2
        tmp.name = vname
        self.__set_units("et")
        self.extra[vname] = deepcopy(tmp)
        return tmp


    def make_df(self, variables:list, gridcell:int,
                         pft_number:int, stand_number:int=0)->pd.DataFrame:
        series = []

        assert type(variables) == list or type(variables) == str, f"wrong input-- {variables} of type {type(variables)}"
        _variables, self.Series = ([variables,], True) if type(variables) == str else (variables, False)

        for var in _variables:
            if var not in self.pft_vars and var not in self.patch_vars:

                assert var in ['nee','reco','et'], f"invalid variable: {var}"

                if var == 'nee':
                    series.append(self.__make_nee(gridcell=gridcell, pft=pft_number))
                    continue

                elif var == 'reco':
                    series.append(self.__make_reco(gridcell=gridcell, pft=pft_number))
                    continue

                elif var == "et":
                    series.append(self.__make_et(gridcell=gridcell, pft=pft_number))
                    continue

            if var in self.pft_vars:
                series.append(self.__get_pft_data(var=var, gridcell=gridcell,
                                                 pft_number=pft_number, stand_number=stand_number))

            elif var in self.patch_vars:
                series.append(self.__get_patch_data(var=var, gridcell=gridcell,
                                                   pft_number=pft_number, stand_number=stand_number))
        if self.Series:
            return deepcopy(series[0])
        df = pd.DataFrame(series).T
        return deepcopy(df)


    def get_tbounds(self, idx):
        return cftime.num2pydate(self.time_index[idx], self.time_unit).strftime("%Y%m%d")


    def get_lonlat(self, gridcell):
        lon = self.Base.variables["Longitude"][:][gridcell]
        lat = self.Base.variables["Latitude"][:][gridcell]
        return lon, lat


    def get_ref_var(self, var:str, gridcell:int=2)->pd.Series:

        """ get monthly reference data FLUXNET2015
            other reference data is yet to be implemented
        """

        # Variables from fluxnet2015
        reference_data = ['nee', 'reco', 'gpp', 'et']

        ref_path:Path=Path("../FLUXNET2015/ref/")
        assert var in reference_data, f'dataset not found for: {var}'

        if self.time_integration != "Monthly":
            print("ref data only in monthly integration")
            return None


        SITES_START = \
            {
                'Hai' : '20000101',
                'Dav' : '19970101',
                'Tha' : '19960101',
                'Lnf' : '20020101',
                'Obe' : '20080101',
                'Lae' : '20040101',
                'BK1' : '20040101',
                'Lkb' : '20090101',
                'Sor' : '19960101',
                'Col' : '19960101',
                'Ren' : '19980101',
                'Fyo' : '19980101',
                'Bra' : '19960101',
                'Vie' : '19960101',
                'Hyy' : '19960101',
                'Let' : '20090101',
                'Sod' : '20010101',
                'Fon' : '20050101',
                'Pue' : '20000101',
                'Cpz' : '19970101',
                'Lav' : '20030101',
                'Loo' : '19960101',
                'RuR' : '20110101'
            }

        gridname = self.GRIDLIST[gridcell][2].split('-')[-1]
        var_path = Path(os.path.join(ref_path, f"{var}_{gridname}_FLUXNET2015.nc"))

        assert var_path.exists(), f"No reference var in {var_path}"

        with Dataset(var_path, mode='r') as _obs:
            obs = deepcopy(_obs.variables[var][:])
            idx2 = pd.date_range(start=SITES_START[gridname], periods=obs.size, freq=self.freq)

        return pd.Series(obs, index=idx2, name=f"{var}_{gridname}_FLX_REF")


    def __del__(self):
        """Manage dataset closing - No circular deps in this class"""
        return None


class reader_GLDAS(guess_data):

   end = datetime(2010, 12, 31).strftime("%Y%m%d")
   gridlist_filepath = "../grd/GLDAS.grd"

   def __init__(self, filepath: Path) -> None:
       super().__init__(filepath, self.end, self.gridlist_filepath)


class reader_FLUXNET2015(guess_data):

   end = datetime(2014, 12, 31).strftime("%Y%m%d")
   gridlist_filepath = "../grd/FLUXNET2015_gridlist.txt"

   def __init__(self, filepath: Path) -> None:
       super().__init__(filepath, self.end, self.gridlist_filepath)


class reader_ISIMIP_SA(guess_data):

   end = datetime(2016, 12, 31).strftime("%Y%m%d")
   gridlist_filepath = "../grd/ISIMIP_SA.grd"

   def __init__(self, filepath: Path) -> None:
       super().__init__(filepath, self.end, self.gridlist_filepath)
