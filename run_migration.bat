@echo off
cd /d "D:\HONEY\Projects\transport-master"

echo Running database migration for vehicle service logs...
"C:\Program Files\Git\bin\git.exe" -m alembic upgrade add_vehicle_service_logs

echo.
if %ERRORLEVEL% == 0 (
    echo Migration completed successfully!
) else (
    echo ERROR: Migration failed. Trying with flask db command...
    python -m flask db upgrade add_vehicle_service_logs
)

pause
