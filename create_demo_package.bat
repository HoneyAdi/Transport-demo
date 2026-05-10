@echo off
echo ========================================
echo Creating Portable Demo Package
echo ========================================
echo.

:: Create demo package directory
set PACKAGE_NAME=Transport_Demo_Package
set PACKAGE_DIR=%CD%\%PACKAGE_NAME%

if exist "%PACKAGE_DIR%" (
    echo Removing existing package directory...
    rmdir /s /q "%PACKAGE_DIR%"
)

echo Creating package directory: %PACKAGE_DIR%
mkdir "%PACKAGE_DIR%"

:: Copy essential application files
echo Copying application files...
xcopy /E /I /H /Y "*.py" "%PACKAGE_DIR%\"
xcopy /E /I /Y "templates" "%PACKAGE_DIR%\templates"
xcopy /E /I /Y "static" "%PACKAGE_DIR%\static"
xcopy /E /I /Y "migrations" "%PACKAGE_DIR%\migrations"
xcopy /E /I /Y "uploads" "%PACKAGE_DIR%\uploads"

:: Copy configuration files
echo Copying configuration files...
copy "requirements.txt" "%PACKAGE_DIR%\"
copy "demo.env" "%PACKAGE_DIR%\"
copy "setup_demo_data.py" "%PACKAGE_DIR%\"
copy "init_db.py" "%PACKAGE_DIR%\"
copy "models.py" "%PACKAGE_DIR%\"
copy "webapp.py" "%PACKAGE_DIR%\"

:: Copy documentation
echo Copying documentation...
copy "WINDOWS_DEMO_GUIDE.md" "%PACKAGE_DIR%\"
copy "DEMO_CREDENTIALS.md" "%PACKAGE_DIR%\"
copy "README.md" "%PACKAGE_DIR%\"

:: Copy setup scripts
echo Copying setup scripts...
copy "setup_demo.bat" "%PACKAGE_DIR%\"

:: Create README for package
echo Creating package README...
(
echo Transport Management System - Demo Package
echo =========================================
echo.
echo This is a portable demo package for the Transport Management System.
echo.
echo Quick Start:
echo -----------
echo 1. Install Python 3.9+ from https://www.python.org/downloads/
echo    Make sure to check "Add Python to PATH"
echo.
echo 2. Install MySQL Community Server from https://dev.mysql.com/downloads/
echo    Create database and user as shown in WINDOWS_DEMO_GUIDE.md
echo.
echo 3. Run setup_demo.bat to install dependencies and setup demo
echo.
echo 4. Start application with: python webapp.py
echo.
echo 5. Open browser to: http://localhost:5000
echo.
echo Login: admin / admin123
echo.
echo For detailed instructions, see WINDOWS_DEMO_GUIDE.md
echo.
echo Created: %date%
echo Version: 1.0
) > "%PACKAGE_DIR%\PACKAGE_README.txt"

:: Create ZIP package (if 7-Zip is available)
echo.
echo Creating ZIP package...
where 7z >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Creating ZIP with 7-Zip...
    7z a -tzip "%PACKAGE_NAME%.zip" "%PACKAGE_DIR%\*" >nul
    echo Package created: %PACKAGE_NAME%.zip
) else (
    echo 7-Zip not found. You can manually ZIP the folder:
    echo   %PACKAGE_DIR%
    echo.
    echo Or install 7-Zip from https://www.7-zip.org/
)

echo.
echo ========================================
echo Demo Package Creation Complete!
echo ========================================
echo.
echo Package location: %PACKAGE_DIR%
echo.
echo Contents:
echo - All application files
echo - Demo configuration
echo - Setup scripts
echo - Documentation
echo - Sample data setup
echo.
echo To use:
echo 1. Copy the entire folder to client computer
echo 2. Follow instructions in WINDOWS_DEMO_GUIDE.md
echo 3. Run setup_demo.bat
echo.
pause
