@echo off
REM ============================================================
REM  keep-the-why one-click health check (Windows)
REM  Double-click this file to run. Read-only: it never
REM  modifies any file.
REM  Python is ONLY needed for this optional health check -
REM  the vault itself works fine without Python.
REM  Install Python: https://www.python.org/downloads/
REM ============================================================

where python >nul 2>nul
if errorlevel 1 (
    echo [SKIP] Python not found - health check skipped.
    echo.
    echo The health check is an OPTIONAL step. Your vault works
    echo fine without Python - this only affects running the check.
    echo.
    echo Install Python from https://www.python.org/downloads/
    echo then double-click this file again.
    echo.
    pause
    exit /b 2
)

python tools\vault_health_check.py --root .
set RC=%errorlevel%

echo.
if "%RC%"=="0" (
    echo [PASS] Health check finished. No problems found.
) else if "%RC%"=="1" (
    echo [FAIL] Health check found problems - see the list above.
) else (
    echo [ERROR] Health check could not run - error code %RC%.
    echo Check that Python is installed correctly.
)
echo.
pause
exit /b %RC%
