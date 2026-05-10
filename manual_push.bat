@echo off
cd /d "D:\HONEY\Projects\transport-master"
"C:\Program Files\Git\bin\git.exe" remote remove origin 2>nul
"C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/HoneyAdi/Transport-Final.git
"C:\Program Files\Git\bin\git.exe" branch -M main
echo.
echo You will be prompted for your GitHub password.
echo If you have 2FA enabled, use a Personal Access Token instead of password.
echo.
"C:\Program Files\Git\bin\git.exe" push -u origin main
echo.
pause
