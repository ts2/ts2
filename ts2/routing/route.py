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

from Qt import QtCore, Qt

from ts2 import utils
from ts2.game import logger
from ts2.scenery import pointsitem
from . import position


class RoutesModel(QtCore.QAbstractTableModel):
    """The RoutesModel is a table model for routes that is used in the editor
    """
    def __init__(self, editor):
        """Constructor for the RoutesModel class"""
        super().__init__()
        self._editor = editor

    def rowCount(self, parent=None, *args, **kwargs):
        """Returns the number of rows of the model, corresponding to the
        number of routes."""
        return len(self._editor.routes)

    def columnCount(self, parent=None, *args, **kwargs):
        """Returns the number of columns of the model"""
        return 4

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole or role == Qt.EditRole:
            routes = list(sorted(self._editor.routes.values()))
            if index.column() == 0:
                return routes[index.row()].routeNum
            elif index.column() == 1:
                return routes[index.row()].beginSignal.name
            elif index.column() == 2:
                return routes[index.row()].endSignal.name
            elif index.column() == 3:
                return routes[index.row()].initialState
        return None

    def setData(self, index, value, role=None):
        """Updates data when modified in the view"""
        if role == Qt.EditRole:
            if index.column() == 3:
                routeNum = int(index.sibling(index.row(), 0).data())
                self._editor.routes[routeNum].initialState = value
                self.dataChanged.emit(index, index)
                return True
        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Returns the header labels"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return self.tr("Route no.")
            elif section == 1:
                return self.tr("Begin Signal")
            elif section == 2:
                return self.tr("End Signal")
            elif section == 3:
                return self.tr("Initial State")
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        retFlag = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() == 3:
            retFlag |= Qt.ItemIsEditable
        return retFlag


