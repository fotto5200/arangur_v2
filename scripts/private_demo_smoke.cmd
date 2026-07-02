@echo off
setlocal

set "BASE_URL=%~1"
if "%BASE_URL%"=="" set "BASE_URL=http://127.0.0.1:8000"
set "SCRIPT_DIR=%~dp0"
set "PAYLOAD=%SCRIPT_DIR%fixtures\private_demo_seed_briefing_spec_set.json"

if not exist "%PAYLOAD%" (
    echo Missing smoke payload: %PAYLOAD%
    exit /b 1
)

echo Private-demo smoke checks against %BASE_URL%
echo This script expects the Docker Compose stack to already be running.
echo.

echo [1/5] GET /api/health
curl.exe --fail --silent --show-error --output NUL "%BASE_URL%/api/health" || goto failed
echo OK
echo.

echo [2/5] GET /app/
curl.exe --fail --silent --show-error --output NUL "%BASE_URL%/app/" || goto failed
echo OK
echo.

echo [3/5] GET /api/report-elements
curl.exe --fail --silent --show-error --output NUL "%BASE_URL%/api/report-elements" || goto failed
echo OK
echo.

echo [4/5] POST /api/briefing-spec-sets
curl.exe --fail --silent --show-error --output NUL -X POST "%BASE_URL%/api/briefing-spec-sets" -H "Content-Type: application/json" --data-binary "@%PAYLOAD%" || goto failed
echo OK
echo.

echo [5/5] GET /api/briefing-spec-sets
curl.exe --fail --silent --show-error --output NUL "%BASE_URL%/api/briefing-spec-sets" || goto failed
echo OK
echo.

echo Private-demo smoke checks completed.
exit /b 0

:failed
echo.
echo Smoke check failed. Confirm Docker Desktop is running with the Linux engine, port 8000 belongs to this stack, and inspect logs with:
echo docker compose --env-file .env.private-demo logs app
exit /b 1
