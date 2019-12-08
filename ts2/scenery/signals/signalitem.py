#
#   Copyright (C) 2008-2014 by Nicolas Piganeau
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

import collections
import copy
import os

import simplejson as json

from Qt import QtCore, QtGui, QtWidgets, Qt
from ts2 import utils
from ts2.scenery import abstract, helper, enditem
from . import signalaspect

translate = QtWidgets.qApp.translate

BUILTIN_SIGNAL_LIBRARY = """{
    "__type__": "SignalLibrary",
    "signalAspects": {
        "BUFFER": {
            "__type__": "SignalAspect",
            "lineStyle": 1,
            "outerShapes": [0, 0, 0, 0, 0, 0],
            "outerColors": ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
            "shapes": [0, 0, 0, 0, 0, 0],
            "shapesColors": ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
            "blink": [false, false, false, false, false, false],
            "actions": [[1, 0]]
        },
        "UK_DANGER": {
            "__type__": "SignalAspect",
            "lineStyle": 0,
            "outerShapes": [0, 0, 0, 0, 0, 0],
            "outerColors": ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
            "shapes": [1, 0, 0, 0, 0, 0],
            "shapesColors": ["#FF0000", "#000000", "#000000", "#000000", "#000000", "#000000"],
            "blink": [false, false, false, false, false, false],
            "actions": [[1, 0]]
        },
        "UK_CAUTION": {
            "__type__": "SignalAspect",
            "lineStyle": 0,
            "outerShapes": [0, 0, 0, 0, 0, 0],
            "outerColors": ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
            "shapes": [1, 0, 0, 0, 0, 0],
            "shapesColors": ["#FFFF00", "#000000", "#000000", "#000000", "#000000", "#000000"],
            "blink": [false, false, false, false, false, false],
            "actions": [[2, 0]]
        },
        "UK_CLEAR": {
            "__type__": "SignalAspect",
            "lineStyle": 0,
            "outerShapes": [0, 0, 0, 0, 0, 0],
            "outerColors": ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
            "shapes": [1, 0, 0, 0, 0, 0],
            "shapesColors": ["#00FF00", "#000000", "#000000", "#000000", "#000000", "#000000"],
            "blink": [false, false, false, false, false, false],
            "actions": [[0, 999]]
        }
    },
    "signalTypes": {
        "BUFFER": {
            "__type__": "SignalType",
            "states": [
                {
                    "__type__": "SignalState",
                    "aspectName": "BUFFER",
                    "conditions": {}
                }
            ]
        },
        "UK_3_ASPECTS": {
            "__type__": "SignalType",
            "states": [
                {
                    "__type__": "SignalState",
                    "aspectName": "UK_CLEAR",
                    "conditions": {
                        "NEXT_ROUTE_ACTIVE": [],
                        "TRAIN_NOT_PRESENT_ON_NEXT_ROUTE": [],
                        "NEXT_SIGNAL_ASPECTS": ["UK_CLEAR", "UK_CAUTION"]
                    }
                },
                {
                    "__type__": "SignalState",
                    "aspectName": "UK_CAUTION",
                    "conditions": {
                        "NEXT_ROUTE_ACTIVE": [],
                        "TRAIN_NOT_PRESENT_ON_NEXT_ROUTE": [],
                        "NEXT_SIGNAL_ASPECTS": ["UK_DANGER", "BUFFER"]
                    }
                },
                {
                    "__type__": "SignalState",
                    "aspectName": "UK_DANGER",
                    "conditions": {}
                }
            ]
        }
    }
}"""


