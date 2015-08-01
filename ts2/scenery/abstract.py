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

from Qt import QtCore, QtGui, QtWidgets, Qt

from ts2 import utils
from ts2.scenery import helper

translate = QtWidgets.qApp.translate


def qPointFStrizer(attr):
    """Returns a function giving the str representation of attr, the
    latter being a QPointF property."""
    def getter(self):
        return "(%i, %i)" % (getattr(self, attr).x(),
                             getattr(self, attr).y())
    return getter


def qPointFDestrizer(attr):
    """Returns a function which updates a QPointF property from a string
    representation of a QPointF."""
    def setter(self, value):
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            x, y = eval(value.strip('()'))
            setattr(self, attr, QtCore.QPointF(x, y))
    return setter


def qPointFTupler(attr):
    """Returns a function giving the tuple representation of attr, the
    latter being a QPointF property."""
    def getter(self):
        return getattr(self, attr).x(), getattr(self, attr).y()
    return getter


def qPointFDetupler(attr):
    """Returns a function which updates a QPointF property from a tuple
    representation of a QPointF."""
    def setter(self, value):
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            x, y = value
            setattr(self, attr, QtCore.QPointF(x, y))
    return setter


class TrackItem(QtCore.QObject):
    """A TrackItem is a piece of scenery. Each item has defined coordinates in
    the scenery layout and is connected to other items so that the trains can
    travel from one to another. The coordinates are expressed in pixels.
    The origin is the top left most corner of the scene.
    The X-axis is from left to right and the Y-axis is from top to bottom.
    """
    def __init__(self, parameters):
        """Constructor for the TrackItem class.

        :param parameters: JSON object holding the parameters to create the
        TrackItem
        """
        super().__init__()
        self.simulation = None
        self._parameters = parameters
        self.tiId = parameters['tiId']
        self._name = parameters['name']
        self._maxSpeed = float(parameters.get('maxSpeed', "0.0"))
        self._nextItem = None
        self._previousItem = None
        self.activeRoute = None
        self.activeRoutePreviousItem = None
        self._selected = False
        self.defaultZValue = 0
        x = parameters['x']
        y = parameters['y']
        self._origin = QtCore.QPointF(x, y)
        self._end = QtCore.QPointF(x + 10, y)
        self._realLength = 1.0
        self._trainHead = -1
        self._trainTail = -1
        self._place = None
        self._conflictTrackItem = None
        self._trainPresentPreviousInfo = False
        self._gi = {}
        self.toBeDeselected = False
        self.properties = self.getProperties()
        self.multiProperties = self.getMultiProperties()

    def initialize(self, simulation):
        """Initialize the item after all items are loaded."""
        if not self._parameters:
            raise Exception("Internal error: TrackItem already initialized !")
        self.simulation = simulation
        params = self._parameters
        self._nextItem = simulation.trackItem(params.get('nextTiId'))
        self._previousItem = simulation.trackItem(params.get('previousTiId'))
        self.conflictTI = simulation.trackItem(params.get('conflictTiId'))

        self._parameters = None
        for gi in self._gi.values():
            simulation.registerGraphicsItem(gi)
        self.updateGraphics()

    def __del__(self):
        """Destructor for the TrackItem class"""
        self.removeAllGraphicsItems()

    trainEntersItem = QtCore.pyqtSignal()
    trainLeavesItem = QtCore.pyqtSignal()

    @staticmethod
    def getProperties():
        return [
            helper.TIProperty("tiTypeStr",
                              translate("TrackItem", "Type"), True),
            helper.TIProperty("tiId", translate("TrackItem", "id"), True),
            helper.TIProperty("name", translate("TrackItem", "Name")),
            helper.TIProperty("originStr", translate("TrackItem", "Position")),
            helper.TIProperty("maxSpeed", translate("TrackItem",
                              "Maximum speed (m/s)")),
            helper.TIProperty("conflictTiId", translate("TrackItem",
                              "Conflict item ID"))]

    @staticmethod
    def getMultiProperties():
        return [helper.TIProperty("tiId", translate("TrackItem", "id"), True),
                helper.TIProperty("maxSpeed",
                                  translate("TrackItem",
                                            "Maximum speed (m/s)"))]

    def for_json(self):
        """Dumps the trackItem to JSON."""
        if self.previousItem is not None:
            previousTiId = self.previousItem.tiId
        else:
            previousTiId = None
        if self.nextItem is not None:
            nextTiId = self.nextItem.tiId
        else:
            nextTiId = None
        return {
            "__type__": self.__class__.__name__,
            "tiId": self.tiId,
            "name": self.name,
            "conflictTiId": self.conflictTiId,
            "x": self.origin.x(),
            "y": self.origin.y(),
            "maxSpeed": self.maxSpeed,
            "previousTiId": previousTiId,
            "nextTiId": nextTiId
        }

    # ## Properties #########################################################

    def _getOrigin(self):
        """Returns the origin QPointF of the TrackItem. The origin is
        generally the left end of the track represented on the TrackItem"""
        return self._origin

    def _setOrigin(self, pos):
        """Setter function for the origin property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            grid = self.simulation.grid
            x = round((pos.x()) / grid) * grid
            y = round((pos.y()) / grid) * grid
            self._origin = QtCore.QPointF(x, y)
            self.graphicsItem.setPos(self._origin)
            self.updateGraphics()

    origin = property(_getOrigin, _setOrigin)
    originStr = property(qPointFStrizer("origin"),
                         qPointFDestrizer("origin"))

    def _getEnd(self):
        """Returns the end QPointF of the TrackItem. The end is
        generally the right end of the track represented on the TrackItem"""
        return self._end

    end = property(_getEnd)

    def _getName(self):
        """Returns the unique name of the trackItem"""
        return self._name

    def _setName(self, value):
        """Setter function for the name property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self._name = value
            self.graphicsItem.setToolTip(self.toolTipText)

    name = property(_getName, _setName)

    @property
    def maxSpeed(self):
        """Returns the maximum speed allowed on this LineItem, in metres per
        second"""
        if self.simulation.context == utils.Context.GAME and \
           self._maxSpeed == 0:
            return float(self.simulation.option("defaultMaxSpeed"))
        else:
            return self._maxSpeed

    @maxSpeed.setter
    def maxSpeed(self, value):
        """Setter function for the maxSpeed property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if value == "":
                value = "0.0"
            self._maxSpeed = float(value)

    @property
    def toolTipText(self):
        """Returns the string to show on the tool tip."""
        return ""

    @property
    def tiTypeStr(self):
        """Returns the type of this TrackItem as a string to be displayed"""
        return str(self.__class__.__name__)

    @property
    def highlighted(self):
        if self.activeRoute is None:
            return False
        else:
            return True

    def _getRealLength(self):
        """Length of this track item in real life."""
        return self._realLength

    realLength = property(_getRealLength)

    @property
    def place(self):
        return self._place

    @property
    def nextItem(self):
        return self._nextItem

    @nextItem.setter
    def nextItem(self, ni):
        self._nextItem = ni

    @property
    def previousItem(self):
        return self._previousItem

    @previousItem.setter
    def previousItem(self, pi):
        self._previousItem = pi

    def _getGraphicsItem(self):
        """Returns the graphics item of this TrackItem"""
        return self._gi[0]

    graphicsItem = property(_getGraphicsItem)

    def _getSelected(self):
        """Returns True if the item is selected."""
        return self._selected

    def _setSelected(self, value):
        """Setter function for the selected property."""
        for gi in self._gi.values():
            if value:
                gi.setZValue(100)
            else:
                gi.setZValue(self.defaultZValue)
        self._selected = value
        self.updateGraphics()

    selected = property(_getSelected, _setSelected)

    @property
    def conflictTI(self):
        return self._conflictTrackItem

    @conflictTI.setter
    def conflictTI(self, ti):
        self._conflictTrackItem = ti
        # TODO: Find a solution for this one ...
        # ti.conflictTI = self

    @property
    def conflictTiId(self):
        """Returns the conflict trackitem ID."""
        if self._conflictTrackItem is not None:
            return str(self._conflictTrackItem.tiId)
        else:
            return None

    @conflictTiId.setter
    def conflictTiId(self, value):
        """Setter function for the conflictTiId property."""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if value is not None and value != "":
                self.conflictTI = self.simulation.trackItem(int(value))
            else:
                self.conflictTI = None

    def _getTrainPresentPreviousInfo(self):
        """Returns True if a train has last been seen present on this TI,
        False otherwise."""
        return self._trainPresentPreviousInfo

    def _setTrainPresentPreviousInfo(self, value):
        """Setter function for the trainPresentPreviousInfo property. Emits
        trainEntersItem and trainLeavesItem signals, when applicable."""
        if value == self._trainPresentPreviousInfo:
            return
        if value:
            self.trainEntersItem.emit()
        else:
            self.trainLeavesItem.emit()
        self._trainPresentPreviousInfo = value

    trainPresentPreviousInfo = property(_getTrainPresentPreviousInfo,
                                        _setTrainPresentPreviousInfo)

    # ## Methods #########################################################

    def getFollowingItem(self, precedingItem, direction=-1):
        """Returns the following TrackItem linked to this one, knowing we come
        from precedingItem
        @param precedingItem TrackItem where we come from (along a route)
        @return Either _nextItem or _previousItem,depending which way we come
        from."""
        if precedingItem == self._previousItem:
            return self._nextItem
        elif precedingItem == self._nextItem:
            return self._previousItem
        else:
            return None

    def setActiveRoute(self, r, previous):
        """Sets the activeRoute and activeRoutePreviousItem informations. It
        is called upon Route activation. These information are used when other
        routes are activated in order to check the potential conflicts.
        @param r The newly active Route on this TrackItem.
        @param previous The previous TrackItem on this route (to know the
        direction)."""
        self.activeRoute = r
        self.activeRoutePreviousItem = previous
        self.updateGraphics()

    def resetActiveRoute(self):
        """Resets the activeRoute and activeRoutePreviousItem informations. It
        is called upon route desactivation."""
        self.activeRoute = None
        self.activeRoutePreviousItem = None
        self.updateGraphics()

    def setTrainHead(self, pos, prevTI=None):
        """Sets the trainHead indication on this TrackItem. The trainHead
        indication enables the drawing of a Train on this TrackItem.
        @param pos is the position of the trainHead in metres. Set to -1 if no
        Train head on this TrackItem
        @param prevTI To define the direction of the train, prevTI is a
        pointer to the previous TrackItem where the Train comes from."""
        if pos == -1:
            self._trainHead = -1
        else:
            if prevTI == self._previousItem:
                self._trainHead = pos
            else:
                self._trainHead = self._realLength - pos
        self.updateTrain()

    def setTrainTail(self, pos, prevTI=None):
        """Same as setTrainHead() but with the trainTail information."""
        if pos == -1:
            self._trainTail = -1
        else:
            if prevTI == self._previousItem:
                self._trainTail = pos
            else:
                self._trainTail = self._realLength - pos
        self.updateTrain()

    def trainPresent(self):
        """Returns True if a train is present on this TrackItem"""
        return self._trainHead != -1 or self._trainTail != -1

    def distanceToTrainEnd(self, previousTI):
        """Returns the distance to the closest end (either trainHead or
        trainTail) of the train from previousTI."""
        if previousTI == self.previousItem:
            return min(self._trainHead, self._trainTail)
        else:
            return min(self.realLength - self._trainHead,
                       self.realLength - self._trainTail)

    def isOnPosition(self, p):
        if p.trackItem() == self:
            return True
        else:
            return False

    def trainHeadActions(self, trainId):
        """Performs the actions to be done when a train head reaches this
        TrackItem"""
        self.trainPresentPreviousInfo = self.trainPresent()

    def trainTailActions(self, trainId):
        """Performs the actions to be done when a train tail reaches this
        TrackItem"""
        if self.activeRoute is not None:
            if not self.activeRoute.persistent:
                beginSignalNextRoute = \
                    self.activeRoute.beginSignal.nextActiveRoute
                if beginSignalNextRoute is None or \
                   beginSignalNextRoute != self.activeRoute:
                    if self.activeRoutePreviousItem.activeRoute is not None \
                       and self.activeRoutePreviousItem.activeRoute \
                       == self.activeRoute:
                        self.activeRoutePreviousItem.resetActiveRoute()
                        self.updateGraphics()
        self.trainPresentPreviousInfo = self.trainPresent()

    def setupTriggers(self):
        """Creates the triggers necessary for this trackItem.
        Base implementation does nothing."""
        pass

    def __eq__(self, ti):
        if ti is not None and self.tiId == ti.tiId:
            return True
        else:
            return False

    def __ne__(self, ti):
        if ti is None or self.tiId != ti.tiId:
            return True
        else:
            return False

    def __updateGraphics(self):
        for gi in self._gi.values():
            gi.update()

    def removeAllGraphicsItems(self):
        """Removes all the graphics items associated with this TrackItem
        from the scene."""
        for gi in self._gi.values():
            self.simulation.scene.removeItem(gi)

    @QtCore.pyqtSlot()
    def updateGraphics(self):
        self.__updateGraphics()

    def updateTrain(self):
        """Updates the graphics item for train only"""
        self.updateGraphics()

    # ## Graphics Methods #################################################

    def getPen(self):
        """Returns the standard pen for drawing trackItems"""
        pen = QtGui.QPen()
        pen.setWidth(3)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        if self.highlighted:
            pen.setColor(Qt.white)
        else:
            pen.setColor(Qt.darkGray)
        return pen

    def drawConnectionRect(self, painter, point):
        """Draws a connection rectangle on the given painter at the given
        point."""
        if self.selected:
            painter.setPen(Qt.magenta)
        else:
            painter.setPen(Qt.cyan)
        painter.setBrush(Qt.NoBrush)
        topLeft = point + QtCore.QPointF(-5, -5)
        painter.drawRect(QtCore.QRectF(topLeft, QtCore.QSizeF(10, 10)))

    def graphicsBoundingRect(self, itemId):
        """This function is called by the owned TrackGraphicsItem to return
        its bounding rectangle"""
        return QtCore.QRectF(0, 0, 1, 1)

    def graphicsShape(self, shape, itemId):
        """This function is called by the owned TrackGraphicsItem to return
        its shape. The given argument is the shape given by the parent class.
        """
        return shape

    def graphicsPaint(self, painter, options, itemId, widget=None):
        """This function is called by the owned TrackGraphicsItem to paint its
        painter. The implementation in the base class TrackItem outlines the
        shape of the item, if it is selected.
        """
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if self.selected:
                pen = QtGui.QPen(Qt.magenta)
                painter.setPen(pen)
                painter.drawPath(self._gi[itemId].shape())
                # painter.drawRect(self._gi[itemId].boundingRect())

    def graphicsMousePressEvent(self, event, itemId):
        """This function is called by the owned TrackGraphicsItem to handle
        its mousePressEvent. The default implementation in the base class
        trackItem does nothing."""
        pass

    def graphicsMouseMoveEvent(self, event, itemId=0):
        """This function is called by the owned TrackGraphicsItem to handle
        its mouseMoveEvent. The implementation in the base class TrackItem
        begins a drag operation."""
        if itemId == 0:
            if (event.buttons() == Qt.LeftButton and
                    self.simulation.context == utils.Context.EDITOR_SCENERY):
                if QtCore.QLineF(
                        event.scenePos(),
                        event.buttonDownScenePos(Qt.LeftButton)).length() < 3.0:
                    return
                drag = QtGui.QDrag(event.widget())
                mime = QtCore.QMimeData()
                pos = event.buttonDownScenePos(Qt.LeftButton) - self.origin
                mime.setText(type(self).__name__ + "#" +
                             str(self.tiId) + "#" +
                             str(pos.x()) + "#" +
                             str(pos.y()) + "#" +
                             "origin")
                drag.setMimeData(mime)
                drag.exec_()

    def graphicsDragEnterEvent(self, event, itemId):
        """This function is called by the owned TrackGraphicsItem to handle
        its dragEnterEvent. The implementation in the base class TrackItem
        does nothing."""
        pass

    def graphicsDragLeaveEvent(self, event, itemId):
        """This function is called by the owned TrackGraphicsItem to handle
        its dragLeaveEvent. The implementation in the base class TrackItem
        does nothing."""
        pass

    def graphicsDropEvent(self, event, itemId):
        """This function is called by the owned TrackGraphicsItem to handle
        its dropEvent. The implementation in the base class TrackItem
        does nothing."""
        pass

    # def graphicsItemSelectedChange(self, value):
        # """This function is called by the owned TrackGraphicsItem to handle
        # its itemSelectedChange event. The implementation in the base TrackItem
        # class handles item selection in the editor. Return True if the item is
        # finally selected False otherwise."""
        # retVal = value
        # if self.simulation.context == utils.Context.EDITOR_SCENERY:
        #     if QtGui.QApplication.keyboardModifiers() == Qt.ShiftModifier:
        #         retVal = 1
        #     QtCore.qDebug("TiId:%i, value:%s, gi.selected:%s" %
        #     (self.tiId, str(retVal), str(self.graphicsItem.isSelected())))
        #     self.simulation.updateSelection(self.tiId, retVal)
        # return retVal


