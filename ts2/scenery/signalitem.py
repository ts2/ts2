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

from Qt import QtGui, QtCore, QtSql, Qt
from ts2.scenery import TrackItem, TrackGraphicsItem, TIProperty
from ts2 import routing
from ts2 import utils

tr = QtCore.QObject().tr

class SignalState:
    """This class holds the different possible states of a signal"""
    CLEAR = 0
    WARNING = 50
    STOP = 100


class SignalItem(TrackItem):
    """ @brief Logical item for signals
    This class holds the logics of a basic signal (CLEAR, WARNING, STOP).
    A signal is the item from and to which routes are created.
    Each instance owns a SignalGraphicsItem which is the graphical item drawn
    on the scene."""

    def __init__(self, simulation, parameters):
        """ Constructor for the SignalItem class."""
        super().__init__(simulation, parameters)
        reverse = parameters["reverse"]
        self._tiType = "S"
        self._selected = False
        self._reverse = reverse
        self._signalState = SignalState.STOP
        self._previousActiveRoute = None
        self._nextActiveRoute = None
        self._trainId = None
        self._signalPos = 0
        sgi = TrackGraphicsItem(self)
        sgi.setPos(self.realOrigin)
        sgi.setCursor(Qt.PointingHandCursor)
        sgi.setToolTip(self.toolTipText)
        sgi.setZValue(50)
        self._gi = sgi
        self._simulation.registerGraphicsItem(self._gi)
        self.updateGraphics()

    properties = TrackItem.properties + [TIProperty("reverse", tr("Reverse"))]

    signalSelected = QtCore.pyqtSignal(int, bool, bool)
    signalUnselected = QtCore.pyqtSignal(int)
    trainSelected = QtCore.pyqtSignal(int)

    @property
    def origin(self):
        """Returns the origin QPointF of the TrackItem. The origin is
        the right end of the track represented on the SignalItem if the
        signal is reversed, the left end otherwise"""
        return self._origin

    @origin.setter
    def origin(self, value):
        """Setter function for the origin property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            if self.reverse:
                self.realOrigin = value + QtCore.QPointF(-60,-2)
            else:
                self.realOrigin = value + QtCore.QPointF(0,-18)

    @property
    def end(self):
        """Returns the end QPointF of the TrackItem. The end is
        generally the right end of the track represented on the TrackItem"""
        if self.reverse:
            return self._origin + QtCore.QPointF(-60, 0)
        else:
            return self._origin + QtCore.QPointF(60, 0)

    @property
    def reverse(self):
        """Returns True if the SignalItem is from right to left, false
        otherwise"""
        return bool(self._reverse)

    @reverse.setter
    def reverse(self, value):
        """Setter function for the reverse property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            self._reverse = bool(value)
            if self._reverse:
                self.realOrigin += QtCore.QPointF(60, 0)
            else:
                self.realOrigin += QtCore.QPointF(-60, 0)
            self.updateGraphics()

    @property
    def toolTipText(self):
        """Returns the string to show on the tool tip"""
        return self.tr("Signal: %s") % self.name

    @property
    def highlighted(self):
        return ((self._activeRoute is not None) or \
               (self._previousActiveRoute is not None) or \
               (self._nextActiveRoute is not None))

    @property
    def signalHighlighted(self):
        return (self._nextActiveRoute is not None)


    @property
    def realOrigin(self):
        """Returns the realOrigin QPointF of the TrackItem. The realOrigin is
        the position of the top left corner of the bounding rectangle of the
        TrackItem. Reimplemented in SignalItem"""
        if self.reverse:
            return self.origin + QtCore.QPointF(-60,-2)
        else:
            return self.origin + QtCore.QPointF(0,-18)

    @realOrigin.setter
    def realOrigin(self, pos):
        """Setter function for the realOrigin property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            grid = self.simulation.grid
            if self.reverse:
                x = round((pos.x() + 60.0) / grid) * grid
                y = round((pos.y() + 2.0) / grid) * grid
            else:
                x = round((pos.x()) / grid) * grid
                y = round((pos.y() + 18.0) / grid) * grid
            self._origin = QtCore.QPointF(x, y)
            self._gi.setPos(self.realOrigin)
            self.updateGraphics()

    @property
    def size(self):
        return QtCore.QSizeF(60, 20)

    @property
    def signalState(self):
        return self._signalState

    @property
    def signalPos(self):
        return self._signalPos

    @property
    def previousActiveRoute(self):
        return self._previousActiveRoute

    @property
    def nextActiveRoute(self):
        return self._nextActiveRoute

    @nextActiveRoute.setter
    def nextActiveRoute(self, route):
        """ Sets the nextActiveRoute information."""
        self._nextActiveRoute = route
        self.updateSignalState()

    def isOnPosition(self, p):
        """ Checks that the signalItem is on the position p,
        i.e. the trackItem and direction are the same
        @param p the position
        @return Returns true if the signalItem is on position p"""
        if p.trackItem == self and p.previousTI == self.previousItem:
            return True
        else:
            return False

    def getSaveParameters(self):
        """Returns the parameters dictionary to save this TrackItem to the
        database"""
        parameters = super().getSaveParameters()
        parameters.update({"reverse":int(self.reverse)})
        return parameters

    def graphicsMousePressEvent(self, e):
        """Reimplemented from TrackItem.graphicsMousePressEvent to handle the
        mousePressEvent of the owned TrackGraphicsItem.
        It processes mouse clicks on the signal and emits the signals
        signalSelected, trainSelected, or signalUnselected depending on the
        case."""
        super().graphicsMousePressEvent(e)
        if e.button() == Qt.LeftButton:
            if (self._reverse and e.pos().x() <= 20) or \
               (not self._reverse and e.pos().x() > 40):
                # The signal itself is selected
                if self.simulation.context == utils.Context.GAME:
                    self._selected = True;
                persistent = (e.modifiers() == Qt.ShiftModifier)
                force = (e.modifiers() == Qt.AltModifier|Qt.ControlModifier)
                self.signalSelected.emit(self.tiId, persistent, force);
            else:
                # The train code is selected
                self.trainSelected.emit(self._trainId)
        elif e.button() == Qt.RightButton:
            if self.simulation.context == utils.Context.EDITOR_SCENERY:
                self.reverse = not self.reverse
            if (self._reverse and e.pos().x() <= 20) or \
               (not self._reverse and e.pos().x() > 40):
                # The signal itself is right-clicked
                if self.simulation.context == utils.Context.GAME:
                    self._selected = False
                self.signalUnselected.emit(self.tiId)
            else:
                # The train code is right-clicked
                train = self._simulation.trains[self._trainId]
                if train is not None:
                    train.showTrainActionsMenu(
                                    self._simulation.simulationWindow.view,
                                    e.screenPos())
        self.updateGraphics()

    def graphicsBoundingRect(self):
        """Reimplemented from TrackItem.graphicsBoundingRect to return the
        bounding rectangle of the owned TrackGraphicsItem."""
        return QtCore.QRectF(0, -2, 60, 25)

    def graphicsPaint(self, p, options, widget = 0):
        """ Reimplemented from TrackItem.graphicsPaint to
        draw the signal on the owned TrackGraphicsItem"""
        # Draws the berth
        linePen = self.getPen()
        textPen = self.getPen()
        textPen.setColor(Qt.white)
        if self.trainPresent():
            linePen.setColor(Qt.red)
        if self._trainId is not None and \
           self.simulation.context == utils.Context.GAME:
            # Draw Train code
            p.setPen(textPen)
            font = QtGui.QFont("Courier new")
            font.setPixelSize(11)
            p.setFont(font)
            textOrigin = QtCore.QPointF(23,6) if self.reverse else \
                         QtCore.QPointF(3,22)
            p.drawText(textOrigin, self.trainServiceCode.rjust(5))
        else:
            # No Train code => Draw Line
            p.setPen(linePen)
            if self.reverse:
                p.drawLine(20, 2, 60, 2)
            else:
                p.drawLine(0, 18, 40, 18)

        # draw the line at the base of the signal
        if self.selected:
            linePen.setColor(Qt.cyan)
        p.setPen(linePen)
        if self.reverse:
            p.drawLine(0, 2, 20, 2)
        else:
            p.drawLine(40, 18, 60, 18)

        # Draw the signal itself
        textPen.setWidth(0)
        if self.signalHighlighted:
            textPen.setColor(Qt.white)
        else:
            textPen.setColor(Qt.darkGray)
        p.setPen(textPen)
        brush = QtGui.QBrush(Qt.SolidPattern)
        if self._signalState == SignalState.CLEAR:
            brush.setColor(Qt.green)
        elif self._signalState == SignalState.WARNING:
            brush.setColor(Qt.yellow)
        elif self._signalState == SignalState.STOP:
            brush.setColor(Qt.red)
        else:
            brush.setColor(Qt.black)
        p.setBrush(brush)
        if self.reverse:
            r = QtCore.QRect(7, 7, 8, 8)
            p.drawLine(18, 2, 18, 11);
            p.drawLine(18, 11, 15, 11);
            p.drawEllipse(r);
            if self._nextActiveRoute is not None and \
               self._nextActiveRoute.persistent:
                # Draw persistent route rectangle marker
                brush.setColor(Qt.white)
                p.setBrush(brush)
                p.drawRect(1,5,4,3)
        else:
            r = QtCore.QRect(45, 5, 8, 8)
            p.drawLine(42, 18, 42, 9)
            p.drawLine(42, 9, 45, 9)
            p.drawEllipse(r)
            if self._nextActiveRoute is not None and \
               self._nextActiveRoute.persistent:
                # Draw persistent route rectangle marker
                brush.setColor(Qt.white)
                p.setBrush(brush)
                p.drawRect(55,12,4,3)

        # Draw the connection rects
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if self.reverse:
                self.drawConnectionRect(p, QtCore.QPointF(0, 2))
                self.drawConnectionRect(p, QtCore.QPointF(60, 2))
            else:
                self.drawConnectionRect(p, QtCore.QPointF(0, 18))
                self.drawConnectionRect(p, QtCore.QPointF(60, 18))


    def resetNextActiveRoute(self, route=None):
        """Resets the nextActiveRoute information. If route is not None, do
        this only if the nextActiveRoute is equal to route."""
        if (route is None or
            (self._nextActiveRoute is not None and
             self._nextActiveRoute == route)):
            self._nextActiveRoute = None
            self.updateSignalState()

    @previousActiveRoute.setter
    def previousActiveRoute(self, route):
        """Sets the previousActiveRoute information."""
        self._previousActiveRoute = route
        self.updateSignalState()

    def resetPreviousActiveRoute(self, route=None):
        """Reset the previousActiveRoute information. If route is not None, do
        this only if the previousActiveRoute is equal to route."""
        if (route is None or
            (self._previousActiveRoute is not None and
             self._previousActiveRoute == route)):
            self._previousActiveRoute = None
            self.updateSignalState()

    @property
    def trainServiceCode(self):
        """Returns the trainServiceCode of this signal. This is for display
        only."""
        if self._trainId is not None:
            return self.simulation.trains[self._trainId].serviceCode
        else:
            return ""

    @property
    def trainId(self):
        """Returns the train internal Id."""
        return self._trainId

    @trainId.setter
    def trainId(self, code):
        """Sets the trainId of this signal to the given Id."""
        self._trainId = code
        self.updateGraphics()

    def resetTrainId(self):
        """Resets the trainId of this signal."""
        self._trainId = None
        self.updateGraphics()

    def trainsAhead(self):
        """ Returns true if there is a train ahead of this signalItem and
        before the next signalItem"""
        pos = routing.Position(self._nextItem, self, 0)
        while not pos.trackItem.tiType.startswith("E"):
            if pos.trackItem.tiType.startswith("S") and \
            pos.trackItem.isOnPosition(pos):
                # We have met the next signal in the same direction without
                # finding any train
                break
            if pos.trackItem.trainPresent():
                return True
            pos = pos.next()
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
        self._selected = False
        self.updateGraphics()

    @QtCore.pyqtSlot()
    def updateSignalState(self):
        """Update the signal state."""
        if self._nextActiveRoute is None or self.trainsAhead():
            self._signalState = SignalState.STOP
        else:
            if self._nextActiveRoute.endSignal.signalState == \
                                                        SignalState.CLEAR:
                self._signalState = SignalState.CLEAR
            elif self._nextActiveRoute.endSignal.signalState == \
                                                        SignalState.WARNING:
                self._signalState = SignalState.CLEAR
            elif self._nextActiveRoute.endSignal.signalState == \
                                                        SignalState.STOP:
                self._signalState = SignalState.WARNING
            else:
                self._signalState = SignalState.STOP
        if self._previousActiveRoute is not None:
            self._previousActiveRoute.beginSignal.updateSignalState()
        self.updateGraphics()
