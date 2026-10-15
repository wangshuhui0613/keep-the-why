@echo off
REM ============================================================
REM  personal-kb-template one-click health check (Windows)
REM  Double-click this file to run. Read-only: it never
REM  modifies any file. Requires Python: https://www.python.org/downloads/
REM ============================================================

python tools\vault_health_check.py --root .

echo.
if errorlevel 1 (
    echo [FAIL] Health check found problems - see the list above.
) else (
    echo [PASS] Health check finished. No problems found.
)
echo.
pause
