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

import copy
from Qt import QtCore, Qt

from ts2 import utils


class ServiceInfoModel(QtCore.QAbstractTableModel):
    """Model for displaying a single service information in a view
    """
    def __init__(self, simulation):
        """Constructor for the ServiceInfoModel class"""
        super().__init__()
        self._service = None
        self._simulation = simulation

    def rowCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of rows of the model, corresponding to the
        number of serviceLines of this service + lines for displaying general
        service information."""
        if self._service is not None:
            return len(self._service._lines) + 3
        else:
            return 0

    def columnCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of columns of the model"""
        if self._service is not None:
            return 4
        else:
            return 0

    def data(self, index, role = Qt.DisplayRole):
        """Returns the data at the given index"""
        if self._service is not None and role == Qt.DisplayRole:
            if index.row() == 0:
                if index.column() == 0:
                    return self.tr("Service no:")
                if index.column() == 1:
                    return self._service.serviceCode
            elif (index.row() == 1):
                if index.column() == 0:
                    return self.tr("Description:")
                if index.column() == 1:
                    return self._service.description
            elif (index.row() == 2):
                return None
            else:
                line = self._service._lines[index.row() - 3]
                if index.column() == 0:
                    return line.place.placeName
                elif index.column() == 1:
                    return line.trackCode
                elif index.column() == 2:
                    return line.scheduledArrivalTime
                elif index.column() == 3:
                    return line.scheduledDepartureTime
        return None

    def headerData(self, column, orientation, role = Qt.DisplayRole):
        """Returns the header labels"""
        if self._service is not None \
           and orientation == Qt.Horizontal\
           and role == Qt.DisplayRole:
            if column == 0:
                return ""
            elif column == 1:
                return self.tr("Track")
            elif column == 2:
                return self.tr("Arrival")
            elif column == 3:
                return self.tr("Departure")
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        return Qt.ItemIsEnabled

    @QtCore.pyqtSlot(str)
    def setServiceCode(self, serviceCode):
        """Sets the service linked with this model from its serviceCode."""
        self._service = self._simulation.service(serviceCode)
        self.reset()

    def reset(self):
        print("FIXME REST")

