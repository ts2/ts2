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

from PyQt4.QtGui import *
from Clock import *

class Panel(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        # Clock
        self._clock = Clock(self)
        # Pause button
        self._pauseButton = QPushButton(tr("Pause"), self)
        self._pauseButton.setCheckable(true)
        self._pauseButton.toggled.connect(Simulation.instance().pause)
        self._pauseButton.toggled.connect(self.changePauseButtonText)
        # Time factor spinBox
        self._timeFactorSpinBox = QSpinBox(self)
        self._timeFactorSpinBox.setRange(0, 50)
        self._timeFactorSpinBox.setSingleStep(1)
        self._timeFactorSpinBox.setValue(1)
        self._timeFactorSpinBox.setSuffix("x")
        self._timeFactorSpinBox.valueChanged.connect(Simulation.instance().setTimeFactor)
        # Zoom spinBox
        self._zoomSpinBox = QSpinBox(self)
        self._zoomSpinBox.setRange(10,200)
        self._zoomSpinBox.setSingleStep(10)
        self._zoomSpinBox.setValue(100)
        self._zoomSpinBox.valueChanged.connect(MainWindow.instance().zoom)

        layout = QHBoxLayout
        layout.addSpacing(5)
        layout.addWidget(self._clock)
        layout.addSpacing(5)
        layout.addWidget(self._pauseButton)
        layout.addSpacing(5)
        layout.addWidget(QLabel(tr("Simulation speed: ")))
        layout.addWidget(self._timeFactorSpinBox)
        layout.addSpacing(5)
        layout.addWidget(QLabel(tr("Zoom: ")))
        layout.addWidget(self._zoomSpinBox)
        layout.addStretch()
        self.setLayout(layout)

        Simulation.instance().simulationLoaded.connect(self.updateWidgets)

    @pyqtProperty(Clock)
    def clock(self):
        return _clock

    @pyqtProperty(QSize)
    def sizeHint(self): 
        return QSize(800,40)
    
    @pyqtProperty(QSize) 
    def minimumSizeHint(self): 
        return QSize(200,40)
    
    @pyqtProperty(QSizePolicy)
    def sizePolicy(self): 
        return QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    @pyqtSlot()
    def updateWidgets(self):
        self._timeFactorSpinBox.setValue(Simulation.instance().option("timeFactor"))

    @pyqtSlot(bool)
    def changePauseButtonText(self, paused):
        if paused:
            self._pauseButton.setText(tr("Continue"));
        else:
            self._pauseButton.setText(tr("Pause"));


