set GUESS=C:\Users\darel\OneDrive\Desktop\GUESS_data\LPJG-home\guess4.1_hydraulics\build\Release\Release\guesscmd.exe
set INSFILE=C:\Users\darel\OneDrive\Desktop\GUESS_data\LPJG-home\ins\amz_test.ins

mpiexec -n 16 %GUESS% -parallel -input ncps %INSFILE%
