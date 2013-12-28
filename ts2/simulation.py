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
from ts2 import utils, routing, scenery, trains
from ts2.game import logger, scorer


class Simulation(QtCore.QObject):
    """The Simulation class holds all the game logic."""

    def __init__(self, simulationWindow):
        """ Constructor for the Simulation class. """
        super().__init__()
        self._database = None
        self._simulationWindow = simulationWindow
        self._scene = QtGui.QGraphicsScene()
        self._timer = QtCore.QTimer(self)
        self._messageLogger = logger.MessageLogger(self)
        self._scorer = scorer.Scorer(self)
        self.initialize()

    def initialize(self):
        """Initialize the simulation."""
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
        self._serviceListModel = trains.ServiceListModel(self)
        self._selectedServiceModel = trains.ServiceInfoModel(self)
        self._trainListModel = trains.TrainListModel(self)
        self._selectedTrainModel = trains.TrainInfoModel(self)

    def load(self, fileName):
        """Loads the simulation from fileName."""
        self.messageLogger.addMessage(self.tr("Simulation loading"),
                                    logger.Message.SOFTWARE_MSG)
        self.initialize()
        self._database = fileName
        conn = sqlite3.connect(fileName)
        conn.row_factory = sqlite3.Row
        self.loadOptions(conn)
        version = float(self.option("version"))
        if version > utils.TS2_FILE_FORMAT:
            conn.close()
            self.messageLogger.addMessage(self.tr(
                        "The simulation is from a newer version of TS2.\n"
                        "Please upgrade TS2 to version %s.") % version,
                        logger.Message.SOFTWARE_MSG)
            return
        if version < utils.TS2_FILE_FORMAT:
            conn.close()
            self.messageLogger.addMessage(self.tr(
                    "The simulation is from an older version of TS2.\n"
                    "Open it in the editor and save it again to play "
                    "with this version of TS2."),
                    logger.Message.SOFTWARE_MSG)
            return
        self.loadTrackItems(conn)
        self.loadRoutes(conn)
        self.loadTrainTypes(conn)
        self.loadServices(conn)
        self.loadTrains(conn)
        conn.close()
        self.setupConnections()
        self._scene.update()
        self._startTime = QtCore.QTime.fromString(
                                self.option("currentTime"), "hh:mm:ss")
        self._time = self._startTime
        self._timer.timeout.connect(self.timerOut)
        #interval = min(max(100, 5000 / float(self.option("timeFactor"))),500)
        interval = 500
        self._timer.setInterval(interval)
        self._timer.start()
        self._scorer.score = self.option("currentScore")
        self.messageLogger.addMessage(self.tr("Simulation loaded"),
                                        logger.Message.SOFTWARE_MSG)

    def saveGame(self, fileName):
        """Saves the game to the given fileName."""
        self.pause()
        self.messageLogger.addMessage(self.tr("Saving simulation"),
                                        logger.Message.SOFTWARE_MSG)
        connFile = sqlite3.connect(fileName)
        if fileName != self._database:
            # Copy the current database to the saved file
            connSimulation = sqlite3.connect(self._database)
            connFile.execute("DROP TABLE IF EXISTS options")
            connFile.execute("DROP TABLE IF EXISTS trackitems")
            connFile.execute("DROP TABLE IF EXISTS routes")
            connFile.execute("DROP TABLE IF EXISTS directions")
            connFile.execute("DROP TABLE IF EXISTS traintypes")
            connFile.execute("DROP TABLE IF EXISTS services")
            connFile.execute("DROP TABLE IF EXISTS servicelines")
            connFile.execute("DROP TABLE IF EXISTS trains")
            connFile.execute("DROP TABLE IF EXISTS messages")
            for line in connSimulation.iterdump():
                if line != "BEGIN TRANSACTION;" and line != "COMMIT;":
                    connFile.execute(line)
            connFile.commit()
            connSimulation.close()
        # Options
        connFile.execute("UPDATE options SET optionvalue=:currentTime "
                         "WHERE optionkey='currentTime'",
                         {"currentTime":self.currentTime.toString("hh:mm:ss")}
                         )
        connFile.execute("UPDATE options SET optionvalue=:timeFactor "
                         "WHERE optionkey='timeFactor'",
                         {"timeFactor":self.option("timeFactor")}
                         )
        connFile.execute("UPDATE options SET optionvalue=:currentScore "
                         "WHERE optionkey='currentScore'",
                         {"currentScore":self.scorer.score}
                         )
        connFile.commit()
        # Routes
        for route in self.routes.values():
            routeState = route.getRouteState()
            connFile.execute("UPDATE routes SET initialstate=:routeState "
                             "WHERE routenum=:routeNum",
                             {"routeNum":route.routeNum,
                              "routeState":routeState})
        connFile.commit()
        # Trains
        connFile.execute("DROP TABLE IF EXISTS trains")
        connFile.execute("CREATE TABLE trains (\n"
                            "trainid INTEGER,\n"
                            "servicecode VARCHAR(10),\n"
                            "traintype VARCHAR(10),\n"
                            "speed DOUBLE,\n"
                            "tiid INTEGER,\n"
                            "previoustiid INTEGER,\n"
                            "posonti DOUBLE,\n"
                            "appeartime TIME,\n"
                            "initialdelay VARCHAR(255),\n"
                            "nextplaceindex INTEGER,\n"
                            "stoppedtime INTEGER)\n")
        for train in self.trains:
            if train.status == trains.TrainStatus.INACTIVE:
                speed = train.initialSpeed
                appearTime = train.appearTimeStr
                initialDelay = train.initialDelayStr
            elif train.status == trains.TrainStatus.OUT:
                continue
            else:
                speed = train.speed
                appearTime = self.currentTime.toString("hh:mm:ss")
                initialDelay = 0
            query = "INSERT INTO trains " \
                    "(trainid, servicecode, traintype, speed, tiid, " \
                    "previoustiid, posonti, appeartime, initialdelay, " \
                    "nextplaceindex, stoppedtime) " \
                    "VALUES " \
                    "(:trainid, :servicecode, :traintype, :speed, :tiid, "\
                    ":previoustiid, :posonti, :appeartime, :initialdelay, "\
                    ":nextplaceindex, :stoppedtime)"
            parameters = {
                    "trainid":train.trainId,
                    "servicecode":train.serviceCode,
                    "traintype":train.trainTypeCode,
                    "speed":speed,
                    "tiid":train.trainHead.trackItem.tiId,
                    "previoustiid":train.trainHead.previousTI.tiId,
                    "posonti":train.trainHead.positionOnTI,
                    "appeartime":appearTime,
                    "initialdelay":initialDelay,
                    "nextplaceindex":train.nextPlaceIndex,
                    "stoppedtime":train.stoppedTime
                    }
            connFile.execute(query, parameters)
        connFile.commit()

        connFile.close()
        self.messageLogger.addMessage(self.tr("Simulation saved"),
                                        logger.Message.SOFTWARE_MSG)

    @property
    def scene(self):
        """Returns the QGraphicsScene on which the simulation scenery is
        displayed"""
        return self._scene

    @property
    def messageLogger(self):
        """Returns the message logger of the simulation."""
        return self._messageLogger

    @property
    def scorer(self):
        """Returns the scorer instance of the simulation."""
        return self._scorer

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
    def startTime(self):
        """Returns the time at which the simulation starts."""
        return self._startTime

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

    @property
    def trains(self):
        return self._trains

    def trackItem(self, id):
        return self._trackItems[id]

    def place(self, placeCode):
        """Returns the place defined by placeCode."""
        if placeCode is not None and placeCode != "":
            return self._places[placeCode]
        else:
            return None

    def service(self, serviceCode):
        return self._services[serviceCode]

    @property
    def services(self):
        return self._services

    def registerGraphicsItem(self, graphicItem):
        self._scene.addItem(graphicItem)

    conflictingRoute = QtCore.pyqtSignal(routing.Route)
    noRouteBetweenSignals = QtCore.pyqtSignal(scenery.SignalItem, \
                                              scenery.SignalItem)
    routeSelected = QtCore.pyqtSignal(routing.Route)
    routeDeleted = QtCore.pyqtSignal(routing.Route)
    timeChanged = QtCore.pyqtSignal(QtCore.QTime)
    timeElapsed = QtCore.pyqtSignal(float)
    trainSelected = QtCore.pyqtSignal(int)
    itemSelected = QtCore.pyqtSignal(int)
    trainStatusChanged = QtCore.pyqtSignal(int)

    @QtCore.pyqtSlot(int, bool, bool)
    def activateRoute(self, siId, persistent=False, force=False):
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
                if r.isActivable() or force:
                    # We can activate it
                    r.activate(persistent)
                    self._selectedSignal.unselect()
                    self._selectedSignal = None
                    si.unselect()
                else:
                    # We cannot activate it (another route is conflicting)
                    self.conflictingRoute.emit(r)
                    si.unselect()
                    self.messageLogger.addMessage(
                                            self.tr("Conflicting route"),
                                            logger.Message.PLAYER_WARNING_MSG)
            else:
                # No route between both signals
                self.noRouteBetweenSignals.emit(self._selectedSignal, si)
                self._selectedSignal.unselect()
                self._selectedSignal = si
                self.messageLogger.addMessage(
                                        self.tr("No route between signals"),
                                        logger.Message.PLAYER_WARNING_MSG)

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
    def pause(self, paused=True):
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
        self.messageLogger.addMessage(self.tr("Loading routes"),
                               logger.Message.SOFTWARE_MSG)
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
            self.messageLogger.addMessage(
                    self.tr("Invalid simulation: Some routes are not valid."),
                    logger.Message.SOFTWARE_MSG)

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
        self.messageLogger.addMessage(self.tr("Loading train types"),
                                      logger.Message.SOFTWARE_MSG)
        for trainType in conn.execute("SELECT * FROM traintypes"):
            code = str(trainType["code"])
            parameters = dict(trainType)
            self._trainTypes[code] = trains.TrainType(self, parameters)

    def loadTrains(self, conn):
        """Creates the instances of Train from the data of the database."""
        self.messageLogger.addMessage(self.tr("Loading trains"),
                                      logger.Message.SOFTWARE_MSG)
        for train in conn.execute("SELECT * FROM trains"):
            parameters = dict(train)
            train = trains.Train(self, parameters)
            train.trainStatusChanged.connect(self.trainStatusChanged)
            train.trainStoppedAtStation.connect(
                                            self.scorer.trainArrivedAtStation)
            train.trainExitedArea.connect(self.scorer.trainExitedArea)
            train.reassignServiceRequested.connect(
                            self.simulationWindow.openReassignServiceWindow)
            self._trains.append(train)
        self._trains.sort(key = lambda x:
                         x.currentService.lines[0].scheduledDepartureTimeStr)


    def loadOptions(self, conn):
        """Populates the options dict with data from the database"""
        self.messageLogger.addMessage(self.tr("Loading options"),
                                      logger.Message.SOFTWARE_MSG)
        self._options = {
                "title":"",
                "description":"",
                "version":utils.TS2_FILE_FORMAT,
                "timeFactor":5,
                "currentTime":"06:00:00",
                "warningSpeed":8.3,
                "currentScore":0,
                "defaultMaxSpeed":44.44,
                "defaultMinimumStopTime":[(45,75,70),(75,90,30)],
                "defaultDelayAtEntry":[(-60,0,50),(0,60,50)]
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
        self.messageLogger.addMessage(self.tr("Loading TrackItems"),
                                      logger.Message.SOFTWARE_MSG)
        self.createAllTrackItems(conn)
        self.linkTrackItems(conn)
        #self.createTrackItemsLinks()
        self.createTrackItemConflicts(conn)
        # Check that all the items are linked
        if not self.checkTrackItemsLinks():
           self.messageLogger(self.tr("Invalid simulation: "
                                      "Not all items are linked."),
                              logger.Message.SOFTWARE_MSG)

    def createAllTrackItems(self, conn):
        """Creates the instances of TrackItem and its subclasses (including
        Places) from the database."""
        for p in conn.execute("SELECT * FROM trackitems WHERE titype='A'"):
            parameters = dict(p)
            tiId = parameters["tiid"]
            place = scenery.Place(self, parameters)
            self._trackItems[tiId] = place
            self._places[place.placeCode] = place

        for trackItem in \
                   conn.execute("SELECT * FROM trackitems WHERE titype<>'A'"):
            parameters = dict(trackItem)
            tiId = parameters["tiid"]
            tiType = parameters["titype"]
            if tiType == "L":
                ti = scenery.LineItem(self, parameters)
            elif tiType == "LP":
                ti = scenery.PlatformItem(self, parameters)
            elif tiType == "LI":
                ti = scenery.InvisibleLinkItem(self, parameters)
            elif tiType == "S":
                ti = scenery.SignalItem(self, parameters)
            elif tiType == "SB":
                ti = scenery.BumperItem(self, parameters)
            elif tiType == "ST":
                ti = scenery.SignalTimerItem(self, parameters)
            elif tiType == "SN":
                ti = scenery.NonReturnItem(self, parameters)
            elif tiType == "P":
                ti = scenery.PointsItem(self, parameters)
            elif tiType == "E":
                ti = scenery.EndItem(self, parameters)
            elif tiType == "ZT":
                ti = scenery.TextItem(self, parameters)
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
        self.messageLogger.addMessage(self.tr("Loading services"),
                                      logger.Message.SOFTWARE_MSG)
        for service in conn.execute("SELECT * FROM services"):
            serviceCode = service["servicecode"]
            parameters = dict(service)
            self._services[serviceCode] = trains.Service(self, parameters)

        for serviceLine in conn.execute("SELECT * FROM serviceLines"):
            serviceCode = serviceLine["servicecode"]
            parameters = dict(serviceLine)
            self._services[serviceCode].addLine(parameters)

    def setupConnections(self):
        """Sets up the connections which need a simulation loaded"""
        #self.timeChanged.connect(self.selectedTrainModel.reset)

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

    def linkTrackItems(self, conn):
        """Link trackItems using the data from the database connection."""
        self.messageLogger.addMessage(self.tr("Linking trackItems"),
                                      logger.Message.SOFTWARE_MSG)
        for trackItem in conn.execute("SELECT * FROM trackitems"):
            tiId = trackItem["tiid"]
            previousTiId = trackItem["ptiid"]
            if previousTiId is not None:
                self._trackItems[tiId].previousItem = \
                                                self._trackItems[previousTiId]
            nextTiId = trackItem["ntiid"]
            if nextTiId is not None:
                self._trackItems[tiId].nextItem = self._trackItems[nextTiId]
            reverseTiId = trackItem["rtiid"]
            if reverseTiId is not None:
                self._trackItems[tiId].reverseItem = \
                                                self._trackItems[reverseTiId]

    def createTrackItemConflicts(self, conn):
        """Create the trackitems' conflicts from the data in database."""
        self.messageLogger.addMessage(self.tr("Creating TrackItem conflicts"),
                                      logger.Message.SOFTWARE_MSG)
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
        self.messageLogger.addMessage(self.tr("Creating TrackItem links"),
                                      logger.Message.SOFTWARE_MSG)
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
        self.messageLogger.addMessage(self.tr("Checking TrackItem links"),
                                      logger.Message.SOFTWARE_MSG)
        for ti in self._trackItems.values():
            if not ti.tiType.startswith(("A", "ZT")):
                if ti.nextItem is None:
                    self.messageLogger.addMessage(
                            self.tr("TrackItem %i is unlinked at (%f, %f)" %
                                    (ti.tiId, ti.end.x(), ti.end.y())),
                            logger.Message.SOFTWARE_MSG)
                    result = False
                if ti.previousItem is None:
                    self.messageLogger.addMessage(
                            self.tr("TrackItem %i is unlinked at (%f, %f)" %
                                    (ti.tiId, ti.origin.x(), ti.origin.y())),
                            logger.Message.SOFTWARE_MSG)
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


