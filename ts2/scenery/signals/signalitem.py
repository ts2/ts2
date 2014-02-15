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

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt

from ts2 import utils
from ts2.scenery import abstract, helper
from ts2.scenery.signals import signaltype

translate = QtCore.QCoreApplication.translate

class SignalItem(abstract.TrackItem):
    """ @brief Logical item for signals
    This class holds the logics of a signal defined by its SignalType.
    A signal is the item from and to which routes are created."""

    def __init__(self, simulation, parameters):
        """ Constructor for the SignalItem class."""
        super().__init__(simulation, parameters)
        reverse = parameters["reverse"]
        self.tiType = "S"
        signalTypeName = parameters["signaltype"]
        self._signalType = simulation.signalTypes[signalTypeName]
        self._routesSetParams = eval(str(parameters["routesset"]))
        self._trainPresentParams = eval(str(parameters["trainpresent"]))
        self._activeAspect = self._signalType.getDefaultAspect()
        self._reverse = reverse
        self._previousActiveRoute = None
        self._nextActiveRoute = None
        self._trainId = None
        sgi = helper.TrackGraphicsItem(self)
        sgi.setPos(self.origin)
        sgi.setCursor(Qt.PointingHandCursor)
        sgi.setToolTip(self.toolTipText)
        sgi.setZValue(50)
        if reverse:
            sgi.setRotation(180)
        self._gi = sgi
        self.simulation.registerGraphicsItem(self._gi)
        self.updateGraphics()

    properties = abstract.TrackItem.properties + [
                        helper.TIProperty("reverse", translate("SignalItem",
                                                               "Reverse")),
                        helper.TIProperty("signalTypeStr",
                                          translate("SignalItem",
                                                    "Signal Type")),
                        helper.TIProperty("routesSetParams",
                                          translate("SignalItem",
                                                    "Route set params")),
                        helper.TIProperty("trainPresentParams",
                                          translate("SignalItem",
                                                    "Train presence params"))]

    signalSelected = QtCore.pyqtSignal(int, bool, bool)
    signalUnselected = QtCore.pyqtSignal(int)
    trainSelected = QtCore.pyqtSignal(int)

    def getSaveParameters(self):
        """Returns the parameters dictionary to save this TrackItem to the
        database"""
        parameters = super().getSaveParameters()
        parameters.update({"reverse":int(self.reverse),
                           "signaltype":self.signalTypeStr,
                           "routesset":str(self.routesSetParamsStr),
                           "trainpresent":str(self.trainPresentParamsStr)})
        return parameters

    ### Properties #########################################################

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
            self._signalType = self.simulation.signalTypes.get(value,
                                  self.simulation.signalTypes["UK_3_ASPECTS"])
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
            self._routesSetParams = eval(str(value))

    routesSetParamsStr = property(_getRouteSetParamsStr,
                                  _setRouteSetParamsStr)

    def _getTrainPresentParams(self):
        """Returns the train present parameters, which is a dictionary with
        the aspect names as keys, and lists of track items as values."""
        return self._trainPresentParams

    trainPresentParams = property(_getTrainPresentParams)

    def _getTrainPresentParamsStr(self):
        """Returns the train present parameters as a string."""
        return str(self._trainPresentParams)

    def _setTrainPresentParamsStr(self, value):
        """Setter function for the trainPresentParamsStr."""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self._trainPresentParams = eval(str(value))

    trainPresentParamsStr = property(_getTrainPresentParamsStr,
                                     _setTrainPresentParamsStr)

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
        return (self.nextActiveRoute is not None)

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

    ### Methods #########################################################

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
            self.resetActiveRoute() # For cleaning purposes:
                                    # activeRoute not used in this direction
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

    @QtCore.pyqtSlot()
    def updateSignalState(self):
        """Update the signal state."""
        self._activeAspect = self.signalType.getDefaultAspect()
        self.updateGraphics()
        #if self.nextActiveRoute is None or self.trainsAhead():
            #self._signalState = SignalState.STOP
        #else:
            #if self.nextActiveRoute.endSignal.signalState == \
                                                        #SignalState.CLEAR:
                #self._signalState = SignalState.CLEAR
            #elif self.nextActiveRoute.endSignal.signalState == \
                                                        #SignalState.WARNING:
                #self._signalState = SignalState.CLEAR
            #elif self.nextActiveRoute.endSignal.signalState == \
                                                        #SignalState.STOP:
                #self._signalState = SignalState.WARNING
            #else:
                #self._signalState = SignalState.STOP
        #if self.previousActiveRoute is not None:
            #self.previousActiveRoute.beginSignal.updateSignalState()
        #self.updateGraphics()

    ### Graphics Methods ################################################

    def graphicsMousePressEvent(self, e):
        """Reimplemented from TrackItem.graphicsMousePressEvent to handle the
        mousePressEvent of the owned TrackGraphicsItem.
        It processes mouse clicks on the signal and emits the signals
        signalSelected, trainSelected, or signalUnselected depending on the
        case."""
        super().graphicsMousePressEvent(e)
        if e.button() == Qt.LeftButton:
            if self.simulation.context == utils.Context.GAME:
                self.selected = True;
            persistent = (e.modifiers() == Qt.ShiftModifier)
            force = (e.modifiers() == Qt.AltModifier|Qt.ControlModifier)
            self.signalSelected.emit(self.tiId, persistent, force);
        elif e.button() == Qt.RightButton:
            if self.simulation.context == utils.Context.EDITOR_SCENERY:
                self.reverse = not self.reverse
            elif self.simulation.context == utils.Context.GAME:
                self.selected = False
                self.signalUnselected.emit(self.tiId)
        self.updateGraphics()

    def graphicsBoundingRect(self):
        """Reimplemented from TrackItem.graphicsBoundingRect to return the
        bounding rectangle of the owned TrackGraphicsItem."""
        return self.activeAspect.boundingRect()

    def graphicsPaint(self, p, options, widget = 0):
        """ Reimplemented from TrackItem.graphicsPaint to
        draw the signal on the owned TrackGraphicsItem"""
        linePen = self.getPen()
        shapePen = self.getPen()
        shapePen.setColor(Qt.white)
        shapePen.setWidth(0)
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
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.drawConnectionRect(p, QtCore.QPointF(0, 0))
            self.drawConnectionRect(p, QtCore.QPointF(10, 0))


