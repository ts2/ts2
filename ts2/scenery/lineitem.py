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
from PyQt4.QtCore import Qt
from ts2.scenery import helper, abstract
from ts2 import utils, routing
from math import sqrt

tr = QtCore.QObject().tr


class LineItem(abstract.ResizableItem):
    """A line is a simple track used to connect other items together. The
    important parameter of a line is its real length, i.e. the length it would
    have in real life, since this will determine the time the train takes to
    travel on it.
    """
    def __init__(self, simulation, parameters):
        """Constructor for the LineItem class"""
        super().__init__(simulation, parameters)
        self.tiType = "L"
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
            realLength = 1.0
        self._realLength = realLength
        self.updateGeometry()
        gli = helper.TrackGraphicsItem(self)
        if simulation.context in utils.Context.EDITORS:
            gli.setCursor(Qt.PointingHandCursor)
        else:
            gli.setCursor(Qt.ArrowCursor)
        gli.setPos(self._origin)
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

    positionSelected = QtCore.pyqtSignal(routing.Position)

    def __del__(self):
        """Destructor for the LineItem class"""
        self.simulation.scene.removeItem(self._tli)
        super().__del__()


    properties = [helper.TIProperty("tiTypeStr", tr("Type"), True),
                  helper.TIProperty("tiId", tr("id"), True),
                  helper.TIProperty("name", tr("Name")),
                  helper.TIProperty("originStr", tr("Point 1")),
                  helper.TIProperty("endStr", tr("Point 2")),
                  helper.TIProperty("placeCode", tr("Place code")),
                  helper.TIProperty("trackCode", tr("Track code")),
                  helper.TIProperty("realLength", tr("Real length (m)")),
                  helper.TIProperty("maxSpeed", tr("Maximum speed (m/s)")),
                  helper.TIProperty("conflictTiId", tr("Conflict item ID"))]

    def getSaveParameters(self):
        """Returns the parameters dictionary to save this TrackItem to the
        database"""
        parameters = super().getSaveParameters()
        parameters.update({
                            "xf":self._end.x(),
                            "yf":self._end.y(),
                            "placecode":self.placeCode,
                            "trackCode":self.trackCode,
                            "reallength":self.realLength,
                            "maxspeed":self._maxSpeed})
        return parameters


    def _setOrigin(self, pos):
        """Setter function for the origin property"""
        super()._setOrigin(pos)
        self.updateGeometry()

    origin = property(abstract.ResizableItem._getOrigin, _setOrigin)

    def _setEnd(self, pos):
        """Setter function for the origin property"""
        super()._setEnd(pos)
        self.updateGeometry()

    end = property(abstract.ResizableItem._getEnd, _setEnd)

    def _setRealOrigin(self, pos):
        """Setter function for the realOrigin property"""
        super()._setRealOrigin(pos)
        self.updateGeometry()

    realOrigin = property(abstract.ResizableItem._getRealOrigin,
                          _setRealOrigin)

    @property
    def realLength(self):
        """Returns the length in metres that the line would have in real life
        """
        return self._realLength

    @realLength.setter
    def realLength(self, value):
        """Setter function for the realLength property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if value == "": value = "0.0"
            self._realLength = float(value)

    @property
    def placeCode(self):
        """Returns the place code corresponding to this LineItem."""
        return self._placeCode

    @placeCode.setter
    def placeCode(self, value):
        """Setter function for the placeCode property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            place = self.simulation.place(value)
            if place is not None:
                self._placeCode = value
                self._place = place
                self._place.addTrack(self)
            else:
                self._placeCode = ""

    @property
    def trackCode(self):
        """Returns the track code corresponding to this LineItem. The
        trackCode enables to identify each line in a place (typically a
        station)"""
        return self._trackCode

    @trackCode.setter
    def trackCode(self, value):
        """Setter function for the trackCode property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if self._place is not None:
                self._trackCode = value
            else:
                self._trackCode = ""

    @property
    def line(self):
        """Returns the line as a QLineF in the item's coordinates."""
        return self._line

    def updateGeometry(self):
        """Updates the internal representation of the line and boundingRect
        when it has been modified"""
        orig = QtCore.QPointF(0, 0)
        end = orig + self._end - self._origin
        self._line = QtCore.QLineF(orig, end)
        x1 = self._line.p1().x()
        x2 = self._line.p2().x()
        y1 = self._line.p1().y()
        y2 = self._line.p2().y()
        lx = min(x1, x2) - 2.0
        rx = max(x1, x2) + 2.0
        ty = min(y1, y2) - 2.0
        by = max(y1, y2) + 2.0
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            lx -= 3.0
            rx += 3.0
            ty -= 3.0
            by += 3.0
        self._boundingRect = QtCore.QRectF(lx, ty, rx - lx, by - ty)

    @property
    def sceneLine(self):
        """Returns the line as a QLineF in the scene's coordinates."""
        return QtCore.QLineF(self._origin, self._end)

    def graphicsBoundingRect(self):
        """Returns the bounding rectangle of the line item"""
        return self._boundingRect

    def graphicsShape(self, shape):
        """This function is called by the owned TrackGraphicsItem to return
        its shape. The given argument is the shape given by the parent class.
        """
        path = QtGui.QPainterPath(self._boundingRect.topLeft())
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            d = 5
        else:
            d = 2
        if self._line.p1().x() < self._line.p2().x():
            x1 = self._line.p1().x()
            y1 = self._line.p1().y()
            x2 = self._line.p2().x()
            y2 = self._line.p2().y()
        else:
            x1 = self._line.p2().x()
            y1 = self._line.p2().y()
            x2 = self._line.p1().x()
            y2 = self._line.p1().y()
        if y1 < y2:
            path.moveTo(x1 - d, y1 - d)
            path.lineTo(x1 - d, y1 + d)
            path.lineTo(x2 - d, y2 + d)
            path.lineTo(x2 + d, y2 + d)
            path.lineTo(x2 + d, y2 - d)
            path.lineTo(x1 + d, y1 - d)
            path.lineTo(x1 - d, y1 - d)
        else:
            path.moveTo(x1 - d, y1 + d)
            path.lineTo(x1 + d, y1 + d)
            path.lineTo(x2 + d, y2 + d)
            path.lineTo(x2 + d, y2 - d)
            path.lineTo(x2 - d, y2 - d)
            path.lineTo(x1 - d, y1 - d)
            path.lineTo(x1 - d, y1 + d)
        return path

    def graphicsPaint(self, p, options, widget):
        """This function is called by the owned TrackGraphicsItem to paint its
        painter. Draws the line."""
        if self.highlighted:
            self._gi.setZValue(6)
        else:
            self._gi.setZValue(1)
        pen = self.getPen()
        p.setPen(pen)
        p.drawLine(self.line)
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.drawConnectionRect(p, self.line.p1())
            self.drawConnectionRect(p, self.line.p2())


    def drawTrain(self):
        """Draws the train on the line, if any"""
        if self.simulation.context == utils.Context.GAME and \
           self.trainPresent():
            if int(self.simulation.option("trackCircuitBased")) == 0:
                tline = QtCore.QLineF(
                        self.sceneLine.pointAt(
                                            self._trainHead/self._realLength),
                        self.sceneLine.pointAt(
                                            self._trainTail/self._realLength))
                if tline.length() < 5.0 and self._trainTail != 0:
                    # Make sure that the train representation is always at least
                    # 5 pixel long.
                    tline.setLength(min(5.0,
                                        (1 - self._trainTail/self._realLength) *
                                        self.sceneLine.length()))
            else:
                tline = self.sceneLine
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
           self.simulation.context == utils.Context.EDITOR_SCENERY:
            if QtCore.QLineF(event.scenePos(),
                         event.buttonDownScenePos(Qt.LeftButton)).length() \
                        < 3.0:
                return
            drag = QtGui.QDrag(event.widget())
            mime = QtCore.QMimeData()
            pos = event.buttonDownPos(Qt.LeftButton)
            if QtCore.QRectF(-5,-5,9,9).contains(pos):
                movedEnd = "origin"
            elif QtCore.QRectF(self.line.p2().x() - 5,
                               self.line.p2().y() - 5, 9, 9).contains(pos):
                movedEnd = "end"
                pos -= self.line.p2()
            elif self._gi.shape().contains(pos):
                movedEnd = "realOrigin"
            if movedEnd is not None:
                mime.setText(self.tiType + "#" +
                            str(self.tiId)+ "#" +
                            str(pos.x()) + "#" +
                            str(pos.y()) + "#" +
                            movedEnd)
                drag.setMimeData(mime)
                drag.exec_()


    def graphicsMousePressEvent(self, event):
        """This function is called by the owned TrackGraphicsItem to handle
        its mousePressEvent. Reimplemented to send the positionSelected
        signal."""
        super().graphicsMousePressEvent(event)
        pos = event.buttonDownPos(Qt.LeftButton)
        if event.button() == Qt.LeftButton and \
           self._gi.shape().contains(pos):
            if self.simulation.context == utils.Context.EDITOR_TRAINS and \
               self.tiId > 0:
                x = event.buttonDownPos(Qt.LeftButton).x()
                ratio = (x - self.line.x1())/(self.line.x2() - self.line.x1())
                self.positionSelected.emit(routing.Position(
                                                    self,
                                                    self.previousItem,
                                                    self.realLength * ratio))

    @QtCore.pyqtSlot()
    def updateGraphics(self):
        """Updates the TrackGraphicsItem owned by this LineItem"""
        self._gi.update()
        self.updateTrain()

    def updateTrain(self):
        """Updates the graphics for trains movements only"""
        self.drawTrain()

