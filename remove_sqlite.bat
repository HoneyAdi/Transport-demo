@echo off
cd /d "D:\HONEY\Projects\transport-master"
echo Removing SQLite database from git tracking...
"C:\Program Files\Git\bin\git.exe" rm --cached instance/transport.db
"C:\Program Files\Git\bin\git.exe" rm --cached instance/transport.db-journal 2>nul
echo. >> .gitignore
echo # SQLite databases >> .gitignore
echo instance/*.db >> .gitignore
echo instance/*.db-journal >> .gitignore
"C:\Program Files\Git\bin\git.exe" add .gitignore
"C:\Program Files\Git\bin\git.exe" commit -m "Remove SQLite db from tracking, add MySQL migrations"
"C:\Program Files\Git\bin\git.exe" push origin main
echo.
echo SQLite removed from git. Only MySQL schema migrations remain.
pause
