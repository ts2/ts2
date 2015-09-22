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

from math import sqrt
import collections
import simplejson as json

from Qt import QtCore, QtWidgets

from ts2 import utils, trains
from ts2.routing import route, position
from ts2.game import logger, scorer
from ts2.scenery import placeitem, lineitem, platformitem, invisiblelinkitem, \
    enditem, pointsitem, textitem
from ts2.scenery.signals import signalitem

translate = QtWidgets.qApp.translate


BUILTIN_OPTIONS = {
    "title": "",
    "description": "",
    "version": utils.TS2_FILE_FORMAT,
    "timeFactor": 5,
    "currentTime": "06:00:00",
    "warningSpeed": 8.3,
    "currentScore": 0,
    "defaultMaxSpeed": 44.44,
    "defaultMinimumStopTime": "[(45,75,70),(75,90,30)]",
    "defaultDelayAtEntry": "[(-60,0,50),(0,60,50)]",
    "trackCircuitBased": 0,
    "defaultSignalVisibility": 100
}


def json_hook(dct):
    """Hook method for json.load()."""
    if not dct.get('__type__'):
        return dct
    elif dct['__type__'] == "Simulation":
        return Simulation(dct['options'], dct['trackItems'], dct['routes'],
                          dct['trainTypes'], dct['services'], dct['trains'],
                          dct['messageLogger'])
    elif dct['__type__'] == "SignalItem":
        return signalitem.SignalItem(parameters=dct)
    elif dct['__type__'] == "EndItem":
        return enditem.EndItem(parameters=dct)
    elif dct['__type__'] == "InvisibleLinkItem":
        return invisiblelinkitem.InvisibleLinkItem(parameters=dct)
    elif dct['__type__'] == "LineItem":
        return lineitem.LineItem(parameters=dct)
    elif dct['__type__'] == "Place":
        return placeitem.Place(parameters=dct)
    elif dct['__type__'] == "PlatformItem":
        return platformitem.PlatformItem(parameters=dct)
    elif dct['__type__'] == "PointsItem":
        return pointsitem.PointsItem(parameters=dct)
    elif dct['__type__'] == "TextItem":
        return textitem.TextItem(parameters=dct)
    elif dct['__type__'] == "Route":
        return route.Route(parameters=dct)
    elif dct['__type__'] == "Position":
        return position.Position(parameters=dct)
    elif dct['__type__'] == "TrainType":
        return trains.TrainType(parameters=dct)
    elif dct['__type__'] == "Service":
        return trains.Service(parameters=dct)
    elif dct['__type__'] == "ServiceLine":
        return trains.ServiceLine(parameters=dct)
    elif dct['__type__'] == "Train":
        return trains.Train(parameters=dct)
    elif dct['__type__'] == "MessageLogger":
        return logger.MessageLogger(parameters=dct)
    elif dct['__type__'] == "Message":
        return logger.Message(dct)
    else:
        raise utils.FormatException(
            translate("json_hook",
                      "Unknown __type__ '%s' in JSON file") % dct['__type__']
        )


def load(simulationWindow, jsonStream):
    """Loads the simulation from fileName and returns it.

    The logic of loading is the following:
    1. We create the graph of objects from json.load(). When initialized,
    each object stores its JSON data.
    2. When all the objects are created, we call the initialize() method of the
    simulation which calls in turn the initialize() method of each object.
    This method will create all the missing links between the object and the
    simulation (and other objects)."""
    simulation = json.load(jsonStream, object_hook=json_hook, encoding='utf-8')
    if not isinstance(simulation, Simulation):
        raise utils.FormatException(
            translate("simulation.load", "Loaded file is not a TS2 simulation")
        )
    simulation.initialize(simulationWindow)
    return simulation


