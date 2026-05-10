@echo off
cd /d "D:\HONEY\Projects\transport-master"
echo Adding MySQL schema to git...
"C:\Program Files\Git\bin\git.exe" add mysql_schema.sql
"C:\Program Files\Git\bin\git.exe" commit -m "Add MySQL schema with gr_date column"
"C:\Program Files\Git\bin\git.exe" push origin main
echo.
echo MySQL schema pushed to https://github.com/HoneyAdi/Transport-Final
echo.
echo To recreate the database on another server:
echo   mysql -u username -p database_name ^< mysql_schema.sql
pause
