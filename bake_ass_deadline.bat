@REM @echo off
set TOOL_PATH=%1
set MAYA_VERSION=%2
set OCIO=%3
set _proj=%4

set MAYA_DISABLE_CLIC_IPM=1
set MAYA_DISABLE_CIP=1
set MAYA_DISABLE_CER=1

set LAUNCH_CMD=import sys;sys.path.append('%TOOL_PATH%');import separate_asset_and_build_ass;separate_asset_and_build_ass.run_json()

set _sq=%5
set _shot=%6
set _RN=%7

set MAYA_APP_DIR=C:\Users\%username%\Documents\NMA\projects\%_proj%\Documents\maya
if not exist %MAYA_APP_DIR% (
    mkdir %MAYA_APP_DIR%
)

set MAYAEXE=C:\Program Files\Autodesk\Maya%MAYA_VERSION%\bin\maya.exe

"C:\Program Files\Autodesk\Maya%MAYA_VERSION%\bin\mayabatch.exe" -command "python(\"%LAUNCH_CMD%\")"
