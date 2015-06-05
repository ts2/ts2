#
#   Copyright (C) 2008-2013 by Nicolas Piganeau
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

from ts2.Qt import QtCore, QtWidgets, Qt

from ts2 import simulation


class ToolBarGroup(QtWidgets.QWidget):
    
    def __init__(self, parent=None, title=None):
        super().__init__(parent)
        
        lay = QtWidgets.QVBoxLayout()
        lay.setContentsMargins(0,0,0,0)
        lay.setSpacing(0)
        self.setLayout(lay)
        
        sty = "background-color: white; font-family: monospace; font-size: 8pt;"
        self.lblTitle = QtWidgets.QLabel()
        self.lblTitle.setStyleSheet(sty)
        self.lblTitle.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.lblTitle)
        
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)
        self.toolbar.setContentsMargins(0,0,0,0)
        self.toolbar.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
        #self.toolbar.setFixedHeight( 30 )
        lay.addWidget(self.toolbar)
        
        if title:
            self.setTitle(title)
            
    def setTitle(self, txt):
        self.lblTitle.setText(txt)
        
    def addWidget(self, widget):
        self.toolbar.addWidget(widget)
        
    def addAction(self, act):
        self.toolbar.addAction(act)

class Clock(QtWidgets.QLCDNumber):

    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.setNumDigits(8)
        self.display("--:--:--")
        self.resize(100,20)

    @QtCore.pyqtSlot(QtCore.QTime)
    def setTime(self, t):
        self.display(t.toString("hh:mm:ss"))


class ToolBarControl(QtWidgets.QToolBar):
    """TContains the zoom, speed and score"""

    zoomChanged = QtCore.pyqtSignal(int)
    
    def __init__(self, parent, simulationWindow):
        """Constructor for the Panel class."""
        super().__init__(parent)
        self.simulation = None
        self.simulationWindow = simulationWindow
       
        
        # Time factor spinBox
        tb = ToolBarGroup(title="Speed")
        self.timeFactorSpinBox = QtWidgets.QSpinBox(self)
        self.timeFactorSpinBox.setRange(0, 10)
        self.timeFactorSpinBox.setSingleStep(1)
        self.timeFactorSpinBox.setValue(1)
        self.timeFactorSpinBox.setSuffix("x")
        tb.addWidget(self.timeFactorSpinBox)
        self.addWidget(tb)
        
        # Zoom spinBox
        tb = ToolBarGroup(title="Zoom")
        self.zoomSpinBox = QtWidgets.QSpinBox(self)
        self.zoomSpinBox.setRange(10,200)
        self.zoomSpinBox.setSingleStep(10)
        self.zoomSpinBox.setValue(100)
        self.zoomSpinBox.valueChanged.connect(self.zoomSpinBoxChanged)
        tb.addWidget(self.zoomSpinBox)
        self.addWidget(tb)
        
        # score display
        tb = ToolBarGroup(title="Score")
        self.scoreDisplay = QtWidgets.QLCDNumber(self)
        self.scoreDisplay.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scoreDisplay.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scoreDisplay.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.scoreDisplay.setNumDigits(5)
        self.scoreDisplay.resize(70, 25)
        tb.addWidget(self.scoreDisplay)
        self.addWidget(tb)
        
        self.simulationWindow.simulationLoaded.connect(self.activate)

    @QtCore.pyqtSlot(simulation.Simulation)
    def activate(self, simulation):
        """Activates the panel with the given simulation."""
        self.simulation = simulation
        self.timeFactorSpinBox.valueChanged.connect(
                                            self.simulation.setTimeFactor)
        self.timeFactorSpinBox.setValue(
                                float(self.simulation.option("timeFactor")))



    @QtCore.pyqtSlot(int)
    def zoomSpinBoxChanged(self, percent):
        self.zoomChanged.emit(percent)

class ToolBarClock(QtWidgets.QToolBar):
    """The hold the clock and sim pause."""
    
    def __init__(self, parent, simulationWindow):
        """Constructor for the Panel class."""
        super().__init__(parent)
        self.simulation = None
        self.simulationWindow = simulationWindow
        # Clock
        self.clock = Clock(self)
        self.addWidget(self.clock)
        
        # Pause button
        self.pauseButton = QtWidgets.QPushButton(self.tr("Pause"), self)
        self.pauseButton.setCheckable(True)
        self.addWidget(self.pauseButton)
        
        
        self.simulationWindow.simulationLoaded.connect(self.activate)

    @QtCore.pyqtSlot(simulation.Simulation)
    def activate(self, simulation):
        """Activates the panel with the given simulation."""
        self.simulation = simulation
        self.pauseButton.toggled.connect(self.simulation.pause)
        self.pauseButton.toggled.connect(self.changePauseButtonText)

    

    @QtCore.pyqtSlot(bool)
    def changePauseButtonText(self, paused):
        if paused:
            self.pauseButton.setText(self.tr("Continue"));
        else:
            self.pauseButton.setText(self.tr("Pause"));

