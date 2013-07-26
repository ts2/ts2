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

from PyQt4.QtSql import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from simulation import *
from service import *
from trackitem import *
# TODO Remove dependancy from mainwindow
from mainwindow import *
from math import *

class LineItem(TrackItem):
    def __init__(self, simulation, record):
        super().__init__(simulation, record)
        self._tiType = "L"
        xf = record.value("xf")
        yf = record.value("yf")
        self._end = QPointF (xf, yf)
        placeCode = record.value("placecode")
        trackCode = record.value("trackcode")
        self._place = simulation.place(placeCode)
        if self._place is not None:
            self._trackCode = trackCode
            self._place.addTrack(self)
        else:
            self._trackCode = ""
        realLength = record.value("reallength")
        if isinstance(realLength, QPyNullVariant) or realLength == 0:
            realLength = sqrt(pow(xf - self.origin.x(), 2) + pow(yf - self.origin.y(), 2))
        self._realLength = realLength

        gli = QGraphicsLineItem();
        gli.setCursor(Qt.ArrowCursor)
        gli.setPen(self.getPen())
        gli.setLine(QLineF(self._origin, self._end))
        self._gi = gli
        simulation.registerGraphicsItem(self._gi)
        
        # draw the "train" graphicLineItem
        p = QPen()
        p.setWidth(3)
        p.setJoinStyle(Qt.RoundJoin)
        p.setCapStyle(Qt.RoundCap)
        p.setColor(Qt.red)
        self._tli = QGraphicsLineItem()
        self._tli.setCursor(Qt.ArrowCursor)
        self._tli.setPen(p)
        self._tli.setZValue(10)
        self._tli.hide()
        simulation.registerGraphicsItem(self._tli)
        self.__updateGraphics()
        
    @property
    def trackCode(self):
        return self._trackCode
    
    def __updateGraphics(self):
        li = self._gi
        pen = self.getPen()
        li.setPen(pen)
        if self.highlighted:
            li.setZValue(5)
        else:
            li.setZValue(0)
        li.update()
        # Draw train if any:
        if self.trainPresent():
            line = self._gi.line()
            tline = QLineF(line.pointAt(self._trainHead/self._realLength), line.pointAt(self._trainTail/self._realLength))
            if tline.length() < 5.0 and self._trainTail != 0:
                # Make sure that the train representation is always at least 5 pixel long.
                tline.setLength(min(5.0, (1 - self._trainTail/self._realLength)*line.length()))
            self._tli.setLine(tline)
            self._tli.show()
            self._tli.update()
        else:
            self._tli.hide()
            self._tli.update()
    
    @pyqtSlot()
    def updateGraphics(self):
        self.__updateGraphics()

    @property
    def graphicsItems(self):
        graphicsItems = super().graphicsItems
        graphicsItems.append(self._tli)
        
        