class Simulation(QtCore.QObject):
    """The Simulation class holds all the game logic."""

    def __init__(self, options, trackItems, routes, trainTypes, services,
                 trns, messageLogger):
        """ Constructor for the Simulation class. """
        super().__init__()
        self.simulationWindow = None
        self._scene = QtWidgets.QGraphicsScene()
        self._timer = QtCore.QTimer(self)
        self._messageLogger = messageLogger
        self._scorer = scorer.Scorer(self)
        self._selectedSignal = None
        self._options = collections.OrderedDict()
        self._options.update(BUILTIN_OPTIONS)
        self._options.update(options)
        self._routes = collections.OrderedDict()
        for key, value in routes.items():
            self._routes[int(key)] = value
        self._trackItems = collections.OrderedDict()
        for key, value in trackItems.items():
            self._trackItems[int(key)] = value
        self.activeRouteNumbers = []
        self._trainTypes = collections.OrderedDict()
        self._trainTypes.update(trainTypes)
        self._services = collections.OrderedDict()
        self._services.update(services)
        self._places = collections.OrderedDict()
        self._trains = trns
        self.signalLibrary = signalitem.signalLibrary
        self._time = QtCore.QTime()
        self._startTime = QtCore.QTime()
        self._serviceListModel = trains.ServiceListModel(self)
        self._selectedServiceModel = trains.ServiceInfoModel(self)
        self._trainListModel = trains.TrainListModel(self)
        self._selectedTrainModel = trains.TrainInfoModel(self)

    def initialize(self, simulationWindow):
        """Initialize the simulation."""
        self.messageLogger.addMessage(self.tr("Simulation initializing"),
                                      logger.Message.SOFTWARE_MSG)
        self.simulationWindow = simulationWindow
        self.updatePlaces()
        for ti in self._trackItems.values():
            ti.initialize(self)
        if not self.checkTrackItemsLinks():
            self.messageLogger.addMessage(
                self.tr("Invalid simulation: Not all items are linked."),
                logger.Message.SOFTWARE_MSG
            )
            raise Exception("Invalid simulation: Not all items are linked.")
        for route in self.routes.values():
            route.initialize(self)
        for route in self.routes.values():
            # We need routes initialized before setting them up
            route.setToInitialState()
        for ti in self.trackItems.values():
            # We need trackItems linked and routes set before setting triggers
            ti.setupTriggers()
        for trainType in self.trainTypes.values():
            trainType.initialize(self)
        for service in self.services.values():
            service.initialize(self)
        for train in self.trains:
            train.initialize(self)
        self._trains.sort(key=lambda x: x.currentService.lines and
                          x.currentService.lines[0].scheduledDepartureTimeStr
                          or x.currentService.serviceCode)
        self.messageLogger.initialize(self)

        self._scene.update()
        self._startTime = QtCore.QTime.fromString(self.option("currentTime"),
                                                  "hh:mm:ss")
        self._time = self._startTime
        self._timer.timeout.connect(self.timerOut)
        interval = 500
        self._timer.setInterval(interval)
        self._timer.start()
        self._scorer.score = self.option("currentScore")
        self.messageLogger.addMessage(self.tr("Simulation loaded"),
                                      logger.Message.SOFTWARE_MSG)

    def for_json(self):
        """Dumps the simulation to JSON."""
        savedOptions = self._options.copy()
        if self.context == utils.Context.GAME:
            savedOptions.update({
                "currentTime": self.currentTime.toString("hh:mm:ss"),
                "currentScore": self.scorer.score
            })
        return {
            "__type__": "Simulation",
            "options": savedOptions,
            "trackItems": self.trackItems,
            "routes": self.routes,
            "trainTypes": self.trainTypes,
            "services": self.services,
            "trains": self.trains,
            "messageLogger": self.messageLogger
        }

    def saveGame(self, fileName):
        """Saves the game to the given fileName."""
        self.pause()
        self.messageLogger.addMessage(self.tr("Saving simulation"),
                                      logger.Message.SOFTWARE_MSG)
        with open(fileName, 'w') as f:
            json.dump(self, f, separators=(',', ':'), for_json=True,
                      encoding='utf-8')
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

    @property
    def trackItems(self):
        """Returns the trackItem dictionary of this simulation."""
        return self._trackItems

    def trackItem(self, tiId):
        return self._trackItems.get(tiId, None)

    def place(self, placeCode):
        """Returns the place defined by placeCode."""
        if placeCode is not None and placeCode != "":
            return self._places[placeCode]
        else:
            return None

    @property
    def places(self):
        """Returns the places dictionary."""
        return self._places

    def service(self, serviceCode):
        return self._services[serviceCode]

    @property
    def services(self):
        return self._services

    def registerGraphicsItem(self, graphicItem):
        self._scene.addItem(graphicItem)

    conflictingRoute = QtCore.pyqtSignal(route.Route)
    noRouteBetweenSignals = QtCore.pyqtSignal(signalitem.SignalItem,
                                              signalitem.SignalItem)
    # routeSelected = QtCore.pyqtSignal(route.Route)
    # routeDeleted = QtCore.pyqtSignal(route.Route)
    timeChanged = QtCore.pyqtSignal(QtCore.QTime)
    timeElapsed = QtCore.pyqtSignal(float)
    trainSelected = QtCore.pyqtSignal(int)
    trainStatusChanged = QtCore.pyqtSignal(int)
    selectionChanged = QtCore.pyqtSignal()

    @QtCore.pyqtSlot(int)
    def updateContext(self, tabNum):
        """Updates the context of the simulation. Does nothing in the base
        class."""
        pass

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

        The following signals are emitted depending of the situation:
        - routeActivated
        - noRouteBetweenSignals
        - conflictingRoute
        @param siId ID of the signalItem owner of the signalGraphicsItem
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
                        logger.Message.PLAYER_WARNING_MSG
                    )
            else:
                # No route between both signals
                self.noRouteBetweenSignals.emit(self._selectedSignal, si)
                self._selectedSignal.unselect()
                self._selectedSignal = si
                self.messageLogger.addMessage(
                    self.tr("No route between signals"),
                    logger.Message.PLAYER_WARNING_MSG
                )

    @QtCore.pyqtSlot(int)
    def desactivateRoute(self, siId):
        """ This slot is normally connected to the signal
        SignalItem.signalUnselected(SignalItem), which itself is emitted when
        a signal is right-clicked. It is in charge of deactivating the routes
        starting from this signal.
        @param siId ID of the signalItem owner of the signalGraphicsItem
        that has been right-clicked."""
        si = self._trackItems[siId]
        if self._selectedSignal is not None:
            # Unselect the selected signal if any
            self._selectedSignal.unselect()
            self._selectedSignal = None
        r = si.nextActiveRoute
        if r is not None:
            r.desactivate()

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

    def updateSelection(self):
        """Updates the trackItem selection. Does nothing in the base
        simulation class."""
        pass

    def updatePlaces(self):
        """Updates the places dictionary from TrackItem data."""
        self._places = {}
        for ti in self.trackItems.values():
            if isinstance(ti, placeitem.Place):
                self._places[ti.placeCode] = ti

    def findRoute(self, si1, si2):
        """Checks whether a route exists between two signals, and return this
        route or None.
        @param si1 The signalItem of the first signal
        @param si2 The signalItem of the second signal
        @return The route between signal si1 and si2 if it exists, None
        otherwise"""
        for r in self._routes.values():
            if r.links(si1, si2):
                return r
        return None

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
                    elif isinstance(vi, pointsitem.PointsItem):
                        if self.distanceBetween(vi.reverse, vj.origin) <= 1.0:
                            vi.reverseItem = vj
                            vj.previousItem = vi
                        elif self.distanceBetween(vi.reverse, vj.end) <= 1.0:
                            vi.reverseItem = vj
                            vj.nextItem = vi
                    elif isinstance(vj, pointsitem.PointsItem):
                        if self.distanceBetween(vi.origin, vj.reverse) <= 1.0:
                            vi.previousItem = vj
                            vj.reverseItem = vi
                        elif self.distanceBetween(vi.end, vj.reverse) <= 1.0:
                            vi.nextItem = vj
                            vj.reverseItem = vi

    def checkTrackItemsLinks(self):
        """Checks that all TrackItems are linked together"""
        result = True
        self.messageLogger.addMessage(self.tr("Checking TrackItem links"),
                                      logger.Message.SOFTWARE_MSG)
        for ti in self._trackItems.values():
            if not isinstance(ti, placeitem.Place) \
                    and not isinstance(ti, platformitem.PlatformItem) \
                    and not isinstance(ti, textitem.TextItem):
                if ti.nextItem is None and not isinstance(ti, enditem.EndItem):
                    self.messageLogger.addMessage(
                        self.tr("TrackItem %i is unlinked at (%f, %f)" %
                                (ti.tiId, ti.end.x(), ti.end.y())),
                        logger.Message.SOFTWARE_MSG
                    )
                    result = False
                if ti.previousItem is None:
                    self.messageLogger.addMessage(
                        self.tr("TrackItem %i is unlinked at (%f, %f)" %
                                (ti.tiId, ti.origin.x(), ti.origin.y())),
                        logger.Message.SOFTWARE_MSG
                    )
                    result = False
        return result

    @staticmethod
    def distanceBetween(p1, p2):
        """Calculates the distance between both points p1 and p2 in pixels
        @param p1
        @param p2
        @return"""
        return sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2)

    def getLineItem(self, placeCode, trackCode):
        """Returns the LineItem instance defined by placeCode and trackCode.
        """
        for ti in self._trackItems.values():
            if isinstance(ti, lineitem.LineItem):
                if ti.placeCode == placeCode and ti.trackCode == trackCode:
                    return ti
        return None
