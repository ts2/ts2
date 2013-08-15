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

from PyQt4.QtCore import *
from ts2.scenery import Place
from ts2.simulation import *


class ServiceInfoModel(QAbstractTableModel):
    """TODO Document ServiceInfoModel"""
    def __init__(self, simulation):
        super().__init__()
        self._service = None
        self._simulation = simulation

    def rowCount(self, parent = QModelIndex()):
        if self._service is not None:
            return len(self._service._lines) + 2
        else:
            return 0

    def columnCount(self, parent = QModelIndex()):
        if self._service is not None:
            return 4
        else:
            return 0

    def data(self, index, role = Qt.DisplayRole):
        if self._service is not None and role == Qt.DisplayRole:
            if index.row() == 0:
                if index.column() == 0:
                    return self.tr("Service no:")
                if index.column() == 1:
                    return self._service._serviceCode
            elif (index.row() == 1):
                return None
            else:
                line = self._service._lines[index.row() - 2]
                if index.column() == 0:
                    return line.place.placeName
                elif index.column() == 1:
                    return line.scheduledArrivalTime
                elif index.column() == 2:
                    return line.scheduledDepartureTime
                elif index.column() == 3:
                    return ""
        return None

    def headerData(self, column, orientation, role = Qt.DisplayRole):
        if self._service is not None \
           and orientation == Qt.Horizontal\
           and role == Qt.DisplayRole:
            if column == 0:
                return ""
            elif column == 1:
                return self.tr("Arrival")
            elif column == 2:
                return self.tr("Departure")
            elif column == 3:
                return self.tr("Remarks")
            else:
                return ""
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled

    def service(self):
        return self._service

    @pyqtSlot()
    def update(self):
        self.reset()

    @pyqtSlot(str)
    def setServiceCode(self, serviceCode):
        self._service = self._simulation.service(serviceCode)
        self.reset()


class ServiceListModel(QAbstractTableModel):
    """TODO Document ServiceListModel"""
    def __init__(self, simulation):
        super().__init__()
        self._simulation = simulation

    def rowCount(self, parent = QModelIndex()):
        return len(self._simulation.services())

    def columnCount(self, parent = QModelIndex()):
        return 4

    def data(self, index, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            service = self._simulation.servicesList()[index.row()]
            if index.column() == 0:
                return service.serviceCode
            elif index.column() == 1:
                return service._lines[0].scheduledDepartureTime
            elif index.column() == 2:
                return service.origin
            elif index.column() == 3:
                return service.destination
            else:
                return ""
        return None

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return self.tr("Code");
            elif section == 1:
                return self.tr("Time")
            elif section == 2:
                return self.tr("From")
            elif section == 3:
                return self.tr("Destination")
            else:
                return ""
        return None

    def flags(self, index):
        return Qt.ItemIsSelectable|Qt.ItemIsEnabled


class ServiceLine:
    """ A serviceLine is a line of the definition of the service.
    It consists of a place (usually a station) with a track number
    and scheduled times to arrive at and depart from this station."""

    def __init__(self, service, placeCode, scheduledArrivalTime, \
                 scheduledDepartureTime, trackCode = "", stop = False):
        self._service = service
        self._placeCode = placeCode
        self._scheduledArrivalTime = scheduledArrivalTime
        self._scheduledDepartureTime = scheduledDepartureTime
        self._trackCode = trackCode
        self._stop = stop

    @property
    def service(self):
        return self._service

    @property
    def place(self):
        return self.service.simulation.place(self._placeCode)

    @property
    def trackCode(self):
        return self._trackCode

    @property
    def mustStop(self):
        return self._stop
    
    @property
    def scheduledDepartureTime(self):
        return self._scheduledDepartureTime

    @property
    def scheduledArrivalTime(self):
        return self._scheduledArrivalTime

    def __lt__(self, other):
        if self.scheduledArrivalTime < other.scheduledArrivalTime:
            return True
        else:
            return False
    
    def __gt__(self, other):
        if self.scheduledArrivalTime > other.scheduledArrivalTime:
            return True
        else:
            return False
        
    def __eq__(self, other):
        if self.scheduledArrivalTime == other.scheduledArrivalTime:
            return True
        else:
            return False


class Service(QObject):
    """ A service defines the expected behaviour of a train, (i.e. mainly its schedule).
    It consists of general information and several "lines" each one being the schedule
    at one station."""
    
    # TODO Remove serviceListModel static parameter and find other implementation

    def __init__(self, simulation, serviceCode, description, nextService):
        super().__init__()
        self._simulation = simulation
        self._serviceCode = serviceCode
        self._description = description
        self._nextService = nextService
        self._current = None
        self._lines = []

    def addLine(self, placeCode, scheduledArrivalTime, scheduledDepartureTime, trackCode = "", stop = False):
        """Add a serviceLine to this Service based on the given parameters."""
        sl = ServiceLine(self, placeCode, scheduledArrivalTime, scheduledDepartureTime, trackCode, stop)
        self._lines.append(sl)
        sl.place.addTimetable(sl)

    def start(self):
        """Call this function once all the lines of the service are filled to initialize
        the pointer to the next Place (station)."""
        self._lines.sort()
        self._current = self._lines[0]
        
    def nextPlace(self):
        """Returns the next Place that this service is scheduled to."""
        if self._current is not None:
            return self._current.place
        else:
            return None

    def nextStop(self):
        """Returns the ServiceLine where this service is scheduled to stop next."""
        if self._current is not None:
            for it in self._lines[self._lines.index(self._current):]:
                if it.mustStop:
                    return it
        return None

    def nextStopName(self):
        """Returns the name of the place where this service is scheduled to stop
        next, or an empty string if there isn't any."""
        sl = self.nextStop()
        if sl is not None:
            return sl.place.placeName
        else:
            return ""

    def nextStopArrivalTime(self):
        """Returns the arrival time in the next place where this service is supposed
        to stop or an empty QTime if there isn't any."""
        sl = self.nextStop()
        if sl is not None:
            return sl.scheduledArrivalTime
        else:
            return QTime()

    def nextStopDepartureTime(self):
        """Returns the departure time in the next place where this service is supposed
        to stop or an empty QTime if there isn't any."""
        sl = self.nextStop()
        if sl is not None:
            return sl.scheduledDepartureTime
        else:
            return QTime()
        
    def jumpToNextPlace(self):
        """Set the _current pointer to the next serviceLine. If there is no serviceLine
        after the current one, change the service of the train to nextService if any."""
        if self._current == self._lines[-1]:
            train = self._simulation.train(self._serviceCode)
            if self._nextService != "":
                train.serviceCode = self._nextService
            else:
                self._current = None
        else:
            i = self._lines.index(self._current)
            self._current = self._lines[i+1]

    def depart(self):
        """Called when leaving a place"""
        self.jumpToNextPlace()

    @property
    def minimumStopTime(self):
        """Returns the minimum stop time applicable for this Service in the next plasce."""
        return float(self._simulation.option("defaultMinimumStopTime"))

    @property
    def origin(self):
        """Returns the departure station of the train as a string"""
        return self._lines[0].place.placeName
    
    @property
    def destination(self):
        """Returns the final destination as a string."""
        return self._lines[-1].place.placeName

    @property
    def serviceCode(self):
        """Returns the service code"""
        return self._serviceCode
    
    @property
    def simulation(self):
        return self._simulation


