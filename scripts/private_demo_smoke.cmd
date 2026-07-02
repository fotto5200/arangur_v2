@echo off
setlocal

set "BASE_URL=%~1"
if "%BASE_URL%"=="" set "BASE_URL=http://127.0.0.1:8000"

echo Checking %BASE_URL%/api/health
curl.exe --fail --silent --show-error "%BASE_URL%/api/health" || exit /b 1
echo.

echo Saving briefing spec-set smoke payload
curl.exe --fail --silent --show-error -X POST "%BASE_URL%/api/briefing-spec-sets" -H "Content-Type: application/json" -d "{\"schema_version\":\"arangur.local_briefing_spec_set.v1\",\"synthetic_data\":true,\"client_context\":{\"client_family\":\"Northstar Family Office\",\"portfolio_context\":\"Docker private-demo smoke\"},\"client_briefing_set\":[],\"advisor_review_set\":[]}" || exit /b 1
echo.

echo Listing briefing spec sets
curl.exe --fail --silent --show-error "%BASE_URL%/api/briefing-spec-sets" || exit /b 1
echo.

echo Private-demo smoke curl checks completed.
