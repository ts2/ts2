

from Qt import QtCore, QtWidgets, Qt


import ts2
from ts2.utils import settings
from ts2.gui import widgets

#translate = QtWidgets.qApp.translate



class SettingsDialog(QtWidgets.QDialog):
    """Settings dialog"""


    def __init__(self, parent, tab=0):
        """Constructor for the OpenDialog."""
        super().__init__(parent)
        self.setWindowTitle(
            self.tr("Settings")
        )
        self.setMinimumWidth(400)
        #self.setMinimumHeight(500)

        containerLayout = QtWidgets.QVBoxLayout()
        containerLayout.setContentsMargins(0,0,0,0)
        self.setLayout(containerLayout)

        # Header
        headerLabel = widgets.HeaderLabel(text="User Settings", align=Qt.AlignRight)
        containerLayout.addWidget(headerLabel)

        m = 20
        middleLayout = QtWidgets.QVBoxLayout()
        middleLayout.setContentsMargins(m,m,m,m)
        containerLayout.addLayout(middleLayout)


        # Startup Options
        grp = QtWidgets.QGroupBox()
        grp.setTitle("Startup")
        grp.setFlat(True)
        middleLayout.addWidget(grp)

        grid = QtWidgets.QGridLayout()
        grp.setLayout(grid)

        # Load Last
        row = 0
        self.chkLoadLast = QtWidgets.QCheckBox(self)
        self.chkLoadLast.setText("Load last sim")
        self.chkLoadLast.toggled.connect(self.onLoadLast)
        grid.addWidget(self.chkLoadLast, row, 1, 1, 1)

        # Zoom
        row += 1
        grid.addWidget(QtWidgets.QLabel("Zoom Level"), row, 0, 1, 1, Qt.AlignRight)
        self.comboZoom = QtWidgets.QComboBox(self)
        for z in range(1, 6):
            self.comboZoom.addItem("%s" % z, "%s" % z)
        self.comboZoom.currentIndexChanged.connect(self.onZoomChanged)
        grid.addWidget(self.comboZoom, row, 1, 1, 1)

        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 10)

        containerLayout.addStretch(20)

        self.loadSettings()

    def loadSettings(self):

        v = bool(settings.value(settings.LOAD_LAST, "0"))
        self.chkLoadLast.setChecked(v)


        z = settings.value(settings.DEFAULT_ZOOM, "1")
        idx = self.comboZoom.findData(z)
        if idx != -1:
            self.comboZoom.setCurrentIndex(idx)

    def onLoadLast(self, chk=None):

        v = 1 if self.chkLoadLast.isChecked() else 0
        settings.setValue(settings.LOAD_LAST, v )
        settings.sync()


    def onZoomChanged(self):
        v = self.comboZoom.itemData(self.comboZoom.currentIndex())
        settings.setValue(settings.DEFAULT_ZOOM, v )
        settings.sync()
