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
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from PyQt4.QtGui import *
from math import sqrt
from route import *
from signalitem import *
from pointsitem import *
from train import *
from lineitem import *
from trackitem import *
from platformitem import *
from bumperitem import *
from enditem import *
from signaltimeritem import *
from traintype import *

class Simulation(QObject):
    
    _self = None
    
    def __init__(self, simulationWindow):
        """ Creates the unique Simulation instance (which is accessible through Simulation::instance())
        or throws an Exception, if a simulation is already loaded. """
        super().__init__()
        if Simulation._self is None or not Simulation._self.hasattr("_scene"):
            Simulation._self = self
            self._simulationWindow = simulationWindow
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
            self._serviceListModel = ServiceListModel(self)
            self._selectedServiceModel = ServiceInfoModel(self)
            self._trainListModel = TrainListModel(self)
            self._selectedTrainModel = TrainInfoModel(self)
        else:
            raise Exception(self.tr("A simulation is already loaded"))

    @property
    def scene(self):
        return self._scene
    
    @property
    def simulationWindow(self):
        return self._simulationWindow
    
    def option(self, key):
        return self._options[key]
        
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

    def reload(self):
        """Load or reload all the data of the simulation from the database."""
        self.loadOptions()
        self.loadPlaces()
        self.loadTrackItems()
        self.loadRoutes()
        self.loadTrainTypes()
        self.loadServices()
        self.loadTrains()
        self.setupConnections()
        QSqlDatabase.database().close()
        self.simulationLoaded.emit()
        self._scene.update()
        self._time = QTime.fromString(self.option("currentTime"), "hh:mm:ss")
        self._timer.timeout.connect(self.timerOut)
        interval = min(max (100, 5000 / float(self.option("timeFactor"))), 500)
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
        if (placeCode != "") and (not isinstance(placeCode, QPyNullVariant)):
            return self._places[placeCode]
        else:
            return None
    
    def service(self, serviceCode):
        return self._services[serviceCode]
    
    def services(self):
        return self._services
    
    def servicesList(self):
        return list(self._services.values())

    def registerGraphicsItem(self, graphicItem):
        self._scene.addItem(graphicItem)

    simulationLoaded = pyqtSignal()
    conflictingRoute = pyqtSignal(Route)
    noRouteBetweenSignals = pyqtSignal(SignalItem, SignalItem)
    routeSelected = pyqtSignal(Route)
    routeDeleted = pyqtSignal(Route)
    timeChanged = pyqtSignal(QTime)
    timeElapsed = pyqtSignal(float)
    trainSelected = pyqtSignal(str)

    @pyqtSlot(int, bool)
    def createRoute(self, siId, persistent = False):
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
                    qWarning(self.tr("Conflicting route"))
            else:
                # No route between both signals
                self.noRouteBetweenSignals.emit(self._selectedSignal, si)
                si.unselect()
                qWarning(self.tr("No route between signals"))
  
    @pyqtSlot(int)
    def deleteRoute(self, siId):
        """ This slot is normally connected to the signal SignalItem.signalUnselected(SignalItem),
        which itself is emitted when a signal is right-clicked.
        It is in charge of deactivating the routes starting from this signal.
        @param si Pointer to the signalItem owner of the signalGraphicsItem that has been
        right-clicked."""
        si = self._trackItems[siId]
        if self._selectedSignal is not None:
            # Unselect the selected signal if any
            self._selectedSignal.unselect()
            self._selectedSignal = None
        r = si.nextActiveRoute
        if r is not None:
            r.desactivate()
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
        self.setOption("timeFactor", min(timeFactor, 10))
        if timeFactor != 0:
            self._timer.start()
    
    @pyqtSlot()
    def timerOut(self):
        """ Changes the simulation time and emits the timeChanged and the
        timeElapsed signals
        This function is normally connected to the timer timeout signal."""
        timeFactor = float(self.option("timeFactor"))
        self._time = self._time.addMSecs((self._timer.interval()) * timeFactor)
        self.timeChanged.emit(self._time)
        secs = self._timer.interval() * timeFactor / 1000
        self.timeElapsed.emit(secs)
            
    def loadRoutes(self):
        """Creates the instances of routes from the data of the database."""
        routeModel = QSqlQueryModel()
        routeModel.setQuery("SELECT * FROM routes")
        for i in range(routeModel.rowCount()):
            routeNum = self.dbReadInt(routeModel, i, "routenum")
            beginSignalId = self.dbReadInt(routeModel, i, "beginsignal")
            endSignalId = self.dbReadInt(routeModel, i, "endsignal")
            bs = self._trackItems[beginSignalId]
            es = self._trackItems[endSignalId]
            route = Route(self, routeNum, bs, es)
            self._routes[routeNum] = route

        routeModel.setQuery("SELECT * FROM directions")
        for i in range(routeModel.rowCount()):
            routeNum = self.dbReadInt(routeModel, i, "routenum")
            tiId = self.dbReadInt(routeModel, i, "tiid")
            direction = self.dbReadInt(routeModel, i, "direction")
            self._routes[routeNum].appendDirection(tiId, direction)

        check = True
        for route in self._routes.values():
            check = (route.createPositionsList() and check)

        if not check:
            qCritical(self.tr("Invalid simulation: Some routes are not valid.\nSee stderr for more information"))
            ### DEBUG 
            #qFatal(self.tr("Invalid simulation: Some routes are not valid.\nSee stderr for more information"))
    
    def loadTrainTypes(self):
        """Creates the instances of TrainType from the data of the database."""
        ttModel = QSqlQueryModel()
        ttModel.setQuery("SELECT * FROM traintypes")
        for i in range(ttModel.rowCount()):
            code = ttModel.record(i).value("code")
            description = ttModel.record(i).value("description")
            maxSpeed = ttModel.record(i).value("maxspeed")
            stdAccel = ttModel.record(i).value("stdaccel")
            stdBraking = ttModel.record(i).value("stdbraking")
            emergBraking = ttModel.record(i).value("emergbraking")
            length = ttModel.record(i).value("tlength")
            self._trainTypes[code] = TrainType(code, description, maxSpeed, stdAccel, stdBraking, emergBraking, length)
    
    def loadTrains(self):
        """Creates the instances of Train from the data of the database."""
        trainModel = QSqlQueryModel()
        trainModel.setQuery("SELECT * FROM trains")
        for i in range(trainModel.rowCount()):
            serviceCode = self.dbReadStr(trainModel, i, "servicecode")
            trainType = self.dbReadStr(trainModel, i, "traintype")
            speed = self.dbReadFloat(trainModel, i, "speed")
            accel = self.dbReadFloat(trainModel, i, "accel")
            tiId = self.dbReadInt(trainModel, i, "tiid")
            previousTiId = self.dbReadInt(trainModel, i, "previoustiid")
            posOnTI = self.dbReadFloat(trainModel, i, "posonti")
            appearTime = QTime.fromString(self.dbReadStr(trainModel, i, "appeartime"))
            train = Train(self, serviceCode, self._trainTypes[trainType], speed, accel, Position( \
                    self._trackItems[tiId], self._trackItems[previousTiId], posOnTI), appearTime)
            self._trains.append(train)
    
    def loadOptions(self):
        """Populates the options dict with data from the database"""
        optionModel = QSqlQueryModel()
        optionModel.setQuery("SELECT * FROM options")
        for i in range(optionModel.rowCount()):
            key = self.dbReadStr(optionModel, i, "optionKey")
            value = self.dbReadStr(optionModel, i, "optionValue")
            if key != "":
                self._options[key] = value
    
    def loadTrackItems(self):
        """Creates the instances of trackItems and its subclasses from the data of the database."""
        tiModel = QSqlQueryModel()
        tiModel.setQuery("SELECT * FROM trackitems")

        for i in range(tiModel.rowCount()):
            record = tiModel.record(i)
            tiId = self.dbReadInt(tiModel, i, "tiid")
            tiType = self.dbReadStr(tiModel, i, "titype")
            if tiType == "L":
                ti = LineItem(self, record)
            elif tiType == "LP":
                ti = PlatformItem(self, record)
            elif tiType == "S":
                ti = SignalItem(self, record)
            elif tiType == "SB":
                ti = BumperItem(self, record)
            elif tiType == "ST":
                ti = SignalTimerItem(self, record, float(self.option("timeFactor")))
            elif tiType == "P":
                ti = PointsItem(self, record)
            elif tiType == "E":
                ti = EndItem(self, record)
            else:
                ti = TrackItem(self, record)
            self._trackItems[tiId] = ti

        # Set the explicit links (i.e. those that are recorded in db)
        for i in range(tiModel.rowCount()):
            tiId = self.dbReadInt(tiModel, i, "tiid")
            nextTiId = self.dbReadInt(tiModel, i, "ntiid")
            previousTiId = self.dbReadInt(tiModel, i, "ptiid")
            reverseTiId = self.dbReadInt(tiModel, i , "rtiid")
            if nextTiId != 0:
                self._trackItems[tiId].nextItem = self._trackItems[nextTiId]
            if previousTiId != 0:
                self._trackItems[tiId].previousItem = self._trackItems[previousTiId]
            if reverseTiId != 0:
                self._trackItems[tiId].reverseItem = self._trackItems[reverseTiId]
        
        # Set the implicit links
        self.createTrackItemsLinks()

        # Create trackItem conflicts
        for i in range(tiModel.rowCount()):
            conflictTiId = self.dbReadInt(tiModel, i, "conflicttiid")
            if conflictTiId != 0:
                tiId = self.dbReadInt(tiModel, i, "tiid")
                self._trackItems[tiId].conflictTI = self._trackItems[conflictTiId]
                self._trackItems[conflictTiId].conflictTI = self._trackItems[tiId]

        # Check that all the items are linked
        if not self.checkTrackItemsLinks():
            qFatal("Invalid simulation: Not all items are linked.\nSee stderr for more information")
            
  
    def loadServices(self):
        """Creates the instances of Service from the data of the database."""
        serviceModel = QSqlQueryModel ()
        serviceModel.setQuery("SELECT * FROM services")
        for i in range(serviceModel.rowCount()):
            serviceCode = self.dbReadStr(serviceModel, i, "servicecode")
            description = self.dbReadStr(serviceModel, i, "description")
            nextService = self.dbReadStr(serviceModel, i, "nextservice")
            self._services[serviceCode] = Service(self, serviceCode, description, nextService)

        serviceModel.setQuery("SELECT * FROM serviceLines")
        for i in range(serviceModel.rowCount()):
            serviceCode = self.dbReadStr(serviceModel, i, "servicecode")
            placeCode = self.dbReadStr(serviceModel, i, "placecode")
            scheduledArrivalTime = QTime.fromString(self.dbReadStr(serviceModel, i, "scheduledarrivaltime"))
            scheduledDepartureTime = QTime.fromString(self.dbReadStr(serviceModel, i, "scheduleddeparturetime"))
            trackCode = self.dbReadStr(serviceModel, i, "trackcode")
            stop = self.dbReadInt(serviceModel, i, "stop")
            self._services[serviceCode].addLine(placeCode, scheduledArrivalTime, scheduledDepartureTime, trackCode, stop)

        for s in self._services.values():
            s.start()
    
    def loadPlaces(self):
        """Creates the instances of Place from the data of the database."""
        placeModel = QSqlQueryModel()
        placeModel.setQuery("SELECT * FROM places")
        for i in range(placeModel.rowCount()):
            placeCode = self.dbReadStr(placeModel, i, "placecode")
            placeName = self.dbReadStr(placeModel, i, "placename")
            x = self.dbReadFloat(placeModel, i, "x")
            y = self.dbReadFloat(placeModel, i, "y")
            place = Place(self, placeCode, placeName, x, y)
            self._places[placeCode] = place
    
    def setupConnections(self):
        """Sets up the connections which need a simulation loaded"""
        self.timeChanged.connect(self.selectedTrainModel.update)

    def findRoute(self, si1, si2):
        """Checks whether a route exists between two signals, and return this route or 0.
        @param si1 The signalItem of the first signal
        @param si2 The signalItem of the second signal
        @return The route between signal si1 and si2 if it exists, 0 otherwise"""
        for r in self._routes.values():
            if r.links(si1, si2):
                return r;
        return None;
    
    def createTrackItemsLinks(self):
        """Find the items that are linked together through their coordinates and populate the 
        _nextItem and _previousItem variables of each items."""
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
    
    def checkTrackItemsLinks(self):
        """Checks that all TrackItems are linked together"""
        result = True;
        qDebug(self.tr("Checking TrackItem links"))
        for ti in self._trackItems.values():
            if ti.nextItem is None:
                qCritical(self.tr("TrackItem %1 is unlinked at (%2, %3)") \
                              .arg(ti.tiId()) \
                              .arg(ti.end().x()) \
                              .arg(ti.end().y())) 
                result = False
            if ti.previousItem is None:
                qCritical(self.tr("TrackItem %1 is unlinked at (%2, %3)") \
                              .arg(ti.tiId()) \
                              .arg(ti.origin().x()) \
                              .arg(ti.origin().y())) 
                result = False
        return result

    def distanceBetween(self, p1, p2):
        """Calculates the distance between both points p1 and p2 in pixels
        @param p1
        @param p2
        @return"""
        return sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2)

    def dbReadInt(self, model, row, column):
        dbOutput = model.record(row).value(column)
        if not isinstance(dbOutput, QPyNullVariant):
            return int(dbOutput)
        else:
            return 0
    
    def dbReadFloat(self, model, row, column):
        dbOutput = model.record(row).value(column)
        if not isinstance(dbOutput, QPyNullVariant):
            return int(dbOutput)
        else:
            return 0
        
    def dbReadStr(self, model, row, column):
        dbOutput = model.record(row).value(column)
        if not isinstance(dbOutput, QPyNullVariant):
            return str(dbOutput)
        else:
            return ""
        