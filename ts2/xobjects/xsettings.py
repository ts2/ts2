#
#   Copyright (C) 2008-2015 by
#     Nicolas Piganeau <npi@m4x.org> & TS2 Team
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

import os
import sys
from os import path

from Qt import QtCore, QtWidgets

import ts2
import ts2.utils


class XSettings(QtCore.QSettings):

    INITIAL_SETUP = "initial_setup"
    LOAD_LAST = "load_last"

    class HACKERS:
        npi = "npi"
        pedro = "pedromorgan"

    def __init__(self):
        super().__init__(ts2.__ORG_NAME__, ts2.__APP_SHORT__)

        self._debug = False

    def getRecent(self):
        """List of recent files
        
        :rtype: lst of str's
        """
        s = self.value("recent")
        if not s:
            return []
        return ts2.utils.from_json(s)

    def addRecent(self, filePath):
        """Add a recent file"""
        lst = self.getRecent()
        if filePath in lst:
            # already in so remove, so move to front
            lst.remove(filePath)
        # insert at front
        lst.insert(0, filePath)
        if len(lst) > 10:
            lst = lst[:10]
        self.setValue("recent", ts2.utils.to_json(lst))
        return lst

    def getEditorRecent(self):
        """List of recent files

        :rtype: lst of str's
        """
        s = self.value("editorRecent")
        if not s:
            return []
        return ts2.utils.from_json(s)

    def addEditorRecent(self, filePath):
        """Add a recent file"""
        lst = self.getEditorRecent()
        if filePath in lst:
            # already in so remove, so move to front
            lst.remove(filePath)
        # insert at front
        lst.insert(0, filePath)
        if len(lst) > 10:
            lst = lst[:10]
        self.setValue("editorRecent", ts2.utils.to_json(lst))
        return lst

    def saveWindow(self, window):
        """Save window geometry and state"""
        self.setValue("window/%s/geometry" % window.objectName(),
                      window.saveGeometry())
        if isinstance(window, QtWidgets.QDialog):
            return
        self.setValue("window/%s/state" % window.objectName(),
                      window.saveState())

    def restoreWindow(self, window):
        """Restore window geometry and state"""
        v = self.value("window/%s/geometry" % window.objectName())
        if v:
            window.restoreGeometry(v)

        if isinstance(window, QtWidgets.QDialog):
            return
        v = self.value("window/%s/state" % window.objectName())
        if v:
            window.restoreState(v)

    def setDebug(self, debug):
        """Set debug flag"""
        self._debug = debug

    @property
    def debug(self):
        return self._debug

    @staticmethod
    def _getUserDataDirectory():
        """Returns the folder in which to put the user data.

        If the source folder is inside the home directory, then we use it
        because it means that we have installed from sources. Otherwise we use
        ~/.ts2/
        """
        homeDir = os.path.expanduser("~")
        if os.path.commonprefix((homeDir, os.getcwd())).startswith(homeDir):
            return os.getcwd()
        else:
            os.makedirs(os.path.join(homeDir, ".ts2", "data"), exist_ok=True)
            os.makedirs(os.path.join(homeDir, ".ts2", "simulations"), exist_ok=True)
            os.makedirs(os.path.join(homeDir, ".ts2", "server"), exist_ok=True)
            return os.path.join(homeDir, ".ts2")

    @property
    def simulationsDir(self):
        return os.path.join(self._getUserDataDirectory(), "simulations")

    @property
    def userDataDir(self):
        return os.path.join(self._getUserDataDirectory(), "data")

    @property
    def serverDir(self):
        return os.path.join(self._getUserDataDirectory(), "server")

    @property
    def serverFileName(self):
        sfn = 'ts2-sim-server'
        if sys.platform == 'win32':
            sfn += '.exe'
        return sfn

    @property
    def serverLoc(self):
        return path.join(self.serverDir, self.serverFileName)

    def i(self, ki, default=None):
        """Return  value as int"""
        v = self.value(ki, default)
        no = default
        try:
            no = int(v)
        except ValueError:
            pass
        return no

    def b(self, ki, default=None):
        """Return value as bool"""
        v = self.i(ki, default)
        return bool(v)
