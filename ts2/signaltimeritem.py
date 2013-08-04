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
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from ts2.signalitem import *

class SignalTimerItem(SignalItem):
    """ TODO Document SignalTimerItem class"""

    def __init__(self, simulation, record, timeFactor):
        super().__init__(simulation, record)
        self._tiType = "ST"
        self._signalState = SignalState.CLEAR
        timerSW = record.value("timersw")
        timerWC = record.value("timerwc")
        self._timerSW = timerSW * 60000 / timeFactor
        self._timerWC = timerWC * 60000 / timeFactor
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.updateSignalState)

    def trainTailActions(self, serviceCode):
        """Actions performed when a train passes :
        Close signal and launch timer."""
        super().trainTailActions(serviceCode)
        self._timer.stop()
        self._signalState = SignalState.STOP
        self._timer.start(self._timerSW)
        self.updateGraphics()

    @pyqtSlot()
    def updateSignalState(self):
        if not self._timer.isActive():
            if self._signalState == SignalState.CLEAR:
                self._signalState = SignalState.CLEAR
            elif self._signalState == SignalState.WARNING:
                self._signalState = SignalState.CLEAR
            elif self._signalState == SignalState.STOP:
                self._signalState = SignalState.WARNING
                self._timer.start(self._timerWC)
        if self._previousActiveRoute is not None:
            self._previousActiveRoute.beginSignal.updateSignalState()
        self.updateGraphics()

