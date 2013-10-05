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

from PyQt4 import QtCore
from ts2.scenery import SignalItem, SignalState, TIProperty
from ts2 import utils

class SignalTimerItem(SignalItem):
    """The SignalTimerItem is a signal that clears after a given period of
    time. It does not represent a real type of signal, instead it is used to
    simulate what is happening outside of the simulation area.
    """
    def __init__(self, simulation, parameters):
        """Constructor for the SignalTimerItem class"""
        super().__init__(simulation, parameters)
        self._tiType = "ST"
        self._signalState = SignalState.CLEAR
        self._timerSW = parameters["timersw"]
        self._timerWC = parameters["timerwc"]
        self._timer = QtCore.QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.updateSignalState)

    properties = SignalItem.properties + [ \
                TIProperty("timerSW", "Time from STOP to WARNING (s)"), \
                TIProperty("timerWC", "Time from WARNING to CLEAR (s)")]

    @property
    def saveParameters(self):
        """Returns the parameters dictionary to save this TrackItem to the
        database"""
        timeFactor = float(self._simulation.option("timeFactor"))
        parameters = super().saveParameters
        parameters.update( {
                            "timersw":self._timerSW,
                            "timerwc":self._timerWC })
        return parameters

    def trainTailActions(self, serviceCode):
        """Actions performed when a train passes :
        Close signal and launch timer."""
        super().trainTailActions(serviceCode)
        self._timer.stop()
        self._signalState = SignalState.STOP
        timeFactor = float(self._simulation.option("timeFactor"))
        self._timer.start(self._timerSW * 1000 / timeFactor)
        self.updateGraphics()

    @QtCore.pyqtSlot()
    def updateSignalState(self):
        if not self._timer.isActive():
            if self._signalState == SignalState.CLEAR:
                self._signalState = SignalState.CLEAR
            elif self._signalState == SignalState.WARNING:
                self._signalState = SignalState.CLEAR
            elif self._signalState == SignalState.STOP:
                self._signalState = SignalState.WARNING
                timeFactor = float(self._simulation.option("timeFactor"))
                self._timer.start(self._timerWC * 1000 / timeFactor)
        if self._previousActiveRoute is not None:
            self._previousActiveRoute.beginSignal.updateSignalState()
        self.updateGraphics()

    @property
    def timerSW(self):
        """Returns the time in minutes for the SignalTimerItem to pass from
        the STOP state to the WARNING state"""
        timeFactor = float(self._simulation.option("timeFactor"))
        return float(self._timerSW)

    @timerSW.setter
    def timerSW(self, value):
        """Setter function for the timerSW property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            timeFactor = float(self._simulation.option("timeFactor"))
            self._timerSW = value

    @property
    def timerWC(self):
        """Returns the time in minutes for the SignalTimerItem to pass from
        the WARNING state to the CLEAR state"""
        timeFactor = float(self._simulation.option("timeFactor"))
        return float(self._timerWC)

    @timerWC.setter
    def timerWC(self, value):
        """Setter function for the timerWC property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            timeFactor = float(self._simulation.option("timeFactor"))
            self._timerWC = value

