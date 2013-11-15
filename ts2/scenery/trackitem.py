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
from ts2 import utils

tr = QtCore.QObject().tr

class TrackGraphicsItem(QtGui.QGraphicsItem):
    """@brief Graphical item of a trackItem
    This class is the graphics of a TrackItem on the scene. Each instance
    belongs to a trackItem which is defined in the constructor and which
    is responsible for all actions related to this graphical item."""
    def __init__(self, trackItem, parent = None):
        """Constructor for the TrackGraphicsItem Class"""
        super().__init__(parent)
        self.trackItem = trackItem
        self.setZValue(0)

    def boundingRect(self):
        """Returns the bounding rectangle of the TrackGraphicsItem.
        See QGraphicsItem::boundingRect() for more info.
        Actually calls the graphicsBoundingRect() function of the owning
        trackItem"""
        return self.trackItem.graphicsBoundingRect()

    def shape(self):
        """Returns the shape of this item as a QPainterPath in local
        coordinates."""
        shape = super().shape()
        return self.trackItem.graphicsShape(shape)

    def paint(self, painter, option, widget = 0):
        """Painting function for the SignalGraphicsItem.
        This function calls the graphicsPaint function of the owning TrackItem
        to paint its painter."""
        #pen = QtGui.QPen(Qt.red)
        #painter.setPen(pen)
        #painter.drawPath(self.shape())
        self.trackItem.graphicsPaint(painter, option, widget)

    def mousePressEvent(self, event):
        """Event handler for mouse pressed.
        This function calls the graphicsMousePressEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsMousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Event handler for mouse pressed.
        This function calls the graphicsMousePressEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsMouseMoveEvent(event)

    def dragEnterEvent(self, event):
        """Event handler for when drag enters the item.
        This function calls the graphicsDragEnterEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsDragEnterEvent(event)

    def dragLeaveEvent(self, event):
        """Event handler for when drag leaves the item.
        This function calls the graphicsDragLeaveEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsDragLeaveEvent(event)

    def dropEvent(self, event):
        """Event handler for drop event on this item.
        This function calls the graphicsDropEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsDropEvent(event)



