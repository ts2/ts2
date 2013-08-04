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
from ts2.trackitem import *
from ts2.lineitem import *
from ts2.place import *

class PFGraphicsItem(QGraphicsRectItem):
    """@brief Graphical item for platforms
    This class is the graphics of a PlatformItem on the scene. Each instance belongs to a PlatformItem
    which is defined in the constructor. Only the clickable part of the platform is represented by this
    class.
    @author Nicolas Piganeau"""
 
    def __init__(self, scene, platformItem, r, parent = None):
        """Constructor for the PlatformGraphicsItem class.
        @param platformItem Pointer to the PlatformItem to which this SignalGraphicsItem belongs to."""
        super().__init__(r, parent, scene)
        self._platformItem = platformItem
        self.setZValue(0)
    
    def mousePressEvent(self, event):
        self._platformItem.select(event)


class PlatformItem(LineItem):
    """ @brief Logical item for platforms
    This class holds the logics of a platform.
    A platform is where a train stops at a station.
    Each instance owns :
    - a PlatformGraphicsItem which is the graphical item for the platform itself (clickable).
    - a LineItem which represents the track along this platform.
    Trains stop with their head at the end of the LineItem.
    @author Nicolas Piganeau"""
    
    platformSelected = pyqtSignal(Place)
    
    def __init__(self, simulation, record):
        super().__init__(simulation, record)
        self._tiType = "LP"
        x1 = record.value("xn")
        x2 = record.value("xr")
        y1 = record.value("yn")
        y2 = record.value("yr")
        self._rect = QRectF(QPointF(x1, y1), QPointF(x2, y2))
        self._pfgi = PFGraphicsItem(simulation.scene, self, self._rect)
        self._pfgi.setCursor(Qt.PointingHandCursor)
        self._pfgi.setPen(QPen(QColor("#88ffbb")))
        self._pfgi.setBrush(QBrush(QColor("#88ffbb")))
        if self.place is not None:
            self._pfgi.setToolTip(self.tr("%s\nPlatform %s") % (self.place.placeName, self.trackCode))
        self._pfgi.update()
        self.platformSelected.connect(Place.selectedPlaceModel.setPlace)

    def select(self, e):
        if e.button() == Qt.LeftButton:
            self.platformSelected.emit(self._place)
        
    @pyqtSlot()
    def updateGraphics(self):
        self.__updateGraphics()
        
    def __updateGraphics(self):
        super().updateGraphics()
        self._pfgi.update()

