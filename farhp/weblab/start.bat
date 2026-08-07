@echo off
python scripts\migrate.py
if errorlevel 1 exit /b 1
if "%FARHP_HOST%"=="" set FARHP_HOST=127.0.0.1
if "%FARHP_PORT%"=="" set FARHP_PORT=8000
if "%FARHP_WORKERS%"=="" set FARHP_WORKERS=1
if "%FARHP_FORWARDED_ALLOW_IPS%"=="" set FARHP_FORWARDED_ALLOW_IPS=127.0.0.1
uvicorn app.main:app --host %FARHP_HOST% --port %FARHP_PORT% --workers %FARHP_WORKERS% --proxy-headers --forwarded-allow-ips %FARHP_FORWARDED_ALLOW_IPS%
