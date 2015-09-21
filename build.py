# cx_freeze setup file

import sys

from cx_Freeze import setup, Executable
from ts2 import utils

build_exe_options = {
    "includes" : ["atexit"],
    "packages" : ["re","sqlite3"],
    "include_files" : [
        ("data/drain.ts2","simulations/drain.ts2"),
        ("data/liverpool-st.ts2","simulations/liverpool-st.ts2"),
        ("README.md","doc/README.txt"),
        ("README_fr.md","doc/README_fr.txt"),
        ("COPYING","doc/COPYING.txt"),
        ("i18n/ts2_fr.qm","i18n/ts2_fr.qm")],
    "include_msvcr" : True,
    "icon" : "images/ts2.ico"}

base = None

if sys.platform == "win32":
    base = "Win32GUI"

setup(
        name = "ts2",
        version = utils.TS2_VERSION,
        description = "Train Signalling Simulation",
        options = {"build_exe" : build_exe_options},
        executables = [Executable("ts2.py", base = base)])

if sys.platform == "linux":

	# Todo: Add Linux support
