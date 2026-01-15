#!/bin/bash
################################################################################
# Linux Build Script for test_setup.py
# Creates a standalone executable using PyInstaller
################################################################################

set -e  # Exit on error

echo "============================================================================"
echo "RF Measurement Setup Test - Linux Build Script"
echo "============================================================================"
echo

# Change to script directory
cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or later"
    exit 1
fi

echo "[1/7] Python found:"
python3 --version
echo

# Check if virtual environment exists, create if not
if [ ! -d "build_env" ]; then
    echo "[2/7] Creating virtual environment..."
    python3 -m venv build_env
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully"
else
    echo "[2/7] Virtual environment already exists"
fi
echo

# Activate virtual environment
echo "[3/7] Activating virtual environment..."
source build_env/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi
echo

# Install/upgrade build requirements
echo "[4/7] Installing build dependencies..."
echo "This may take a few minutes on first run..."
python -m pip install --upgrade pip
pip install -r build_requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install build requirements"
    exit 1
fi
echo

# Clean previous build
echo "[5/7] Cleaning previous build artifacts..."
rm -rf build dist __pycache__
echo "Clean complete"
echo

# Build the executable
echo "[6/7] Building executable with PyInstaller..."
echo "This will take several minutes..."
pyinstaller --clean test_setup.spec
if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Build failed!"
    echo "Check the output above for error details"
    exit 1
fi
echo

# Generate VERSION.txt (without keys)
echo "[7/7] Generating VERSION.txt..."

BUILD_DATE=$(date '+%Y-%m-%d %H:%M:%S')
BUILD_HOST=$(hostname)
BUILDER=$(whoami)
PYINSTALLER_VER=$(pyinstaller --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
PYTHON_VER=$(python3 --version 2>&1)

# Read template and substitute variables
if [ -f "VERSION.txt.template" ]; then
    sed -e "s/{BUILD_DATE}/$BUILD_DATE/g" \
        -e "s/{BUILD_HOST}/$BUILD_HOST/g" \
        -e "s/{BUILDER}/$BUILDER/g" \
        -e "s/{PYINSTALLER_VERSION}/$PYINSTALLER_VER/g" \
        -e "s/{PYTHON_VERSION}/$PYTHON_VER/g" \
        VERSION.txt.template > VERSION.txt

    if [ $? -eq 0 ]; then
        echo "VERSION.txt created successfully"

        # Redact any encryption keys (hex strings) from VERSION.txt
        echo "Redacting encryption keys..."
        # Pattern 1: "key: <hex>" -> "key: [REDACTED]"
        # Pattern 2: Standalone 32+ char hex strings -> "[REDACTED]"
        sed -i -E 's/([Kk]ey[: ]+)[0-9a-fA-F]{16,}/\1[REDACTED]/g' VERSION.txt
        sed -i -E 's/\b[0-9a-fA-F]{32,}\b/[REDACTED]/g' VERSION.txt

        if [ $? -eq 0 ]; then
            echo "Keys successfully redacted from VERSION.txt"
        else
            echo "WARNING: Could not redact keys from VERSION.txt"
        fi
    else
        echo "WARNING: Could not generate VERSION.txt"
    fi
else
    echo "WARNING: VERSION.txt.template not found"
fi
echo

# Check if executable was created
if [ -f "dist/test_setup" ]; then
    echo "============================================================================"
    echo "BUILD SUCCESSFUL!"
    echo "============================================================================"
    echo
    echo "Executable location: dist/test_setup"
    echo
    echo "File size:"
    ls -lh dist/test_setup | awk '{print "  " $5 " (" $9 ")"}'
    echo
    echo "You can now:"
    echo "  1. Run the executable: ./dist/test_setup"
    echo "  2. Copy it to another Linux machine (same architecture)"
    echo "  3. Distribute it to users"
    echo
    echo "BUILD COMPLETED SUCCESSFULLY!"
    echo
    BUILD_SUCCESS=1
else
    echo "============================================================================"
    echo "BUILD FAILED - Executable not found"
    echo "============================================================================"
    echo
    echo "The build process completed but the executable was not created."
    echo "Check the PyInstaller output above for errors."
    echo
    BUILD_SUCCESS=0
fi

if [ "$BUILD_SUCCESS" -eq 1 ]; then
    echo
    echo "============================================================================"
    echo "Ready to distribute!"
    echo "============================================================================"
else
    echo
    echo "============================================================================"
    echo "Please review errors and try again"
    echo "============================================================================"
fi

echo
read -p "Press Enter to exit..."
