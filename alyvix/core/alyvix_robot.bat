@echo off

for %%i in ("%~dp0..") do set "python_folder=%%~fi"

REG ADD "HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" /V "%python_folder%\python.exe" /T REG_SZ /D ~HIGHDPIAWARE /F >NUL

call %~dp0..\python.exe %~dp0..\Lib\site-packages\alyvix\core\alyvix_robot.py %*