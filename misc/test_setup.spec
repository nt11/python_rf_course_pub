# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for test_setup.py
Builds a standalone Windows executable for RF measurement system testing
"""

import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all submodules and data for critical packages
pyvisa_datas, pyvisa_binaries, pyvisa_hiddenimports = collect_all('pyvisa')
pyvisa_py_datas, pyvisa_py_binaries, pyvisa_py_hiddenimports = collect_all('pyvisa_py')
pyarbtools_datas, pyarbtools_binaries, pyarbtools_hiddenimports = collect_all('pyarbtools')

# Additional hidden imports that might not be auto-detected
hidden_imports = [
    'pyvisa',
    'pyvisa_py',
    'pyvisa_py.protocols',
    'pyvisa_py.protocols.rpc',
    'pyvisa_py.protocols.usbtmc',
    'pyvisa_py.protocols.usbutil',
    'pyvisa_py.protocols.vxi11',
    'pyvisa_py.tcpip',
    'pyvisa_py.serial',
    'pyvisa_py.usb',
    'pyvisa_py.gpib',
    'pyvisa.ctwrapper',
    'pyvisa.ctwrapper.functions',
    'pyvisa.ctwrapper.highlevel',
    'pyvisa.ctwrapper.types',
    'pyarbtools',
    'pyarbtools.instruments',
    'pyarbtools.communications',
    'pyarbtools.error',
    'numpy',
    'numpy.core',
    'numpy.core._methods',
    'numpy.lib',
    'numpy.lib.format',
    'typing_extensions',
    'socketscpi',
] + pyvisa_hiddenimports + pyvisa_py_hiddenimports + pyarbtools_hiddenimports

# Remove duplicates
hidden_imports = list(set(hidden_imports))

# Combine all data files
datas = pyvisa_datas + pyvisa_py_datas + pyarbtools_datas

# Combine all binaries
binaries = pyvisa_binaries + pyvisa_py_binaries + pyarbtools_binaries

a = Analysis(
    ['test_setup.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude GUI frameworks we don't need
        'tkinter',
        'matplotlib',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        # Exclude other large packages we don't use
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='test_setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file path here if desired
    version=None,
)
