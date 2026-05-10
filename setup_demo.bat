@echo off
echo ========================================
echo Transport Management System Demo Setup
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found successfully
echo.

:: Copy demo environment file
if not exist .env (
    echo Creating environment file...
    copy demo.env .env >nul
    echo Environment file created from demo.env
) else (
    echo Environment file already exists
)

:: Install Python dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

echo Dependencies installed successfully
echo.

:: Check MySQL connection
echo Testing MySQL connection...
python -c "import pymysql; pymysql.connect(host='localhost', user='transport_user', password='demo123', database='transport_db'); print('MySQL connection successful')" 2>nul

if %ERRORLEVEL% neq 0 (
    echo WARNING: Cannot connect to MySQL database
    echo Please ensure MySQL is installed and configured with:
    echo   - Database: transport_db
    echo   - User: transport_user
    echo   - Password: demo123
    echo.
    echo You can create these using MySQL Command Line Client:
    echo   CREATE DATABASE transport_db;
    echo   CREATE USER 'transport_user'@'localhost' IDENTIFIED BY 'demo123';
    echo   GRANT ALL PRIVILEGES ON transport_db.* TO 'transport_user'@'localhost';
    echo   FLUSH PRIVILEGES;
    echo.
    pause
) else (
    echo MySQL connection successful
)

:: Initialize database if needed
echo.
echo Initializing database...
python init_db.py

if %ERRORLEVEL% neq 0 (
    echo WARNING: Database initialization failed
    echo This might be normal if database is already set up
)

:: Run migrations
echo.
echo Running database migrations...
python -m flask db upgrade

if %ERRORLEVEL% neq 0 (
    echo WARNING: Migration failed or no migrations needed
)

:: Setup demo data
echo.
echo Setting up demo data...
python setup_demo_data.py

if %ERRORLEVEL% neq 0 (
    echo WARNING: Demo data setup failed
    echo You may need to create demo data manually
)

echo.
echo ========================================
echo Demo Setup Complete!
echo ========================================
echo.
echo To start the application:
echo   python webapp.py
echo.
echo Then open your browser to: http://localhost:5000
echo.
echo Default login credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo Press any key to start the application now...
pause >nul

python webapp.py
