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

from PyQt4.QtCore import *
from PyQt4.QtSql import *
from math import sqrt

class Simulation(QObject):
    def __init__(self):
        """ Creates the unique Simulation instance (which is accessible through Simulation::instance())
        or throws an Exception, if a simulation is already loaded. """
        super().__init__()
        if not Simulation._self.hasattr(_scene):
            Simulation._self = self
            self._scene = QGraphicsScene()
            self._selectedSignal = None
            self._timer = QTimer(self)
            self._options = {}
            self._routes = {}
            self._trackItems = {}
            self._activeRouteNumbers = []
            self._trainTypes = {}
            self._services = {}
            self._places = {}
            self._trains = []
            self._time = QTime()
            self._timer = QTimer()
        else:
            raise Exception(tr("A simulation is already loaded"))
    
    @staticmethod
    def instance():
        return Simulation._self

    @pyqtProperty(QGraphicsScene)
    def scene(self):
        return self._scene
    
    def option(self, key):
        return self._options[key]
        
    def setOption(self, key, value): 
        self._options[key] = value

    @pyqtProperty(QTime)
    def currentTime(self):
        return self._time

    def reload():
        """Load or reload all the data of the simulation from the database."""
        self.loadOptions()
        self.loadPlaces()
        self.loadTrackItems()
        self.loadRoutes()
        self.loadTrainTypes()
        self.loadServices()
        self.loadTrains()
        self.setupConnections()
        QSqlDatabase.database.close()
        self.simulationLoaded.emit()
        self._scene.update()
        
        self._time = QTime.fromString(option("currentTime"), "hh:mm:ss")
        self._timer.timeout.connect(self.timerOut)
        self.interval = qBound(100, (int)(5000 / option("timeFactor").toDouble()), 500);
        self._timer.setInterval(interval)
        self._timer.start()
    
    def train(self, serviceCode):
        """Returns the Train object corresponding to the train whose serviceCode is currently serviceCode"""
        for t in self._trains:
            if t.serviceCode == serviceCode:
                return t
        return None
    
    def trains(self):
        return self._trains

    def trackItem(self, id):
        return self._trackItems[id]
    
    def place(self, placeCode):
        return self._places[placeCode]
    
    def service(self, serviceCode):
        return self._services[serviceCode]
    
    def services(self):
        return self._services

    def registerGraphicsItem(self, graphicItem):
        self._scene.addItem(graphicItem)

    simulationLoaded = pyqtSignal()
    conflictingRoute = pyqtSignal(Route)
    noRouteBetweenSignals = pyqtSignal(SignalItem, SignalItem)
    routeSelected = pyqtSignal(Route)
    routeDeleted = pyqtSignal(Route)
    timeChanged = pyqtSignal(QTime)
    timeElapsed = pyqtSignal(float)

    @pyqtSlot(SignalItem, bool)
    def createRoute(self, si, persistent = false):
        """This slot is normally connected to the signal SignalItem.signalSelected(SignalItem),
        which itself is emitted when a signal is left-clicked.
        It is in charge of:
        - Checking whether this is the first signal to be selected, if it the case,
        _selectedSignal is set to this signal and the function returns;
        - Otherwise, it checks whether there exists a possible route between
        _selectedSignal and this signal. If it is the case, and that no other active
        route conflicts with this route, it is activated.
        
        The following signals are emited depending of the situation:
        - routeActivated
        - noRouteBetweenSignals
        - conflictingRoute
        @param si Pointer to the signalItem owner of the signalGraphicsItem that has been
        left-clicked."""
        if self._selectedSignal is None or self._selectedSignal == si:
            # First signal selected
            self._selectedSignal = si
        else:
            # Second signal selected
            r = findRoute(self._selectedSignal, si)
            if r is not None:
                # There exists a route between both signals
                if r.isActivable:
                    # We can activate it
                    r.activate(persistent)
                    self._selectedSignal.unselect()
                    self._selectedSignal = None
                    si.unselect()
                else:
                    # We cannot activate it (another route is conflicting)
                    self.conflictingRoute.emit(r)
                    si.unselect()
                    qWarning.add(tr("Conflicting route"))
            else:
                # No route between both signals
                self.noRouteBetweenSignals.emit(_selectedSignal, si)
                si.unselect()
                qWarning.add(tr("No route between signals"))
  
    @pyqtSlot(SignalItem)
    def deleteRoute(self, si):
        """ This slot is normally connected to the signal SignalItem.signalUnselected(SignalItem),
        which itself is emitted when a signal is right-clicked.
        It is in charge of deactivating the routes starting from this signal.
        @param si Pointer to the signalItem owner of the signalGraphicsItem that has been
        right-clicked."""
        if self._selectedSignal is not None:
            # Unselect the selected signal if any
            self._selectedSignal.unselect()
            self._selectedSignal = None
        r = si.nextActiveRoute()
        if r is not None:
            r.desactivate
            self.routeDeleted.emit(r)
    
    @pyqtSlot(bool)
    def pause(self, paused):
        """ Toggle pause.
        @param paused If paused is true pause the game, else restart.
        """
        if paused:
            self._timer.stop()
        else:
            self._timer.start()
    
    @pyqtSlot(int)
    def setTimeFactor(self, timeFactor):
        """Sets the time factor to timeFactor."""
        self._timer.stop()
        self.setOption("timeFactor", timeFactor)
        if timeFactor != 0:
            self._timer.start()
    
    @pyqtSlot()
    def timerOut(self):
        """ Changes the simulation time and emits the timeChanged and the
        timeElapsed signals
        This function is normally connected to the timer timeout signal."""
        timeFactor = self.option("timeFactor");
        self._time = self._time.addMSecs((self._timer.interval) * timeFactor)
        self.timeChanged.emit(self._time)
        secs = self._timer.interval * timeFactor / 1000
        self.timeElapsed.emit(secs)

    def loadRoutes(self):
        """Creates the instances of routes from the data of the database."""
        routeModel = QSqlQueryModel()
        routeModel.setQuery("SELECT * FROM routes")
        for i in range(routeModel.rowCount()):
            routeNum = routeModel.record(i).value("routenum").toInt()
            beginSignal = routeModel.record(i).value("beginsignal").toInt()
            endSignal = routeModel.record(i).value("endsignal").toInt()
            bs = self._trackItems[beginSignal]
            es = self._trackItems[endSignal]
            route = Route(self, routeNum, bs, es)
            self._routes[routeNum] = route

        routeModel.setQuery("SELECT * FROM directions")
        for i in range(routeModel.rowCount()):
            routeNum = routeModel.record(i).value("routenum").toInt()
            tiId = routeModel.record(i).value("tiid").toInt()
            direction = routeModel.record(i).value("direction").toInt()
            self._routes[routeNum].appendDirection(tiId, direction)

        routeModel.setQuery("SELECT * FROM routeconflicts")
        for i in (routeModel.rowCount()):
            routeNum1 = routeModel.record(i).value("routenum1").toInt()
            routeNum2 = routeModel.record(i).value("routenum2").toInt()
            self._routes[routeNum1].addConflictRouteNumber(routeNum2)
            self._routes[routeNum2].addConflictRouteNumber(routeNum1)

        check = true
        for route in self._routes:
            check = (route.createPositionsList() and check)

        if not check:
            qFatal("Invalid simulation: Some routes are not valid.\nSee stderr for more information")
    
    def loadTrainTypes(self):
        """Creates the instances of TrainType from the data of the database."""
        ttModel = QSqlQueryModel()
        ttModel.setQuery("SELECT * FROM traintypes")
        for i in range(ttModel.rowCount()):
            code = ttModel.record(i).value("code").toString()
            description = ttModel.record(i).value("description").toString()
            maxSpeed = ttModel.record(i).value("maxspeed").toDouble()
            stdAccel = ttModel.record(i).value("stdaccel").toDouble()
            stdBraking = ttModel.record(i).value("stdbraking").toDouble()
            emergBraking = ttModel.record(i).value("emergbraking").toDouble()
            length = ttModel.record(i).value("tlength").toDouble()
            self._trainTypes[code] = TrainType(code, description, maxSpeed, stdAccel, stdBraking, emergBraking, length)
    
    def loadTrains(self):
        """Creates the instances of Train from the data of the database."""
        trainModel = QSqlQueryModel()
        trainModel.setQuery("SELECT * FROM trains")
        for i in range(trainModel.rowCount()):
            serviceCode = trainModel.record(i).value("servicecode").toString()
            trainType = trainModel.record(i).value("traintype").toString()
            speed = trainModel.record(i).value("speed").toDouble()
            accel = trainModel.record(i).value("accel").toDouble()
            tiId = trainModel.record(i).value("tiid").toInt()
            previousTiId = trainModel.record(i).value("previoustiid").toInt()
            posOnTI = trainModel.record(i).value("posonti").toDouble()
            appearTime = trainModel.record(i).value("appeartime").toTime()
            train = Train(serviceCode, _trainTypes[trainType], speed, accel, Position( \
                    _trackItems[tiId], _trackItems[previousTiId], posOnTI), appearTime)
            self._trains.append(train)
    
    def loadOptions(self):
        """Populates the options dict with data from the database"""
        optionModel = QSqlQueryModel()
        optionModel.setQuery("SELECT * FROM options")
        for i in range(optionModel.rowCount()):
            key = optionModel.record(i).value("optionKey").toString()
            value = optionModel.record(i).value("optionValue").toString()
            self._options[key] = value
    
    def loadTrackItems(self):
        """Creates the instances of trackItems and its subclasses from the data of the database."""
        tiModel = QSqlQueryModel()
        tiModel.setQuery("SELECT * FROM trackitems")

        for i in range(tiModel.rowCount()):
            record = tiModel.record(i)
            tiId = record.value("tiid").toInt()
            tiType = record.value("titype").toString()
            if tiType == "L":
                ti = LineItem(self, record)
            elif tiType == "LP":
                ti = PlatformItem(self, record)
            elif tiType == "S":
                ti = SignalItem(self, record)
            elif tiType == "SB":
                ti = BumperItem(self, record)
            elif tiType == "ST":
                ti = SignalTimerItem(self, record)
            elif tiType == "P":
                ti = PointsItem(self, record)
            elif tiType == "E":
                ti = EndItem(self, record)
            else:
                ti = TrackItem(self, record)
            self._trackItems[tiId] = ti

        # Set the explicit links (i.e. those that are recorded in db)
        for i in range(tiModel.rowCount()):
            tiId = tiModel.record(i).value("tiid").toInt()
            nextTiId = tiModel.record(i).value("ntiid").toInt()
            previousTiId = tiModel.record(i).value("ptiid").toInt()
            reverseTiId = tiModel.record(i).value("rtiid").toInt()
            if nextTiId != 0:
                self._trackItems[tiId].setNextItem(self._trackItems[nextTiId])
            if previousTiId != 0:
                self._trackItems[tiId].setPreviousItem(self._trackItems[previousTiId])
            if reverseTiId != 0 and self._trackItems[tiId].tiType == "P":
                self._trackItems[tiId].setReverseItem(self._trackItems[reverseTiId])
        
        # Set the implicit links
        self.createTrackItemsLinks()

        
        # Create trackItem conflicts
        for i in range(tiModel.rowCount()):
            conflictTiId = tiModel.record(i).value("conflicttiid").toInt()
            if conflictTiId != 0:
                tiId = tiModel.record(i).value("tiid").toInt()
                self._trackItems[tiId].setConflictTI(self._trackItems[conflictTiId])
                self._trackItems[conflictTiId].setConflictTI(self._trackItems[tiId])

        # Check that all the items are linked
        if not checkTrackItemsLinks():
            qFatal("Invalid simulation: Not all items are linked.\nSee stderr for more information")
  
    def loadServices(self):
        """Creates the instances of Service from the data of the database."""
        serviceModel = QSqlQueryModel ()
        serviceModel.setQuery("SELECT * FROM services")
        for i in range(serviceModel.rowCount()):
            serviceCode = serviceModel.record(i).value("servicecode").toString()
            description = serviceModel.record(i).value("description").toString()
            nextService = serviceModel.record(i).value("nextservice").toString()
            self._services[serviceCode] = Service(serviceCode, description, nextService)

        serviceModel.setQuery("SELECT * FROM serviceLines")
        for i in range(serviceModel.rowCount()):
            serviceCode = serviceModel.record(i).value("servicecode").toString()
            placeCode = serviceModel.record(i).value("placecode").toString()
            scheduledArrivalTime = serviceModel.record(i).value("scheduledarrivaltime").toTime()
            scheduledDepartureTime = serviceModel.record(i).value("scheduleddeparturetime").toTime()
            trackCode = serviceModel.record(i).value("trackcode").toString()
            stop = serviceModel.record(i).value("stop").toBool()
            self._services[serviceCode].addLine(placeCode, scheduledArrivalTime, scheduledDepartureTime, trackCode, stop)

        for s in _services:
            s.start()
    
    def loadPlaces(self):
        """Creates the instances of Place from the data of the database."""
        placeModel = QSqlQueryModel()
        placeModel.setQuery("SELECT * FROM places")
        for i in range(placeModel.rowCount()):
            placeCode = placeModel.record(i).value("placecode").toString()
            placeName = placeModel.record(i).value("placename").toString()
            x = placeModel.record(i).value("x").toDouble()
            y = placeModel.record(i).value("y").toDouble()
            self._places[placeCode] = Place(placeCode, placeName, x, y)
    
    def setupConnections(self):
        """Sets up the connections which need a simulation loaded"""
        self.timeChanged.connect(Train.selectedTrainModel.update)

    def findRoute(self, si1, si2):
        """Checks whether a route exists between two signals, and return this route or 0.
        @param si1 The signalItem of the first signal
        @param si2 The signalItem of the second signal
        @return The route between signal si1 and si2 if it exists, 0 otherwise"""
        for r in _routes:
            if r.links(si1, si2):
                return r;
        return None;
    
    def createTrackItemsLinks(self):
        """Find the items that are linked together through their coordinates and populate the 
        _nextItem and _previousItem variables of each items."""
        keys = self._trackItems.keys()
        values = self._trackItems.values()
        for i in range(len(keys)): # this iteration on the index of the keys is really dirty ...
            ri = values[i]
            if ri != 0:
                for j in values[i+1:]:
                    rj = values[j]
                    if rj != 0:
                        if distanceBetween(ri.origin, rj.origin) <= 1.0:
                            ri.setPreviousItem(rj)
                            rj.setPreviousItem(ri)
                        elif distanceBetween(ri.origin(), rj.end()) <= 1.0:
                            ri.setPreviousItem(rj)
                            rj.setNextItem(ri)
                        elif distanceBetween(ri.end(), rj.origin()) <= 1.0:
                            ri.setNextItem(rj)
                            rj.setPreviousItem(ri)
                        elif distanceBetween(ri.end(), rj.end()) <= 1.0:
                            ri.setNextItem(rj)
                            rj.setNextItem(ri)
    
    
    def checkTrackItemsLinks(self):
        """Checks that all TrackItems are linked together"""
        result = true;
        for ti in _trackItems:
            if ti.nextItem is None:
                qCritical(tr("TrackItem %1 is unlinked at (%2, %3)") \
                              .arg(ti.tiId()) \
                              .arg(ti.end().x()) \
                              .arg(ti.end().y())) 
                result = false
            if ti.previousItem is None:
                qCritical(tr("TrackItem %1 is unlinked at (%2, %3)") \
                              .arg(ti.tiId()) \
                              .arg(ti.origin().x()) \
                              .arg(ti.origin().y())) 
                result = false
        return result

    def distanceBetween(self, p1, p2):
        """Calculates the distance between both points p1 and p2 in pixels
        @param p1
        @param p2
        @return"""
        return sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2)