class SignalItem(abstract.TrackItem):
    """Logical item for signals.

    - This class holds the logic of a signal defined by its
      :class:`~ts2.scenery.signals.signalitem.SignalType`.
    - A signal is the item from and to which routes are created.
    """

    SIGNAL_GRAPHIC_ITEM = 0
    BERTH_GRAPHIC_ITEM = 1
    SIGNAL_NUMBER_ITEM = 2

    def __init__(self, parameters):
        """
        :param dict parameters:
        """
        self._reverse = False
        self._signalType = None
        self._berthOrigin = QtCore.QPointF()
        self._berthRect = None
        super().__init__(parameters)
        self.setBerthRect()
        self._activeAspect = signalLibrary.signalAspects.get(parameters.get("activeAspect"))
        self._previousActiveRoute = None
        self._nextActiveRoute = None
        self._trainId = None
        self.defaultZValue = 50
        sgi = helper.TrackGraphicsItem(self, SignalItem.SIGNAL_GRAPHIC_ITEM)
        sgi.setPos(self.origin)
        sgi.setCursor(Qt.PointingHandCursor)
        sgi.setToolTip(self.toolTipText)
        sgi.setZValue(self.defaultZValue)
        if self._reverse:
            sgi.setRotation(180)
        self._gi[SignalItem.SIGNAL_GRAPHIC_ITEM] = sgi
        bgi = helper.TrackGraphicsItem(self, SignalItem.BERTH_GRAPHIC_ITEM)
        bgi.setPos(self._berthOrigin)
        bgi.setCursor(Qt.PointingHandCursor)
        bgi.setZValue(self.defaultZValue)
        self._gi[SignalItem.BERTH_GRAPHIC_ITEM] = bgi
        self.lightOn = True

    def display_signal_number(self):
        sni = QtWidgets.QGraphicsSimpleTextItem()
        font = sni.font()
        font.setPixelSize(8)
        font.setFamily("Courier New")
        sni.setFont(font)
        brush = sni.brush()
        brush.setColor(Qt.white)
        sni.setBrush(brush)
        if self._reverse:
            sni.setText(self.name)
            sni.setPos(self.origin + QtCore.QPointF(0, 2))
        else:
            txt = (" " * 5 + self.name)[-5:]
            sni.setText(txt)
            sni.setPos(self.origin + QtCore.QPointF(-24, -10))
        sni.setZValue(1)
        self._gi[SignalItem.SIGNAL_NUMBER_ITEM] = sni

    def updateFromParameters(self, parameters):
        super(SignalItem, self).updateFromParameters(parameters)
        reverse = bool(parameters.get("reverse", 0))
        for key, customProperty in signalLibrary.tiProperties.items():
            # Initialize backend vars for custom properties
            propName = "_" + customProperty.name[:-3]
            customProps = parameters.get("customProperties") or {}
            setattr(self, propName, eval(str(customProps.get(key, {}))))
        try:
            xb = float(parameters.get("xn", ""))
        except ValueError:
            xb = self.origin.x() - 40
        try:
            yb = float(parameters.get("yn", ""))
        except ValueError:
            yb = self.origin.y() + 5
        self._berthOrigin = QtCore.QPointF(xb, yb)
        self._reverse = reverse

    def initialize(self, simulation):
        """Initialize the signal item once everything is loaded."""
        params = self._parameters
        if not params:
            raise Exception("Internal error: TrackItem %s already initialized"
                            % self.tiId)
        try:
            self._signalType = simulation.signalLibrary.signalTypes[
                params['signalType']
            ]
        except KeyError as err:
            raise utils.MissingDependencyException(
                self.tr("This simulation uses %s signal types which are not "
                        "available on this computer. You can download the "
                        "missing files from the server in File->Open dialog" %
                        (str(err)))
            )
        self._activeAspect = self._signalType.getDefaultAspect()
        if simulation.context == utils.Context.GAME:
            self.signalSelected.connect(simulation.activateRoute)
            self.signalUnselected.connect(simulation.desactivateRoute)
            self.display_signal_number()
        else:
            self.signalSelected.connect(simulation.prepareRoute)
            self.signalUnselected.connect(simulation.deselectRoute)
        self.trainSelected.connect(simulation.trainSelected)
        simulation.timeChanged.connect(self.updateBlink)
        super().initialize(simulation)

    def updateData(self, msg):
        if "nextActiveRoute" in msg:
            if msg["nextActiveRoute"]:
                self.nextActiveRoute = self.simulation.routes[msg["nextActiveRoute"]]
            else:
                self.nextActiveRoute = None
        if "previousActiveRoute" in msg:
            if msg["previousActiveRoute"]:
                self.previousActiveRoute = self.simulation.routes[msg["previousActiveRoute"]]
            else:
                self.previousActiveRoute = None
        if "activeAspect" in msg:
            if msg["activeAspect"]:
                self._activeAspect = signalLibrary.signalAspects[msg["activeAspect"]]
            else:
                self._activeAspect = None
        if "trainID" in msg:
            if msg["trainID"]:
                self._trainId = msg["trainID"]
            else:
                self._trainId = None
        super(SignalItem, self).updateData(msg)

    @staticmethod
    def getProperties():
        signalTypeNames = sorted(
            list(signalLibrary.signalTypes.keys())
        )
        signalCustomProperties = list(signalLibrary.tiProperties.values())
        return abstract.TrackItem.getProperties() + [
            helper.TIProperty("reverse",
                              translate("SignalItem", "Reverse")),
            helper.TIProperty("signalTypeStr",
                              translate("SignalItem", "Signal Type"),
                              False,
                              "enum",
                              signalTypeNames,
                              signalTypeNames),
            helper.TIProperty("berthOriginStr",
                              translate("SignalItem", "Berth Origin"))
        ] + signalCustomProperties

    def for_json(self):
        """Dumps the signalItem to JSON."""
        jsonData = super().for_json()
        signalCustomProperties = {}
        for key, customProp in signalLibrary.tiProperties.items():
            if customProp:
                signalCustomProperties[key] = getattr(self, customProp.name[:-3])
        jsonData.update({
            "customProperties": signalCustomProperties,
            "reverse": self.reverse,
            "signalType": self.signalTypeStr,
            "xn": self.berthOrigin.x(),
            "yn": self.berthOrigin.y()
        })
        return jsonData

    signalSelected = QtCore.pyqtSignal(str, bool, bool)
    """pyqtSignal(int, bool, bool)"""

    signalUnselected = QtCore.pyqtSignal(str)
    """pyqtSignal(int)"""

    trainSelected = QtCore.pyqtSignal(str)
    """pyqtSignal(int)"""

    aspectChanged = QtCore.pyqtSignal()
    """pyqtSignal()"""

    # ## Properties #########################################################

    origin = property(abstract.TrackItem._getOrigin,
                      abstract.TrackItem._setOrigin)

    def _getEnd(self):
        """Returns the end QPointF of the TrackItem. The end is
        generally the right end of the track represented on the TrackItem"""
        if not self.reverse:
            return self._origin + QtCore.QPointF(10, 0)
        else:
            return self._origin + QtCore.QPointF(-10, 0)

    end = property(_getEnd)

    def _getReverse(self):
        """
        :return: True if the SignalItem is from right to left, otherwise False
        :rtype: bool
        """
        return bool(self._reverse)

    def _setReverse(self, value):
        """Setter function for the reverse property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            oldReverse = self._reverse
            self._reverse = bool(value)
            if self._reverse != oldReverse:
                if not self._reverse:
                    self.origin += QtCore.QPointF(-10, 0)
                    self.graphicsItem.setRotation(0)
                else:
                    self.origin += QtCore.QPointF(10, 0)
                    self.graphicsItem.setRotation(180)
                self.updateGraphics()

    reverse = property(_getReverse, _setReverse)

    def _getBerthItem(self):
        """Returns the berth graphics item."""
        return self._gi[SignalItem.BERTH_GRAPHIC_ITEM]

    berthItem = property(_getBerthItem)

    def _getSignalType(self):
        """Returns the signal type of this SignalItem."""
        return self._signalType

    signalType = property(_getSignalType)

    def _getSignalTypeStr(self):
        """Returns the signal type name of this SignalItem."""
        return self._signalType.name

    def _setSignalTypeStr(self, value):
        """Setter function for the signalType property."""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            signalTypes = self.simulation.signalLibrary.signalTypes
            self._signalType = signalTypes.get(
                value, signalTypes["UK_3_ASPECTS"]
            )
            self.updateSignalParams()
            self.updateSignalState()

    signalTypeStr = property(_getSignalTypeStr, _setSignalTypeStr)

    def _getBerthOrigin(self):
        """Returns the origin of the berth graphics item as a QPointF."""
        return self._berthOrigin

    def _setBerthOrigin(self, value):
        """Setter function for the berthOrigin property."""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self._berthOrigin = value
            self._gi[SignalItem.BERTH_GRAPHIC_ITEM].setPos(value)

    berthOrigin = property(_getBerthOrigin, _setBerthOrigin)
    berthOriginStr = property(abstract.qPointFStrizer("berthOrigin"),
                              abstract.qPointFDestrizer("berthOrigin"))

    @property
    def berthRect(self):
        """Returns the boundingRect of the berth graphics items."""
        return self._berthRect

    @property
    def toolTipText(self):
        """Returns the string to show on the tool tip"""
        return self.tr("Signal: %s") % self.name

    @property
    def highlighted(self):
        return ((self.activeRoute is not None) or
                (self.previousActiveRoute is not None) or
                (self.nextActiveRoute is not None))

    @property
    def signalHighlighted(self):
        return self.nextActiveRoute is not None

    def _getNextActiveRoute(self):
        """Returns the active route starting from this signal if it exists.
        """
        return self._nextActiveRoute

    def _setNextActiveRoute(self, route):
        """Sets the nextActiveRoute information."""
        self._nextActiveRoute = route
        self.updateSignalState()

    nextActiveRoute = property(_getNextActiveRoute, _setNextActiveRoute)

    def resetNextActiveRoute(self, route=None):
        """Resets the nextActiveRoute information. If route is not None, do
        this only if the nextActiveRoute is equal to route."""
        if (route is None or
                (self.nextActiveRoute is not None and
                 self.nextActiveRoute == route)):
            self._nextActiveRoute = None
            self.updateSignalState()

    def _getPreviousActiveRoute(self):
        """Returns the active route ending at this signal if it exists."""
        return self._previousActiveRoute

    def _setPreviousActiveRoute(self, route):
        """Sets the previousActiveRoute information."""
        self._previousActiveRoute = route
        self.updateSignalState()

    previousActiveRoute = property(_getPreviousActiveRoute,
                                   _setPreviousActiveRoute)

    def resetPreviousActiveRoute(self, route=None):
        """Reset the previousActiveRoute information. If route is not None, do
        this only if the previousActiveRoute is equal to route."""
        if (route is None or
                (self.previousActiveRoute is not None and
                 self.previousActiveRoute == route)):
            self._previousActiveRoute = None
            self.updateSignalState()

    def _getTrainId(self):
        """Returns the train internal Id."""
        return self._trainId

    def _setTrainId(self, code):
        """Sets the trainId of this signal to the given Id."""
        self._trainId = code
        self.updateGraphics()

    trainId = property(_getTrainId, _setTrainId)

    def resetTrainId(self):
        """Resets the trainId of this signal."""
        self._trainId = None
        self.updateGraphics()

    def _getActiveAspect(self):
        """Returns the current aspect of the signal."""
        return self._activeAspect

    activeAspect = property(_getActiveAspect)

    @property
    def trainServiceCode(self):
        """Returns the trainServiceCode of this signal. This is for display
        only."""
        if self._trainId is not None:
            return self.simulation.trains[int(self._trainId)].serviceCode
        else:
            return ""

    # ## Methods #########################################################

    def getNextSignal(self):
        """Helper function that returns the next signal of SignalItem.

        If a route starts from this signal, the next signal is the end signal
        of this route. Otherwise, it is the next signal found on the line."""
        if self.nextActiveRoute is not None:
            return self.nextActiveRoute.endSignal

        cur = self.getFollowingItem(self.previousItem)
        prev = self
        while cur:
            if isinstance(cur, SignalItem):
                if prev == cur.previousItem:
                    return cur
            elif isinstance(cur, enditem.EndItem):
                return None
            oldPrev = prev
            prev = cur
            cur = cur.getFollowingItem(oldPrev)
        return None

    def setBerthRect(self):
        """Sets the berth graphics item boundingRect."""
        font = QtGui.QFont("Courier New")
        font.setPixelSize(11)
        rect = QtGui.QFontMetricsF(font).boundingRect("XXXXX")
        self._berthRect = rect

    def isOnPosition(self, p):
        """ Checks that the signalItem is on the position p,
        i.e. the trackItem and direction are the same
        :param p: the position
        :return True if the signalItem is on position p"""
        if p.trackItem == self and p.previousTI == self.previousItem:
            return True
        else:
            return False

    def trainsAhead(self):
        """ Returns true if there is a train ahead of this signalItem and
        before the end of the next active route or the next signal if no route
        is set."""
        return False

    @QtCore.pyqtSlot()
    def unselect(self):
        """Unselect the signal."""
        self.selected = False

    def updateSignalParams(self):
        """Updates signal custom parameters according to the SignalType."""
        self.signalType.updateParams(self)

    @QtCore.pyqtSlot()
    def updateBlink(self):
        self.lightOn = not self.lightOn
        self.updateGraphics()

    @QtCore.pyqtSlot()
    def updateSignalState(self):
        """Update the signal current aspect."""
        self.updateGraphics()

    def setupTriggers(self):
        """Create the triggers necessary for this Item."""
        self.updateSignalState()

    # ## Graphics Methods ################################################

    def graphicsMousePressEvent(self, e, itemId):
        """Reimplemented from TrackItem.graphicsMousePressEvent to handle the
        mousePressEvent of the owned TrackGraphicsItem.
        It processes mouse clicks on the signal and emits the signals
        signalSelected, trainSelected, or signalUnselected depending on the
        case."""
        super().graphicsMousePressEvent(e, itemId)
        if e.button() == Qt.LeftButton:
            if itemId == SignalItem.SIGNAL_GRAPHIC_ITEM:
                if self.simulation.context != utils.Context.EDITOR_SCENERY:
                    self.selected = True
                persistent = (e.modifiers() == Qt.ShiftModifier)
                force = (e.modifiers() == Qt.AltModifier | Qt.ControlModifier)
                self.signalSelected.emit(self.tiId, persistent, force)
            elif itemId == SignalItem.BERTH_GRAPHIC_ITEM:
                if self.trainId is not None:
                    self.trainSelected.emit(self.trainId)
        elif e.button() == Qt.RightButton:
            if self.simulation.context == utils.Context.EDITOR_SCENERY:
                self.reverse = not self.reverse
            if itemId == SignalItem.SIGNAL_GRAPHIC_ITEM:
                # The signal itself is right-clicked
                if self.simulation.context != utils.Context.EDITOR_SCENERY:
                    self.selected = False
                self.signalUnselected.emit(self.tiId)
            elif itemId == SignalItem.BERTH_GRAPHIC_ITEM:
                # The train code is right-clicked
                if self._trainId is not None:
                    train = self.simulation.trains[int(self._trainId)]
                    if train is not None:
                        train.showTrainActionsMenu(
                            self.simulation.simulationWindow.view, e.screenPos()
                        )
        self.updateGraphics()

    def graphicsBoundingRect(self, itemId):
        """Reimplemented from TrackItem.graphicsBoundingRect to return the
        bounding rectangle of the owned TrackGraphicsItem."""
        if itemId == SignalItem.SIGNAL_GRAPHIC_ITEM:
            return self.activeAspect.boundingRect()
        elif itemId == SignalItem.BERTH_GRAPHIC_ITEM:
            rect = copy.copy(self.berthRect)
            if self.simulation.context == utils.Context.EDITOR_SCENERY:
                rect.adjust(-5, -5, 5, 5)
            return rect

    def graphicsPaint(self, p, options, itemId, widget=0):
        """ Reimplemented from TrackItem.graphicsPaint to
        draw the signal on the owned TrackGraphicsItem"""
        super().graphicsPaint(p, options, itemId, widget)
        isGame = (self.simulation.context == utils.Context.GAME)
        isEditorScenery = \
            (self.simulation.context == utils.Context.EDITOR_SCENERY)
        linePen = self.getPen()
        shapePen = self.getPen()
        shapePen.setColor(Qt.white)
        shapePen.setWidth(0)
        if itemId == SignalItem.SIGNAL_GRAPHIC_ITEM:
            if self.trainPresent():
                linePen.setColor(Qt.red)
            if self.selected:
                linePen.setColor(Qt.cyan)
            if self.signalHighlighted:
                shapePen.setColor(Qt.white)
            else:
                shapePen.setColor(Qt.darkGray)

            persistent = (self.nextActiveRoute is not None and
                          self.nextActiveRoute.persistent)
            self.activeAspect.drawAspect(p, linePen, shapePen, persistent, self.lightOn)

            # Draw the connection rects
            if isEditorScenery:
                self.drawConnectionRect(p, QtCore.QPointF(0, 0))
                self.drawConnectionRect(p, QtCore.QPointF(10, 0))

        elif itemId == SignalItem.BERTH_GRAPHIC_ITEM:
            # Berth
            if (isGame and self.trainId is not None) or isEditorScenery:
                shapePen.setColor(Qt.black)
                brush = QtGui.QBrush(Qt.black)
                p.setPen(shapePen)
                p.setBrush(brush)
                p.drawRect(self.berthRect)

                shapePen.setColor(Qt.white)
                p.setPen(shapePen)
                font = QtGui.QFont("Courier new")
                font.setPixelSize(11)
                p.setFont(font)
                if self.simulation.context == utils.Context.GAME:
                    text = self.trainServiceCode or "*****"
                else:
                    text = "XXXXX"
                p.drawText(QtCore.QPointF(0, 0), text.rjust(5))

                # Draw connection rects
                if isEditorScenery:
                    self.drawConnectionRect(p, QtCore.QPointF(0, 0))

    def graphicsMouseMoveEvent(self, event, itemId=0):
        """This function is called by the owned TrackGraphicsItem to handle
        its mouseMoveEvent. The implementation in the base class TrackItem
        begins a drag operation."""
        super().graphicsMouseMoveEvent(event, itemId)
        if itemId == SignalItem.BERTH_GRAPHIC_ITEM:
            if event.buttons() == Qt.LeftButton and \
                    self.simulation.context == utils.Context.EDITOR_SCENERY:
                if QtCore.QLineF(
                        event.scenePos(),
                        event.buttonDownScenePos(Qt.LeftButton)).length() < 3.0:
                    return
                drag = QtGui.QDrag(event.widget())
                mime = QtCore.QMimeData()
                pos = \
                    event.buttonDownScenePos(Qt.LeftButton) - self.berthOrigin
                mime.setText(type(self).__name__ + "#" +
                             str(self.tiId) + "#" +
                             str(pos.x()) + "#" +
                             str(pos.y()) + "#" +
                             "berthOrigin")
                drag.setMimeData(mime)
                drag.exec_()


class SignalState:
    """A SignalState is an aspect of a signal with a set of conditions to
    display this aspect."""

    def __init__(self, parameters):
        """Constructor for the SignalState class."""
        self.aspect = None
        self.parameters = parameters
        self.conditions = parameters["conditions"]

    def initialize(self, signalLib):
        """Initializes the SignalState once we know the SignalState it belongs
        to."""
        if not self.parameters:
            raise Exception("Internal error: SignalState already initialized")
        params = self.parameters
        self.aspect = signalLib.signalAspects[params["aspectName"]]
        self.parameters = None

    def for_json(self):
        """Dumps this SignalState to JSON."""
        return {
            "__type__": "SignalState",
            "aspectName": self.aspect.name,
            "conditions": self.conditions
        }

    def conditionsMet(self, signalItem, params=None):
        """Returns True if all conditions of this SignalState are met (or if
        there is no conditions) on the given signalItem instance."""
        if params is None:
            params = {}

        applicableSolvers = {k: v for (k, v) in SignalLibrary.solvers.items() if
                             k in self.conditions.keys()}
        for conditionName in self.conditions.keys():
            parameters = copy.copy(self.conditions[conditionName])
            conditions = params.get(conditionName, {})
            parameters.extend(conditions.get(self.aspect.name, []))
            if not applicableSolvers[conditionName](signalItem, parameters):
                return False
        return True


class SignalType:
    """A ``SignalType`` describes a type of signals which can have different
    aspects and the logic for displaying aspects."""

    def __init__(self, parameters):
        """
        :param dict parameters: dict with the data of the signal type
        """
        self.name = parameters["name"]
        self.states = []
        for ssDict in parameters["states"]:
            ss = SignalState(ssDict)
            self.states.append(ss)

    def initialize(self, signalLib):
        """Initializes this SignalType once
        the :class:`~ts2.scenery.signals.signalitem.SignalLibrary` is loaded.
        """
        for state in self.states:
            state.initialize(signalLib)

    def for_json(self):
        """Dumps this signalType to JSON."""
        return {
            "__type__": "SignalType",
            "states": self.states
        }

    def getDefaultAspect(self):
        """
        :return: The default aspect for this
                 :class:`~ts2.scenery.signals.signalitem.SignalType`.
        :rtype: :class:`~ts2.scenery.signals.signalitem.SignalState`
        """
        return self.states[-1].aspect

    def getCustomParams(self, signalItem):
        """
        :param signalItem: A :class:`~ts2.scenery.signals.signalitem.SignalItem`
               instance
        :return: The custom parameters of
                 :class:`~ts2.scenery.signals.signalitem.SignalItem`.
                 The params dict has keys which are condition names and values
                 which are dict with signal aspect name as keys and a list of
                 parameters as values.
        :rtype: dict
        """
        params = {}
        conditionNames = {c for state in self.states for c in state.conditions}
        applicableUpdaters = [v for k, v in SignalLibrary.updaters.items()
                              if k in conditionNames]
        for updater in applicableUpdaters:
            params = updater(signalItem, params)
        return params

    def updateParams(self, signalItem):
        """Updates all user parameters of signalItem according to this
        SignalType."""
        params = self.getCustomParams(signalItem)
        allProperties = [p.name
                         for p in SignalLibrary.tiProperties.values()]
        for prop in allProperties:
            setattr(signalItem, prop, {})

        # Update properties from params dict
        for k, v in params.items():
            propName = SignalLibrary.tiProperties[k].name
            setattr(signalItem, propName, str(v))

    def getAspect(self, signalItem):
        """Returns the aspect that must be active in the context of signalItem.
        """
        for state in self.states:
            params = self.getCustomParams(signalItem)
            if state.conditionsMet(signalItem, params):
                return state.aspect
        else:
            return self.getDefaultAspect()


class SignalLibrary:
    """A SignalLibrary holds the informations about the signal types and signal
    aspects available in the simulation.

    At runtime, each simulation has SignalLibrary instance which is filled with:
    - The built-in UK_3_ASPECTS  and BUFFER signal types and their aspects
    - The signal types defined in tsl files in the data directory
    - The signal types defined in the simulation itself."""

    def __init__(self, parameters):
        """Constructor for the SignalLibrary class."""
        self.signalAspects = {}
        self.signalTypes = {}
        signalAspects = parameters["signalAspects"]
        for name, saDict in signalAspects.items():
            saDict["name"] = name
            sa = signalaspect.SignalAspect(saDict)
            self.signalAspects[name] = sa
        signalTypes = parameters["signalTypes"]
        for name, stDict in signalTypes.items():
            stDict["name"] = name
            st = SignalType(stDict)
            self.signalTypes[name] = st

    def initialize(self):
        """Initializes the SignalLibrary once it is totally loaded."""
        for st in self.signalTypes.values():
            st.initialize(self)

    solvers = {}
    tiProperties = {}
    updaters = {}
    triggers = {}

    def for_json(self):
        """Dumps this SignalLibrary to JSON."""
        return {
            "__type__": "SignalLibrary",
            "signalAspects": self.signalAspects,
            "signalTypes": self.signalTypes
        }

    def filtered(self, signalTypes):
        """Returns a new SignalLibrary with only the given signalTypes.
        It automatically gets the needed signal aspects."""
        res = copy.deepcopy(self)
        aspects = []
        for name, st in self.signalTypes.items():
            if st in signalTypes:
                aspects.extend([s.aspect for s in st.states])
            else:
                del res.signalTypes[name]
        aspects = set(aspects)
        for name, asp in self.signalAspects.items():
            if asp not in aspects:
                del res.signalAspects[name]
        return res

    @staticmethod
    def update(libDict, other):
        """Updates this SignalLibrary dict by adding signal aspects and
        signal types from the other SignalLibrary. If signal aspects or signal
        types of the same name exists in both SignalLibrary instance, the data
        in the other SignalLibray will overwrite the data of this SignalLibrary.
        """
        libDict["signalAspects"].update(other["signalAspects"])
        libDict["signalTypes"].update(other["signalTypes"])

    @staticmethod
    def createSignalLibrary():
        """Returns a SignalLibrary dict with the builtin signal types and those
        defined in tsl files in the data directory."""
        builtinLibraryDict = json.loads(BUILTIN_SIGNAL_LIBRARY, encoding="utf-8")
        # General data directory
        tslGenFiles = [os.path.join("data", f) for f in os.listdir("data")
                       if f.endswith('.tsl')]
        # User data directory
        tslUserFiles = [os.path.join(utils.settings.userDataDir, f)
                        for f in os.listdir(utils.settings.userDataDir)
                        if f.endswith('.tsl')]

        tslFiles = list(set(tslGenFiles + tslUserFiles))
        tslFiles.sort()
        for tslFile in tslFiles:
            with open(tslFile) as fileStream:
                sl = json.load(fileStream, encoding="utf-8")
                SignalLibrary.update(builtinLibraryDict, sl)
        return builtinLibraryDict


signalLibraryDict = SignalLibrary.createSignalLibrary()
signalLibrary = SignalLibrary(signalLibraryDict)


def condition(cls):
    """Decorator to register a class as a condition.

    Conditions are classes which include:
    - A 'code' class attribute
    - A 'solver' function with a signalItem and a params list as parameters. The
    solver function must return True if the signalItem currently meets the
    condition(s) defined by the condition class.
    - A 'tiProperty' class attribute being the TIProperty of custom parameters
    associated to this condition. The TIProperty name must not finish by 'Str'.
    - An 'updater' function which takes a signalItem and a params dict as
    parameters. The params dict has keys which are condition codes and values
    which are dict with signal aspect name as keys and a list of parameters as
    values. The updater function must update this params dict according to the
    signal item.
    - A 'trigger' function which sets up triggers as Qt signals/slot
    connections between other objects and this signal.
    """
    SignalLibrary.solvers[cls.code] = cls.solver

    if hasattr(cls, 'tiProperty'):

        propName = cls.tiProperty.name

        def _propertyGetter(self):
            return getattr(self, "_" + propName)

        def _propertyStrGetter(self):
            return str(dict(getattr(self, str("_" + propName))))

        def _propertyStrSetter(self, value):
            if self.simulation.context == utils.Context.EDITOR_SCENERY:
                try:
                    value = collections.OrderedDict(eval(str(value)))
                except (ValueError, SyntaxError, NameError):
                    value = self.signalType.getCustomParams(self).get(cls.code)
                if isinstance(value, dict):
                    setattr(self, "_" + propName, value)
                else:
                    setattr(self, "_" + propName, collections.OrderedDict())

        cls.tiProperty.name += "Str"
        SignalLibrary.tiProperties[cls.code] = cls.tiProperty
        setattr(SignalItem,
                propName,
                property(_propertyGetter))
        setattr(SignalItem,
                propName + "Str",
                property(_propertyStrGetter, _propertyStrSetter))

    if hasattr(cls, 'updater'):
        SignalLibrary.updaters[cls.code] = cls.updater

    if hasattr(cls, 'trigger'):
        SignalLibrary.triggers[cls.code] = cls.trigger

    return cls


@condition
class NextActiveRouteCondition:
    code = "NEXT_ROUTE_ACTIVE"

    @staticmethod
    def solver(signalItem, params=None):
        """This solver returns True if the next route of the signal is active.
        """
        return bool(signalItem.nextActiveRoute)


@condition
class PreviousActiveRouteCondition:
    code = "PREVIOUS_ROUTE_ACTIVE"

    @staticmethod
    def solver(signalItem, params=None):
        """This solver returns True if a route ending at this signal is active.
        """
        return bool(signalItem.previousActiveRoute)


@condition
class NextActiveRouteCondition:
    code = "ROUTE_SET_ACROSS"

    @staticmethod
    def solver(signalItem, params=None):
        """This solver returns True if a route is set across this signal in the
        same direction (but not starting or ending at this signal).
        """
        if signalItem.activeRoute:
            for pos in signalItem.activeRoute.positions[1:-1]:
                if signalItem.isOnPosition(pos):
                    return True
        return False


@condition
class TrainNotPresentOnNextRouteCondition:
    code = "TRAIN_NOT_PRESENT_ON_NEXT_ROUTE"

    @staticmethod
    def solver(signalItem, params=None):
        """This solver returns True if no route is active starting from this
        signal or if there is no train on any items of the active route starting
        from this signal."""
        return not signalItem.trainsAhead()


@condition
class TrainNotPresentOnItems:
    code = "TRAIN_NOT_PRESENT_ON_ITEMS"
    tiProperty = helper.TIProperty(
        "trainNotPresentParams", translate("SignalItem", "No train params")
    )

    @staticmethod
    def solver(signalItem, params=None):
        """This solver returns True if no train is found on any trackItems given
        in the params list. params must be a list of trackItem IDs."""
        if params is None:
            params = []
        simulation = signalItem.simulation
        trackItems = [simulation.trackItem(tiId) for tiId in params]
        return not any([ti.trainPresent() for ti in trackItems])

    @staticmethod
    def updater(signalItem, params):
        code = TrainNotPresentOnItems.code
        tnp = signalItem.trainNotPresentParams
        aspectNames = [st.aspect.name for st in signalItem.signalType.states
                       if code in st.conditions.keys()]
        params[code] = {
            aspectName: tnp.get(aspectName, []) for aspectName in aspectNames
        }
        return params

    @staticmethod
    def trigger(signalItem):
        tiIds = []
        for tnp in signalItem.trainNotPresentParams.values():
            tiIds.extend(tnp)
        for tiId in tiIds:
            try:
                signalItem.simulation.trackItems[tiId].trainEntersItem.connect(
                    signalItem.updateSignalState
                )
                signalItem.simulation.trackItems[tiId].trainLeavesItem.connect(
                    signalItem.updateSignalState
                )
            except KeyError as err:
                raise utils.FormatException(
                    translate("TrainNotPresentOnItems",
                              "Error in simulation definition: SignalItem %s "
                              "references unknown track item %s") %
                    (signalItem.tiId, str(err))
                )


@condition
class TrainPresentOnItems:
    code = "TRAIN_PRESENT_ON_ITEMS"
    tiProperty = helper.TIProperty(
        "trainPresentParams", translate("SignalItem", "Train Present Params")
    )

    @staticmethod
    def solver(signalItem, params=None):
        """This solver returns True if a train is found on all trackItems given
        in the params list. params must be a list of trackItem IDs."""
        if params is None:
            params = []
        simulation = signalItem.simulation
        trackItems = [simulation.trackItem(tiId) for tiId in params]
        return all([ti.trainPresent() for ti in trackItems])

    @staticmethod
    def updater(signalItem, params):
        code = TrainPresentOnItems.code
        tp = signalItem.trainPresentParams
        aspectNames = [st.aspect.name for st in signalItem.signalType.states
                       if code in st.conditions.keys()]
        params[code] = {
            aspectName: tp.get(aspectName, []) for aspectName in aspectNames
        }
        return params

    @staticmethod
    def trigger(signalItem):
        tiIds = []
        for tp in signalItem.trainPresentParams.values():
            tiIds.extend(tp)
        for tiId in tiIds:
            try:
                signalItem.simulation.trackItems[tiId].trainEntersItem.connect(
                    signalItem.updateSignalState
                )
                signalItem.simulation.trackItems[tiId].trainLeavesItem.connect(
                    signalItem.updateSignalState
                )
            except KeyError as err:
                raise utils.FormatException(
                    translate("TrainPresentOnItems",
                              "Error in simulation definition: SignalItem %s "
                              "references unknown track item %s") %
                    (signalItem.tiId, str(err))
                )


@condition
class RouteSetCondition:
    code = "ROUTES_SET"
    tiProperty = helper.TIProperty(
        "routesSetParams", translate("SignalItem", "Route set params")
    )

    @staticmethod
    def solver(signalItem, params=None):
        """This solver returns True if at least one of the routes given in the
        params list is active. These routes don't have to start at this signal.
        params must be a list of route numbers."""
        if params is None:
            params = []
        simulation = signalItem.simulation
        routes = [simulation.routes[routeNum] for routeNum in params
                  if routeNum in simulation.routes]
        return any([(r.getRouteState() != 0) for r in routes])

    @staticmethod
    def updater(signalItem, params):
        code = RouteSetCondition.code
        rs = signalItem.routesSetParams
        aspectNames = [st.aspect.name for st in signalItem.signalType.states
                       if code in st.conditions.keys()]
        params[code] = {
            aspectName: rs.get(aspectName, []) for aspectName in aspectNames
        }
        return params

    @staticmethod
    def trigger(signalItem):
        routeNums = []
        for rs in signalItem.routesSetParams.values():
            routeNums.extend(rs)
        for routeNum in routeNums:
            try:
                signalItem.simulation.routes[routeNum].routeSelected.connect(
                    signalItem.updateSignalState
                )
                signalItem.simulation.routes[routeNum].routeUnselected.connect(
                    signalItem.updateSignalState
                )
            except KeyError as err:
                raise utils.FormatException(
                    translate("RouteSetCondition",
                              "Error in simulation definition: SignalItem %s "
                              "references unknown route %s") %
                    (signalItem.tiId, str(err))
                )


@condition
class NextSignalAspectsCondition:
    code = "NEXT_SIGNAL_ASPECTS"

    @staticmethod
    def solver(signalItem, params=None):
        """This solver returns True if a route starting from this signal is
        active and the ending signal of this route is showing one of the aspects
        given in params. params must be a list of signal aspect names."""
        if params is None:
            params = []

        nextSignal = signalItem.getNextSignal()
        if nextSignal:
            aspectName = nextSignal.activeAspect.name
            if aspectName in params:
                return True
        return False

    @staticmethod
    def trigger(signalItem):
        """Trigger to connect to next signal (used only when no route)."""
        nextItem = signalItem.getNextSignal()
        if nextItem:
            nextItem.aspectChanged.connect(signalItem.updateSignalState)
            signalItem.updateSignalState()
