#
#   Copyright (C) 2008-2015 by Nicolas Piganeau
#   npi@m4x.org
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

from Qt import QtCore, QtWidgets, Qt

from ts2 import simulation


class ClockWidget(QtWidgets.QLCDNumber):
    """Clock LCD Widget"""
    def __init__(self, parent):
        """Constructor for the ClockWidget class."""
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.setNumDigits(8)
        self.display("--:--:--")
        self.resize(100, 20)

    @QtCore.pyqtSlot(QtCore.QTime)
    def setTime(self, t):
        self.display(t.toString("hh:mm:ss"))


class ZoomWidget(QtWidgets.QWidget):
    """Zoom slider bar with associated spinBox."""

    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        """Constructor for the ZoomWidget class."""
        super().__init__(parent)
        #self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
        #                   QtWidgets.QSizePolicy.Minimum)
        self.button = QtWidgets.QPushButton(self.tr("100%"), self)

        self.slider = QtWidgets.QSlider(Qt.Horizontal, self)
        self.slider.setRange(10, 200)
        self.slider.setValue(100)
        self.slider.setSingleStep(10)

        self.spinBox = QtWidgets.QSpinBox(self)
        self.spinBox.setRange(10, 200)
        self.spinBox.setSingleStep(1)
        self.spinBox.setValue(100)
        self.spinBox.setSuffix("%")
        self.spinBox.setCorrectionMode(
            QtWidgets.QAbstractSpinBox.CorrectToNearestValue
        )

        self.button.clicked.connect(self.setDefaultZoom)
        self.slider.valueChanged.connect(self.spinBox.setValue)
        self.spinBox.valueChanged.connect(self.slider.setValue)
        self.spinBox.valueChanged.connect(self.valueChanged)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(0,0,0,0)
        hlayout.addWidget(self.button)
        hlayout.addWidget(self.slider)
        hlayout.addWidget(self.spinBox)
        self.setLayout(hlayout)

    @QtCore.pyqtSlot()
    def setDefaultZoom(self):
        """Sets the zoom to 100%."""
        self.spinBox.setValue(100)
    """
    def sizeHint(self):
        return QtCore.QSize(300, 50)

    def minimumSizeHint(self):
        return QtCore.QSize(300, 50)
    """

class ControlBarWidget(QtWidgets.QWidget):
    """The ControlBarWidget is the display rectangle below the scene holding the widgets
    necessary to play the simulation (e.g. clock)."""

    def __init__(self, parent, simulationWindow):
        """Constructor for the ControlBarWidget class."""
        super().__init__(parent)
        self.simulation = None
        self.simulationWindow = simulationWindow
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Fixed)
        # Clock
        self.clock = ClockWidget(self)

        # Pause button
        self.pauseButton = QtWidgets.QPushButton(self.tr("Pause"), self)
        self.pauseButton.setCheckable(True)

        # Time factor spinBox
        self.timeFactorSpinBox = QtWidgets.QSpinBox(self)
        self.timeFactorSpinBox.setRange(0, 10)
        self.timeFactorSpinBox.setSingleStep(1)
        self.timeFactorSpinBox.setValue(1)
        self.timeFactorSpinBox.setSuffix("x")

        # Zoom spinBox
        self.zoomWidget = ZoomWidget(self)
        self.zoomWidget.valueChanged.connect(self.simulationWindow.zoom)

        # Score display
        self.scoreDisplay = QtWidgets.QLCDNumber(self)
        self.scoreDisplay.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scoreDisplay.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scoreDisplay.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.scoreDisplay.setNumDigits(5)
        self.scoreDisplay.resize(70, 25)

        layout = QtWidgets.QHBoxLayout()
        layout.addSpacing(5)
        layout.addWidget(self.clock)
        layout.addSpacing(5)
        layout.addWidget(self.pauseButton)
        layout.addSpacing(5)
        layout.addWidget(QtWidgets.QLabel(self.tr("Simulation speed: ")))
        layout.addWidget(self.timeFactorSpinBox)
        layout.addSpacing(5)
        # layout.addWidget(QtWidgets.QLabel(self.tr("Zoom: ")))
        layout.addWidget(self.zoomWidget)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(self.tr("Penalty points: ")))
        layout.addWidget(self.scoreDisplay)
        self.setLayout(layout)

        self.simulationWindow.simulationLoaded.connect(self.activate)

    @QtCore.pyqtSlot(simulation.Simulation)
    def activate(self, sim):
        """Activates the panel with the given simulation."""
        self.simulation = sim
        self.pauseButton.toggled.connect(self.simulation.pause)
        self.pauseButton.toggled.connect(self.changePauseButtonText)
        self.timeFactorSpinBox.valueChanged.connect(
            self.simulation.setTimeFactor
        )
        self.timeFactorSpinBox.setValue(
            float(self.simulation.option("timeFactor"))
        )

    zoomChanged = QtCore.pyqtSignal(int)

    def sizeHint(self):
        return QtCore.QSize(800, 40)

    def minimumSizeHint(self):
        return QtCore.QSize(200, 40)

    @QtCore.pyqtSlot(bool)
    def changePauseButtonText(self, paused):
        if paused:
            self.pauseButton.setText(self.tr("Continue"))
        else:
            self.pauseButton.setText(self.tr("Pause"))

    @QtCore.pyqtSlot(int)
    def zoomWidgetChanged(self, percent):
        self.zoomChanged.emit(percent)


