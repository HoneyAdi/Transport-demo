@echo off
cd /d "D:\HONEY\Projects\transport-master"

echo Creating vehicle service log tables...
python create_service_tables.py

echo.
pause
