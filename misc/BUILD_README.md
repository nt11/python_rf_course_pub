# Windows Standalone Build for test_setup.py

This directory contains everything needed to build a standalone Windows executable for the RF Measurement Setup Test script.

## Overview

The build system creates a single executable file (`test_setup.exe`) that can run on any Windows machine without requiring Python or any dependencies to be installed.

## Build Files

- **`test_setup.py`** - The main script to be compiled
- **`test_setup.spec`** - PyInstaller specification file with all build configuration
- **`build_requirements.txt`** - Python packages needed for the build process
- **`build_windows.bat`** - Automated build script for Windows
- **`VERSION.txt.template`** - Template for build tracking file (keys redacted)
- **`BUILD_README.md`** - This file
- **`VERSION.txt`** - Auto-generated during build (excluded from git)

## Prerequisites

### Required Software
- **Windows 10/11** (or Windows Server 2016+)
- **Python 3.8 or later** (3.9-3.12 recommended)
  - Download from: https://www.python.org/downloads/
  - **IMPORTANT**: During installation, check "Add Python to PATH"

### Disk Space
- At least 500 MB free disk space for build environment
- Final executable size: ~30-50 MB

## Quick Start

### Method 1: Automated Build (Recommended)

1. Open Command Prompt or PowerShell
2. Navigate to the `misc` directory:
   ```cmd
   cd path\to\python_rf_course_pub\misc
   ```
3. Run the build script:
   ```cmd
   build_windows.bat
   ```
4. Wait for the build to complete (5-10 minutes on first run)
5. Find your executable at: `dist\test_setup.exe`

### Method 2: Manual Build

If you prefer to build manually or need more control:

1. Create a virtual environment:
   ```cmd
   python -m venv build_env
   ```

2. Activate the virtual environment:
   ```cmd
   build_env\Scripts\activate.bat
   ```

3. Install build requirements:
   ```cmd
   pip install -r build_requirements.txt
   ```

4. Run PyInstaller:
   ```cmd
   pyinstaller --clean test_setup.spec
   ```

5. Find the executable in `dist\test_setup.exe`

## Build Output

After a successful build, you'll find:

```
misc/
├── build/              (Temporary build files - can be deleted)
├── dist/
│   └── test_setup.exe  (Your standalone executable!)
├── build_env/          (Virtual environment - can be deleted after build)
├── VERSION.txt         (Build tracking file - auto-generated)
└── ...
```

## Build Tracking (VERSION.txt)

The build process automatically generates a `VERSION.txt` file for tracking build information:

**What's included:**
- Build date and time
- Build machine hostname and username
- PyInstaller and Python versions
- All dependency versions
- Build configuration details

**Security Note:**
- The VERSION.txt file does NOT contain any encryption keys or sensitive credentials
- All sensitive information is marked as `[REDACTED]` in the generated file
- The file is excluded from git commits (.gitignore) to prevent accidental exposure
- Keys (if any) are embedded directly in the executable, not stored in VERSION.txt

**Template:**
The `VERSION.txt.template` file defines the format. The build script fills in build metadata automatically while keeping sensitive fields redacted for security.

## Using the Executable

### On the Build Machine
Simply run:
```cmd
dist\test_setup.exe
```

### On Other Windows Machines
1. Copy `test_setup.exe` to the target machine
2. No installation needed - just double-click or run from command line
3. The executable includes all dependencies (Python, PyVISA, numpy, pyarbtools, etc.)

### Running the Tests
The executable will:
1. Prompt for Signal Generator IP address
2. Prompt for Spectrum Analyzer IP address
3. Run comprehensive connectivity and functionality tests
4. Display results with pass/fail status

## Troubleshooting

### Build Issues

**Problem**: "Python is not installed or not in PATH"
- **Solution**: Reinstall Python and check "Add Python to PATH" during installation
- Or manually add Python to PATH in System Environment Variables

**Problem**: "Failed to install build requirements"
- **Solution**:
  - Check internet connection
  - Try: `python -m pip install --upgrade pip`
  - Run build script again

**Problem**: "Build failed" or "Executable not found"
- **Solution**:
  - Check if you have enough disk space (500 MB+)
  - Look for error messages in the build output
  - Try deleting `build_env`, `build`, and `dist` folders and rebuild
  - Ensure antivirus isn't blocking PyInstaller

**Problem**: Build is very slow
- **Solution**: This is normal on first build (5-10 minutes). Subsequent builds are faster (2-3 minutes)

### Runtime Issues

