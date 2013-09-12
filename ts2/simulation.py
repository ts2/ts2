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

from PyQt4 import QtCore, QtSql, QtGui
from PyQt4.QtCore import Qt
from math import sqrt
import sqlite3
from ts2 import utils
from ts2 import routing
from ts2 import scenery
from ts2 import trains

class Simulation(QtCore.QObject):
    """The Simulation class holds all the game logic."""

    def __init__(self, simulationWindow):
        """ Constructor for the Simulation class """
        super().__init__()
        self._simulationWindow = simulationWindow
        self._scene = QtGui.QGraphicsScene()
        self._timer = QtCore.QTimer(self)
        self.initialize()
        self._routes = {}
        self._serviceListModel = trains.ServiceListModel(self)
        self._selectedServiceModel = trains.ServiceInfoModel(self)
        self._trainListModel = trains.TrainListModel(self)
        self._selectedTrainModel = trains.TrainInfoModel(self)

    @property
    def scene(self):
        """Returns the QGraphicsScene on which the simulation scenery is
        displayed"""
        return self._scene

    @property
    def simulationWindow(self):
        return self._simulationWindow

    @property
    def context(self):
        """Returns the context of this Simulation object"""
        return utils.Context.GAME

    def option(self, key):
        """Returns the simulation option specified by key"""
        return self._options.get(key)

    def setOption(self, key, value):
        self._options[key] = value

    @property
    def currentTime(self):
        return self._time

    @property
    def serviceListModel(self):
        return self._serviceListModel

    @property
    def selectedServiceModel(self):
        return self._selectedServiceModel

    @property
    def trainListModel(self):
        return self._trainListModel

    @property
    def selectedTrainModel(self):
        return self._selectedTrainModel

    @property
    def routes(self):
        """Returns the routes of the simulation"""
        return self._routes

    @property
    def trainTypes(self):
        """Returns the list of rolling stock types of the simulation"""
        return self._trainTypes

    def reload(self, fileName):
        """Load or reload all the data of the simulation from the database."""
        self.initialize()
        conn = sqlite3.connect(fileName)
        conn.row_factory = sqlite3.Row
        self.loadOptions(conn)
        #self.loadPlaces(conn)
        self.loadTrackItems(conn)
        self.loadRoutes(conn)
        self.loadTrainTypes(conn)
        self.loadServices(conn)
        self.loadTrains(conn)
        conn.close()
        self.setupConnections()
        self.simulationLoaded.emit()
        self._scene.update()
        self._time = QtCore.QTime.fromString(\
                                    self.option("currentTime"), "hh:mm:ss")
        self._timer.timeout.connect(self.timerOut)
        interval = min(max(100, 5000 / float(self.option("timeFactor"))), 500)
        self._timer.setInterval(interval)
        self._timer.start()

    def initialize(self):
        """Clears and initialize the current simulation"""
        self._selectedSignal = None
        self._timer.stop()
        try:
            self._timer.timeout.disconnect()
        except:
            pass
        self._options = {}
        self._routes = {}
        self._trackItems = {}
        self._activeRouteNumbers = []
        self._trainTypes = {}
        self._services = {}
        self._places = {}
        self._trains = []
        self._scene.clear()
        self._time = QtCore.QTime()

    def train(self, serviceCode):
        """Returns the Train object corresponding to the train whose
        serviceCode is currently serviceCode"""
        for t in self._trains:
            if t.serviceCode == serviceCode:
                return t
        return None

    @property
    def trains(self):
        return self._trains

    def trackItem(self, id):
        return self._trackItems[id]

    def place(self, placeCode):
        if placeCode is not None and placeCode != "":
            for ti in self._trackItems.values():
                if ti.tiType.startswith("A") and ti.placeCode == placeCode:
                    return ti
        return None

    def service(self, serviceCode):
        return self._services[serviceCode]

    @property
    def services(self):
        return self._services

    def registerGraphicsItem(self, graphicItem):
        self._scene.addItem(graphicItem)

    simulationLoaded = QtCore.pyqtSignal()

    conflictingRoute = QtCore.pyqtSignal(routing.Route)
    noRouteBetweenSignals = QtCore.pyqtSignal(scenery.SignalItem, \
                                              scenery.SignalItem)
    routeSelected = QtCore.pyqtSignal(routing.Route)
    routeDeleted = QtCore.pyqtSignal(routing.Route)
    timeChanged = QtCore.pyqtSignal(QtCore.QTime)
    timeElapsed = QtCore.pyqtSignal(float)
    trainSelected = QtCore.pyqtSignal(str)
    itemSelected = QtCore.pyqtSignal(int)

    @QtCore.pyqtSlot(int, bool)
    def activateRoute(self, siId, persistent = False):
        """This slot is normally connected to the signal
        SignalItem.signalSelected(SignalItem), which itself is emitted when a
        signal is left-clicked.
        It is in charge of:
        - Checking whether this is the first signal to be selected, if it the
        case, selectedSignal is set to this signal and the function returns;
        - Otherwise, it checks whether there exists a possible route between
        _selectedSignal and this signal. If it is the case, and that no other
        active route conflicts with this route, it is activated.

        The following signals are emited depending of the situation:
        - routeActivated
        - noRouteBetweenSignals
        - conflictingRoute
        @param si Pointer to the signalItem owner of the signalGraphicsItem
        that has been left-clicked."""
        si = self._trackItems[siId]
        if self._selectedSignal is None or self._selectedSignal == si:
            # First signal selected
            self._selectedSignal = si
        else:
            # Second signal selected
            r = self.findRoute(self._selectedSignal, si)
            if r is not None:
                # There exists a route between both signals
                if r.isActivable():
                    # We can activate it
                    r.activate(persistent)
                    self._selectedSignal.unselect()
                    self._selectedSignal = None
                    si.unselect()
                else:
                    # We cannot activate it (another route is conflicting)
                    self.conflictingRoute.emit(r)
                    si.unselect()
                    QtCore.qWarning(self.tr("Conflicting route"))
            else:
                # No route between both signals
                self.noRouteBetweenSignals.emit(self._selectedSignal, si)
                si.unselect()
                QtCore.qWarning(self.tr("No route between signals"))

    @QtCore.pyqtSlot(int)
    def desactivateRoute(self, siId):
        """ This slot is normally connected to the signal
        SignalItem.signalUnselected(SignalItem), which itself is emitted when
        a signal is right-clicked. It is in charge of deactivating the routes
        starting from this signal.
        @param si Pointer to the signalItem owner of the signalGraphicsItem
        that has been right-clicked."""
        si = self._trackItems[siId]
        if self._selectedSignal is not None:
            # Unselect the selected signal if any
            self._selectedSignal.unselect()
            self._selectedSignal = None
        r = si.nextActiveRoute
        if r is not None:
            r.desactivate()
            self.routeDeleted.emit(r)

    @QtCore.pyqtSlot(bool)
    def pause(self, paused):
        """ Toggle pause.
        @param paused If paused is true pause the game, else restart.
        """
        if paused:
            self._timer.stop()
        else:
            self._timer.start()

    @QtCore.pyqtSlot(int)
    def setTimeFactor(self, timeFactor):
        """Sets the time factor to timeFactor."""
        self._timer.stop()
        self.setOption("timeFactor", min(timeFactor, 10))
        if timeFactor != 0:
            self._timer.start()

    @QtCore.pyqtSlot()
    def timerOut(self):
        """ Changes the simulation time and emits the timeChanged and the
        timeElapsed signals
        This function is normally connected to the timer timeout signal."""
        timeFactor = float(self.option("timeFactor"))
        self._time = self._time.addMSecs((self._timer.interval())*timeFactor)
        self.timeChanged.emit(self._time)
        secs = self._timer.interval() * timeFactor / 1000
        self.timeElapsed.emit(secs)

    def loadRoutes(self, conn):
        """Creates the instances of routes from the data of the database."""
        QtCore.qDebug("Loading routes")
        for route in conn.execute("SELECT * FROM routes"):
            routeNum = route["routenum"]
            beginSignalId = route["beginsignal"]
            endSignalId = route["endsignal"]
            initialState = route["initialstate"]
            bs = self._trackItems[beginSignalId]
            es = self._trackItems[endSignalId]
            route = routing.Route(self, routeNum, bs, es, initialState)
            self._routes[routeNum] = route

        for direction in conn.execute("SELECT * FROM directions"):
            routeNum = direction["routenum"]
            tiId = direction["tiid"]
            direction = direction["direction"]
            self._routes[routeNum].appendDirection(tiId, direction)

        check = True
        for route in self._routes.values():
            check = (route.createPositionsList() and check)

        if not check:
            QtCore.qFatal(self.tr("""Invalid simulation: Some routes are not
valid.\nSee stderr for more information"""))

        # Activates routes who are to be activated at the beginning of the
        # simulation
        if self.context == utils.Context.GAME:
            for route in self._routes.values():
                if route.initialState == 2:
                    route.activate(True)
                elif route.initialState == 1:
                    route.activate(False)

    def loadTrainTypes(self, conn):
        """Creates the instances of TrainType from the data of the database.
        """
        for trainType in conn.execute("SELECT * FROM traintypes"):
            code = str(trainType["code"])
            parameters = dict(trainType)
            self._trainTypes[code] = trains.TrainType(self, parameters)

    def loadTrains(self, conn):
        """Creates the instances of Train from the data of the database."""
        for train in conn.execute("SELECT * FROM trains"):
            parameters = dict(train)
            train = trains.Train(self, parameters)
            self._trains.append(train)

    def loadOptions(self, conn):
        """Populates the options dict with data from the database"""
        self._options = {
                "title":"",
                "description":"",
                "timeFactor":5,
                "currentTime":"06:00:00",
                "warningSpeed":8.3,
                "defaultMaxSpeed":18,
                "defaultMinimumStopTime":30
            }
        options = {}
        for option in conn.execute("SELECT * FROM options"):
            key = option["optionkey"]
            value = option["optionvalue"]
            if key != "":
                options[key] = value
        self._options.update(options)

    def loadTrackItems(self, conn):
        """Loads the instances of trackItems and its subclasses from the
        data of the database, and make all the necessary links"""
        self.createAllTrackItems(conn)
        self.createTrackItemsLinks()
        self.createTrackItemConflicts(conn)
        # Check that all the items are linked
        if not self.checkTrackItemsLinks():
            QtCore.qFatal("Invalid simulation: Not all items are linked.\n \
                           See stderr for more information")

    def createAllTrackItems(self, conn):
        """Creates the instances of TrackItem and its subclasses (including
        Places) from the database."""
        for place in \
                    conn.execute("SELECT * FROM trackitems WHERE titype='A'"):
            parameters = dict(place)
            tiId = parameters["tiid"]
            placeCode = parameters["placecode"]
            place = scenery.Place(self, parameters)
            self._trackItems[tiId] = place

        for trackItem in \
                   conn.execute("SELECT * FROM trackitems WHERE titype<>'A'"):
            parameters = dict(trackItem)
            tiId = parameters["tiid"]
            tiType = parameters["titype"]
            if tiType == "L":
                ti = scenery.LineItem(self, parameters)
            elif tiType == "LP":
                ti = scenery.PlatformItem(self, parameters)
            elif tiType == "S":
                ti = scenery.SignalItem(self, parameters)
            elif tiType == "SB":
                ti = scenery.BumperItem(self, parameters)
            elif tiType == "ST":
                ti = scenery.SignalTimerItem(self, parameters)
            elif tiType == "P":
                ti = scenery.PointsItem(self, parameters)
            elif tiType == "E":
                ti = scenery.EndItem(self, parameters)
            else:
                ti = scenery.TrackItem(self, parameters)
            self.makeTrackItemSignalSlotConnections(ti)
            self._trackItems[tiId] = ti


    def makeTrackItemSignalSlotConnections(self, ti):
        """Makes all signal-slot connections for TrackItem ti"""
        if ti.tiType.startswith("S"):
            ti.signalSelected.connect(self.activateRoute)
            ti.signalUnselected.connect(self.desactivateRoute)
            ti.trainSelected.connect(self.trainSelected)


    def loadServices(self, conn):
        """Creates the instances of Service from the data of the database."""
        for service in conn.execute("SELECT * FROM services"):
            serviceCode = service["servicecode"]
            parameters = dict(service)
            self._services[serviceCode] = trains.Service(self, parameters)

        for serviceLine in conn.execute("SELECT * FROM serviceLines"):
            serviceCode = serviceLine["servicecode"]
            parameters = dict(serviceLine)
            self._services[serviceCode].addLine(parameters)

        for s in self._services.values():
            s.start()

    def setupConnections(self):
        """Sets up the connections which need a simulation loaded"""
        self.timeChanged.connect(self.selectedTrainModel.reset)

    def findRoute(self, si1, si2):
        """Checks whether a route exists between two signals, and return this
        route or None.
        @param si1 The signalItem of the first signal
        @param si2 The signalItem of the second signal
        @return The route between signal si1 and si2 if it exists, None
        otherwise"""
        for r in self._routes.values():
            if r.links(si1, si2):
                return r;
        return None;

    def createTrackItemConflicts(self, conn):
        """Create the trackitems' conflicts from the data in database."""
        for trackItem in conn.execute("SELECT * FROM trackitems"):
            conflictTiId = trackItem["conflicttiid"]
            if conflictTiId is not None and conflictTiId != 0:
                tiId = trackItem["tiid"]
                self._trackItems[tiId].conflictTI = \
                                self._trackItems[conflictTiId]
                self._trackItems[conflictTiId].conflictTI = \
                                self._trackItems[tiId]

    def createTrackItemsLinks(self):
        """Find the items that are linked together through their coordinates
        and populate the _nextItem and _previousItem variables of each items.
        """
        for ki, vi in self._trackItems.items():
            for kj, vj in self._trackItems.items():
                if ki < kj:
                    if self.distanceBetween(vi.origin, vj.origin) <= 1.0:
                        vi.previousItem = vj
                        vj.previousItem = vi
                    elif self.distanceBetween(vi.origin, vj.end) <= 1.0:
                        vi.previousItem = vj
                        vj.nextItem = vi
                    elif self.distanceBetween(vi.end, vj.origin) <= 1.0:
                        vi.nextItem = vj
                        vj.previousItem = vi
                    elif self.distanceBetween(vi.end, vj.end) <= 1.0:
                        vi.nextItem = vj
                        vj.nextItem = vi
                    elif vi.tiType.startswith("P"):
                        if self.distanceBetween(vi.reverse, vj.origin) <= 1.0:
                            vi.reverseItem = vj
                            vj.previousItem = vi
                        elif self.distanceBetween(vi.reverse, vj.end) <= 1.0:
                            vi.reverseItem = vj
                            vj.nextItem = vi
                    elif vj.tiType.startswith("P"):
                        if self.distanceBetween(vi.origin, vj.reverse) <= 1.0:
                            vi.previousItem = vj
                            vj.reverseItem = vi
                        elif self.distanceBetween(vi.end, vj.reverse) <= 1.0:
                            vi.nextItem = vj
                            vj.reverseItem = vi


    def checkTrackItemsLinks(self):
        """Checks that all TrackItems are linked together"""
        result = True;
        QtCore.qDebug(self.tr("Checking TrackItem links"))
        for ti in self._trackItems.values():
            if not ti.tiType.startswith("A"):
                if ti.nextItem is None:
                    QtCore.qCritical(
                            self.tr("TrackItem %i is unlinked at (%f, %f)" % \
                                    (ti.tiId, ti.end.x(), ti.end.y())))
                    result = False
                if ti.previousItem is None:
                    QtCore.qCritical(
                            self.tr("TrackItem %i is unlinked at (%f, %f)" % \
                                    (ti.tiId, ti.origin.x(), ti.origin.y())))
                    result = False
        return result

    def distanceBetween(self, p1, p2):
        """Calculates the distance between both points p1 and p2 in pixels
        @param p1
        @param p2
        @return"""
        return sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2)

    def getLineItem(self, placeCode, trackCode):
        """Returns the LineItem instance defined by placeCode and trackCode.
        """
        for ti in self._trackItems.values():
            if ti.tiType.startswith("L"):
                if ti.placeCode == placeCode and ti.trackCode == trackCode:
                    return ti
        return None


