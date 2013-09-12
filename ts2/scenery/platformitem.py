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

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from ts2.utils import Context
from ts2.scenery import LineItem, Place, TIProperty

tr = QtCore.QObject().tr

class PFGraphicsItem(QtGui.QGraphicsRectItem):
    """@brief Graphical item for platforms
    This class is the graphics of a PlatformItem on the scene. 
    Each instance belongs to a PlatformItem which is defined in the 
    constructor. Only the clickable part of the platform is represented by 
    this class.
    """
    def __init__(self, rect, platformItem):
        """Constructor for the PlatformGraphicsItem class.
        @param platformItem Pointer to the PlatformItem to which this
        SignalGraphicsItem belongs to."""
        super().__init__(rect)
        self.trackItem = platformItem
        self.setZValue(0)
    
    def mousePressEvent(self, event):
        self.trackItem.platformGraphicsItemClicked(event)


class PlatformItem(LineItem):
    """Platform items are a special type of line items but including the 
    drawing of a colored rectangle to symbolise the platform. This colored 
    rectangle also permits user interaction. 
    """
    def __init__(self, simulation, parameters):
        """Constructor for the PlatformItem class"""
        super().__init__(simulation, parameters)
        self._tiType = "LP"
        x1 = parameters["xn"]
        x2 = parameters["xr"]
        y1 = parameters["yn"]
        y2 = parameters["yr"]
        self._rect = QtCore.QRectF(QtCore.QPointF(x1, y1), \
                                   QtCore.QPointF(x2, y2))
        self._pfgi = PFGraphicsItem(self._rect, self)
        self._pfgi.setCursor(Qt.PointingHandCursor)
        self._pfgi.setPen(QtGui.QPen(QtGui.QColor("#88ffbb")))
        self._pfgi.setBrush(QtGui.QBrush(QtGui.QColor("#88ffbb")))
        if self.place is not None:
            self._pfgi.setToolTip(self.tr("%s\nPlatform %s") % \
                                  (self.place.placeName, self.trackCode))
        self._simulation.registerGraphicsItem(self._pfgi)
        self._pfgi.update()
        self.platformSelected.connect(Place.selectedPlaceModel.setPlace)

    def __del__(self):
        """Destructor for the PlatformItem class"""
        self._simulation.scene.removeItem(self._pfgi)
        super().__del__()
        

    properties = LineItem.properties + [ 
                    TIProperty("topLeftPFStr", 
                                           tr("Platform top left point")), 
                    TIProperty("bottomRightPFStr", 
                                           tr("Platform bottom right point"))]

    platformSelected = QtCore.pyqtSignal(Place)

    @property
    def saveParameters(self):
        """Returns the parameters dictionary to save this TrackItem to the 
        database"""
        parameters = super().saveParameters
        parameters.update({ \
                            "xn":self._rect.topLeft().x(), \
                            "yn":self._rect.topLeft().y(), \
                            "xr":self._rect.bottomRight().x(), \
                            "yr":self._rect.bottomRight().y(), \
                          })
        return parameters
    
    @property
    def topLeftPFStr(self):
        """Returns the top left QPointF of the platform in a string format"""
        return "(%i,%i)" % (self._rect.topLeft().x(), \
                            self._rect.topLeft().y())
    
    @topLeftPFStr.setter
    def topLeftPFStr(self, value):
        """Setter function for the topLeftPFStr property"""
        if self._simulation.context == Context.EDITOR_SCENERY:
            x, y = eval(value.strip('()'))
            self._rect.setTopLeft(QtCore.QPointF(x, y))
            self._pfgi.setRect(self._rect)
            self._pfgi.update()
        
    @property
    def bottomRightPFStr(self):
        """Returns the bottom right QPointF of the platform in a string
        format"""
        return "(%i,%i)" % (self._rect.bottomRight().x(), \
                            self._rect.bottomRight().y())
    
    @bottomRightPFStr.setter
    def bottomRightPFStr(self, value):
        """Setter function for the bottomRightPFStr property"""
        if self._simulation.context == Context.EDITOR_SCENERY:
            x, y = eval(value.strip('()'))
            self._rect.setBottomRight(QtCore.QPointF(x, y))
            self._pfgi.setRect(self._rect)
            self._pfgi.update()
        
    def platformGraphicsItemClicked(self, e):
        """Called by the owned PFGraphicsItem when clicked. Emits the 
        platformSelected and trackItemClicked signals"""
        if e.button() == Qt.LeftButton:
            self.trackItemClicked.emit(self.tiId)
            self.platformSelected.emit(self._place)
        
    @QtCore.pyqtSlot()
    def updateGraphics(self):
        self._gi.update()
        self._pfgi.update()
        self.updateTrain()
        