class ServiceListModel(QtCore.QAbstractTableModel):
    """Model for displaying services during the game. This model makes a
    copy of the services of the simulation at the time it is created.
    """
    def __init__(self, simulation):
        """Constructor for the ServiceInfoModel class"""
        super().__init__()
        self._simulation = simulation
        self.updateModel()

    def updateModel(self):
        """Updates the internal copy of the services with the simulation
        services."""
        self._services = sorted(self._simulation.services.values(),
                        key = lambda x: x.lines[0].scheduledDepartureTimeStr)

    def rowCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of rows of the model, corresponding to the
        number of services in the simulation."""
        return len(self._services)

    def columnCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of columns of the model"""
        return 5

    def data(self, index, role = Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole:
            service = self._services[index.row()]
            if index.column() == 0:
                return service.serviceCode
            elif index.column() == 1:
                return service._lines[0].scheduledDepartureTime
            elif index.column() == 2:
                return service.description
            elif index.column() == 3:
                return service.entryPlaceName
            elif index.column() == 4:
                return service.exitPlaceName
        return None

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        """Returns the header labels"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return self.tr("Code");
            elif section == 1:
                return self.tr("Time")
            elif section == 2:
                return self.tr("Description")
            elif section == 3:
                return self.tr("Entry point")
            elif section == 4:
                return self.tr("Exit point")
            else:
                return ""
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        return Qt.ItemIsSelectable|Qt.ItemIsEnabled


class ServicesModel(QtCore.QAbstractTableModel):
    """Model for Service class used in the editor
    """
    def __init__(self, editor):
        """Constructor for the ServicesModel class"""
        super().__init__(editor)
        self._editor = editor

    def rowCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of rows of the model, corresponding to the
        number of services of the editor"""
        return len(self._editor.services)

    def columnCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of columns of the model"""
        return 5

    def data(self, index, role = Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole or role == Qt.EditRole:
            service = list(self._editor.services.values())[index.row()]
            if index.column() == 0:
                return str(service.serviceCode)
            elif index.column() == 1:
                return service.description
            elif index.column() == 2:
                return service.nextServiceCode
            elif index.column() == 3:
                return bool(service.autoReverse)
            elif index.column() == 4:
                return service.plannedTrainType
        return None

    def setData(self, index, value, role):
        """Updates data when modified in the view"""
        if role == Qt.EditRole:
            code = index.sibling(index.row(), 0).data()
            if index.column() == 0:
                if (value is not None) and (value != ""):
                    self._editor.services[value] = \
                                  copy.copy(self._editor.services[code])
                    self._editor.services[value].serviceCode = value
                    del self._editor.services[code]
            elif index.column() == 1:
                self._editor.services[code].description = value
            elif index.column() == 2:
                self._editor.services[code].nextServiceCode = value
            elif index.column() == 3:
                self._editor.services[code].autoReverse = value
            elif index.column() == 4:
                self._editor.services[code].plannedTrainType = value
            else:
                return False
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        """Returns the header labels"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return self.tr("Code")
            elif section == 1:
                return self.tr("Description")
            elif section == 2:
                return self.tr("Next service code")
            elif section == 3:
                return self.tr("Auto reverse")
            elif section == 4:
                return self.tr("Planned Train Type")
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


class ServiceLine:
    """ A serviceLine is a line of the definition of the service.
    It consists of a place (usually a station) with a track number
    and scheduled times to arrive at and depart from this station.
    """
    def __init__(self, service, parameters):
        """Constructor for the ServiceLine class"""
        self._service = service
        self._simulation = service.simulation
        self._placeCode = parameters["placecode"]
        self._scheduledArrivalTime = \
                QtCore.QTime.fromString(parameters["scheduledarrivaltime"])
        self._scheduledDepartureTime = \
                QtCore.QTime.fromString(parameters["scheduleddeparturetime"])
        self._trackCode = parameters["trackcode"]
        self._stop = int(parameters["stop"])

    @property
    def service(self):
        """Returns the service this ServiceLine belongs to"""
        return self._service

    @property
    def place(self):
        """Returns the place of this ServiceLine"""
        return self.service.simulation.place(self._placeCode)

    @property
    def placeCode(self):
        """Returns the place code of this ServiceLine"""
        return self._placeCode

    @placeCode.setter
    def placeCode(self, value):
        """Setter function for the placeCode property"""
        if self._simulation.context == utils.Context.EDITOR_SERVICES:
            self._placeCode = value

    @property
    def trackCode(self):
        """Returns the trackCode of this ServiceLine"""
        return self._trackCode

    @trackCode.setter
    def trackCode(self, value):
        """Setter function for the trackCode property"""
        if self._simulation.context == utils.Context.EDITOR_SERVICES:
            self._trackCode = value

    @property
    def mustStop(self):
        """Returns true if this service is supposed to stop at the place of
        this ServiceLine"""
        return self._stop

    @mustStop.setter
    def mustStop(self, value):
        """Setter function for the mustStop property"""
        if self._simulation.context == utils.Context.EDITOR_SERVICES:
            self._stop = value

    @property
    def scheduledDepartureTime(self):
        """Returns the scheduled departure time of this service at the place
        of this ServiceLine, as a QTime"""
        return self._scheduledDepartureTime

    @property
    def scheduledDepartureTimeStr(self):
        """Returns the scheduled departure time of this service at the place
        of this ServiceLine, as a string"""
        return self._scheduledDepartureTime.toString("HH:mm:ss")

    @scheduledDepartureTimeStr.setter
    def scheduledDepartureTimeStr(self, value):
        """Setter function for the scheduledDepartureTime property"""
        if self._simulation.context == utils.Context.EDITOR_SERVICES:
            self._scheduledDepartureTime = QtCore.QTime.fromString(value)

    @property
    def scheduledArrivalTime(self):
        """Returns the scheduled arrival time of this service at the place
        of this ServiceLine, as a QTime"""
        return self._scheduledArrivalTime

    @property
    def scheduledArrivalTimeStr(self):
        """Returns the scheduled arrival time of this service at the place
        of this ServiceLine as a string"""
        return self._scheduledArrivalTime.toString("HH:mm:ss")

    @scheduledArrivalTimeStr.setter
    def scheduledArrivalTimeStr(self, value):
        """Setter function for the scheduledArrivalTime property"""
        if self._simulation.context == utils.Context.EDITOR_SERVICES:
            self._scheduledArrivalTime = QtCore.QTime.fromString(value)

    def __eq__(self, other):
        """Equal operator"""
        if self.placeCode == other.placeCode and \
           self.scheduledDepartureTime == other.scheduledDepartureTime:
            return True
        else:
            return False


class ServiceLinesModel(QtCore.QAbstractTableModel):
    """Model for ServiceLine class used in the editor
    """
    def __init__(self, editor):
        """Constructor for the ServicesModel class"""
        super().__init__(editor)
        self._service = None
        self._editor = editor

    def rowCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of rows of the model, corresponding to the
        number of serviceLines of this service"""
        if self._service is not None:
            return len(self._service._lines)
        else:
            return 0

    def columnCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of columns of the model"""
        return 5

    def data(self, index, role = Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole or role == Qt.EditRole:
            line = self._service.lines[index.row()]
            if index.column() == 0:
                return str(line.placeCode)
            elif index.column() == 1:
                return str(line.trackCode)
            elif index.column() == 2:
                return line.scheduledArrivalTimeStr
            elif index.column() == 3:
                return line.scheduledDepartureTimeStr
            elif index.column() == 4:
                return bool(line.mustStop)
        return None

    def setData(self, index, value, role):
        """Updates data when modified in the view"""
        if role == Qt.EditRole:
            line = self._service.lines[index.row()]
            if index.column() == 0:
                line.placeCode = value
            elif index.column() == 1:
                line.trackCode = value
            elif index.column() == 2:
                line.scheduledArrivalTimeStr = value
            elif index.column() == 3:
                line.scheduledDepartureTimeStr = value
            elif index.column() == 4:
                line.mustStop = value
            else:
                return False
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        """Returns the header labels"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return self.tr("Place code")
            elif section == 1:
                return self.tr("Track code")
            elif section == 2:
                return self.tr("Arrival time")
            elif section == 3:
                return self.tr("Departure time")
            elif section == 4:
                return self.tr("Stop")
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    @QtCore.pyqtSlot(str)
    def setServiceCode(self, serviceCode):
        """Sets the service linked with this model from its serviceCode."""
        self._service = self._editor.service(serviceCode)
        self.reset()

    @property
    def service(self):
        """Returns the service this model is attached to"""
        return self._service


class Service:
    """A Service is mainly a predefined schedule that trains are supposed to
    follow with a few additional informations.
    The schedule is composed of several "lines" of type ServiceLine
    """
    def __init__(self, simulation, parameters):
        """Constructor for the Service class"""
        self._simulation = simulation
        self._serviceCode = parameters["servicecode"]
        self._description = parameters["description"]
        self._nextServiceCode = parameters["nextservice"]
        self._autoReverse = parameters["autoreverse"]
        self._plannedTrainType = parameters.get("plannedtraintype")
        self._current = None
        self._lines = []

    def addLine(self, parameters):
        """Add a serviceLine to this Service based on the given parameters."""
        sl = ServiceLine(self, parameters)
        self._lines.append(sl)
        sl.place.addTimetable(sl)

    @property
    def lines(self):
        """Returns the lines of this service"""
        return self._lines

    #@property
    #def minimumStopTime(self):
        #"""Returns the minimum stop time applicable for this Service in the
        #next plasce."""
        #return float(self._simulation.option("defaultMinimumStopTime"))

    @property
    def entryPlaceName(self):
        """Returns the place of entry of the train as a string"""
        return self._lines[0].place.placeName

    def getEntryPlaceData(self):
        """Returns the placeCode and trackCode of the entry point of the train
        """
        return (self._lines[0].place.placeCode, self._lines[0].trackCode)

    @property
    def exitPlaceName(self):
        """Returns the place where the train is due to exit as a string."""
        return self._lines[-1].place.placeName

    @property
    def serviceCode(self):
        """Returns the service code"""
        return self._serviceCode

    @serviceCode.setter
    def serviceCode(self, value):
        """Setter function for the serviceCode property"""
        if self._simulation.context == utils.Context.EDITOR_SERVICES:
            self._serviceCode = value

    @property
    def description(self):
        """Returns the service code"""
        return self._description

    @description.setter
    def description(self, value):
        """Setter function for the description property"""
        if self._simulation.context == utils.Context.EDITOR_SERVICES:
            self._description = value

    @property
    def nextServiceCode(self):
        """Returns the service code that should be assigned to the train that
        just ended this service"""
        return self._nextServiceCode

    @nextServiceCode.setter
    def nextServiceCode(self, value):
        """Setter function for the nextServiceCode property"""
        if self._simulation.context == utils.Context.EDITOR_SERVICES:
            self._nextServiceCode = value

    @property
    def autoReverse(self):
        """Returns true if the train is to be reversed when the service ends
        """
        return self._autoReverse

    @autoReverse.setter
    def autoReverse(self, value):
        """Setter function for the autoReverse property"""
        if self._simulation.context == utils.Context.EDITOR_SERVICES:
            self._autoReverse = value

    @property
    def simulation(self):
        """Returns the simulation this service belongs to"""
        return self._simulation

    @property
    def plannedTrainType(self):
        """Returns the planned train type for this service, which is not
        necessarily the actual train type of the train to which this service
        is assigned."""
        return self._plannedTrainType

    @plannedTrainType.setter
    def plannedTrainType(self, value):
        """Setter function for the plannedTrainType property."""
        if self._simulation.context == utils.Context.EDITOR_SERVICES:
            self._plannedTrainType = value
