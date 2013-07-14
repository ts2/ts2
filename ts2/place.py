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
from lineitem import *
from service import *


class Place(QObject):

    selectedPlaceModel = PlaceInfoModel()
    
    def __init__(self, placeCode, placeName, x, y):
        super().__init__()
        self._placeCode = placeCode
        self._placeName = placeName
        self._origin = QPointF(x, y)
        self._gi = QGraphicsSimpleTextItem(_placeName)
        self._gi.setBrush(QBrush(Qt.white))
        self._gi.setPos(self._origin)
        Simulation.instance().registerGraphicsItem(_gi)
        self._timetable = {}
        self._tracks = {}
        

    def addTrack(self, li):
        self._tracks[li.trackCode()] = li
    
    def addTimetable(self, sl):
        self._timetable[sl.scheduledDepartureTime()] = sl

    @pyqtProperty(str)
    def placeName(self):
        return self._placeName
    
    @pyqtProperty(int)
    def timetable(self):
        return self._timetable

    def track(self, trackCode):
        qDebug() << "Place: trackCode" << trackCode << self._tracks.value(trackCode).tiId()
        return self._tracks[trackCode]
    
    @staticmethod
    def findByCode(placeCode):
        return Simulation.instance().place(placeCode)


class PlaceInfoModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._place = None

    def rowCount(self, parent = QModelIndex()):
        if self._place is not None:
            return self._place.timetable().count() + 2
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
                    return tr("Station:")
                if index.column() == 1:
                    return _place.placeName()
            elif index.row() == 1:
                return ""
            else:
                line = self._place.timetable().values().value(index.row() - 2)
                if index.column() == 0:
                    return line.scheduledDepartureTime()
                elif index.column() == 1:
                    return line.service().serviceCode()
                elif index.column() == 2:
                    return line.service().destination()
                elif index.column() == 3:
                    return line.trackCode()
                elif index.column() == 4:
                    return ""
        return QVariant()

    def headerData (self, section, orientation, role = Qt.DisplayRole):
        if self._place is not None and orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if column == 0:
                return tr("Time")
            elif column == 1:
                return tr("Code")
            elif column == 2:
                return tr("Destination")
            elif column == 3:
                return tr("Platform")
            elif column == 4:
                return tr("Remarks")
            else:
                return ""
        return QVariant()
    
    def flags (self, index):
        return Qt.ItemIsEnabled
    
    @pyqtProperty(Place)
    def place(self):
        return self._place


    @pyqtSlot()
    def update(self):
        self.reset()

    @pyqtSlot(Place)
    @place.setter
    def setPlace(self, place):
        self._place = place
        self.reset()


