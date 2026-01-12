@echo off
REM ============================================================================
REM Test Script for test_setup.exe
REM Verifies that the executable was built correctly and runs
REM ============================================================================

echo ============================================================================
echo Testing test_setup.exe
echo ============================================================================
echo.

cd /d "%~dp0"

REM Check if executable exists
if not exist "dist\test_setup.exe" (
    echo ERROR: test_setup.exe not found!
    echo.
    echo Expected location: dist\test_setup.exe
    echo.
    echo Please build the executable first by running:
    echo   build_windows.bat
    echo.
    pause
    exit /b 1
)

echo [OK] Executable found: dist\test_setup.exe
echo.

REM Display file info
echo File information:
dir dist\test_setup.exe | find "test_setup.exe"
echo.

REM Test 1: Check if executable runs
echo ============================================================================
echo Test 1: Smoke Test - Check if executable launches
echo ============================================================================
echo.
echo This will launch the executable and exit immediately.
echo The executable should prompt for IP addresses.
echo.
echo Press Ctrl+C when you see the IP address prompt to exit.
echo Press any key to start the test...
pause >nul
echo.

REM Run executable (user will need to Ctrl+C to exit)
dist\test_setup.exe

echo.
echo ============================================================================
echo Test complete!
echo ============================================================================
echo.
echo If you saw the IP address prompts, the executable is working correctly.
echo.
echo To run a full test with your instruments:
echo   1. Ensure your instruments are powered on and connected to the network
echo   2. Run: dist\test_setup.exe
echo   3. Enter the IP addresses when prompted
echo   4. Verify all tests pass
echo.
pause