class ResizableItem(TrackItem):
    """ResizableItem is the base class for all TrackItems which can be
    resized by the user in the editor, such as line items or platform items.
    """
    def __init__(self, parameters):
        """Constructor for the ResizableItem class."""
        super().__init__(parameters)
        xf = float(parameters['xf'])
        yf = float(parameters['yf'])
        self._end = QtCore.QPointF(xf, yf)

    @staticmethod
    def getProperties():
        return [
            helper.TIProperty("tiTypeStr", translate("LineItem", "Type"), True),
            helper.TIProperty("tiId", translate("LineItem", "id"), True),
            helper.TIProperty("name", translate("LineItem", "Name")),
            helper.TIProperty("originStr", translate("LineItem", "Point 1")),
            helper.TIProperty("endStr", translate("LineItem", "Point 2")),
            helper.TIProperty("maxSpeed", translate("LineItem",
                                                    "Maximum speed (m/s)")),
            helper.TIProperty("conflictTiId", translate("LineItem",
                                                        "Conflict item ID"))
        ]

    def for_json(self):
        """Dumps this resizeable item to JSON."""
        jsonData = super().for_json()
        jsonData.update({
            "xf": self._end.x(),
            "yf": self._end.y()
        })
        return jsonData

    # ## Properties #################################################

    def _setOrigin(self, pos):
        """Setter function for the origin property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            grid = self.simulation.grid
            x = round((pos.x()) / grid) * grid
            y = round((pos.y()) / grid) * grid
            vector = QtCore.QPointF(x, y) - self._origin
            self._origin += vector
            self._end += vector
            self.graphicsItem.setPos(self.origin)
            self.updateGraphics()

    origin = property(TrackItem._getOrigin, _setOrigin)

    def _setEnd(self, pos):
        """Setter function for the origin property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            grid = self.simulation.grid
            x = round((pos.x()) / grid) * grid
            y = round((pos.y()) / grid) * grid
            self.graphicsItem.prepareGeometryChange()
            self._end = QtCore.QPointF(x, y)
            self.updateGraphics()

    end = property(TrackItem._getEnd, _setEnd)
    endStr = property(qPointFStrizer("end"),
                      qPointFDestrizer("end"))

    def _getStart(self):
        """Returns the start QPointF of the TrackItem. The start is
        a point that is in the same place than origin, but resizes
        the item when moved instead of moving the item."""
        return self.origin

    def _setStart(self, pos):
        """Setter function for the start property."""
        self.graphicsItem.prepareGeometryChange()
        super()._setOrigin(pos)

    start = property(_getStart, _setStart)

    # ## Graphics Methods #################################################

    def graphicsBoundingRect(self, itemId):
        """Returns the bounding rectangle of this ResizableItem."""
        x1 = self.origin.x()
        y1 = self.origin.y()
        x2 = self.end.x()
        y2 = self.end.y()
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            return QtCore.QRectF(-5, -5, x2 - x1 + 10, y2 - y1 + 10)
        else:
            return QtCore.QRectF(0, 0, x2 - x1, y2 - y1)

    def graphicsMouseMoveEvent(self, event, itemId=0):
        """This function is called by the owned TrackGraphicsItem to handle
        its mouseMoveEvent. Reimplemented in the ResizableItem class to begin
        a drag operation on corners."""
        if event.buttons() == Qt.LeftButton and \
           self.simulation.context == utils.Context.EDITOR_SCENERY:
            if QtCore.QLineF(
                    event.scenePos(),
                    event.buttonDownScenePos(Qt.LeftButton)).length() < 3.0:
                return
            drag = QtGui.QDrag(event.widget())
            mime = QtCore.QMimeData()
            pos = event.buttonDownScenePos(Qt.LeftButton) - self.origin
            if QtCore.QRectF(-5, -5, 9, 9).contains(pos):
                movedEnd = "start"
            elif QtCore.QRectF(self.end.x() - self.origin.x() - 5,
                               self.end.y() - self.origin.y() - 5,
                               9, 9).contains(pos):
                movedEnd = "end"
                pos -= self.end - self.origin
            # elif self._gi[itemId].shape().contains(pos):
            else:
                movedEnd = "origin"
            if movedEnd is not None:
                mime.setText(type(self).__name__ + "#" +
                             str(self.tiId) + "#" +
                             str(pos.x()) + "#" +
                             str(pos.y()) + "#" +
                             movedEnd)
                drag.setMimeData(mime)
                drag.exec_()
