# cx_freeze setup file
#
# Call this script on Windows with:
# python build.py build

import sys, os

from cx_Freeze import setup, Executable
from ts2 import __APP_SHORT__, __APP_LONG__, __VERSION__


def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

# print("############# Generating translation files ###################")
# out = os.system("lrelease i18n/ts2.pro")


print("############# Freezing TS2 as an executable ###################")
build_exe_options = {
    "includes": ["atexit"],
    "excludes": ["tkinter", "test"],
    "packages": ["re", "simplejson", "websocket", "requests", "idna", "queue"],
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
}

base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

setup(
    name=__APP_SHORT__,
    version=__VERSION__,
    description=__APP_LONG__,
    options={"build_exe": build_exe_options},
    executables=[Executable("start-ts2.py", base=base, targetName="ts2.exe", icon="images/ts2.ico")]
)

if sys.platform == "win32":
    print("############# Making the installer ###################")
    compiler = find_file('Compil32.exe', 'C:\\Program Files (x86)')
    if not compiler:
        compiler = find_file('Compil32.exe', 'C:\\Program Files')
    if compiler:
        print("Inno Setup Compiler found at: %s" % compiler)
        os.system("\"%s\" /cc setup.iss" % compiler)
    else:
        print("No Inno Setup Compiler found, exiting.")
        sys.exit()

print("############### End of building process ##############")