#
#   Copyright (C) 2008-2015 by Nicolas Piganeau
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

import ts2.routing.position
import ts2.utils as utils
from Qt import QtCore, QtGui, QtWidgets, Qt
from ts2.scenery import helper, abstract

translate = QtWidgets.qApp.translate


class LineItem(abstract.ResizableItem):
    """A line is a simple track used to connect other items together. The
    important parameter of a line is its real length, i.e. the length it would
    have in real life, since this will determine the time the train takes to
    travel on it.
    """

    def __init__(self, parameters):
        """Constructor for the LineItem class"""
        self._placeCode = ""
        self._trackCode = ""
        self._realLength = ""
        super().__init__(parameters)
        self.defaultZValue = 1
        self._line = QtCore.QLineF()
        self._boundingRect = QtCore.QRectF()
        self.updateGeometry()
        gli = helper.TrackGraphicsItem(self)
        gli.setPos(self._origin)
        gli.setZValue(self.defaultZValue)
        self._gi[0] = gli
        self._tli = []

    def updateFromParameters(self, parameters):
        super(LineItem, self).updateFromParameters(parameters)
        self._placeCode = parameters.get("placeCode", "")
        self._trackCode = parameters.get("trackCode", "")
        self._realLength = parameters.get('realLength', 1.0)

    def initialize(self, simulation):
        """Initialize the item after all items are loaded."""
        self._place = simulation.place(self._placeCode)
        trackCode = self._parameters.get("trackCode")
        if self._place is not None:
            self._trackCode = trackCode
            self._place.addTrack(self)
        if simulation.context in utils.Context.EDITORS:
            self._gi[0].setCursor(Qt.PointingHandCursor)
            self.positionSelected.connect(simulation.setSelectedTrainHead)
        else:
            self._gi[0].setCursor(Qt.ArrowCursor)
        self.simulation = simulation
        self.drawTrain()
        self.updateGeometry()
        super().initialize(simulation)

    @staticmethod
    def getProperties():
        return abstract.ResizableItem.getProperties() + [
            helper.TIProperty("placeCode", translate("LineItem", "Place code")),
            helper.TIProperty("trackCode", translate("LineItem", "Track code")),
            helper.TIProperty("realLength",
                              translate("LineItem", "Real length (m)"))
        ]

    positionSelected = QtCore.pyqtSignal(ts2.routing.position.Position)

    def for_json(self):
        """Dumps this line item to JSON."""
        jsonData = super().for_json()
        jsonData.update({
            "placeCode": self.placeCode,
            "trackCode": self.trackCode,
            "realLength": self.realLength,
            "maxSpeed": self._maxSpeed
        })
        return jsonData

    # ## Properties #####################################################

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

    def _setStart(self, pos):
        """Setter function for the start property"""
        super()._setStart(pos)
        self.updateGeometry()

    start = property(abstract.ResizableItem._getStart, _setStart)

    def _setRealLength(self, value):
        """Setter function for the realLength property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if value == "":
                value = "0.0"
            self._realLength = float(value)

    realLength = property(abstract.TrackItem._getRealLength, _setRealLength)

    @property
    def placeCode(self):
        """Returns the place code corresponding to this LineItem."""
        return self._placeCode

    @placeCode.setter
    def placeCode(self, value):
        """Setter function for the placeCode property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            place = self.simulation.place(value, raise_if_not_found=False)
            if place:
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

    @property
    def sceneLine(self):
        """Returns the line as a QLineF in the scene's coordinates."""
        return QtCore.QLineF(self.origin, self.end)

    # ## Methods ########################################################

    def updateGeometry(self):
        """Updates the internal representation of the line and boundingRect
        when it has been modified"""
        orig = QtCore.QPointF(0, 0)
        end = orig + self.end - self.origin
        self._line = QtCore.QLineF(orig, end)
        x1 = self._line.p1().x()
        x2 = self._line.p2().x()
        y1 = self._line.p1().y()
        y2 = self._line.p2().y()
        lx = min(x1, x2) - 5.0
        rx = max(x1, x2) + 5.0
        ty = min(y1, y2) - 5.0
        by = max(y1, y2) + 5.0
        if self.tiId.startswith("__EDITOR__"):
            # Library item in editor
            lx -= 15
            rx += 15
            ty -= 20
            by += 20
        self._boundingRect = QtCore.QRectF(lx, ty, rx - lx, by - ty)

    @QtCore.pyqtSlot()
    def updateGraphics(self):
        """Updates the TrackGraphicsItem owned by this LineItem"""
        if self.simulation.context == utils.Context.GAME:
            self.updateTrain()
        else:
            super().updateGraphics()

    def updateTrain(self):
        """Updates the graphics for trains movements only"""
        self.drawTrain()
        super().updateGraphics()

    # ## Graphics Methods ###############################################

    def graphicsBoundingRect(self, itemId):
        """Returns the bounding rectangle of the line item"""
        return self._boundingRect

    def graphicsShape(self, shape, itemId):
        """This function is called by the owned TrackGraphicsItem to return
        its shape. The given argument is the shape given by the parent class.
        """
        path = QtGui.QPainterPath(self._boundingRect.topLeft())
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if self.tiId.startswith("__EDITOR__"):
                # Tool box item
                d = 20
            else:
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

    def graphicsPaint(self, p, options, itemId, widget=None):
        """This function is called by the owned TrackGraphicsItem to paint its
        painter. Draws the line."""
        super().graphicsPaint(p, options, itemId, widget)
        if self.highlighted:
            # To have the activated line overlap crossing lines if any
            self.graphicsItem.setZValue(6)
        else:
            self.graphicsItem.setZValue(0)
        pen = self.getPen()
        p.setPen(pen)
        p.drawLine(self.line)
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.drawConnectionRect(p, self.line.p1())
            self.drawConnectionRect(p, self.line.p2())

    def drawTrain(self):
        """Draws the train(s) on the line, if any"""
        tlines = []
        if self.simulation.context == utils.Context.GAME:
            for i in range(len(self._trainHeads)):
                tlines.append(QtCore.QLineF(
                    self.sceneLine.pointAt(self._trainHeads[i] /
                                           self._realLength),
                    self.sceneLine.pointAt(self._trainTails[i] /
                                           self._realLength)
                ))
                if tlines[i].length() < 5.0 and self._trainTails[i] != 0:
                    # Make sure that the train representation is always
                    # at least 5 pixel long.
                    tlines[i].setLength(
                        min(5.0,
                            (1 - self._trainTails[i] / self._realLength) *
                            self.sceneLine.length()))
        self.showTrainLineItem(tlines)

    def showTrainLineItem(self, lines):
        """Shows the given lines (representing trains) on the scenery."""
        if lines:
            # Set the pen
            p = QtGui.QPen()
            p.setWidth(3)
            p.setJoinStyle(Qt.RoundJoin)
            p.setCapStyle(Qt.RoundCap)
            p.setColor(Qt.red)
            for i in range(len(lines)):
                try:
                    self._tli[i].setLine(lines[i])
                except IndexError:
                    newTli = QtWidgets.QGraphicsLineItem()
                    newTli.setCursor(Qt.ArrowCursor)
                    newTli.setPen(p)
                    newTli.setZValue(10)
                    newTli.setLine(lines[i])
                    self.simulation.registerGraphicsItem(newTli)
                    self._tli.append(newTli)
                    newTli.show()
                self._tli[i].update()
        for i in range(len(lines), len(self._tli)):
            self._tli[i].hide()
            self._tli[i].update()
        del self._tli[len(lines):]

    def graphicsMousePressEvent(self, event, itemId):
        """This function is called by the owned TrackGraphicsItem to handle
        its mousePressEvent. Reimplemented to send the positionSelected
        signal."""
        super().graphicsMousePressEvent(event, itemId)
        # pos = event.buttonDownPos(Qt.LeftButton)
        if event.button() == Qt.LeftButton:
            # and self.graphicsItem.shape().contains(pos):
            if (self.simulation.context == utils.Context.EDITOR_TRAINS and
                    not self.tiId.startswith("__EDITOR__")):
                x = event.buttonDownPos(Qt.LeftButton).x()
                ratio = (x - self.line.x1()) / (self.line.x2() - self.line.x1())
                self.positionSelected.emit(
                    ts2.routing.position.Position(self, self.previousItem,
                                                  self.realLength * ratio)
                )
