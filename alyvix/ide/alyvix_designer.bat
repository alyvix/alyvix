@echo off

for %%i in ("%~dp0..") do set "python_folder=%%~fi"

REG ADD "HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" /V "%python_folder%\python.exe" /T REG_SZ /D ~HIGHDPIAWARE /F >NUL
call %python_folder%\python.exe %python_folder%\Lib\site-packages\alyvix\ide\alyvix_designer.py %*