class Route(QtCore.QObject):
    """@brief Path between two signals
    A route is a path between two signals. If a route is activated, the path
    is selected, and the signals at the beginning and the end of the route are
    changed and the conflicting possible other routes are inhibited. Routes
    are static and defined in the game file. The player can only activate or
    deactivate them.
    """
    def __init__(self, parameters):
        """Constructor of the Route class. After construction, the directions
        dictionary must be filled and then the _positions list must be
        populated by calling createPositionsList().

        :param parameters: json dict with data to create the route
        """
        super().__init__()
        self.simulation = None
        self._parameters = parameters
        self._routeNum = parameters['routeNum']
        self._directions = {}
        for key, value in parameters['directions'].items():
            self._directions[int(key)] = value
        self._initialState = parameters.get('initialState', 0)
        self._persistent = False
        self._positions = []

    def initialize(self, simulation):
        """Initializes the route once all trackitems are loaded."""
        if not self._parameters:
            raise Exception("Internal error: Route already initialized !")
        self.simulation = simulation
        beginSignal = simulation.trackItem(self._parameters['beginSignal'])
        endSignal = simulation.trackItem(self._parameters['endSignal'])
        bsp = position.Position(beginSignal, beginSignal.previousItem, 0)
        esp = position.Position(endSignal, endSignal.previousItem, 0)
        self._positions = [bsp, esp]
        if not self.createPositionsList():
            simulation.messageLogger.addMessage(
                self.tr("Invalid simulation: Route %i is not valid."
                        % self.routeNum), logger.Message.SOFTWARE_MSG
            )
        self._parameters = None

    def setToInitialState(self):
        """Setup routes according to their initial state."""
        if self.simulation.context == utils.Context.GAME:
            if self.initialState == 2:
                self.activate(True)
            elif self.initialState == 1:
                self.activate(False)

    def for_json(self):
        """Dumps this route to JSON."""
        if self.simulation.context == utils.Context.GAME:
            initialState = self.getRouteState()
        else:
            initialState = self.initialState
        return {
            "__type__": "Route",
            "routeNum": self.routeNum,
            "beginSignal": self.beginSignal.tiId,
            "endSignal": self.endSignal.tiId,
            "directions": self.directions,
            "initialState": initialState
        }

    routeSelected = QtCore.pyqtSignal()
    routeUnselected = QtCore.pyqtSignal()

    @property
    def positions(self):
        """Returns the positions list of this route."""
        return self._positions

    @property
    def routeNum(self):
        """Returns this route number"""
        return self._routeNum

    @property
    def beginSignal(self):
        """ Returns the SignalItem where this route starts."""
        return self._positions[0].trackItem

    @property
    def endSignal(self):
        """Returns the SignalItem where this route ends."""
        return self._positions[-1].trackItem

    @property
    def initialState(self):
        """Returns the state of the route at the beginning of the simulation.
        0 => Not activated
        1 => Activated, non persistent
        2 => Activated, persistent"""
        return self._initialState

    @initialState.setter
    def initialState(self, value):
        """Setter function for the initialState property"""
        value = int(value)
        if value < 0 or value > 2:
            value = 0
        self._initialState = value

    def getRouteState(self):
        """Returns the current route state:
        0 => Not activated
        1 => Activated, non persistent
        2 => Activated, persistent."""
        if self.beginSignal.nextActiveRoute is not None and \
           self.beginSignal.nextActiveRoute == self:
            if self._persistent:
                return 2
            else:
                return 1
        else:
            return 0

    @property
    def directions(self):
        """Returns the directions dictionary"""
        return self._directions

    def direction(self, tiId):
        """Returns the direction of this route at the trackItem with id tiId
        """
        return self._directions[tiId]

    def appendDirection(self, tiId, direction):
        """ Appends a direction to a TrackItem on the Route.
        @param tiId The trackItem number to which we add direction
        @param direction The direction to append.
        For points, 0 means normal and other values means reverse"""
        self._directions[tiId] = direction

    def createPositionsList(self):
        """ Populates the _positions list.
        If the route is invalid, it leaves the _positions list empty.
        Also completes the _directions map, with obvious directions."""
        cur = self._positions[0].next()
        it = 1
        while not cur.isOut():
            if cur == self._positions[-1]:
                return True
            self._positions.insert(it, cur)
            it += 1
            if isinstance(cur.trackItem, pointsitem.PointsItem):
                if cur.previousTI == cur.trackItem.normalItem:
                    self._directions[cur.trackItem.tiId] = 0
                elif cur.previousTI == cur.trackItem.reverseItem:
                    self._directions[cur.trackItem.tiId] = 1
                elif cur.previousTI == cur.trackItem.commonItem \
                        and cur.trackItem.tiId not in self._directions:
                    self._directions[cur.trackItem.tiId] = 0
            cur = cur.next(0, self._directions.get(cur.trackItem.tiId, -1))
        QtCore.qCritical(self.tr("Invalid route %i. Impossible to link "
                                 "beginSignal with endSignal" % self.routeNum))
        return False

    def links(self, si1, si2):
        """ Returns true if the route links SignalItem si1 to SignalItem si2.
        @param si1 First SignalItem
        @param si2 Last SignalItem"""
        if self.beginSignal == si1 and self.endSignal == si2:
            return True
        else:
            return False

    def activate(self, persistent=False):
        """ This function is called by the simulation when the route is
        activated."""
        for pos in self._positions:
            pos.trackItem.setActiveRoute(self, pos.previousTI)
        self.endSignal.previousActiveRoute = self
        self.beginSignal.nextActiveRoute = self
        self.persistent = persistent
        self.routeSelected.emit()

    def desactivate(self):
        """This function is called by the simulation when the route is
        desactivated."""
        self.beginSignal.resetNextActiveRoute(self)
        self.endSignal.resetPreviousActiveRoute()
        for pos in self._positions:
            if pos.trackItem.activeRoute is None or \
               pos.trackItem.activeRoute == self:
                pos.trackItem.resetActiveRoute()
        self.routeUnselected.emit()

    def isActivable(self):
        """Returns true if this route can be activated, i.e. that no other
        active route is conflicting with this route."""
        flag = False
        for pos in self._positions:
            if pos.trackItem != self.beginSignal and \
               pos.trackItem != self.endSignal:
                if pos.trackItem.conflictTI is not None \
                   and pos.trackItem.conflictTI.activeRoute is not None:
                    # The trackItem has a conflict item and this conflict item
                    # has an active route
                    return False
                if pos.trackItem.activeRoute is not None:
                    # The trackItem already has an active route
                    if isinstance(pos.trackItem, pointsitem.PointsItem) \
                            and not flag:
                        # The trackItem is a pointsItem and it is the first
                        # trackItem with active route that we meet
                        return False
                    if pos.previousTI != pos.trackItem.activeRoutePreviousItem:
                        # The direction of this route is different from that
                        # of the active route of the TI
                        return False
                    if pos.trackItem.activeRoute == self:
                        # Always allow to setup the same route again
                        return True
                    else:
                        # We set flag to true to remember we have come across
                        # a TI with activeRoute with same dir. This enables
                        # the user to set a route ending with the same end
                        # signal when it is cleared by a train still
                        # on the route
                        flag = True
                elif flag:
                    # We had a route with same direction but does not end with
                    # the same signal
                    return False
        return True

    @property
    def persistent(self):
        """Returns True if this route is persistent"""
        return self._persistent

    @persistent.setter
    def persistent(self, p=True):
        """Setter function for the persistent property"""
        self._persistent = p

    def __eq__(self, other):
        """Two routes are equal if they have the save routeNum or if both
        beginSignal and endSignal are equal"""
        if (self.routeNum == other.routeNum or
            (self.beginSignal == other.beginSignal and
             self.endSignal == other.endSignal)):
            return True
        else:
            return False

    def __ne__(self, other):
        """Two routes are not equal if they have different routeNum and if
        at least one of beginSignal or endSignal is different"""
        if (self.routeNum != other.routeNum and
            (self.beginSignal != other.beginSignal or
             self.endSignal != other.endSignal)):
            return True
        else:
            return False

    def __lt__(self, other):
        """Route is lower than other when its routeNum is lower"""
        return self.routeNum < other.routeNum

    def __gt__(self, other):
        """Route is greater than other when its routeNum is greater"""
        return self.routeNum > other.routeNum