**Problem**: Executable won't run or shows "missing DLL" error
- **Solution**: Install Visual C++ Redistributable:
  - Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
  - This is needed on some Windows machines

**Problem**: "Cannot connect to instrument"
- **Solution**: This is not a build issue - check:
  - Instrument IP addresses are correct
  - Instruments are powered on and connected to network
  - Network firewall allows VISA communication
  - Run the test on the same network as the instruments

**Problem**: Antivirus flags the executable
- **Solution**: This is a false positive common with PyInstaller executables
  - Add exception in your antivirus software
  - The executable is safe - built from the source code in this repo

## Advanced Configuration

### Customizing the Build

Edit `test_setup.spec` to customize:

- **Add an icon**: Set `icon='path/to/icon.ico'` in the `EXE` section
- **Change executable name**: Modify `name='test_setup'` in the `EXE` section
- **Disable UPX compression**: Set `upx=False` (increases file size, may fix compatibility issues)
- **Add more hidden imports**: Append to the `hidden_imports` list
- **Enable debug mode**: Set `debug=True` in the `EXE` section

### Build for Different Python Versions

The executable includes the Python version used to build it. To build for a different version:

1. Install the desired Python version
2. Modify the build script or create a new virtual environment with that version
3. Rebuild

### Optimizing Executable Size

Current size: ~30-50 MB. To reduce:

1. Enable UPX compression (already enabled by default)
2. Remove unused imports from `test_setup.py`
3. Use `--exclude-module` for large unused packages

## Build Environment Details

### Python Packages Bundled
- PyVISA (1.15.0) - VISA communication
- PyVISA-py (0.8.1) - Pure Python VISA backend
- pyarbtools (2025.6.1) - ARB waveform generation
- numpy (2.3.4) - Numerical computations
- socketscpi (2025.2.0) - SCPI communication
- And all their dependencies

### PyInstaller Configuration
- **Mode**: One-file bundle (single .exe)
- **Console**: Enabled (shows output in command prompt)
- **Compression**: UPX enabled
- **Platform**: Windows x64

## Testing the Build

After building, test the executable:

1. **Smoke test** (no instruments):
   ```cmd
   echo. | dist\test_setup.exe
   ```
   Should prompt for IP addresses and exit gracefully

2. **Full test** (requires instruments):
   - Run the executable
   - Enter your instrument IP addresses
   - Verify all tests pass

3. **Test on clean Windows machine**:
   - Copy the .exe to a machine without Python
   - Run it to ensure true standalone operation

## Rebuilding

When to rebuild:
- After modifying `test_setup.py`
- After updating dependencies
- When Python version changes

Quick rebuild:
```cmd
build_windows.bat
```

Clean rebuild (if having issues):
```cmd
rmdir /s /q build dist build_env
build_windows.bat
```

## Distribution

### Sharing the Executable

You can distribute `test_setup.exe` to users by:
1. Email attachment (30-50 MB)
2. USB drive
3. Network share
4. Cloud storage (Dropbox, Google Drive, etc.)

### License Compliance

Ensure compliance with licenses of bundled packages:
- PyVISA: MIT License
- PyVISA-py: MIT License
- pyarbtools: Check package license
- numpy: BSD License

The bundled packages maintain their original licenses.

## Support

### Getting Help

If you encounter issues:
1. Check the Troubleshooting section above
2. Review PyInstaller output for specific errors
3. Verify Python and pip versions
4. Check GitHub issues for similar problems

### Reporting Build Issues

When reporting build problems, include:
- Windows version
- Python version (`python --version`)
- Full build output (copy from terminal)
- Any error messages

## File Checklist

Before building, ensure these files exist:
- [ ] `test_setup.py` - Main script
- [ ] `test_setup.spec` - PyInstaller config
- [ ] `build_requirements.txt` - Build dependencies
- [ ] `build_windows.bat` - Build automation script
- [ ] `BUILD_README.md` - This documentation

## Version History

- **v1.0** (2026-01-12)
  - Initial Windows build configuration
  - PyInstaller spec file with full dependency detection
  - Automated build script
  - Comprehensive documentation

## Notes

- The build process creates a virtual environment (`build_env`) to avoid conflicts with system Python packages
- Build artifacts in `build/` and `dist/` folders are ignored by git
- The `.spec` file is the source of truth for build configuration
- First build takes longer due to downloading and processing dependencies
- Subsequent builds are faster as pip caches packages

---

**Ready to build?** Run `build_windows.bat` and you'll have a standalone executable in minutes!