class TrackPropertiesModel(QtCore.QAbstractTableModel):
    """This class is a model for accessing TrackItem properties in the editor
    """
    def __init__(self, trackItem):
        """Constructor for the TrackPropertiesModel class"""
        super().__init__()
        self._trackItem = trackItem
        self._simulation = trackItem.simulation

    def rowCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of rows of the model, corresponding to the
        number of properties."""
        return len(self._trackItem.properties)

    def columnCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of columns of the model, i.e. 2, one for the
        property name, and one for the property value."""
        return 2

    def data(self, index, role = Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 0:
                return self._trackItem.properties[index.row()].display
            elif index.column() == 1:
                return getattr(self._trackItem,
                               self._trackItem.properties[index.row()].name)
        return None

    def setData(self, index, value, role = Qt.EditRole):
        """Sets the data to the model"""
        if role == Qt.EditRole:
            if index.column() == 1:
                setattr(self._trackItem,
                        self._trackItem.properties[index.row()].name,
                        value)
                self.dataChanged.emit(index, index)
                return True
        return False

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        """Returns the header labels"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return self.tr("Property")
            elif section == 1:
                return self.tr("Value")
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        retFlag = Qt.ItemIsEnabled
        if not self._trackItem.properties[index.row()].readOnly and \
            index.column() == 1:
                retFlag |= Qt.ItemIsEditable | Qt.ItemIsSelectable
        return retFlag


class TIProperty():
    """This class holds a TrackItem property that can be edited by the editor
    """
    def __init__(self, name, display, readOnly = False):
        """Constructor for the TIProperty class"""
        self._name = name
        self._display = display
        self._readOnly = readOnly

    @property
    def name(self):
        """The name of the property. This name must be the name of a python
        property of the TrackItem"""
        return self._name

    @property
    def display(self):
        """The property name to display in the editor"""
        return self._display

    @property
    def readOnly(self):
        """Returns True if the property can not be modified in the editor"""
        return bool(self._readOnly)


class TrackItem(QtCore.QObject):
    """A TrackItem is a piece of scenery. Each item has defined coordinates in
    the scenery layout and is connected to other items so that the trains can
    travel from one to another. The coordinates are expressed in pixels.
    The origin is the top left most corner of the scene.
    The X-axis is from left to right and the Y-axis is from top to bottom.
    """
    def __init__(self, simulation, parameters):
        """ Constructor for the TrackItem class"""
        super().__init__()
        self._simulation = simulation
        self._tiId = parameters["tiid"]
        self._name = parameters["name"]
        if parameters["maxspeed"] == "" or parameters["maxspeed"] is None:
            parameters["maxspeed"] = "0.0"
        self._maxSpeed = float(parameters["maxspeed"])
        self._tiType = "0"
        self._nextItem = None
        self._previousItem = None
        self._activeRoute = None
        self._activeRoutePreviousItem = None
        self._selected = False
        x = parameters["x"]
        y = parameters["y"]
        self._origin = QtCore.QPointF(x, y)
        self._realLength = 1.0
        self._trainHead = -1
        self._trainTail = -1
        self._place = None
        self._conflictTrackItem = None
        self._gi = TrackGraphicsItem(self)
        self.trackItemClicked.connect(self._simulation.itemSelected)

    def __del__(self):
        """Destructor for the TrackItem class"""
        self._simulation.scene.removeItem(self._gi)
        super().__del__()

    properties = [TIProperty("tiTypeStr", tr("Type"), True),
                  TIProperty("tiId", tr("id"), True),
                  TIProperty("name", tr("Name")),
                  TIProperty("originStr", tr("Position")),
                  TIProperty("maxSpeed", tr("Maximum speed (m/s)")),
                  TIProperty("conflictTiId", tr("Conflict item ID"))]

    fieldTypes = {
                    "tiid":"INTEGER PRIMARY KEY",
                    "titype":"VARCHAR(5)",
                    "name":"VARCHAR(100)",
                    "conflicttiid":"INTEGER",
                    "x":"DOUBLE",
                    "y":"DOUBLE",
                    "xf":"DOUBLE",
                    "yf":"DOUBLE",
                    "xr":"DOUBLE",
                    "yr":"DOUBLE",
                    "xn":"DOUBLE",
                    "yn":"DOUBLE",
                    "reverse":"BOOLEAN",
                    "reallength":"DOUBLE",
                    "maxspeed":"DOUBLE",
                    "placecode":"VARCHAR(10)",
                    "trackcode":"VARCHAR(10)",
                    "timersw":"DOUBLE",
                    "timerwc":"DOUBLE",
                 }

    trackItemClicked = QtCore.pyqtSignal(int)

    @property
    def origin(self):
        """Returns the origin QPointF of the TrackItem. The origin is
        generally the left end of the track represented on the TrackItem"""
        return self._origin

    @origin.setter
    def origin(self, value):
        """Setter function for the origin property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            self.realOrigin = value

    @property
    def realOrigin(self):
        """Returns the realOrigin QPointF of the TrackItem. The realOrigin is
        the position of the top left corner of the bounding rectangle of the
        TrackItem. Equals to origin in the implementation of the base
        TrackItem class"""
        return self._origin

    @realOrigin.setter
    def realOrigin(self, pos):
        """Setter function for the realOrigin property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            self._origin = pos
            self._gi.setPos(pos)
            self.updateGraphics()

    @property
    def originStr(self):
        """Returns a string representation of the QPointF origin"""
        return "(%i, %i)" % (self.origin.x(), self.origin.y())

    @originStr.setter
    def originStr(self, value):
        """Setter for the originStr property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            x, y = eval(value.strip('()'))
            self.origin = QtCore.QPointF(x, y)

    @property
    def end(self):
        """Returns the end QPointF of the TrackItem. The end is
        generally the right end of the track represented on the TrackItem"""
        return self._origin

    @property
    def name(self):
        """Returns the unique name of the trackItem"""
        return self._name

    @name.setter
    def name(self, value):
        """Setter function for the name property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            self._name = value
            self._gi.setToolTip(self.toolTipText)

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
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            if value == "": value = "0.0"
            self._maxSpeed = float(value)

    @property
    def toolTipText(self):
        """Returns the string to show on the tool tip."""
        return ""

    @property
    def tiId(self):
        """Returns the trackItem internal unique id."""
        return int(self._tiId)

    @property
    def tiType(self):
        return self._tiType

    @property
    def tiTypeStr(self):
        """Returns the type of this TrackItem as a string to be displayed"""
        return str(self.__class__.__name__)

    @property
    def simulation(self):
        return self._simulation

    @property
    def highlighted(self):
        if self._activeRoute is None:
            return False
        else:
            return True

    @property
    def selected(self):
        return self._selected

    @property
    def realLength(self):
        return self._realLength

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

    def getFollowingItem(self, precedingItem, direction = -1):
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

    @property
    def activeRoute(self):
        return self._activeRoute

    @property
    def activeRoutePreviousItem(self):
        return self._activeRoutePreviousItem

    @property
    def saveParameters(self):
        """Returns the parameters dictionary to save this TrackItem to the
        database"""
        return  {
                    "tiid":self.tiId,
                    "titype":self.tiType,
                    "name":self.name,
                    "conflicttiid":self.conflictTiId,
                    "x":self.origin.x(),
                    "y":self.origin.y(),
                    "maxspeed":self.maxSpeed
                }

    @property
    def graphicsItem(self):
        """Returns the graphics item of this TrackItem"""
        return self._gi

    def setActiveRoute(self, r, previous):
        """Sets the activeRoute and activeRoutePreviousItem informations. It
        is called upon Route activation. These information are used when other
        routes are activated in order to check the potential conflicts.
        @param r The newly active Route on this TrackItem.
        @param previous The previous TrackItem on this route (to know the
        direction)."""
        self._activeRoute = r
        self._activeRoutePreviousItem = previous
        self.updateGraphics()

    def resetActiveRoute(self):
        """Resets the activeRoute and activeRoutePreviousItem informations. It
        is called upon route desactivation."""
        self._activeRoute = None
        self._activeRoutePreviousItem = None
        self.updateGraphics()

    def setTrainHead(self, pos, prevTI = None):
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


    def setTrainTail(self, pos, prevTI = None):
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
        if self._trainHead != -1 or self._trainTail != -1:
            return True
        else:
            return False

    def isOnPosition(self, p):
        if p.trackItem() == self:
            return True
        else:
            return False

    def trainHeadActions(self, serviceCode):
        """Performs the actions to be done when a train head reaches this
        TrackItem"""
        pass

    def trainTailActions(self, serviceCode):
        """Performs the actions to be done when a train tail reaches this
        TrackItem"""
        if self.activeRoute is not None:
            if not self.activeRoute.persistent:
                beginSignalNextRoute = \
                            self.activeRoute.beginSignal.nextActiveRoute
                if beginSignalNextRoute is None or \
                   beginSignalNextRoute != self.activeRoute:
                    self.activeRoutePreviousItem.resetActiveRoute()
                    self.updateGraphics()

    @property
    def conflictTI(self):
        return self._conflictTrackItem

    @conflictTI.setter
    def conflictTI(self, ti):
        self._conflictTrackItem = ti

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
                self._conflictTrackItem = \
                                        self.simulation.trackItem(int(value))
            else:
                self._conflictTrackItem = None

    def __eq__(self, ti):
        if ti is not None and self._tiId == ti._tiId:
            return True
        else:
            return False

    def __ne__(self, ti):
        if ti is None or self._tiId != ti._tiId:
            return True
        else:
            return False

    def __updateGraphics(self):
        self._gi.update()

    @QtCore.pyqtSlot()
    def updateGraphics(self):
        self.__updateGraphics()

    def updateTrain(self):
        """Updates the graphics item for train only"""
        self.updateGraphics()

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
        painter.setPen(Qt.cyan)
        painter.setBrush(Qt.NoBrush)
        topLeft = point + QtCore.QPointF(-5, -5)
        painter.drawRect(QtCore.QRectF(topLeft, QtCore.QSizeF(10, 10)))

    def graphicsBoundingRect(self):
        """This function is called by the owned TrackGraphicsItem to return
        its bounding rectangle"""
        return QtCore.QRectF(0, 0, 1, 1)

    def graphicsShape(self, shape):
        """This function is called by the owned TrackGraphicsItem to return
        its shape. The given argument is the shape given by the parent class.
        """
        return shape

    def graphicsPaint(self, painter, options, widget = 0):
        """This function is called by the owned TrackGraphicsItem to paint its
        painter. The implementation in the base class TrackItem does nothing.
        """
        pass

    def graphicsMousePressEvent(self, event):
        """This function is called by the owned TrackGraphicsItem to handle
        its mousePressEvent. In the base TrackItem class, this function only
        emits the trackItemClicked signal."""
        if event.button() == Qt.LeftButton and \
           self.tiId > 0:
            self.trackItemClicked.emit(self.tiId)

    def graphicsMouseMoveEvent(self, event):
        """This function is called by the owned TrackGraphicsItem to handle
        its mouseMoveEvent. The implementation in the base class TrackItem
        begins a drag operation."""
        if event.buttons() == Qt.LeftButton and \
           self._simulation.context == utils.Context.EDITOR_SCENERY:
            if QtCore.QLineF(event.scenePos(), \
                         event.buttonDownScenePos(Qt.LeftButton)).length() \
                        < 3.0:
                return
            drag = QtGui.QDrag(event.widget())
            mime = QtCore.QMimeData()
            pos = event.buttonDownPos(Qt.LeftButton)
            mime.setText(self.tiType + "#" + \
                         str(self.tiId)+ "#" + \
                         str(pos.x()) + "#" + \
                         str(pos.y()) + "#" + \
                         "realOrigin")
            drag.setMimeData(mime)
            drag.exec_()

    def graphicsDragEnterEvent(self, event):
        """This function is called by the owned TrackGraphicsItem to handle
        its dragEnterEvent. The implementation in the base class TrackItem
        does nothing."""
        pass

    def graphicsDragLeaveEvent(self, event):
        """This function is called by the owned TrackGraphicsItem to handle
        its dragLeaveEvent. The implementation in the base class TrackItem
        does nothing."""
        pass

    def graphicsDropEvent(self, event):
        """This function is called by the owned TrackGraphicsItem to handle
        its dropEvent. The implementation in the base class TrackItem
        does nothing."""
        pass

