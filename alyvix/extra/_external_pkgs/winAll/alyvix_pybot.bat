@ECHO OFF

goto comment

Alyvix allows you to automate and monitor all types of applications
Copyright (C) 2016 Alan Pipitone

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Developer: Alan Pipitone (Violet Atom) - http://www.violetatom.com/
Supporter: Wuerth Phoenix - http://www.wuerth-phoenix.com/
Official website: http://www.alyvix.com/
:comment

ver > nul

SET resultdir=
SET suitefile=
SET outputdir=
SET testcase=
SET suitename=
SET checktarget=
SET outputmsg=
SET pathavailable=
SET exitcode=
SET logtmp=0

SET suitefile=%1

rem echo sf=%suitefile%

IF [%suitefile%] == [] (

    ECHO First argument has to be the full suite file name, it is mandatory.
    ECHO Optional arguments are:
    ECHO     --test testcase_name
    ECHO     --outputdir log_folder
    ECHO     --exitcode the_exitcode
    
    EXIT /B 3

)

SET namewithext=
FOR %%A IN (%suitefile%) DO (
    rem SET Folder=%%~dpA
    SET namewithext=%%~nxA
)
rem ECHO Folder is: %Folder%
rem ECHO Name is: %namewithext%

FOR /f "tokens=* delims= " %%F IN ('echo %namewithext%') DO (
    SET suitename=%%~nF
)

rem echo name = %suitename%

SHIFT

rem & SHIFT

:loop

IF NOT "%1"=="" (
    IF "%1"=="--outputdir" (
        SET outputdir=%2
        SHIFT
    )
    IF "%1"=="--test" (
        SET testcase=%2
        SHIFT
    )
    IF "%1"=="--exitcode" (
        SET exitcode=%2
        SHIFT
    )
    SHIFT
    GOTO :loop
)

IF NOT EXIST %suitefile% (

    ECHO Error: Suite file doesn't exist!
    ECHO.
    ECHO Below the help:
    ECHO     First argument has to be the full suite file name, it is mandatory.
    ECHO     Optional arguments are:
    ECHO         --test testcase_name
    ECHO         --outputdir log_folder
    ECHO         --exitcode the_exitcode
    
    EXIT /B 3

)

IF [%testcase%] == [] (

    SET checktarget=test suite "%suitename%"

) ELSE (

    SET checktarget=test case "%testcase%" in test suite "%suitename%"
)

IF [%outputdir%] == [] (
    
    SET outputdir=%temp%\alyvix_pybot\%suitename%\log
    SET pathavailable=1
    SET logtmp=1

) ELSE (

    if not exist "%outputdir%\dummy\" (
        MKDIR "%outputdir%\dummy" > NUL 2>&1
    )

    IF EXIST "%outputdir%\dummy\" (
        RD %outputdir%\dummy /s /q > NUL 2>&1
        SET pathavailable=1

    ) ELSE (
        SET pathavailable=0
        SET outputdir=%temp%\alyvix_pybot\%suitename%\log
        SET logtmp=1
    )

)

SET resultdir=%temp%\alyvix_pybot\%suitename%\result

rem ECHO checktarget = %checktarget%
rem ECHO resultdir = %resultdir%
rem ECHO outputdir = %outputdir%

IF EXIST %resultdir% rd %resultdir% /s /q > NUL 2>&1

IF EXIST %outputdir% (
    IF %logtmp%==1 rd %outputdir% /s /q > NUL 2>&1
)

IF NOT EXIST %resultdir% MKDIR %resultdir%

IF NOT EXIST %outputdir% MKDIR %outputdir%

SET outputmsg=UNKNOWN - %s generated no output or exit code

rem ECHO suite = %suite%
rem ECHO outputdir = %outputdir%
rem ECHO testcase = %testcase%


IF [%testcase%] == [] (

    python -m robot.run --outputdir %outputdir% %suitefile% > NUL 2>&1
    
) ELSE (

    python -m robot.run --outputdir %outputdir% --test %testcase% %suitefile% > NUL 2>&1
    
)

IF EXIST %resultdir%\message.txt (

    IF %pathavailable% == 0 (
        ECHO | set /p=[PLEASE NOTE: Outputdir is not available] 
    )

    TYPE %resultdir%\message.txt
) ELSE (

    ECHO UNKNOWN - %checktarget% generated no output or exit code

)

IF EXIST %resultdir%\exitcode.txt (
    
    SET /p exitcode=<%resultdir%\exitcode.txt
    
)

rd %resultdir% /s /q > NUL 2>&1

IF %logtmp%==1 rd %outputdir% /s /q > NUL 2>&1

EXIT /B %exitcode%