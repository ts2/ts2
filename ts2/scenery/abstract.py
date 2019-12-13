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
    """A ``TrackItem`` is a piece of scenery and is a **base class**. Each item
    has defined coordinates in the scenery layout and is connected to other
    items so that the trains can travel from one to another.

    - The coordinates are expressed in pixels
    - The :attr:`~ts2.scenery.abstract.TrackItem.origin` is the top left most
      corner of the scene
    - The X-axis is from left to right
    - The Y-axis is from top to bottom.
    """
    def __init__(self, parameters):
        """
        :param parameters: JSON object holding the parameters to create the
                            :class:`~ts2.scenery.abstract.TrackItem`
        """
        super().__init__()
        self.simulation = None
        self._parameters = parameters
        self.tiId = parameters['tiId']
        self._name = ""
        self._maxSpeed = 0
        self._origin = QtCore.QPointF()
        self._end = QtCore.QPointF()
        self._nextItem = None
        self._previousItem = None
        self.activeRoute = None
        self.activeRoutePreviousItem = None
        self._selected = False
        self.defaultZValue = 0
        self._realLength = 1.0
        self._trains = []
        self._trainHeads = []
        self._trainTails = []
        self._place = None
        self._conflictTrackItem = None
        self._gi = {}
        self.toBeDeselected = False
        self.properties = []
        self.multiProperties = []
        self.updateFromParameters(parameters)

    def updateFromParameters(self, parameters):
        self._parameters.update(parameters)
        self._name = parameters.get('name', "")
        self._maxSpeed = float(parameters.get('maxSpeed', "0.0"))
        x = parameters.get('x', 0.0)
        y = parameters.get('y', 0.0)
        self._origin = QtCore.QPointF(x, y)
        self._end = QtCore.QPointF(x + 10, y)
        self._realLength = float(parameters.get('realLength', "1.0"))

    def initialize(self, simulation):
        """Initialize the item after all items are loaded."""
        self.simulation = simulation
        params = self._parameters
        self._nextItem = simulation.trackItem(params.get('nextTiId'))
        self._previousItem = simulation.trackItem(params.get('previousTiId'))
        self._conflictTrackItem = simulation.trackItem(
            params.get('conflictTiId')
        )
        self.properties = self.getProperties()
        self.multiProperties = self.getMultiProperties()
        for gi in self._gi.values():
            simulation.registerGraphicsItem(gi)
        self.updateGraphics()

    def updateData(self, msg):
        if "activeRoute" in msg:
            if msg["activeRoute"]:
                self.activeRoute = self.simulation.routes[msg["activeRoute"]]
            else:
                self.activeRoute = None
        if "activeRoutePreviousItem" in msg:
            if msg["activeRoutePreviousItem"]:
                self.activeRoutePreviousItem = self.simulation.trackItems[msg["activeRoutePreviousItem"]]
            else:
                self.activeRoutePreviousItem = None
        if "trainEndsFW" in msg:
            self._trainHeads = [v for v in msg["trainEndsFW"].values()]
        if "trainEndsBK" in msg:
            self._trainTails = [v for v in msg["trainEndsBK"].values()]
        self.updateGraphics()

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
        """
        :return: Dumps this item to JSON.
        :rtype: dict
        """
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
        """
        :return: The origin of  :class:`~ts2.scenery.abstract.TrackItem`  is
                 generally the left end of the track represented on the
                 :class:`~ts2.scenery.abstract.TrackItem`
        :rtype: QPointF
        """
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
        """
        :return: The end  of the :class:`~ts2.scenery.abstract.TrackItem` is
                generally the right end of the track represented on the
                :class:`~ts2.scenery.abstract.TrackItem`
        :rtype: QPointF
        """
        return self._end

    end = property(_getEnd)

    def _getName(self):
        """
        :return: the unique name of the trackItem
        :rtype: str
        """
        return self._name

    def _setName(self, value):
        """Setter function for the name property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self._name = value
            self.graphicsItem.setToolTip(self.toolTipText)

    name = property(_getName, _setName)

    @property
    def maxSpeed(self):
        """
        :return: The maximum speed allowed on this LineItem, in metres per
                 second
        :rtype: float
        """
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
        """
        :return: the text to show on the tool tip.
        :rtype: str
        """
        return ""

    @property
    def tiTypeStr(self):
        """
        :return: the type of this TrackItem as a txt to be displayed
        :rtype: str
        """
        return str(self.__class__.__name__)

    @property
    def highlighted(self):
        if self.activeRoute is None:
            return False
        return True

    def _getRealLength(self):
        """
        :return: Length of this track item in real life metres.
        :rtype: int
        """
        return self._realLength

    realLength = property(_getRealLength)

    @property
    def place(self):
        return self._place

    @property
    def nextItem(self):
        """
         :return: Next Item
         :rtype: :class:`~ts2.scenery.abstract.TrackItem`
        """
        return self._nextItem

    @nextItem.setter
    def nextItem(self, ni):
        self._nextItem = ni

    @property
    def previousItem(self):
        """
        :return: Previous Item
        :rtype: :class:`~ts2.scenery.abstract.TrackItem`
        """
        return self._previousItem

    @previousItem.setter
    def previousItem(self, pi):
        self._previousItem = pi

    def _getGraphicsItem(self):
        """Returns the graphics item of this TrackItem"""
        return self._gi[0]

    graphicsItem = property(_getGraphicsItem)

    def _getSelected(self):
        """
        :return: True if the item is selected.
        :rtype: bool
        """
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
        """
        :return: The conflicting item
        :rtype: :class:`~ts2.scenery.abstract.TrackItem`
        """
        return self._conflictTrackItem

    @property
    def conflictTiId(self):
        """
        :return: the conflict trackitem ID.
        :rtype: str
        """
        if hasattr(self._conflictTrackItem, "tiId"):
            return self._conflictTrackItem.tiId
        else:
            return None

    @conflictTiId.setter
    def conflictTiId(self, value):
        """Setter function for the conflictTiId property."""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if value:
                self._conflictTrackItem = self.simulation.trackItem(value)
                if self._conflictTrackItem:
                    self._conflictTrackItem._conflictTrackItem = self
            else:
                if self._conflictTrackItem:
                    self._conflictTrackItem._conflictTrackItem = None
                self._conflictTrackItem = None

    # ## Methods #########################################################

    def getFollowingItem(self, precedingItem, direction=-1):
        """
        :param precedingItem: TrackItem where we come from (along a route)
        :param direction: The direction
        :return: the following :class:`~ts2.scenery.abstract.TrackItem` linked
                 to this one, knowing we come from ``precedingItem``.

                Returned isEither _nextItem or _previousItem,depending which way
                we come from.
        :rtype: :class:`~ts2.scenery.abstract.TrackItem`
        """
        if precedingItem == self._previousItem:
            return self._nextItem
        elif precedingItem == self._nextItem:
            return self._previousItem
        else:
            raise Exception("Items not linked: %s and %s" %
                            (self.tiId, precedingItem.tiId))

    def trainPresent(self):
        """
        :return: ``True`` if at least one train is present on this TrackItem.
        :rtype: bool
        """
        return self._trainHeads or self._trainTails

    def distanceToTrainEnd(self, pos):
        """
        :param pos:
        :type pos:
        :return: the distance in metres to the closest end (either trainHead or
        trainTail) of the closest train when on pos.
        :rtype: float
        """
        if pos.previousTI == self.previousItem:
            return min([x - pos.positionOnTI for x in self._trainTails
                        if (x - pos.positionOnTI) > 0] or
                       [-1])
        else:
            return min([(self.realLength - x) - pos.positionOnTI
                        for x in self._trainHeads
                        if (self.realLength - x) - pos.positionOnTI > 0] or
                       [-1])

    def isOnPosition(self, p):
        """
        :param p:
        :type p:
        :return: todo
        :rtype: bool
        """
        if p.trackItem() == self:
            return True
        return False

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
        """
        :return: the standard pen for drawing trackItems
        :rtype: ``QPen``
        """
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
        """Draws a connection rectangle on the given painter at the given point.

        :param painter: the painter to paint on
        :type painter: ``QPainter``
        :param point: the point to draw on
        :type point: ``QPointF``
        """
        pen = self.getPen()
        pen.setWidth(0)
        if self.selected:
            pen.setColor(Qt.magenta)
        else:
            pen.setColor(Qt.cyan)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        topLeft = point + QtCore.QPointF(-5, -5)
        painter.drawRect(QtCore.QRectF(topLeft, QtCore.QSizeF(10, 10)))

    def graphicsBoundingRect(self, itemId):
        """
        :return: The bounding rectangle of the owned
                 :class:`~ts2.scenery.helper.TrackGraphicsItem`.
        :rtype: ``QRectF``
        """
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
    """``ResizableItem`` is the base class for all
    :class:`~ts2.scenery.abstract.TrackItem`'s which can be
    resized by the user in the editor, such as
    :class:`~ts2.scenery.lineitem.LineItem`'s or
    :class:`~ts2.scenery.platformitem.PlatformItem`'s.
    """

    def updateFromParameters(self, parameters):
        super(ResizableItem, self).updateFromParameters(parameters)
        xf = float(parameters.get('xf', 0.0))
        yf = float(parameters.get('yf', 0.0))
        self._end = QtCore.QPointF(xf, yf)

    @staticmethod
    def getProperties():
        """
        :return: a ``list`` of properties
        :rtype: list
        """
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
        """
        :return: Dumps this resizeable item to JSON.
        :rtype: dict
        """
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
        """
        :return: The start of a :class:`~ts2.scenery.abstract.TrackItem` is a
                 point that is in the same place than origin, but resizes
                 the item when moved instead of moving the item.
        :rtype: QPointF
        """
        return self.origin

    def _setStart(self, pos):
        """Setter function for the start property."""
        self.graphicsItem.prepareGeometryChange()
        super()._setOrigin(pos)

    start = property(_getStart, _setStart)

    # ## Graphics Methods #################################################

    def graphicsBoundingRect(self, itemId):
        """
        :return:  the bounding rectangle of this ``ResizableItem``.
        :rtype: QRect """
        x1 = self.origin.x()
        y1 = self.origin.y()
        x2 = self.end.x()
        y2 = self.end.y()
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            return QtCore.QRectF(-5, -5, x2 - x1 + 10, y2 - y1 + 10)
        else:
            return QtCore.QRectF(0, 0, x2 - x1, y2 - y1)

    def graphicsMouseMoveEvent(self, event, itemId=0):
        """This function is called by the owned
        :class:`~ts2.scenery.helper.TrackGraphicsItem` to handle
        its :meth:`~ts2.scenery.helper.TrackGraphicsItem.mouseMoveEvent`.
        Reimplemented in the ResizableItem class to begin a drag operation on
        corners."""
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
