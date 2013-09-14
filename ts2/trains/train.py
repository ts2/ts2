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
from math import sqrt

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

from ts2 import serviceassigndialog
from ts2 import scenery
from ts2 import routing
from ts2 import utils

tr = QtCore.QObject().tr

class TrainStatus:
    """This class holds the enum describing the status of a train"""

    INACTIVE = 0        # Not yet entered on the scene
    RUNNING = 10        # Running with a positive speed
    STOPPED = 20        # Scheduled stop, e.g. at a station
    WAITING = 30        # Unscheduled stop, e.g. at a red signal
    OUT = 40            # Exited the area
    END_OF_SERVICE = 50 # Ended its service and no new service assigned

    @classmethod
    def text(cls, status):
        """Returns the text corresponding to each status to display in the
        application."""
        if status == cls.INACTIVE:
            return tr("Inactive")
        elif status == cls.RUNNING:
            return tr("Running")
        elif status == cls.STOPPED:
            return tr("Stopped at station")
        elif status == cls.WAITING:
            return tr("Waiting at red signal")
        elif status == cls.OUT:
            return tr("Exited the area")
        elif status == cls.END_OF_SERVICE:
            return tr("End of service")
        else:
            return ""


class TrainListModel(QtCore.QAbstractTableModel):
    """Model for displaying trains as a list during the game
    """
    def __init__(self, simulation):
        """Constructor for the TrainListModel class"""
        super().__init__()
        self._simulation = simulation

    def rowCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of rows of the model, corresponding to the
        number of trains of the simulation"""
        return len(self._simulation.trains)

    def columnCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of columns of the model"""
        return 7

    def data(self, index, role = Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole:
            train = self._simulation.trains[index.row()]
            if index.column() ==  0:
                return train.serviceCode
            elif index.column() == 1:
                return TrainStatus.text(train.status)
            elif index.column() == 2:
                return train.currentService.entryPlaceName
            elif index.column() == 3:
                return train.currentService.exitPlaceName
            elif index.column() == 4:
                return train.currentService.nextStopName()
            elif index.column() == 5:
                return train.currentService.nextStopArrivalTime()
            elif index.column() == 6:
                return train.currentService.nextStopDepartureTime()
            else:
                return ""
        return None

    def headerData(self, column, orientation, role = Qt.DisplayRole):
        """Returns the column headers to display"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if column == 0:
                return self.tr("Code")
            elif column == 1:
                return self.tr("Status")
            elif column == 2:
                return self.tr("From")
            elif column == 3:
                return self.tr("Destination")
            elif column == 4:
                return self.tr("Next stop")
            elif column == 5:
                return self.tr("Arrival time")
            elif column == 6:
                return self.tr("Departure time")
            else:
                return ""
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        return Qt.ItemIsSelectable|Qt.ItemIsEnabled

    @QtCore.pyqtSlot()
    def update(self):
        """Emits the dataChanged signal for indexes which change with time,
        i.e. the status, next stop, arrival and departure times columns"""
        self.dataChanged.emit(self.index(0, 1),
                              self.index(self.rowCount() - 1, 1))
        self.dataChanged.emit(self.index(0, 4),
                              self.index(self.rowCount() - 1, 6))



class TrainsModel(QtCore.QAbstractTableModel):
    """Model for displaying trains as a list in the editor
    """
    def __init__(self, editor):
        """Constructor for the TrainsModel class"""
        super().__init__()
        self._editor = editor

    def rowCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of rows of the model, corresponding to the
        number of trains of the editor"""
        return len(self._editor.trains)

    def columnCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of columns of the model"""
        return 6

    def data(self, index, role = Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole or role == Qt.EditRole:
            train = self._editor.trains[index.row()]
            if index.column() ==  0:
                return index.row()
            elif index.column() == 1:
                return train.serviceCode
            elif index.column() == 2:
                return train.trainTypeCode
            elif index.column() == 3:
                return train.appearTimeStr
            elif index.column() == 4:
                return train.trainHeadStr
            elif index.column() == 5:
                return train.initialSpeed
            else:
                return ""
        return None

    def headerData(self, column, orientation, role = Qt.DisplayRole):
        """Returns the column headers to display"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if column == 0:
                return self.tr("id")
            elif column == 1:
                return self.tr("Service code")
            elif column == 2:
                return self.tr("Train type")
            elif column == 3:
                return self.tr("Entry time")
            elif column == 4:
                return self.tr("Entry position")
            elif column == 5:
                return self.tr("Entry speed")
            else:
                return ""
        return None

    def setData(self, index, value, role):
        """Updates data when modified in the view"""
        if role == Qt.EditRole:
            if index.column() == 1:
                self._editor.trains[index.row()].serviceCode = value
            elif index.column() == 2:
                self._editor.trains[index.row()].trainTypeCode = value
            elif index.column() == 3:
                self._editor.trains[index.row()].appearTimeStr = value
            elif index.column() == 4:
                self._editor.trains[index.row()].trainHeadStr = value
            elif index.column() == 5:
                self._editor.trains[index.row()].initialSpeed = value
            else:
                return False
            self.dataChanged.emit(index, index)
            return True
        return False


    def flags(self, index):
        """Returns the flags of the model"""
        flags = Qt.ItemIsSelectable|Qt.ItemIsEnabled
        if index.column() != 0:
            flags |= Qt.ItemIsEditable
        return flags

    @property
    def simulation(self):
        """Returns the simulation this model is attached to."""
        return self._editor


class TrainInfoModel(QtCore.QAbstractTableModel):
    """Model for displaying a single service information in a view
    """
    def __init__(self, simulation):
        """Constructor for the TrainInfoModel class"""
        super().__init__()
        self._simulation = simulation
        self._train = None

    def rowCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of rows in the model"""
        if self._train is not None:
            return 11
        else:
            return 0

    def columnCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of columns of the model"""
        if self._train is not None:
            return 3
        else:
            return 0

    def data(self, index, role = Qt.DisplayRole):
        """Returns the data at the given index"""
        if self._train is not None:
            if role == Qt.DisplayRole:
                if index.column() == 0:
                    if index.row() == 0:
                        return self.tr("Service Code:")
                    elif index.row() == 1:
                        return self.tr("Status")
                    elif index.row() == 2:
                        return self.tr("Speed:")
                    elif index.row() == 3:
                        return self.tr("Train Type:")
                    elif index.row() == 4:
                        return ""
                    elif index.row() == 5:
                        return self.tr("From:")
                    elif index.row() == 6:
                        return self.tr("Destination:")
                    elif index.row() == 7:
                        return ""
                    elif index.row() == 8:
                        return self.tr("Next Stop:")
                    elif index.row() == 9:
                        return self.tr("Arrival time:")
                    elif index.row() == 10:
                        return self.tr("Departure time:")
                elif index.column() == 1:
                    if index.row() == 0:
                        return self._train.serviceCode
                    elif index.row() == 1:
                        return TrainStatus.text(self._train.status)
                    elif index.row() == 2:
                        return self.tr("%3.0d km/h") % \
                                       (float(self._train.speed) * 3.6)
                    elif index.row() == 3:
                        return self._train.trainType.description
                    elif index.row() == 4:
                        return ""
                    elif index.row() == 5:
                        return self._train.currentService.entryPlaceName
                    elif index.row() == 6:
                        return self._train.currentService.exitPlaceName
                    elif index.row() == 7:
                        return ""
                    elif index.row() == 8:
                        return self._train.currentService.nextStopName()
                    elif index.row() == 9:
                        return self._train.currentService\
                                .nextStopArrivalTime().toString("hh:mm:ss")
                    elif index.row() == 10:
                        return self._train.currentService\
                                .nextStopDepartureTime().toString("hh:mm:ss")
                    else:
                        return ""
        return None

    def headerData(self, column, orientation, role = Qt.DisplayRole):
        """Returns the headers for this model"""
        if self._train is not None \
           and orientation == Qt.Horizontal \
           and role == Qt.DisplayRole:
            if column == 0:
                return self.tr("Key")
            elif column == 1:
                return self.tr("Value")
            else:
                return ""
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        return Qt.ItemIsEnabled

    @property
    def train(self):
        """Returns the train instance associated with this model"""
        return self._train

    @QtCore.pyqtSlot(str)
    def setTrainByServiceCode(self, serviceCode):
        """Sets the train instance associated with this model from its
        serviceCode"""
        self._train = self._simulation.train(serviceCode)
        self.reset()


class Train(QtCore.QObject):
    """A train is a stock running on a track at a certain speed and to which
    is assigned a service.
    """

    trainStoppedAtStation = QtCore.pyqtSignal(scenery.Place)
    trainDepartedFromStation = QtCore.pyqtSignal(scenery.Place)

    def __init__(self, simulation, parameters):
        """Constructor for the Train class"""
        super().__init__()
        self._simulation = simulation
        self._serviceCode = parameters["servicecode"]
        self._trainType = self.simulation.trainTypes[parameters["traintype"]]
        self._speed = 0
        self._initialSpeed = float(parameters["speed"])
        self._accel = 0
        tiId = parameters["tiid"]
        previousTiId = parameters["previoustiid"]
        posOnTI = parameters["posonti"]
        self._trainHead = routing.Position(
                                    self.simulation.trackItem(tiId),
                                    self.simulation.trackItem(previousTiId),
                                    posOnTI)
        self._status = TrainStatus.INACTIVE
        self._stoppedTime = 0
        self._appearTime = QtCore.QTime.fromString(parameters["appeartime"])
        self._previousSignal = self.findPreviousSignal()
        self.findNextSignal().trainServiceCode = self._serviceCode
        self._simulation.timeElapsed.connect(self.advance)
        self._simulation.timeChanged.connect(self.activate)
        # FIXME Throw back all these actions to MainWindow
        self.assignAction = QtGui.QAction(self.tr("Reassign service..."),
                                            self)
        self.assignAction.triggered.connect(self.reassignService)
        self.resetServiceAction = QtGui.QAction(self.tr("Reset service"),
                                                  self)
        self.resetServiceAction.triggered.connect(self.resetService)
        self.reverseAction = QtGui.QAction(self.tr("Reverse"), self)
        self.reverseAction.triggered.connect(self.reverse)

    def isOut(self):
        """Returns true if the train exited the area"""
        return self._trainHead.isOut() and \
               self._trainHead.positionOnTI() > self._trainType.length()

    def isActive(self):
        """Returns true if the train is in the area and its current service
        is not finished"""
        return self._status != TrainStatus.INACTIVE and \
               self._status != TrainStatus.OUT and \
               self._status != TrainStatus.END_OF_SERVICE

    @property
    def serviceCode(self):
        """Returns the service code of this train"""
        return self._serviceCode

    @serviceCode.setter
    def serviceCode(self, serviceCode):
        """Changes the train current service code to serviceCode"""
        self._serviceCode = serviceCode
        self.drawTrain(0)
        self.findNextSignal().trainServiceCode = serviceCode

    @property
    def simulation(self):
        """Returns the simulation owning this train"""
        return self._simulation

    @property
    def status(self):
        """Returns the status of the train"""
        return self._status

    @property
    def currentService(self):
        """Returns the Service object assigned to this train"""
        return self._simulation.service(self._serviceCode)

    def showTrainActionsMenu(self, widget, pos):
        """Pops-up the train actions menu on the given QWidget"""
        contextMenu = QtGui.QMenu(widget)
        contextMenu.addAction(self.assignAction)
        contextMenu.addAction(self.resetServiceAction)
        contextMenu.addAction(self.reverseAction)
        contextMenu.exec_(pos)

    @property
    def trainType(self):
        """Returns the TrainType of this Train"""
        return self._trainType

    @property
    def trainTypeCode(self):
        """Returns the code of the train type"""
        return self._trainType.code

    @trainTypeCode.setter
    def trainTypeCode(self, value):
        """Setter function for the trainTypeCode property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINS:
            self._trainType = self.simulation.trainTypes[value]

    @property
    def speed(self):
        """Returns the current speed of the Train."""
        return self._speed

    @property
    def initialSpeed(self):
        """Returns the initial speed of the train, i.e. the speed it has when
        it appears on the scene"""
        return self._initialSpeed

    @initialSpeed.setter
    def initialSpeed(self, value):
        """Setter function for the initialSpeed property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINS:
            if value is None or value == "": value = "0.0"
            self._initialSpeed = float(value)

    @property
    def trainHead(self):
        """Returns the Position of the head of this train."""
        return self._trainHead

    @trainHead.setter
    def trainHead(self, value):
        """Setter function for the trainHead property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINS:
            self._trainHead = value

    @property
    def trainHeadStr(self):
        """Returns the Position of the head of this train."""
        return str(self._trainHead)

    @trainHeadStr.setter
    def trainHeadStr(self, value):
        """Setter function for the trainHeadStr property."""
        if self._simulation.context == utils.Context.EDITOR_TRAINS:
            tiId, ptiId, posOnTI = eval(value.strip('()'))
            trackItem = self.simulation.trackItem(tiId)
            previousTI = self.simulation.trackItem(ptiId)
            self.trainHead = routing.Position(trackItem, previousTI, posOnTI)

    @property
    def appearTimeStr(self):
        """Returns the time at which this train appears on the scene as a
        String."""
        return self._appearTime.toString("HH:mm:ss")

    @appearTimeStr.setter
    def appearTimeStr(self, value):
        """Setter function for the appearTime property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINS:
            self._appearTime = QtCore.QTime.fromString(value)


    @QtCore.pyqtSlot(float)
    def advance(self, secs):
        """Advances the train by a step corresponding to the elapsed secs,
        and executes all the associated actions."""
        if self.isActive():
            self.setSpeed(secs)
            advanceLength = self._speed * secs
            self._trainHead += advanceLength
            #self.updateSignals()
            self.updateStatus(secs)
            self.drawTrain(advanceLength)
            self.executeActions(advanceLength)

    @QtCore.pyqtSlot(QtCore.QTime)
    def activate(self, time):
        """Activate this Train if time is after this Train appearTime."""
        if self._status == TrainStatus.INACTIVE:
            if self._appearTime < time:
                self._status = TrainStatus.RUNNING
                self._speed = self._initialSpeed
                self.drawTrain()
                signalBehind = self.findPreviousSignal()
                if signalBehind is not None:
                    signalBehind.updateSignalState()
                invertedHead = self._trainHead.reversed()
                signalAhead = self.findPreviousSignal(invertedHead)
                if signalAhead is not None:
                    signalAhead.updateSignalState()


    @QtCore.pyqtSlot()
    def reverse(self):
        """Reverses the train direction."""
        if self._speed == 0:
            self.findNextSignal().resetTrainServiceCode()
            activeRoute = self.trainHead.trackItem.activeRoute
            if activeRoute is not None:
                activeRoute.desactivate()
            trainTail = self._trainHead - self._trainType.length
            self._trainHead = trainTail.reversed()
            self._speed = 0
            self.findNextSignal().trainServiceCode = self.serviceCode


    @QtCore.pyqtSlot()
    def reassignService(self):
        """ Pops up a dialog for the user to choose the new service and
        reassign it to this train, if the service is not already assigned
        to another train"""
        sad = serviceassigndialog.ServiceAssignDialog(
                                        self._simulation.simulationWindow)
        if sad.exec_() == QtGui.QDialog.Accepted:
            newServiceCode = sad.getServiceCode()
            if newServiceCode != "" and \
               self._simulation.train(newServiceCode) is None:
                self.serviceCode = newServiceCode
                self._status = TrainStatus.INACTIVE

    @QtCore.pyqtSlot()
    def resetService(self):
        """Resets the service, i.e. sets the pointer to the first station."""
        if QtGui.QMessageBox.question(
                    self._simulation.simulationWindow,
                    self.tr("Reset a service"),
                    self.tr("Are you sure you really "\
                            "want to reset service %s?"
                            % self.serviceCode),
                    QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel
                    ) == QtGui.QMessageBox.Ok:
            self._status = TrainStatus.INACTIVE
            self.currentService.start()

    def executeActions(self, advanceLength):
        """ Execute actions that have to be done when the train head enters
        a trackItem or when the train tail leaves another.
        For each case this is done in two stages:
        - first execute actions related to the train itself and
        - then call TrackItem.trainHeadActions() or
        TrackItem.trainTailActions())."""
        # Train head
        oth = self._trainHead - advanceLength
        for ti in oth.trackItemsToPosition(self._trainHead):
            if ti.tiType.startswith("L"):
                if self.currentService.nextPlace() == ti.place:
                    # We are at the nextPlace
                    if self.currentService.nextStopLine() is not None and \
                       self.currentService.nextPlace() != \
                                    self.currentService.nextStopLine().place:
                        # Train does not stop at this place
                        self.currentService.jumpToNextPlace()
            ti.trainHeadActions(self._serviceCode)
        # Train tail
        tt = self._trainHead - self._trainType.length
        ott = tt - advanceLength
        for ti in ott.trackItemsToPosition(tt):
            ti.trainTailActions(self._serviceCode)
            if ti.tiType.startswith("E"):
                self._status = TrainStatus.OUT
                self._speed = 0
                break

    def updateStatus(self, secs):
        """Updates the status of the train"""
        if self._status == TrainStatus.OUT or \
           self._status == TrainStatus.INACTIVE or \
           self._status == TrainStatus.END_OF_SERVICE:
            return
        if self._speed != 0:
            self._status = TrainStatus.RUNNING
        else:
            if self.currentService.nextStopLine() is not None and \
               self._trainHead.trackItem.place == \
                                    self.currentService.nextStopLine().place:
                # Train is stopped at the scheduled nextStop place
                if self._status == TrainStatus.RUNNING:
                    # Train just stopped
                    self._status = TrainStatus.STOPPED
                    self._stoppedTime = 0
                    self.trainStoppedAtStation.emit(
                                            self._trainHead.trackItem.place)
                else:
                    if self.currentService.nextStopDepartureTime() > \
                                            self._simulation.currentTime or \
                       self.currentService.minimumStopTime > \
                                            self._stoppedTime or \
                       self.currentService.nextStopDepartureTime() == \
                                            QtCore.QTime():
                        # Conditions to depart are not met
                        self._status = TrainStatus.STOPPED
                        self._stoppedTime += secs
                    else:
                        # Train departs
                        currentService = self.currentService
                        self.currentService.depart()
                        if self.currentService != currentService:
                            # The service code has changed
                            self._status = TrainStatus.STOPPED
                        elif self.currentService.nextPlace() is not None:
                            self._status = TrainStatus.RUNNING
                        else:
                            self._status = TrainStatus.END_OF_SERVICE
            else:
                # Train is stopped but not at a scheduled station
                self._status = TrainStatus.WAITING

    def drawTrain(self, advanceLength = 0):
        """This function draws the train on the scene by setting the correct
        trainHead and trainTail to the different trackItems met.
        @param advanceLength : The length that the train has advanced since
        the last call to this function."""
        trainTail = self._trainHead - self._trainType.length
        oldTrainHead = self._trainHead - advanceLength
        oldTrainTail = trainTail - advanceLength
        # Draw the train in its new position
        self._trainHead.trackItem.setTrainHead(self._trainHead.positionOnTI,
                                                 self._trainHead.previousTI)
        self._trainHead.trackItem.setTrainTail(0, self._trainHead.previousTI)
        if trainTail.trackItem != self._trainHead.trackItem:
            p = self._trainHead.previous()
            while p.trackItem != trainTail.trackItem:
                p.trackItem.setTrainHead(p.trackItem.realLength,
                                           p.previous().trackItem)
                p.trackItem.setTrainTail(0, p.previous().trackItem)
                p = p.previous()
            trainTail.trackItem.setTrainHead(trainTail.trackItem.realLength,
                                               trainTail.previousTI)
        trainTail.trackItem.setTrainTail(trainTail.positionOnTI,
                                           trainTail.previousTI)
        # Remove behind
        if oldTrainTail.trackItem != trainTail.trackItem:
            p = trainTail.previous()
            while p.trackItem != oldTrainTail.trackItem:
                p.trackItem.setTrainHead(-1, p.previous().trackItem)
                p.trackItem.setTrainTail(-1, p.previous().trackItem)
                p = p.previous()
            oldTrainTail.trackItem.setTrainHead(-1, oldTrainTail.previousTI)
            oldTrainTail.trackItem.setTrainTail(-1, oldTrainTail.previousTI)

    def findNextSignal(self, pos=routing.Position()):
        """ @return The first signal ahead the train head
        or ahead of the given position if specified"""
        nsp = self.findNextSignalPosition(pos).trackItem
        if nsp is not None:
            return nsp
        else:
            return None

    def findPreviousSignal(self, pos=routing.Position()):
        """ @return The first signal behind the train head"""
        psp = self.findPreviousSignalPosition(pos).trackItem
        if psp is not None:
            return psp
        else:
            return None

    def findNextSignalPosition(self, pos=routing.Position()):
        """Returns the position of first signal ahead of the train head or
        ahead of the given position if specified"""
        # FIXME Redundant with SignalItem.findNextSignal
        if pos == routing.Position():
            pos = self._trainHead
        if not pos.trackItem.tiType.startswith("E"):
            cur = pos.next()
            while not cur.trackItem.tiType.startswith("E"):
                ti = cur.trackItem
                if ti.tiType.startswith("S"):
                    if ti.isOnPosition(cur):
                        return cur + ti.signalPos
                cur = cur.next()
        return routing.Position()

    def findPreviousSignalPosition(self, pos=routing.Position()):
        """ Finds the position of the first signal behind the train head or
        the given position.
        @return The position of the first signal behind"""
        # FIXME Redundant with SignalItem.findPreviousSignal
        if pos == routing.Position():
            cur = self._trainHead
        else:
            cur = pos
        while not cur.trackItem.tiType.startswith("E"):
            ti = cur.trackItem
            if ti.tiType.startswith("S"):
                if ti.isOnPosition(cur):
                    return cur
            cur = cur.previous()
        return routing.Position()

    def getDistanceToNextSignal(self):
        """Returns the distance to the next Signal"""
        nsp = self.findNextSignalPosition()
        if nsp != routing.Position():
            return self._trainHead.distanceToPosition(nsp)
        else:
            return -1

    def getDistanceToNextStop(self, maxDistance):
        """Returns the distance to the next stop by looking forward of
        the _trainHead up to a maximum distance of maxDistance."""
        if self.currentService.nextStopLine() is None:
            return -1
        pos = self._trainHead
        distance = pos.trackItem.realLength - self._trainHead.positionOnTI
        while (not pos.trackItem.tiType.startswith("E")) and \
              (distance < maxDistance):
            ti = pos.trackItem
            if ti.tiType.startswith("S"):
                if ti.isOnPosition(pos) and \
                   ti.signalState == scenery.SignalState.STOP:
                    return -1
            if ti.place == self.currentService.nextStopLine().place:
                return distance
            pos = pos.next()
            distance += pos.trackItem.realLength
        return -1

    def setSpeed(self, secs):
        if not self.isActive() or self._status == TrainStatus.STOPPED:
            self._speed = 0
            return

        warningSpeed = float(self._simulation.option("warningSpeed"))
        maxSpeed = min(self._trainType.maxSpeed, \
                       float(self._simulation.option("defaultMaxSpeed")))
        # k is the gain factor to set acceleration from the difference
        # between current speed and target speed
        k = 1 / secs
        # d is the maximum distance that can be travelled during the last
        # sample. It is used to determine when to stop the train.
        d = 0.5 * self.trainType.stdBraking * secs**2

        # Next Signal
        distanceToNextSignal = self.getDistanceToNextSignal()
        # Next station
        maxDistance = max(self._speed**2 / self._trainType.stdBraking, 50.0)
        distanceToNextStation = self.getDistanceToNextStop(maxDistance)

        # Choose target and define speed
        if distanceToNextStation != -1:
            if distanceToNextStation < d:
                targetSpeedForStation = 0
            else:
                targetSpeedForStation = self.targetSpeed(secs,
                                                        distanceToNextStation,
                                                        0)
        else:
            targetSpeedForStation = maxSpeed
        if distanceToNextSignal != -1:
            nextSignal = self.findNextSignalPosition().trackItem
            if nextSignal.signalState == scenery.SignalState.CLEAR:
                targetSpeedForSignal = maxSpeed
            elif nextSignal.signalState == scenery.SignalState.WARNING:
                targetSpeedForSignal = self.targetSpeed(secs,
                                                        distanceToNextSignal,
                                                        warningSpeed)
            elif nextSignal.signalState == scenery.SignalState.STOP:
                if distanceToNextSignal < d:
                    targetSpeedForSignal = 0
                else:
                    targetSpeedForSignal = min(warningSpeed,
                                        self.targetSpeed(secs,
                                                        distanceToNextSignal,
                                                        0))
        else:
            targetSpeedForSignal = maxSpeed

        ts = min(targetSpeedForSignal, targetSpeedForStation)
        self._accel = max(-self._trainType.emergBraking,
                          min(k * (ts - self._speed),
                              self._trainType.stdAccel))
        self._speed = max(0.0,
                          min(self._speed + self._accel * secs, maxSpeed))
        #QtCore.qDebug("SC:%s, Secs:%f, Accel=%f; ts=%f, speed=%f,
                # dtnstation:%f, dtnsignal:%f" % (self.serviceCode, secs,
                # self._accel, ts , self._speed, distanceToNextStation,
                # distanceToNextSignal))

    def targetSpeed(self,
                    secs,
                    targetDistance=-1,
                    targetSpeedAtPos=0):
        """ Defines the current target speed of the train depending on the
        parameters:
        - targetDistance : the distance at which the train should be at
        targetSpeedAtPos
        - targetSpeedAtPos : the target speed when the train will be at
        targetDistance
        Returns the current target speed for the train, including sampling
        margin."""
        maxSpeed = min(self._trainType.maxSpeed, \
                       float(self._simulation.option("defaultMaxSpeed")))
        # TODO Enable max speed depending on trackItem
        if targetDistance == -1:
            return maxSpeed
        theoreticalSpeed = self.calculatedSpeed(targetDistance,
                                                 targetSpeedAtPos,
                                                 maxSpeed)
        # s1 is half the distance run at the train's current speed during secs
        # This value is used to get a centered sampling of the braking curve.
        s1 = self._speed * secs / 2
        # s2 is equivalent to s1, but taking into account the theoreticalSpeed
        s2 = theoreticalSpeed * secs / 2
        if theoreticalSpeed < self._speed:
            return self.calculatedSpeed(targetDistance - s1,
                                         targetSpeedAtPos,
                                         maxSpeed)
        else:
            return self.calculatedSpeed(targetDistance - s2,
                                        targetSpeedAtPos,
                                        maxSpeed)


    def calculatedSpeed(self, targetDistance, targetSpeedAtPos, maxSpeed):
        """Returns the speed the train should be right now to be able to be
        at a speed of targetSpeedAtPos at a distance of targetDistance from
        the train head, not exceeding maxSpeed. This function does not take
        into account any sampling margin."""
        return min(maxSpeed,
                   sqrt(2 * targetDistance * self._trainType.stdBraking +
                        targetSpeedAtPos**2))