class XGraphicsView(QtWidgets.QGraphicsView):
    """QGraphicsView with wheel events"""

    wheelChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        """Constructor for the XGraphicsView class."""
        super().__init__(parent)

    def wheelEvent(self, ev):
        if ev.angleDelta().y() > 1:
            self.wheelChanged.emit(+1)
        else:
            self.wheelChanged.emit(-1)


class StatusBar(QtWidgets.QWidget):


    def __init__(self, parent=None):
        """Constructor for the StatusBar class."""
        super().__init__(parent)

        self.lay = QtWidgets.QHBoxLayout()
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.lay)

        self.statusBar = QtWidgets.QStatusBar()
        self.lay.addWidget(self.statusBar, 1)
        self.statusBar.showMessage("IDLE")


        self.progressBar = QtWidgets.QProgressBar()
        self.lay.addWidget(self.progressBar, 1)
        self.progressBar.hide()


    def showMessage(self, txt, timeout=1):
        self.statusBar.showMessage(txt)
        # TODO set timeout

    def showBusy(self, is_busy):
        if is_busy:
            self.progressBar.setRange(0,0)
        else:
            self.progressBar.setRange(0,1)
        self.progressBar.setVisible(is_busy)

class ToolBarGroup(QtWidgets.QWidget):

    def __init__(self, parent=None, title=None):
        """Constructor for the ToolBarGroup class."""
        super().__init__(parent)

        # Main Layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins( 0, 0, 0, 0 )
        mainLayout.setSpacing( 0 )
        self.setLayout( mainLayout )

        # Label
        self.label = QtWidgets.QLabel()
        lbl_sty = "background: #cccccc; " # qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #fefefe, stop: 1 #CECECE);"
        lbl_sty += " color: #333333; font-size: 7pt; padding: 1px;" # border: 1px outset #cccccc;"
        self.label.setStyleSheet( lbl_sty )
        self.label.setAlignment( QtCore.Qt.AlignCenter )
        mainLayout.addWidget( self.label )

        # Toolbar
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setToolButtonStyle( QtCore.Qt.ToolButtonTextBesideIcon )
        self.toolbar.setFixedHeight( 30 )
        mainLayout.addWidget( self.toolbar )

        if title:
            self.setTitle(title)

    def setTitle(self, title):
        self.label.setText( "%s" % title )

    def addWidget(self, widget):
        self.toolbar.addWidget(widget)

    def addAction(self, action):
        self.toolbar.addAction(action)
