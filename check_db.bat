@echo off
cd /d "D:\HONEY\Projects\transport-master"
echo Checking if database file is tracked...
"C:\Program Files\Git\bin\git.exe" ls-files | findstr "\.db"
if %ERRORLEVEL% == 0 (
    echo Database file IS tracked in git
) else (
    echo Database file is NOT tracked in git
)
echo.
echo Database files found:
dir /s /b *.db 2>nul
pause
