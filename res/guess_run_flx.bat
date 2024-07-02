@echo off

set ROOT=C:\Users\darel\OneDrive\Desktop\GUESS_data\LPJG-home
@REM set VERSION=guess4.1_hydraulics
set VERSION=LPJ-GUESS
set NPROCESS=16
set INPUT_MODULE=ncps

set NEW=VPD_BASED_GC
set VPD= %ROOT%\FLUXNET2015\vpd_FLUXNET2015.nc
set PR= %ROOT%\FLUXNET2015\pr_FLUXNET2015.nc


@echo RUNNING LPJ-GUESS - FLUXNET WITH %NPROCESS% CORES

set GUESS=C:\Users\darel\OneDrive\Desktop\GUESS_data\LPJG-home\%VERSION%\build\Release\guesscmd.exe
set INSFILE=C:\Users\darel\OneDrive\Desktop\GUESS_data\LPJG-home\ins\hyd_ins_craft.ins

py write_flx_ins.py %NEW% %PR% %VPD%

mpiexec -n %NPROCESS% %GUESS% -parallel -input %INPUT_MODULE% %INSFILE%

pause
