@echo off

for %%i in ("%~dp0..") do set "python_folder=%%~fi"

call %~dp0..\python.exe %~dp0..\Lib\site-packages\alyvix\core\alyvix_cipher.py %*