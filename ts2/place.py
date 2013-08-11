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
from ts2.service import *


class PlaceInfoModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._place = None

    def rowCount(self, parent = QModelIndex()):
        if self._place is not None:
            return len(self._place.timetable) + 2
        else:
            return 0

    def columnCount (self, parent = QModelIndex()):
        if self._place is not None:
            return 5
        else:
            return 0
    
    def data (self, index, role = Qt.DisplayRole):
        if self._place is not None and role == Qt.DisplayRole:
            if index.row() == 0:
                if index.column() == 0:
                    return self.tr("Station:")
                if index.column() == 1:
                    return self._place.placeName
            elif index.row() == 1:
                return ""
            else:
                line = self._place.timetable[index.row() - 2]
                if index.column() == 0:
                    return line.scheduledDepartureTime
                elif index.column() == 1:
                    return line.service.serviceCode
                elif index.column() == 2:
                    return line.service.destination
                elif index.column() == 3:
                    return line.trackCode
                elif index.column() == 4:
                    return ""
        return None

    def headerData (self, column, orientation, role = Qt.DisplayRole):
        if self._place is not None and orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if column == 0:
                return self.tr("Time")
            elif column == 1:
                return self.tr("Code")
            elif column == 2:
                return self.tr("Destination")
            elif column == 3:
                return self.tr("Platform")
            elif column == 4:
                return self.tr("Remarks")
            else:
                return ""
        return None
    
    def flags (self, index):
        return Qt.ItemIsEnabled
    
    @property
    def place(self):
        return self._place

    @place.setter
    def place(self, place):
        self._place = place
        self.reset()
        
    @pyqtSlot(str)
    def setPlace(self, place):
        self.place = place

    @pyqtSlot()
    def update(self):
        self.reset()



class Place(QObject):

    selectedPlaceModel = PlaceInfoModel()
    
    def __init__(self, simulation, placeCode, placeName, x, y):
        super().__init__()
        self._simulation = simulation
        self._placeCode = placeCode
        self._placeName = placeName
        self._origin = QPointF(x, y)
        self._gi = QGraphicsSimpleTextItem(self._placeName)
        self._gi.setBrush(QBrush(Qt.white))
        self._gi.setPos(self._origin)
        self._simulation.registerGraphicsItem(self._gi)
        self._timetable = []
        self._tracks = {}

    def addTrack(self, li):
        self._tracks[li.trackCode] = li
    
    def addTimetable(self, sl):
        self._timetable.append(sl)
        self._timetable.sort(key=lambda x: x.scheduledDepartureTime)
        
    @property
    def graphicsItem(self):
        return self._gi

    @property
    def placeName(self):
        return self._placeName
    
    @property
    def timetable(self):
        return self._timetable
    
    def track(self, trackCode):
        qDebug("Place: trackCode %s, %i" % (trackCode, self._tracks[trackCode].tiId))
        return self._tracks[trackCode]
    


