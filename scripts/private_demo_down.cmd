@echo off
setlocal

if /I "%~1"=="--reset" goto reset

echo Stopping private-demo stack.
docker compose --env-file .env.private-demo down
set "STATUS=%ERRORLEVEL%"
echo.
echo To also delete the local Postgres demo volume, run:
echo scripts\private_demo_down.cmd --reset
exit /b %STATUS%

:reset
echo WARNING: This removes the local private-demo Postgres volume and saved demo metadata.
choice /M "Continue with docker compose --env-file .env.private-demo down -v"
if errorlevel 2 exit /b 1
docker compose --env-file .env.private-demo down -v
exit /b %ERRORLEVEL%
