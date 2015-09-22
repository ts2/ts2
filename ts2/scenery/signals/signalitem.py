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

import copy
import os
import collections
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
            "outerColors": [0, 0, 0, 0, 0, 0],
            "shapes": [0, 0, 0, 0, 0, 0],
            "shapesColors": [0, 0, 0, 0, 0, 0],
            "actions": [[1, 0]]
        },
        "UK_DANGER": {
            "__type__": "SignalAspect",
            "lineStyle": 0,
            "outerShapes": [0, 0, 0, 0, 0, 0],
            "outerColors": [0, 0, 0, 0, 0, 0],
            "shapes": [1, 0, 0, 0, 0, 0],
            "shapesColors": ["#FF0000", 0, 0, 0, 0, 0],
            "actions": [[1, 0]]
        },
        "UK_CAUTION": {
            "__type__": "SignalAspect",
            "lineStyle": 0,
            "outerShapes": [0, 0, 0, 0, 0, 0],
            "outerColors": [0, 0, 0, 0, 0, 0],
            "shapes": [1, 0, 0, 0, 0, 0],
            "shapesColors": ["#FFFF00", 0, 0, 0, 0, 0],
            "actions": [[2, 0]]
        },
        "UK_CLEAR": {
            "__type__": "SignalAspect",
            "lineStyle": 0,
            "outerShapes": [0, 0, 0, 0, 0, 0],
            "outerColors": [0, 0, 0, 0, 0, 0],
            "shapes": [1, 0, 0, 0, 0, 0],
            "shapesColors": ["#00FF00", 0, 0, 0, 0, 0],
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


def json_hook(dct):
    """Hook method for json loading of signal library."""
    if not dct.get('__type__'):
        return dct
    elif dct['__type__'] == "SignalLibrary":
        return SignalLibrary(parameters=dct)
    elif dct['__type__'] == "SignalType":
        return SignalType(parameters=dct)
    elif dct['__type__'] == "SignalState":
        return SignalState(parameters=dct)
    elif dct['__type__'] == "SignalAspect":
        return signalaspect.SignalAspect(parameters=dct)


class ConditionCode:
    """This class holds the possible conditions to display a Signal aspect."""
    # Without parameters
    NEXT_ROUTE_ACTIVE = 1
    PREVIOUS_ROUTE_ACTIVE = 2
    TRAIN_NOT_PRESENT_ON_NEXT_ROUTE = 4
    # With parameters
    TRAIN_NOT_PRESENT_ON_ITEMS = 1024   # No train on any item in list
    ROUTES_SET = 2048                   # At least one route set in list
    NEXT_SIGNAL_ASPECTS = 4096          # Aspect in list


class SignalItem(abstract.TrackItem):
    """ @brief Logical item for signals
    This class holds the logics of a signal defined by its SignalType.
    A signal is the item from and to which routes are created."""

    SIGNAL_GRAPHIC_ITEM = 0
    BERTH_GRAPHIC_ITEM = 1

    def __init__(self, parameters):
        """ Constructor for the SignalItem class."""
        super().__init__(parameters)
        reverse = bool(parameters.get("reverse", 0))
        self._signalType = None
        for customProperty in signalLibrary.tiProperties.values():
            # Initialize backend vars for custom properties
            propName = "_" + customProperty.name[:-3]
            setattr(self, propName,
                    eval(str(parameters.get(customProperty.name[:-3], {}))))
        try:
            xb = float(parameters.get("xn", ""))
        except ValueError:
            xb = self.origin.x() - 40
        try:
            yb = float(parameters.get("yn", ""))
        except ValueError:
            yb = self.origin.y() + 5
        self._berthOrigin = QtCore.QPointF(xb, yb)
        self._berthRect = None
        self.setBerthRect()
        self._activeAspect = None
        self._reverse = reverse
        self._previousActiveRoute = None
        self._nextActiveRoute = None
        self._trainId = None
        self.defaultZValue = 50
        sgi = helper.TrackGraphicsItem(self, SignalItem.SIGNAL_GRAPHIC_ITEM)
        sgi.setPos(self.origin)
        sgi.setCursor(Qt.PointingHandCursor)
        sgi.setToolTip(self.toolTipText)
        sgi.setZValue(self.defaultZValue)
        if reverse:
            sgi.setRotation(180)
        self._gi[SignalItem.SIGNAL_GRAPHIC_ITEM] = sgi
        bgi = helper.TrackGraphicsItem(self, SignalItem.BERTH_GRAPHIC_ITEM)
        bgi.setPos(self._berthOrigin)
        bgi.setCursor(Qt.PointingHandCursor)
        bgi.setZValue(self.defaultZValue)
        self._gi[SignalItem.BERTH_GRAPHIC_ITEM] = bgi

    def initialize(self, simulation):
        """Initialize the signal item once everything is loaded."""
        params = self._parameters
        if not params:
            raise Exception("Internal error: TrackItem %s already initialized"
                            % self.tiId)
        self._signalType = simulation.signalLibrary.signalTypes[
            params['signalType']
        ]
        self._activeAspect = self._signalType.getDefaultAspect()
        if simulation.context == utils.Context.GAME:
            self.signalSelected.connect(simulation.activateRoute)
            self.signalUnselected.connect(simulation.desactivateRoute)
        else:
            self.signalSelected.connect(simulation.prepareRoute)
            self.signalUnselected.connect(simulation.deselectRoute)
        self.trainSelected.connect(simulation.trainSelected)
        super().initialize(simulation)

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
        signalCustomProperties = list(signalLibrary.tiProperties.values())
        for customProp in signalCustomProperties:
            jsonData[customProp.name[:-3]] = getattr(self, customProp.name)
        jsonData.update({
            "reverse": int(self.reverse),
            "signalType": self.signalTypeStr,
            "xn": self.berthOrigin.x(),
            "yn": self.berthOrigin.y()
        })
        return jsonData

    signalSelected = QtCore.pyqtSignal(int, bool, bool)
    signalUnselected = QtCore.pyqtSignal(int)
    trainSelected = QtCore.pyqtSignal(int)
    aspectChanged = QtCore.pyqtSignal()

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
        """Returns True if the SignalItem is from right to left, false
        otherwise"""
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
            return self.simulation.trains[self._trainId].serviceCode
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
        if self.nextActiveRoute is not None:
            for pos in self.nextActiveRoute.positions:
                if pos.trackItem.trainPresent():
                    return True
        else:
            cur = self.getFollowingItem(self.previousItem)
            prev = self
            while cur:
                if cur.trainPresent():
                    return True
                if isinstance(cur, SignalItem):
                    if prev == cur.previousItem:
                        break
                elif isinstance(cur, enditem.EndItem):
                    break
                oldPrev = prev
                prev = cur
                cur = cur.getFollowingItem(oldPrev)
        return False

    def trainHeadActions(self, trainId):
        """Actions to be performed when the train head reaches this signal.

        Pushes the train code to the next signal."""
        if self.trainId == trainId:
            # Only push train code if this signal has the descriptor
            # Typically to prevent opposite signals to get it
            nextSignal = self.getNextSignal()
            if nextSignal:
                nextSignal.trainId = trainId
            self.resetTrainId()
        super().trainHeadActions(trainId)

    def trainTailActions(self, trainId):
        """Actions that are to be done when a train tail reaches this signal.
        It deals with desactivating this signal."""
        if (self.activeRoute is not None and
                (self.activeRoutePreviousItem != self.previousItem or
                 (self.activeRoute.beginSignal != self and
                  self.activeRoute.endSignal != self))):
            # The line is highlighted by an opposite direction route or this
            # signal is not the starting/ending signal of this route.
            # => base TrackItem actions
            super().trainTailActions(trainId)
        else:
            # For cleaning purposes: activeRoute not used in this direction
            self.resetActiveRoute()

            if (self.previousActiveRoute is not None) and \
               (not self.previousActiveRoute.persistent):
                beginSignalNextRoute = \
                    self.previousActiveRoute.beginSignal.nextActiveRoute
                if beginSignalNextRoute is None or \
                   beginSignalNextRoute != self.previousActiveRoute:
                    # Only reset previous route if the user did not
                    # reactivate it in the meantime
                    self.previousItem.resetActiveRoute()
                    self.resetPreviousActiveRoute()
            if (self.nextActiveRoute is not None) and \
               (not self.nextActiveRoute.persistent):
                self.resetNextActiveRoute()
            self.updateSignalState()

    @QtCore.pyqtSlot()
    def unselect(self):
        """Unselect the signal."""
        self.selected = False

    def setActiveRoute(self, r, previous):
        """Overridden here to update signal state."""
        super().setActiveRoute(r, previous)
        self.updateSignalState()

    def resetActiveRoute(self):
        """Overridden here to update signal state."""
        super().resetActiveRoute()
        self.updateSignalState()

    def updateSignalParams(self):
        """Updates signal custom parameters according to the SignalType."""
        self.signalType.updateParams(self)

    @QtCore.pyqtSlot()
    def updateSignalState(self):
        """Update the signal current aspect."""
        oldAspect = self.activeAspect
        self._activeAspect = self.signalType.getAspect(self)

        if self.activeAspect != oldAspect:
            self.aspectChanged.emit()

        if self.previousActiveRoute is not None:
            self.previousActiveRoute.beginSignal.updateSignalState()

        self.updateGraphics()

    def setupTriggers(self):
        """Create the triggers necessary for this Item."""
        for trigger in self.simulation.signalLibrary.triggers.values():
            trigger(self)
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
                    train = self.simulation.trains[self._trainId]
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
            self.activeAspect.drawAspect(p, linePen, shapePen, persistent)

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
                    text = self.trainServiceCode
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
    """A SignalType describes a type of signals which can have different
    aspects and the logic for displaying aspects."""

    def __init__(self, parameters):
        """Constructor for the SignalType class."""
        self.name = "__UNNAMED__"
        self.states = parameters["states"]

    def initialize(self, signalLib):
        """Initializes this SignalType once the SignalLibrary is loaded."""
        for state in self.states:
            state.initialize(signalLib)

    def for_json(self):
        """Dumps this signalType to JSON."""
        return {
            "__type__": "SignalType",
            "states": self.states
        }

    def getDefaultAspect(self):
        """Returns the default aspect for this signal type."""
        return self.states[-1].aspect

    def getCustomParams(self, signalItem):
        """Returns a dict of the custom parameters of signalItem.
        The params dict has keys which are condition names and values which are
        dict with signal aspect name as keys and a list of parameters as values.
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
        self.signalAspects = parameters["signalAspects"]
        for name, sa in self.signalAspects.items():
            sa.name = name
        self.signalTypes = parameters["signalTypes"]
        for name, st in self.signalTypes.items():
            st.name = name

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

    def update(self, other):
        """Updates this SignalLibrary instance by adding signal aspects and
        signal types from the other SignalLibrary. If signal aspects or signal
        types of the same name exists in both SignalLibrary instance, the data
        in the other SignalLibray will overwrite the data of this SignalLibrary.
        """
        self.signalAspects.update(other.signalAspects)
        self.signalTypes.update(other.signalTypes)

    @staticmethod
    def createSignalLibrary():
        """Returns a SignalLibrary with the builtin signal types and those
        defined in tsl files in the data directory."""
        builtinLibrary = json.loads(BUILTIN_SIGNAL_LIBRARY,
                                    object_hook=json_hook, encoding="utf-8")
        tslFiles = [f for f in os.listdir("data") if f.endswith('.tsl')]
        tslFiles.sort()
        for tslFile in tslFiles:
            fileName = "data" + os.sep + tslFile
            with open(fileName) as fileStream:
                sl = json.load(fileStream, object_hook=json_hook,
                               encoding="utf-8")
                builtinLibrary.update(sl)
        builtinLibrary.initialize()
        return builtinLibrary


signalLibrary = SignalLibrary.createSignalLibrary()


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
                value = collections.OrderedDict(eval(str(value)))
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
            signalItem.simulation.trackItem(tiId).trainEntersItem.connect(
                signalItem.updateSignalState
            )
            signalItem.simulation.trackItem(tiId).trainLeavesItem.connect(
                signalItem.updateSignalState
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
            signalItem.simulation.trackItem(tiId).trainEntersItem.connect(
                signalItem.updateSignalState
            )
            signalItem.simulation.trackItem(tiId).trainLeavesItem.connect(
                signalItem.updateSignalState
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
        tiIds = []
        for rs in signalItem.routesSetParams.values():
            tiIds.extend(rs)
        for tiId in tiIds:
            signalItem.simulation.routes[tiId].routeSelected.connect(
                signalItem.updateSignalState
            )
            signalItem.simulation.routes[tiId].routeUnselected.connect(
                signalItem.updateSignalState
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
