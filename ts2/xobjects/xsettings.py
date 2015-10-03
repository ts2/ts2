<<<<<<< HEAD
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

    def get_recent(self):
        """List of recent files
        
        :rtype: lst of str's
        """
        s = self.value("recent")
        if not s:
            return []
        return ts2.utils.from_json(s)

    def add_recent(self, file_path):
        """Add a recent file"""
        lst = self.get_recent()
        if file_path in lst:
            # already in so remove, so move to front
            lst.remove(file_path)
        # insert at front
        lst.insert(0, file_path)
        self.setValue("recent", ts2.utils.to_json(lst))
        return lst

    def save_window(self, window):
        self.setValue("window/%s/geometry" % window.objectName(),
                      window.saveGeometry())
        self.setValue("window/%s/state" % window.objectName(),
                      window.saveState())

    def restore_window(self, window):
        v = self.value("window/%s/geometry" % window.objectName())
        if not v:
            return
        window.restoreGeometry(v)

        v = self.value("window/%s/state" % window.objectName())
        if not v:
            return
        window.restoreState(v)

    def save_splitter(self, window, splitter):
        self.setValue("window/%s/splitter" % window.objectName(),
                      splitter.saveState())

    def restore_splitter(self, window, splitter):
        splitter.restoreState(self.value(
            "window/%s/splitter" % window.objectName()).toByteArray())

    def save_tree(self, tree):
        self.settings.setValue("tree/%s" % tree._settings_ki,
                               tree.header().saveState())

    def restore_tree(self, tree):
        tree.header().restoreState(
            self.settings.value("tree/%s" % tree._settings_ki).toByteArray())
