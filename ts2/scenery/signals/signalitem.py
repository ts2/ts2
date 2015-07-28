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

from Qt import QtCore, QtGui, QtWidgets, Qt

from ts2 import utils
from ts2.scenery import abstract, helper
from ts2.scenery.signals import signaltype
from ts2.scenery.signals.signaltype import ConditionCode as stCode

translate = QtWidgets.qApp.translate


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
        self._routesSetParams = eval(str(parameters["routesSetParams"])) or {}
        self._trainNotPresentParams = \
            eval(str(parameters["trainNotPresentParams"])) or {}
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
        self._signalType = simulation.signalTypes[params['signalType']]
        self._activeAspect = self._signalType.getDefaultAspect()
        self.signalSelected.connect(simulation.activateRoute)
        self.signalUnselected.connect(simulation.desactivateRoute)
        self.trainSelected.connect(simulation.trainSelected)
        super().initialize(simulation)

    @staticmethod
    def getProperties():
        # TODO: Remove builtin reference below to allow custom signal types
        signalTypeNames = [x["name"] for x in signaltype.builtin_signal_types]
        return abstract.TrackItem.getProperties() + [
            helper.TIProperty("reverse",
                              translate("SignalItem", "Reverse")),
            helper.TIProperty("signalTypeStr",
                              translate("SignalItem", "Signal Type"),
                              False,
                              "enum",
                              signalTypeNames,
                              signalTypeNames),
            helper.TIProperty("routesSetParamsStr",
                              translate("SignalItem", "Route set params")),
            helper.TIProperty("trainNotPresentParamsStr",
                              translate("SignalItem", "No train params")),
            helper.TIProperty("berthOriginStr",
                              translate("SignalItem", "Berth Origin"))
        ]

    def for_json(self):
        """Dumps the signalItem to JSON."""
        jsonData = super().for_json()
        jsonData.update({
            "reverse": int(self.reverse),
            "signalType": self.signalTypeStr,
            "routesSetParams": str(self.routesSetParamsStr),
            "trainNotPresentParams": str(self.trainNotPresentParamsStr),
            "xn": self.berthOrigin.x(),
            "yn": self.berthOrigin.y()
        })

    signalSelected = QtCore.pyqtSignal(int, bool, bool)
    signalUnselected = QtCore.pyqtSignal(int)
    trainSelected = QtCore.pyqtSignal(int)


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
            self._signalType = self.simulation.signalTypes.get(
                value, self.simulation.signalTypes["UK_3_ASPECTS"]
            )
            self.updateSignalParams()
            self.updateSignalState()

    signalTypeStr = property(_getSignalTypeStr, _setSignalTypeStr)

    def _getRouteSetParams(self):
        """Returns the route set parameters, which is a dictionary with the
        aspect names as keys, and lists of routes as values."""
        return self._routesSetParams

    routesSetParams = property(_getRouteSetParams)

    def _getRouteSetParamsStr(self):
        """Returns the route set parameters as a string."""
        return str(self._routesSetParams)

    def _setRouteSetParamsStr(self, value):
        """Setter function for the routesSetParamsStr property."""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if value == "":
                self._routesSetParams = {}
            else:
                self._routesSetParams = eval(str(value))

    routesSetParamsStr = property(_getRouteSetParamsStr,
                                  _setRouteSetParamsStr)

    def _getTrainNotPresentParams(self):
        """Returns the train present parameters, which is a dictionary with
        the aspect names as keys, and lists of track items as values."""
        return self._trainNotPresentParams

    trainNotPresentParams = property(_getTrainNotPresentParams)

    def _getTrainNotPresentParamsStr(self):
        """Returns the train present parameters as a string."""
        return str(self._trainNotPresentParams)

    def _setTrainNotPresentParamsStr(self, value):
        """Setter function for the trainPresentParamsStr."""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if value == "":
                self._trainNotPresentParams = {}
            else:
                self._trainNotPresentParams = eval(str(value))

    trainNotPresentParamsStr = property(_getTrainNotPresentParamsStr,
                                        _setTrainNotPresentParamsStr)

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

    def setBerthRect(self):
        """Sets the berth graphics item boundingRect."""
        font = QtGui.QFont("Courier New")
        font.setPixelSize(11)
        rect = QtGui.QFontMetricsF(font).boundingRect("XXXXX")
        self._berthRect = rect

    def isOnPosition(self, p):
        """ Checks that the signalItem is on the position p,
        i.e. the trackItem and direction are the same
        @param p the position
        @return Returns true if the signalItem is on position p"""
        if p.trackItem == self and p.previousTI == self.previousItem:
            return True
        else:
            return False

    def trainsAhead(self):
        """ Returns true if there is a train ahead of this signalItem and
        before the end of the next active route. Note that this function
        returns False if no route is set from this signal."""
        if self.nextActiveRoute is not None:
            for pos in self.nextActiveRoute.positions:
                if pos.trackItem.trainPresent():
                    return True
        return False

    def trainHeadActions(self, trainId):
        """Actions to be performed when the train head reaches this signal.
        Pushes the train code to the next signal."""
        if self.nextActiveRoute is not None:
            self.nextActiveRoute.endSignal.trainId = trainId
            self.resetTrainId()
        super().trainHeadActions(trainId)

    def trainTailActions(self, trainId):
        """Actions that are to be done when a train tail reaches this signal.
        It deals with desactivating this signal."""
        if self.activeRoute is not None and \
           self.activeRoutePreviousItem != self.previousItem:
            # The line is highlighted by an opposite direction route
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
        self.updateGraphics()

    def updateSignalParams(self):
        """Updates routeSetParams and trainNotPresentParams according to the
        SignalType."""
        tnp = {}
        for sc in self.signalType.conditions:
            if sc.conditionCode & stCode.TRAIN_NOT_PRESENT_ON_ITEMS:
                tnp[sc.aspect.name] = \
                    self.trainNotPresentParams.get(sc.aspect.name, [])
        self.trainNotPresentParamsStr = str(tnp)
        rs = {}
        for sc in self.signalType.conditions:
            if sc.conditionCode & stCode.ROUTES_SET:
                rs[sc.aspect.name] = \
                    self.routesSetParams.get(sc.aspect.name, [])
        self.routesSetParamsStr = str(rs)

    @QtCore.pyqtSlot()
    def updateSignalState(self):
        """Update the signal current aspect."""
        for sc in self.signalType.conditions:
            currentSituation = 0
            if self.nextActiveRoute is not None:
                currentSituation |= stCode.NEXT_ROUTE_ACTIVE
            if self.previousActiveRoute is not None:
                currentSituation |= stCode.PREVIOUS_ROUTE_ACTIVE
            if not self.trainsAhead():
                currentSituation |= stCode.TRAIN_NOT_PRESENT_ON_NEXT_ROUTE
            if self.nextActiveRoute is not None:
                for sa in sc.params.get(stCode.NEXT_SIGNAL_ASPECTS, []):
                    if self.nextActiveRoute.endSignal.activeAspect.name == sa:
                        currentSituation |= stCode.NEXT_SIGNAL_ASPECTS
                        break
            aspectName = sc.aspect.name
            if aspectName in self.routesSetParams:
                routesSet = self.routesSetParams[aspectName]
                for rnum in routesSet:
                    if self.simulation.routes[rnum].getRouteState() != 0:
                        currentSituation |= stCode.ROUTES_SET
                        break
            if aspectName in self.trainNotPresentParams:
                trainPresent = self.trainNotPresentParams[aspectName]
                tnp = True
                for tiId in trainPresent:
                    if self.simulation.trackItems[tiId].trainPresent():
                        tnp = False
                        break
                if tnp:
                    currentSituation |= stCode.TRAIN_NOT_PRESENT_ON_ITEMS

            if currentSituation & sc.conditionCode == sc.conditionCode:
                self._activeAspect = sc.aspect
                break
        else:
            self._activeAspect = self.signalType.getDefaultAspect()

        if self.previousActiveRoute is not None:
            self.previousActiveRoute.beginSignal.updateSignalState()
        self.updateGraphics()

    def setupTriggers(self):
        """Create the triggers necessary for this Item."""
        # Add triggers to trackItems defined in trainNotPresentParams
        tiIds = []
        for tnp in self.trainNotPresentParams.values():
            tiIds.extend(tnp)
        for tiId in tiIds:
            self.simulation.trackItem(tiId).trainEntersItem.connect(
                self.updateSignalState
            )
            self.simulation.trackItem(tiId).trainLeavesItem.connect(
                self.updateSignalState
            )

        # Add triggers to routes defined in routeSetParams
        tiIds = []
        for rs in self.routesSetParams.values():
            tiIds.extend(rs)
        for tiId in tiIds:
            self.simulation.routes[tiId].routeSelected.connect(
                self.updateSignalState
            )
            self.simulation.routes[tiId].routeUnselected.connect(
                self.updateSignalState
            )

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
                if self.simulation.context == utils.Context.GAME:
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
                if self.simulation.context == utils.Context.GAME:
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
                mime.setText(self.tiType + "#" +
                             str(self.tiId) + "#" +
                             str(pos.x()) + "#" +
                             str(pos.y()) + "#" +
                             "berthOrigin")
                drag.setMimeData(mime)
                drag.exec_()
