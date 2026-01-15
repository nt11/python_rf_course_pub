@echo off
REM ============================================================================
REM Windows Build Script for test_setup.py
REM Creates a standalone Windows executable using PyInstaller
REM ============================================================================

echo ============================================================================
echo RF Measurement Setup Test - Windows Build Script
echo ============================================================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later and add it to PATH
    pause
    exit /b 1
)

echo [1/6] Python found:
python --version
echo.

REM Check if virtual environment exists, create if not
if not exist "build_env" (
    echo [2/6] Creating virtual environment...
    python -m venv build_env
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo [2/6] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call build_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Install/upgrade build requirements
echo [4/6] Installing build dependencies...
echo This may take a few minutes on first run...
python -m pip install --upgrade pip
pip install -r build_requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install build requirements
    pause
    exit /b 1
)
echo.

REM Clean previous build
echo [5/7] Cleaning previous build artifacts...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__
echo Clean complete
echo.

REM Build the executable
echo [6/7] Building executable with PyInstaller...
echo This will take several minutes...
pyinstaller --clean test_setup.spec
if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for error details
    pause
    exit /b 1
)
echo.

REM Generate VERSION.txt (without keys)
echo [7/7] Generating VERSION.txt...
powershell -Command "$date = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'; $host_name = $env:COMPUTERNAME; $user = $env:USERNAME; $pyinstaller_ver = (pyinstaller --version 2>&1 | Select-String -Pattern '\d+\.\d+' | ForEach-Object { $_.Matches.Value } | Select-Object -First 1); $python_ver = (python --version 2>&1); $content = Get-Content 'VERSION.txt.template' -Raw; $content = $content -replace '\{BUILD_DATE\}', $date; $content = $content -replace '\{BUILD_HOST\}', $host_name; $content = $content -replace '\{BUILDER\}', $user; $content = $content -replace '\{PYINSTALLER_VERSION\}', $pyinstaller_ver; $content = $content -replace '\{PYTHON_VERSION\}', $python_ver; $content | Out-File -FilePath 'VERSION.txt' -Encoding UTF8 -NoNewline"
if errorlevel 1 (
    echo WARNING: Could not generate VERSION.txt
) else (
    echo VERSION.txt created successfully

    REM Redact any encryption keys (hex strings) from VERSION.txt
    echo Redacting encryption keys...
    powershell -Command "$content = Get-Content 'VERSION.txt' -Raw; $content = $content -replace '([Kk]ey[:\s]+)[0-9a-fA-F]{16,}', '$1[REDACTED]'; $content = $content -replace '([0-9a-fA-F]{32,})', '[REDACTED]'; $content | Out-File -FilePath 'VERSION.txt' -Encoding UTF8 -NoNewline"
    if errorlevel 1 (
        echo WARNING: Could not redact keys from VERSION.txt
    ) else (
        echo Keys successfully redacted from VERSION.txt
    )
)
echo.

REM Check if executable was created
if exist dist\test_setup.exe (
    echo ============================================================================
    echo BUILD SUCCESSFUL!
    echo ============================================================================
    echo.
    echo Executable location: dist\test_setup.exe
    echo.
    echo File size:
    for %%I in (dist\test_setup.exe) do echo   %%~zI bytes ^(~%%~zI bytes^)
    echo.
    echo You can now:
    echo   1. Run the executable: dist\test_setup.exe
    echo   2. Copy it to another Windows machine ^(no Python needed^)
    echo   3. Distribute it to users
    echo.
    echo BUILD COMPLETED SUCCESSFULLY!
    echo.
    set BUILD_SUCCESS=1
) else (
    echo ============================================================================
    echo BUILD FAILED - Executable not found
    echo ============================================================================
    echo.
    echo The build process completed but the executable was not created.
    echo Check the PyInstaller output above for errors.
    echo.
    set BUILD_SUCCESS=0
)

if "%BUILD_SUCCESS%"=="1" (
    echo.
    echo ============================================================================
    echo Ready to distribute!
    echo ============================================================================
) else (
    echo.
    echo ============================================================================
    echo Please review errors and try again
    echo ============================================================================
)

echo Press any key to exit...
pause >nul
