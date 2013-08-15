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
from ts2.scenery import TrackItem, TrackGraphicsItem, TIProperty
from ts2.utils import Context
from math import sqrt

tr = QtCore.QObject().tr

class LineItem(TrackItem):
    """A line is a simple track used to connect other items together. The 
    important parameter of a line is its real length, i.e. the length it would
    have in real life, since this will determine the time the train takes to 
    travel on it.
    """
    def __init__(self, simulation, parameters):
        """Constructor for the LineItem class"""
        super().__init__(simulation, parameters)
        self._tiType = "L"
        xf = float(parameters["xf"])
        yf = float(parameters["yf"])
        self._end = QtCore.QPointF (xf, yf)
        self._placeCode = parameters["placecode"]
        trackCode = parameters["trackcode"]
        self._place = simulation.place(self._placeCode)
        if self._place is not None:
            self._trackCode = trackCode
            self._place.addTrack(self)
        else:
            self._trackCode = ""
        realLength = parameters["reallength"]
        if realLength is None or realLength == 0:
            realLength = sqrt(pow(xf - self.origin.x(), 2) + \
                              pow(yf - self.origin.y(), 2))
        self._realLength = realLength
        self._maxSpeed = parameters["maxspeed"]
        gli = TrackGraphicsItem(self)
        if simulation.context == Context.EDITOR:
            gli.setCursor(Qt.PointingHandCursor)
        else:
            gli.setCursor(Qt.ArrowCursor)
        gli.setPos(self.realOrigin)
        self._gi = gli
        simulation.registerGraphicsItem(self._gi)
        
        # draw the "train" graphicLineItem
        p = QtGui.QPen()
        p.setWidth(3)
        p.setJoinStyle(Qt.RoundJoin)
        p.setCapStyle(Qt.RoundCap)
        p.setColor(Qt.red)
        self._tli = QtGui.QGraphicsLineItem()
        self._tli.setCursor(Qt.ArrowCursor)
        self._tli.setPen(p)
        self._tli.setZValue(10)
        self._tli.hide()
        simulation.registerGraphicsItem(self._tli)
        self.drawTrain()

    def __del__(self):
        """Destructor for the LineItem class"""
        self._simulation.scene.removeItem(self._tli)
        super().__del__()


    properties = [TIProperty("tiTypeStr", tr("Type"), True),\
                  TIProperty("tiId", tr("id"), True), \
                  TIProperty("name", tr("Name")), \
                  TIProperty("originStr", tr("Point 1")), \
                  TIProperty("endStr", tr("Point 2")), \
                  TIProperty("placeCode", tr("Place code")), \
                  TIProperty("trackCode", tr("Track code")), \
                  TIProperty("realLength", tr("Real length (m)")), \
                  TIProperty("maxSpeed", tr("Maximum speed (m/s)"))]

    @property
    def saveParameters(self):
        """Returns the parameters dictionary to save this TrackItem to the 
        database"""
        parameters = super().saveParameters
        parameters.update({ \
                            "xf":self._end.x(), \
                            "yf":self._end.y(), \
                            "placecode":self.placeCode, \
                            "trackCode":self.trackCode, \
                            "reallength":self.realLength, \
                            "maxspeed":self._maxSpeed})
        return parameters

    @property
    def origin(self):
        """Returns the origin QPointF of the TrackItem. The origin is 
        one end of the LineItem"""
        return self._origin
    
    @origin.setter
    def origin(self, pos):
        """Setter function for the origin property"""
        if self._simulation.context == Context.EDITOR:
            grid = self._simulation.grid
            x = round((pos.x()) / grid) * grid
            y = round((pos.y()) / grid) * grid
            self._gi.prepareGeometryChange()
            self._origin = QtCore.QPointF(x, y)
            self._gi.setPos(self.realOrigin)
            self.updateGraphics()
    
    @property
    def end(self):
        """Returns the end QPointF of the TrackItem. The end is 
        the opposite end of the line from origin"""        
        return self._end

    @end.setter
    def end(self, pos):
        """Setter function for the origin property"""
        if self._simulation.context == Context.EDITOR:
            grid = self._simulation.grid
            x = round((pos.x()) / grid) * grid
            y = round((pos.y()) / grid) * grid
            self._gi.prepareGeometryChange()
            self._end = QtCore.QPointF(x, y)
            self.updateGraphics()
    
    @property
    def realLength(self):
        """Returns the length in metres that the line would have in real life
        """
        return self._realLength
    
    @realLength.setter
    def realLength(self, value):
        """Setter function for the realLength property"""
        if self._simulation.context == Context.EDITOR:
            self._realLength = value
    
    @property
    def maxSpeed(self):
        """Returns the maximum speed allowed on this LineItem, in metres per
        second"""
        return self._maxSpeed
    
    @maxSpeed.setter
    def maxSpeed(self, value):
        """Setter function for the maxSpeed property"""
        if self._simulation.context == Context.EDITOR:
            self._maxSpeed = value
    
    @property
    def endStr(self):
        """Returns a string representation of the QPointF end"""
        return "(%i, %i)" % (self.end.x(), self.end.y())
    
    @endStr.setter
    def endStr(self, value):
        """Setter for the endStr property"""
        if self._simulation.context == Context.EDITOR:
            x, y = eval(value.strip('()'))
            self.end = QtCore.QPointF(x, y)

    @property
    def realOrigin(self):
        """Returns the realOrigin QPointF of the TrackItem. The realOrigin is 
        the position of the top left corner of the bounding rectangle of the
        TrackItem. Reimplemented in SignalItem"""
        if self._simulation.context == Context.EDITOR:
            return self.origin + QtCore.QPointF(-5, -5)
        else:
            return self.origin + QtCore.QPointF(-2, -2)
        
    @realOrigin.setter
    def realOrigin(self, pos):
        """Setter function for the realOrigin property."""
        if self._simulation.context == Context.EDITOR:
            grid = self._simulation.grid
            x = round((pos.x() + 5.0) / grid) * grid
            y = round((pos.y() + 5.0) / grid) * grid
            vector = QtCore.QPointF(x, y) - self._origin
            self._gi.prepareGeometryChange()
            self._origin += vector
            self._end += vector
            self._gi.setPos(self.realOrigin)
            self.updateGraphics()

    @property
    def placeCode(self):
        """Returns the place code corresponding to this LineItem."""
        return self._placeCode

    @placeCode.setter
    def placeCode(self, value):
        """Setter function for the placeCode property"""
        if self.simulation.context == Context.EDITOR:
            self._placeCode = value

    @property
    def trackCode(self):
        """Returns the track code corresponding to this LineItem. The 
        trackCode enables to identify each line in a place (typically a 
        station)"""
        return self._trackCode

    @trackCode.setter
    def trackCode(self, value):
        """Setter function for the trackCode property"""
        if self.simulation.context == Context.EDITOR:
            self._trackCode = value

    @property
    def line(self):
        """Returns the line as a QLineF in the item's coordinates."""
        orig = QtCore.QPointF(2, 2)
        if self._simulation.context == Context.EDITOR:
            orig += QtCore.QPointF(3, 3)
        end = orig + self._end - self._origin
        return QtCore.QLineF(orig, end)
    
    @property
    def sceneLine(self):
        """Returns the line as a QLineF in the scene's coordinates."""
        return QtCore.QLineF(self._origin, self._end)

    def graphicsBoundingRect(self):
        """Returns the bounding rectangle of the line item"""
        x1 = self.line.p1().x()
        x2 = self.line.p2().x()
        y1 = self.line.p1().y()
        y2 = self.line.p2().y()
        lx = min(x1, x2) - 2.0
        rx = max(x1, x2) + 2.0
        ty = min(y1, y2) - 2.0
        by = max(y1, y2) + 2.0
        if self._simulation.context == Context.EDITOR:
            lx -= 3.0
            rx += 3.0
            ty -= 3.0
            by += 3.0
        return QtCore.QRectF(lx, ty, rx - lx, by - ty)

    def graphicsPaint(self, p, options, widget):
        """This function is called by the owned TrackGraphicsItem to paint its 
        painter. Draws the line and calls drawTrain to draw the train"""
        if self.highlighted:
            self._gi.setZValue(5)
        else:
            self._gi.setZValue(0)
        pen = self.getPen()
        p.setPen(pen)
        p.drawLine(self.line)
        if self._simulation.context == Context.EDITOR:
            p.setPen(QtGui.QPen(Qt.white))
            p.drawRect(0,0,9,9)
            p.drawRect(self.line.p2().x() - 5, self.line.p2().y() - 5, 9, 9)
        else:
            self.drawTrain()
       
    def drawTrain(self):
        """Draws the train on the line, if any"""
        if self.trainPresent():
            tline = QtCore.QLineF( \
                    self.sceneLine.pointAt(self._trainHead/self._realLength),\
                    self.sceneLine.pointAt(self._trainTail/self._realLength))
            if tline.length() < 5.0 and self._trainTail != 0:
                # Make sure that the train representation is always at least 
                # 5 pixel long.
                tline.setLength(min(5.0, \
                                    (1 - self._trainTail/self._realLength) * \
                                     self.sceneLine.length()))
            self._tli.setLine(tline)
            self._tli.show()
            self._tli.update()
        else:
            self._tli.hide()
            self._tli.update()

    def graphicsMouseMoveEvent(self, event):
        """This function is called by the owned TrackGraphicsItem to handle
        its mouseMoveEvent. Reimplemented in the LineItem class to begin a 
        drag operation on the origin or the end."""
        if event.buttons() == Qt.LeftButton and \
           self._simulation.context == Context.EDITOR:
            if QtCore.QLineF(event.scenePos(), \
                         event.buttonDownScenePos(Qt.LeftButton)).length() \
                        < 3.0:
                return
            drag = QtGui.QDrag(event.widget())
            mime = QtCore.QMimeData()
            pos = event.buttonDownPos(Qt.LeftButton)
            if QtCore.QRectF(0,0,9,9).contains(pos):
                movedEnd = "origin"
            elif QtCore.QRectF(self.line.p2().x() - 5, \
                               self.line.p2().y() - 5, 9, 9).contains(pos):
                movedEnd = "end"
                pos -= self.line.p2()
            else:
                movedEnd = "realOrigin"
            if movedEnd is not None:
                mime.setText(self.tiType + "#" + \
                            str(self.tiId)+ "#" + \
                            str(pos.x()) + "#" + \
                            str(pos.y()) + "#" + \
                            movedEnd)
                drag.setMimeData(mime)
                drag.exec_()
    
    @QtCore.pyqtSlot()
    def updateGraphics(self):
        """Updates the TrackGraphicsItem owned by this LineItem"""
        super().updateGraphics()
        self.drawTrain()
