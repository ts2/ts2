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
import stat
import sys
import zipfile
from io import BytesIO
from os import path

import requests

import ts2
from Qt import QtWidgets, Qt
from ts2.gui import widgets
from ts2.utils import settings


class SettingsDialog(QtWidgets.QDialog):
    """Settings dialog"""

    def __init__(self, parent):
        """Constructor for the OpenDialog."""
        super().__init__(parent)
        self.setWindowTitle(
            self.tr("Settings")
        )
        self.setMinimumWidth(550)

        containerLayout = QtWidgets.QVBoxLayout()
        containerLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(containerLayout)

        # Header
        headerLabel = widgets.HeaderLabel(text=self.tr("User Settings"),
                                          align=Qt.AlignRight)
        containerLayout.addWidget(headerLabel)

        m = 20
        middleLayout = QtWidgets.QVBoxLayout()
        middleLayout.setContentsMargins(m, m, m, m)
        containerLayout.addLayout(middleLayout)

        # ======================
        # Startup Options
        grp = QtWidgets.QGroupBox()
        grp.setTitle(self.tr("Startup"))
        grp.setFlat(True)
        middleLayout.addWidget(grp)

        grid = QtWidgets.QGridLayout()
        grp.setLayout(grid)

        # Load Last
        row = 0
        self.chkLoadLast = QtWidgets.QCheckBox(self)
        self.chkLoadLast.setText(self.tr("Load last used sim"))
        self.chkLoadLast.toggled.connect(self.onLoadLast)
        grid.addWidget(self.chkLoadLast, row, 1, 1, 1)

        # ======================
        # Server Options
        grp = QtWidgets.QGroupBox()
        grp.setTitle(self.tr("Server"))
        grp.setFlat(True)
        middleLayout.addWidget(grp)

        grid = QtWidgets.QHBoxLayout()
        grp.setLayout(grid)

        self.btnDownloadServer = QtWidgets.QToolButton()
        self.btnDownloadServer.clicked.connect(self.downloadServer)
        self.btnDownloadServer.setText(self.tr("Download server"))
        grid.addWidget(self.btnDownloadServer)

        self.txtServerFound = QtWidgets.QLabel()
        self.updateServerLabel()
        grid.addWidget(self.txtServerFound)

        grid.addStretch(1)

        # ======================
        # Path Options
        grp = QtWidgets.QGroupBox()
        grp.setTitle("Directories")
        grp.setFlat(True)
        middleLayout.addWidget(grp)

        grid = QtWidgets.QGridLayout()
        grp.setLayout(grid)

        # Data dir
        row = 0
        grid.addWidget(QtWidgets.QLabel(self.tr("Data Dir")), row, 0, 1, 1,
                       Qt.AlignRight)

        self.txtDataDir = QtWidgets.QLineEdit()
        self.txtDataDir.setEnabled(False)
        grid.addWidget(self.txtDataDir, row, 1, 1, 1)

        butt = QtWidgets.QToolButton()
        butt.setText(self.tr("Default"))
        grid.addWidget(butt, row, 2, 1, 1)

        # Server dir
        row += 1
        grid.addWidget(QtWidgets.QLabel(self.tr("Server Dir")), row, 0, 1, 1,
                       Qt.AlignRight)

        self.txtServerDir = QtWidgets.QLineEdit()
        self.txtServerDir.setEnabled(False)
        grid.addWidget(self.txtServerDir, row, 1, 1, 1)

        butt = QtWidgets.QToolButton()
        butt.setText(self.tr("Default"))
        grid.addWidget(butt, row, 2, 1, 1)

        # Sims dir
        row += 1
        grid.addWidget(QtWidgets.QLabel(self.tr("Simulations Dir")), row, 0, 1,
                       1, Qt.AlignRight)
        self.txtSimsDir = QtWidgets.QLineEdit()
        self.txtSimsDir.setEnabled(False)
        grid.addWidget(self.txtSimsDir, row, 1, 1, 1)

        butt = QtWidgets.QToolButton()
        butt.setText(self.tr("Default"))
        grid.addWidget(butt, row, 2, 1, 1)

        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 10)
        grid.setColumnStretch(2, 0)

        # ======
        containerLayout.addStretch(20)

        self.loadSettings()

    def updateServerLabel(self):
        pass
        if path.isfile(settings.serverLoc):
            txt = self.tr('<span style="color: green;">Server found in Server Dir</span>')
        else:
            txt = self.tr('<span style="color: red;">Server not found. Click on Download</span>')
        self.txtServerFound.setText(txt)

    def loadSettings(self):
        v = settings.b(settings.LOAD_LAST, False)
        self.chkLoadLast.setChecked(v)

        self.txtDataDir.setText(settings.userDataDir)
        self.txtSimsDir.setText(settings.simulationsDir)
        self.txtServerDir.setText(settings.serverDir)

    def onLoadLast(self):
        v = 1 if self.chkLoadLast.isChecked() else 0
        settings.setValue(settings.LOAD_LAST, v)
        settings.sync()

    def closeEvent(self, ev):
        settings.setValue(settings.INITIAL_SETUP, "1")
        settings.sync()

    def downloadServer(self):
        QtWidgets.qApp.setOverrideCursor(Qt.WaitCursor)
        if sys.maxsize > 2 ** 32:
            bits = 'x86_64'
        else:
            bits = 'i386'

        url = "%s/releases/download/v%s/ts2-sim-server_%s_%s_%s.zip" % (
            ts2.get_info()['server_repo'],
            ts2.get_info()['server_version'],
            ts2.get_info()['server_version'],
            ts2.PLATFORMS_MAP[sys.platform],
            bits
        )

        response = requests.get(url)

        try:
            with zipfile.ZipFile(BytesIO(response.content)) as zf:
                zf.extract(settings.serverFileName, settings.serverDir)
        except zipfile.BadZipFile:
            QtWidgets.QMessageBox.critical(self, "Download Error",
                                           "Error while downloading %s."
                                           "Download server manually and put the executable in the server dir" % url)
            self.updateServerLabel()
            QtWidgets.qApp.restoreOverrideCursor()
            return

        st = os.stat(settings.serverLoc)
        os.chmod(settings.serverLoc, st.st_mode | stat.S_IEXEC)
        self.updateServerLabel()

        QtWidgets.qApp.restoreOverrideCursor()
