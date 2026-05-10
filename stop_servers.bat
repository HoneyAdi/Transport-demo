@echo off
echo Stopping all servers...
echo.

echo Stopping Python processes (Flask, etc.)...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
echo Python processes stopped.

echo.
echo Stopping MySQL (if running as standalone)...
taskkill /F /IM mysqld.exe 2>nul
echo MySQL processes stopped.

echo.
echo Stopping any Node.js servers...
taskkill /F /IM node.exe 2>nul
echo Node.js processes stopped.

echo.
echo Checking for any remaining processes on common ports...
netstat -ano | findstr ":5000\|:8000\|:3000\|:8080" | findstr "LISTENING"

echo.
echo All servers stopped!
pause
