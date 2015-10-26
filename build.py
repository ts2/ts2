# cx_freeze setup file

import sys, os

from cx_Freeze import setup, Executable
from ts2 import __APP_SHORT__, __APP_LONG__, __VERSION__

# Generate the qm translation files
out = os.system("lrelease i18n/ts2.pro")

# Freeze the software into an exe
build_exe_options = {
    "includes": ["atexit"],
    "packages": ["re"],
    "include_files": [
        ("README.md", "doc/README.txt"),
        ("README_fr.md", "doc/README_fr.txt"),
        ("COPYING", "doc/COPYING.txt"),
        ("AUTHORS", "doc/AUTHORS.txt"),
        ("i18n/ts2_fr.qm", "i18n/ts2_fr.qm"),
        ("i18n/ts2_pl.qm", "i18n/ts2_pl.qm"),
        ("data/README", "data/README"),
    ],
    "include_msvcr": True,
    "icon": "images/ts2.ico"}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name=__APP_SHORT__,
    version=__VERSION__,
    description=__APP_LONG__,
    options={"build_exe": build_exe_options},
    executables=[Executable("start-ts2.py", base=base, targetName="ts2.exe")]
)

# Make the installer
