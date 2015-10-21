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

from Qt import QtWidgets, Qt

from ts2.utils import settings
from ts2.gui import widgets


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
        # Path Options
        grp = QtWidgets.QGroupBox()
        grp.setTitle("Directories - TODO")
        grp.setFlat(True)
        middleLayout.addWidget(grp)

        grid = QtWidgets.QGridLayout()
        grp.setLayout(grid)

        # Data dir
        row = 0
        grid.addWidget(QtWidgets.QLabel(self.tr("Data Dir")), row, 0, 1, 1,
                       Qt.AlignRight)

        self.txtDataDir = QtWidgets.QLineEdit()
        grid.addWidget(self.txtDataDir, row, 1, 1, 1)

        butt = QtWidgets.QToolButton()
        butt.setText(self.tr("Default"))
        grid.addWidget(butt, row, 2, 1, 1)

        # Sims dir
        row += 1
        grid.addWidget(QtWidgets.QLabel(self.tr("Simulations Dir")), row, 0, 1,
                       1, Qt.AlignRight)
        self.txtSimsDir = QtWidgets.QLineEdit()
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

    def loadSettings(self):
        v = settings.b(settings.LOAD_LAST, False)
        self.chkLoadLast.setChecked(v)

        self.txtDataDir.setText(settings.userDataDir)
        self.txtSimsDir.setText(settings.simulationsDir)

    def onLoadLast(self):
        v = 1 if self.chkLoadLast.isChecked() else 0
        settings.setValue(settings.LOAD_LAST, v)
        settings.sync()

    def closeEvent(self, ev):
        settings.setValue(settings.INITIAL_SETUP, "1")
        settings.sync()
