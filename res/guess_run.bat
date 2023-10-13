@echo off

set NPROCESS=16
set INPUT_MODULE=ncps

@echo RUNNING LPJ-GUESS WITH %NPROCESS% CORES

set GUESS=C:\Users\darel\OneDrive\Desktop\GUESS_data\LPJG-home\guess4.1_hydraulics\build\Release\guesscmd.exe
set INSFILE=C:\Users\darel\OneDrive\Desktop\GUESS_data\LPJG-home\ins\amz_test.ins

mpiexec -n %NPROCESS% %GUESS% -parallel -input %INPUT_MODULE% %INSFILE%

pause
