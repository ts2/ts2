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

from Qt import QtCore

import ts2
import ts2.utils


class XSettings(QtCore.QSettings):
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

    def saveWindow(self, window):
        """Save window geometry and state"""
        self.setValue("window/%s/geometry" % window.objectName(),
                      window.saveGeometry())
        self.setValue("window/%s/state" % window.objectName(),
                      window.saveState())

    def restoreWindow(self, window):
        """Restore window geometry and state"""
        v = self.value("window/%s/geometry" % window.objectName())
        if v:
            window.restoreGeometry(v)

        v = self.value("window/%s/state" % window.objectName())
        if v:
            window.restoreState(v)

    def saveSplitter(self, window, splitter):
        self.setValue("window/%s/splitter" % window.objectName(),
                      splitter.saveState())

    def restoreSplitter(self, window, splitter):
        splitter.restoreState(self.value(
            "window/%s/splitter" % window.objectName()).toByteArray())

    def saveTree(self, tree):
        self.settings.setValue("tree/%s" % tree._settings_ki,
                               tree.header().saveState())

    def restoreTree(self, tree):
        tree.header().restoreState(
            self.settings.value("tree/%s" % tree._settings_ki).toByteArray())


    def setDebug(self, debug):
        """Set debug flag"""
        self._debug = debug

    @property
    def debug(self):
        return self._debug
