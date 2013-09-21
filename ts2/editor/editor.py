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

import sqlite3
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from ts2 import simulation
from ts2 import scenery, utils, trains, routing
import ts2.editor

class TrashBinItem(QtGui.QGraphicsPixmapItem):
    """The TrashBinItem is the graphics item on which to drag TrackItems to be
    deleted
    """
    def __init__(self, editor, scene, pos):
        """Constructor for the TrashBinItem class"""
        super().__init__(None, scene)
        self.setPos(pos)
        self.setPixmap(QtGui.QPixmap(":/bin.png"))
        self.setAcceptDrops(True)
        self._editor = editor

    def dropEvent(self, event):
        """Handler for the drop event. Deletes the TrackItem that has been
        dropped on the TrashBinItem"""
        if event.mimeData().hasText():
            tiType, tiId, ox, oy, point = event.mimeData().text().split("#")
            if int(tiId) < 0:
                event.ignore()
            else:
                event.accept()
                self._editor.deleteTrackItem(tiId)
        else:
            event.ignore()


class WhiteLineItem(QtGui.QGraphicsLineItem):
    """Shortcut class to make white line items"""
    def __init__(self, x1, y1, x2, y2, parent, scene):
        """Constructor for the WhiteLineItem class"""
        super().__init__(x1, y1, x2, y2, parent, scene)
        self.setPen(Qt.white)
        self.update()


class OptionsModel(QtCore.QAbstractTableModel):
    """Model for editing options in the editor.
    """
    def __init__(self, editor):
        """Constructor for the OptionsModel class"""
        super().__init__()
        self._editor = editor

    def rowCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of rows of the model, corresponding to the
        number of real options."""
        return self._editor.realOptionsLength

    def columnCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of columns of the model"""
        return 2

    def data(self, index, role = Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole or role == Qt.EditRole:
            optionKeys = list(self._editor.realOptions.keys())
            optionValues = list(self._editor.realOptions.values())
            if index.column() == 0:
                return optionKeys[index.row()]
            elif index.column() == 1:
                return optionValues[index.row()]
        return None

    def setData(self, index, value, role):
        """Updates data when modified in the view"""
        if role == Qt.EditRole:
            if index.column() == 1:
                optionKey = str(index.sibling(index.row(), 0).data())
                self._editor.setOption(optionKey, value)
                return True
        return False

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        """Returns the header labels"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return self.tr("Option")
            elif section == 1:
                return self.tr("Value")
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        retFlag = Qt.ItemIsEnabled
        if index.column() == 1:
            retFlag |= Qt.ItemIsEditable | Qt.ItemIsSelectable
        return retFlag



class Editor(simulation.Simulation):
    """The Editor class holds all the logic behind the simulation editor. It
    is a subclass of the Simulation class.
    """
    def __init__(self, editorWindow):
        """Constructor for the Editor class"""
        super().__init__(editorWindow)
        self._context = utils.Context.EDITOR_GENERAL
        self._libraryScene = QtGui.QGraphicsScene(0, 0, 200, 250, self)
        self._sceneBackground = ts2.editor.EditorSceneBackground(
                                                        self, 0, 0, 800, 600)
        self._sceneBackground.setZValue(-100)
        self._scene.addItem(self._sceneBackground)
        self.drawToolBox()
        self._sceneryValidated = False
        self._routesModel = routing.RoutesModel(self)
        self._trainTypesModel = trains.TrainTypesModel(self)
        self._servicesModel = trains.ServicesModel(self)
        self._serviceLinesModel = trains.ServiceLinesModel(self)
        self._trainsModel = trains.TrainsModel(self)
        self._optionsModel = OptionsModel(self)
        self._database = None
        self._nextId = 1
        self._nextRouteId = 1
        self._grid = 5.0
        self._preparedRoute = None
        self._selectedRoute = None
        self._selectedTrain = None
        self._displayedPositionGI = routing.PositionGraphicsItem(self)
        self.registerGraphicsItem(self._displayedPositionGI)
        self.trainsChanged.connect(self.unselectTrains)

    sceneryIsValidated = QtCore.pyqtSignal(bool)
    routesChanged = QtCore.pyqtSignal()
    trainTypesChanged = QtCore.pyqtSignal()
    servicesChanged = QtCore.pyqtSignal()
    serviceLinesChanged = QtCore.pyqtSignal()
    trainsChanged = QtCore.pyqtSignal()
    optionsChanged = QtCore.pyqtSignal()

    def drawToolBox(self):
        """Construct the library tool box"""
        # Lines
        WhiteLineItem(0, 0, 0, 350, None, self._libraryScene)
        WhiteLineItem(100, 0, 100, 300, None, self._libraryScene)
        WhiteLineItem(200, 0, 200, 350, None, self._libraryScene)
        WhiteLineItem(0, 0, 200, 0, None, self._libraryScene)
        WhiteLineItem(0, 50, 200, 50, None, self._libraryScene)
        WhiteLineItem(0, 100, 200, 100, None, self._libraryScene)
        WhiteLineItem(0, 150, 200, 150, None, self._libraryScene)
        WhiteLineItem(0, 200, 200, 200, None, self._libraryScene)
        WhiteLineItem(0, 250, 200, 250, None, self._libraryScene)
        WhiteLineItem(0, 300, 200, 300, None, self._libraryScene)
        WhiteLineItem(0, 350, 200, 350, None, self._libraryScene)
        # Items
        self.librarySignalItem = scenery.SignalItem(self,
                {"tiid":-1, "name":"Signal", "x":20, "y":30, "reverse":0,
                 "maxspeed":0.0})
        self.librarySignalTimerItem = scenery.SignalTimerItem(self,
                {"tiid":-2, "name":"Timer Signal", "x":120, "y":30,
                 "reverse":0, "maxspeed":0.0, "timersw":1.0, "timerwc":1.0})
        self.libraryPointsItem = scenery.PointsItem(self,
                {"tiid":-3, "name":"Points", "maxspeed":0.0, "x":50, "y":75,
                 "xf":-5, "yf":0, "xn":5, "yn":0, "xr":5, "yr":-5})
        self.libraryBumperItem = scenery.BumperItem(self,
                {"tiid":-4, "name":"Bumper", "maxspeed":0.0, "x":120, "y":75,
                 "reverse":0})
        self.libraryLineItem = scenery.LineItem(self,
                {"tiid":-5, "name":"Line", "x":20, "y":125, "xf":80,
                 "yf":125, "maxspeed":0.0, "reallength":1.0,
                 "placecode":None, "trackcode":None})
        self.libraryPlatformItem = scenery.PlatformItem(self,
                {"tiid":-6, "name":"Platform", "x":120, "y":135, "xf":180,
                 "yf":135,  "xn":125, "yn":120, "xr":175, "yr":130,
                 "maxspeed":0.0, "reallength":1.0,
                 "placecode":None, "trackcode":None})
        self.libraryEndItem = scenery.EndItem(self,
                {"tiid":-7, "name":"End", "maxspeed":0.0, "x":50, "y":175})
        self.libraryPlaceItem = scenery.Place(self,
                {"tiid":-8, "name":"PLACE", "placecode":"", "maxspeed":0.0,
                 "x":132, "y":180})
        self.libraryNonReturnItem = scenery.NonReturnItem(self,
                {"tiid":-9, "name":"Non-return", "maxspeed":0.0, "x":20,
                 "y":225, "reverse":0})
        self.libraryInvisibleLinkItem = scenery.InvisibleLinkItem(self,
                {"tiid":-10, "name":"Invisible link", "x":120, "y":225,
                 "xf":180, "yf":225, "maxspeed":0.0, "reallength":1.0,
                 "placecode":None, "trackcode":None})
        self.libraryTextItem = scenery.TextItem(self,
                {"tiid":-11, "name":"TEXT", "x":36, "y":280, "maxspeed":0.0,
                 "reallength":1.0, })
        self.libraryBinItem = TrashBinItem(self,
                                           self._libraryScene,
                                           QtCore.QPointF(86, 310))

    @property
    def libraryScene(self):
        """The pseudo-scene for the TrackItem "tool box" """
        return self._libraryScene

    @property
    def routesModel(self):
        """Returns the RoutesModel of this editor instance"""
        return self._routesModel

    @property
    def trainTypesModel(self):
        """Returns the TrainTypesModel of this editor"""
        return self._trainTypesModel

    @property
    def servicesModel(self):
        """Returns the ServicesModel of this editor"""
        return self._servicesModel

    @property
    def serviceLinesModel(self):
        """Returns the ServiceLinesModel of this editor"""
        return self._serviceLinesModel

    @property
    def trainsModel(self):
        """Returns the TrainsModel of this editor"""
        return self._trainsModel

    @property
    def optionsModel(self):
        """Returns the OptionsModel of this editor."""
        return self._optionsModel

    @property
    def database(self):
        """Returns the database filename, with full path"""
        return self._database

    @database.setter
    def database(self, value):
        """Setter function for the database property"""
        self._database = value

    @property
    def selectedRoute(self):
        """Returns the selected route in the route editor."""
        return self._selectedRoute

    @selectedRoute.setter
    def selectedRoute(self, value):
        """Setter function for the selectedRoute property"""
        if self._selectedRoute is not None:
            self._selectedRoute.desactivate()
        self._selectedRoute = value
        if self._selectedRoute is not None:
            self._selectedRoute.activate()

    @property
    def displayedPosition(self):
        """Returns the position that is currently selected in this editor"""
        return self._displayedPositionGI.position

    @displayedPosition.setter
    def displayedPosition(self, position):
        """Setter function for the displayedPosition property"""
        if self.context == utils.Context.EDITOR_TRAINS:
            self._displayedPositionGI.position = position

    @property
    def realOptions(self):
        """Returns a dictionary with the real options for the editor, i.e.
        without the title, description and version fields."""
        options = {}
        options.update(self._options)
        del options["title"]
        del options["description"]
        del options["version"]
        return options

    @property
    def realOptionsLength(self):
        """Returns the number of realOptions"""
        return len(self._options) - 3

    def reload(self, fileName):
        """Load or reload all the data of the simulation from the database."""
        conn = sqlite3.connect(fileName)
        conn.row_factory = sqlite3.Row
        self.loadOptions(conn)
        self.optionsChanged.emit()
        self.createAllTrackItems(conn)
        self.createTrackItemConflicts(conn)
        self.adjustSceneBackground()
        try:
            self._nextId = max(self._trackItems.keys()) + 1
        except ValueError:
            self._nextId = 1
        if self.validateScenery():
            self.loadRoutes(conn)
            try:
                self._nextRouteId = max(self._routes.keys()) + 1
            except ValueError:
                self._nextRouteId = 1
            self.routesChanged.emit()
        self.loadTrainTypes(conn)
        try:
            self._nextTrainTypeId = max(self._trainTypes.keys()) + 1
        except:
            self._nextTrainTypeId = 1
        self.trainTypesChanged.emit()
        self.loadServices(conn)
        self.servicesChanged.emit()
        self.loadTrains(conn)
        self.trainsChanged.emit()

    def save(self):
        """Saves the data of the simulation to the database"""
        # Set up database
        self.setOption("version", "0.3")
        conn = sqlite3.connect(self._database)
        self.saveOptions(conn)
        self.saveTrackItems(conn)
        self.saveRoutes(conn)
        self.saveTrainTypes(conn)
        self.saveServices(conn)
        self.saveTrains(conn)
        conn.close()

    def saveOptions(self, conn):
        """Saves the options of this editor in the database"""
        conn.execute("DROP TABLE IF EXISTS options")
        conn.execute("CREATE TABLE options (\n"
                     "optionkey VARCHAR(30),\n"
                     "optionvalue VARCHAR(50))")
        for key, value in self._options.items():
            query = "INSERT INTO options " \
                    "(optionkey, optionvalue) " \
                    "VALUES " \
                    "(:optionkey, :optionvalue)"
            parameters = {
                    "optionkey":key,
                    "optionvalue":value
                    }
            conn.execute(query, parameters)
        conn.commit()


    def saveTrackItems(self, conn):
        """Saves the TrackItem instances of this editor in the database"""
        conn.execute("DROP TABLE IF EXISTS trackitems")
        fieldString = "("
        for name, type in scenery.TrackItem.fieldTypes.items():
            fieldString += "%s %s," % (name, type)
        fieldString = fieldString[:-1] + ")"
        conn.execute("CREATE TABLE trackitems %s" % fieldString)
        for ti in self._trackItems.values():
            keysCodes = map(lambda a:":%s" % a, ti.saveParameters.keys())
            query = "INSERT INTO trackitems %s VALUES (" % \
                                        str(tuple(ti.saveParameters.keys()))
            for k in ti.saveParameters.keys():
                query += ":%s," % k
            query = query[:-1] + ")"
            conn.execute(query, ti.saveParameters)
            conn.commit()

    def saveRoutes(self, conn):
        """Saves the Route instances of this editor in the database"""
        # Save routes themselves
        conn.execute("DROP TABLE IF EXISTS routes")
        conn.execute("CREATE TABLE routes (\n"
                            "routenum INTEGER PRIMARY KEY,\n"
                            "beginsignal INTEGER,\n"
                            "endsignal INTEGER,\n"
                            "initialstate INTEGER)\n"
                    )
        for route in self._routes.values():
            query = "INSERT INTO routes " \
                    "(routenum, beginsignal, endsignal, initialstate) " \
                    "VALUES " \
                    "(:routenum, :beginsignal, :endsignal, :initialstate)"
            parameters = {
                    "routenum":route.routeNum,
                    "beginsignal":route.beginSignal.tiId,
                    "endsignal":route.endSignal.tiId,
                    "initialstate":route.initialState
                         }
            conn.execute(query, parameters)

        # Save the directions
        conn.execute("DROP TABLE IF EXISTS directions")
        conn.execute("CREATE TABLE directions (\n" \
                        "routenum INTEGER,\n" \
                        "tiid INTEGER,\n" \
                        "direction INTEGER)\n" \
                    )
        for route in self._routes.values():
            for tiId, direction in route.directions.items():
                query = "INSERT INTO directions " \
                        "(routenum, tiid, direction) " \
                        "VALUES " \
                        "(:routenum, :tiid, :direction)"
                parameters = { \
                        "routenum":route.routeNum, \
                        "tiid":tiId, \
                        "direction":direction \
                             }
                conn.execute(query, parameters)
        conn.commit()

    def saveTrainTypes(self, conn):
        """Saves the TrainType instances of this editor in the database"""
        conn.execute("DROP TABLE IF EXISTS traintypes")
        conn.execute("CREATE TABLE traintypes (\n" \
                            "code VARCHAR(10),\n" \
                            "description VARCHAR(200),\n" \
                            "maxspeed DOUBLE,\n" \
                            "stdaccel DOUBLE,\n" \
                            "stdbraking DOUBLE,\n" \
                            "emergbraking DOUBLE,\n" \
                            "tlength DOUBLE)")

        for trainType in self._trainTypes.values():
            query = "INSERT INTO traintypes " \
                    "(code, description, maxspeed, stdaccel, "\
                    "stdbraking, emergbraking, tlength) " \
                    "VALUES " \
                    "(:code, :description, :maxspeed, :stdaccel, "\
                    ":stdbraking, :emergbraking, :tlength)"
            parameters = { \
                    "code":trainType.code, \
                    "description":trainType.description, \
                    "maxspeed":trainType.maxSpeed, \
                    "stdaccel":trainType.stdAccel, \
                    "stdbraking":trainType.stdBraking, \
                    "emergbraking":trainType.emergBraking, \
                    "tlength":trainType.length}
            conn.execute(query, parameters)
        conn.commit()

    def saveServices(self, conn):
        """Saves the Service instances of this editor in the database"""
        conn.execute("DROP TABLE IF EXISTS services")
        conn.execute("CREATE TABLE services (\n" \
                            "servicecode VARCHAR(10),\n" \
                            "description VARCHAR(200),\n" \
                            "nextservice VARCHAR(10),\n" \
                            "autoreverse BOOLEAN)" \
                    )
        for service in self._services.values():
            query = "INSERT INTO services "\
                    "(servicecode, description, nextservice, autoreverse) "\
                    "VALUES " \
                    "(:servicecode, :description, :nextservice, :autoreverse)"
            parameters = { \
                    "servicecode":service.serviceCode,
                    "description":service.description,
                    "nextservice":service.nextServiceCode,
                    "autoreverse":service.autoReverse
                         }
            conn.execute(query, parameters)

        # Save the directions
        conn.execute("DROP TABLE IF EXISTS servicelines")
        conn.execute("CREATE TABLE servicelines (\n"
                            "servicecode VARCHAR(10),\n"
                            "placecode VARCHAR(10),\n"
                            "scheduledarrivaltime TIME,\n"
                            "scheduleddeparturetime TIME,\n"
                            "trackcode VARCHAR(10),\n"
                            "stop BOOLEAN)"
                    )
        for service in self._services.values():
            for sl in service.lines:
                query = "INSERT INTO servicelines " \
                        "(servicecode, placecode, scheduledarrivaltime, "\
                        "scheduleddeparturetime, trackcode, stop) " \
                        "VALUES " \
                        "(:servicecode, :placecode, :scheduledarrivaltime, " \
                        ":scheduleddeparturetime, :trackcode, :stop) "
                parameters = {
                    "servicecode":service.serviceCode,
                    "placecode":sl.placeCode,
                    "scheduledarrivaltime":sl.scheduledArrivalTimeStr,
                    "scheduleddeparturetime":sl.scheduledDepartureTimeStr,
                    "trackcode":sl.trackCode,
                    "stop":sl.mustStop
                             }
                conn.execute(query, parameters)
        conn.commit()

    def saveTrains(self, conn):
        """Saves the Train instances of this editor in the database"""
        conn.execute("DROP TABLE IF EXISTS trains")
        conn.execute("CREATE TABLE trains (\n"
                            "servicecode VARCHAR(10),\n"
                            "traintype VARCHAR(10),\n"
                            "speed DOUBLE,\n"
                            "tiid INTEGER,\n"
                            "previoustiid INTEGER,\n"
                            "posonti DOUBLE,\n"
                            "appeartime TIME)\n")

        for train in self._trains:
            query = "INSERT INTO trains " \
                    "(servicecode, traintype, speed, tiid, previoustiid, "\
                    "posonti, appeartime) " \
                    "VALUES " \
                    "(:servicecode, :traintype, :speed, :tiid, "\
                    ":previoustiid, :posonti, :appeartime)"
            parameters = {
                    "servicecode":train.serviceCode,
                    "traintype":train.trainTypeCode,
                    "speed":train.initialSpeed,
                    "tiid":train.trainHead.trackItem.tiId,
                    "previoustiid":train.trainHead.previousTI.tiId,
                    "posonti":train.trainHead.positionOnTI,
                    "appeartime":train.appearTimeStr
                    }
            conn.execute(query, parameters)
        conn.commit()


    def exportServicesToFile(self, fileName):
        """Exports the services to the file with the given fileName in ts2
        services CSV format"""
        file = open(fileName, "w", encoding="utf-8")
        file.write("servicecode;description;nextservice;autoreverse;")
        file.write("places=>;placecode;scheduledarrivaltime;")
        file.write("scheduleddeparturetime;trackcode;stop\n")
        for service in self.services.values():
            file.write("\"%s\";" % service.serviceCode)
            file.write("\"%s\";" % service.description)
            file.write("\"%s\";" % service.nextServiceCode)
            file.write("%s;" % service.autoReverse)

            file.write(";")
            for line in service.lines:
                file.write("\"%s\";" % line.placeCode)
                file.write("%s;" % line.scheduledArrivalTimeStr)
                file.write("%s;" % line.scheduledDepartureTimeStr)
                file.write("\"%s\";" % line.trackCode)
                file.write("%s;" % line.mustStop)
            file.write("\n")
        file.close()

    def importServicesFromFile(self, fileName):
        """Imports the services from the ts2 formatted CSV file given by
        fileName, deleting any previous service in the editor if any."""
        self._services = {}
        allowedHeaders = ["servicecode","description","nextservice",
                          "autoreverse","places=>","placecode",
                          "scheduledarrivaltime", "scheduleddeparturetime",
                          "trackcode","stop"]
        file = open(fileName, "r", encoding="utf-8")
        headers = file.readline().split(";")
        headers = [h.strip('" \n') for h in headers]
        lineHeaders = []
        placesIndex = 0
        inPlaces = False
        for header in headers:
            if header != "":
                if header not in allowedHeaders:
                    raise Exception(self.tr(
                            "Format Error: invalid header %s detected") % header)
                if header == "places=>":
                    inPlaces = True
                    placesIndex = headers.index(header)
                    continue
                if inPlaces:
                    lineHeaders.append(header)

        for line in file.readlines():
            params = line.split(";")
            if len(params) > 1:
                params = [p.strip('" \n') for p in params]
                serviceParameters = dict(zip(headers[:placesIndex],
                                            params[:placesIndex]))
                serviceCode = serviceParameters["servicecode"]
                self.services[serviceCode] = trains.Service(
                                                    self, serviceParameters)
                lineLength = len(lineHeaders)
                for i in range((len(params)-placesIndex-1) // lineLength):
                    startIndex = placesIndex + 1 + i * lineLength
                    endIndex = startIndex + lineLength + 1
                    lineParameters = dict(zip(lineHeaders,
                                            params[startIndex:endIndex]))
                    if lineParameters["placecode"] != "":
                        self.services[serviceCode].addLine(lineParameters)
        file.close()
        self.servicesChanged.emit()


    def registerGraphicsItem(self, graphicItem):
        """Reimplemented from Simulation. Adds the graphicItem to the scene
        or to the libraryScene (if tiId <0)."""
        if hasattr(graphicItem, "trackItem") and \
           graphicItem.trackItem.tiId < 0:
            self._libraryScene.addItem(graphicItem)
        else:
            self._scene.addItem(graphicItem)

    @property
    def context(self):
        """Reimplemented from Simulation to return the EDITOR Context"""
        return self._context

    @property
    def grid(self):
        """Returns the size of the grid for placing trackItems"""
        return self._grid

    def option(self, key):
        """Reimplemented from Simulation so as to provide editor specific
        defaults."""
        defaults = {"timeFactor": 1.0}
        value = super().option(key)
        if value is None:
            if key in defaults:
                return defaults[key]
            else:
                return None
        else:
            return value

    def createTrackItem(self, tiType, pos, posEnd = None):
        """Creates a TrackItem of type type at the position pos"""
        pos = QtCore.QPointF(round(pos.x() / self.grid) * self.grid,
                             round(pos.y() / self.grid) * self.grid)
        if posEnd is None:
            if tiType.startswith("P"):
                posEnd = QtCore.QPointF(-5, 0)
            elif tiType.startswith("L"):
                posEnd = pos + QtCore.QPointF(60, 0)
            else:
                posEnd = QtCore.QPointF(0, 0)
        parameters = {
                    "tiid": self._nextId,
                    "name": "%i" % self._nextId,
                    "titype":tiType,
                    "x": pos.x(),
                    "y": pos.y(),
                    "xf": posEnd.x(),
                    "yf": posEnd.y(),
                    "xn": 5,
                    "yn": 0,
                    "xr": 5,
                    "yr": -5,
                    "reverse": 0,
                    "timersw": 1.0,
                    "timerwc": 1.0,
                    "maxspeed": 0.0,
                    "reallength": 0.0,
                    "placecode":None,
                    "trackcode":None}

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
        elif tiType == "A":
            ti = scenery.Place(self, parameters)
        elif tiType == "ZT":
            ti = scenery.TextItem(self, parameters)
        else:
            ti = scenery.TrackItem(self, parameters)
        self.makeTrackItemSignalSlotConnections(ti)
        self.expandBackgroundTo(ti)
        self._trackItems[self._nextId] = ti
        ti.trackItemClicked.emit(int(self._nextId))
        self._nextId += 1

    def makeTrackItemSignalSlotConnections(self, ti):
        """Makes all signal-slot connections for TrackItem ti"""
        if ti.tiType.startswith("S"):
            ti.signalSelected.connect(self.prepareRoute)
            ti.signalUnselected.connect(self.deselectRoute)
        elif ti.tiType.startswith("L"):
            ti.positionSelected.connect(self.setSelectedTrainHead)

    def deleteTrackItem(self, tiId):
        """Delete the TrackItem given by tiId"""
        tiId = int(tiId)
        self._scene.removeItem(self._trackItems[tiId]._gi)
        del self._trackItems[tiId]

    def deleteTrackItemLinks(self):
        """Delete all links between TrackItems"""
        for ti in self._trackItems.values():
            ti.previousItem = None
            ti.nextItem = None
            if hasattr(ti, "reverseItem"):
                ti.reverseItem = None

    def moveTrackItem(self, tiId, pos, clickPos, point):
        """Moves the TrackItem with id tiId to position pos.
        @param clickPos is the position in the item's coordinates on which the
        mouse was clicked. it is used only if point equals "realOrigin".
        point is the property of the TrackItem that will be modified."""
        ti = self.trackItem(int(tiId))
        pos = QtCore.QPointF(round(pos.x() / self.grid) * self.grid, \
                             round(pos.y() / self.grid) * self.grid)
        if point == "realOrigin":
            pos -= clickPos
        setattr(ti, point, pos)
        self.expandBackgroundTo(ti)
        ti.trackItemClicked.emit(int(tiId))

    def expandBackgroundTo(self, trackItem):
        """Expands the EditorSceneBackground to 300px around the given
        TrackItem, if it is not already the case."""
        tl = trackItem.graphicsItem.boundingRect().topLeft() + \
                            trackItem.graphicsItem.pos() + \
                            QtCore.QPointF(-300, -300)
        br = trackItem.graphicsItem.boundingRect().bottomRight() + \
                            trackItem.graphicsItem.pos() + \
                            QtCore.QPointF(300, 300)
        rect = self._sceneBackground.rect()
        if not self._sceneBackground.rect().contains(tl):
            rect.setTopLeft(tl)
        if not self._sceneBackground.rect().contains(br):
            rect.setBottomRight(br)
        self._sceneBackground.setRect(rect)
        self._sceneBackground.update()

    def adjustSceneBackground(self):
        """Adjusts the EditorSceneBackground to 300px around all trackitems of
        the scene"""
        self._sceneBackground.setRect(QtCore.QRectF(0, 0, 800, 600))
        for ti in self._trackItems.values():
            self.expandBackgroundTo(ti)

    @QtCore.pyqtSlot()
    def validateScenery(self):
        """Validates the scenery, i.e. tries to create all links between
        TrackItems, checks and set sceneryValidated to True if succeeded"""
        self.createTrackItemsLinks()
        if self.checkTrackItemsLinks():
            self.sceneryIsValidated.emit(True)
            self._sceneryValidated = True
            return True
        else:
            self.sceneryIsValidated.emit(False)
            self._sceneryValidated = False
            return False

    @QtCore.pyqtSlot()
    def invalidateScenery(self):
        """Invalidates the scenery, i.e. removes all links between TrackItems,
        and set sceneryValidated to False"""
        self.deleteTrackItemLinks()
        self._sceneryValidated = False
        self.sceneryIsValidated.emit(False)

    def addRoute(self):
        """Adds the route that is selected on the scene to the routes."""
        if self.context == utils.Context.EDITOR_ROUTES:
            if (self._preparedRoute is not None) and \
               (self._preparedRoute not in self._routes.values()):
                routeNum = self._preparedRoute.routeNum
                self._routes[routeNum] = self._preparedRoute
                self.routesChanged.emit()
                self.deselectRoute()
                return True
        self.deselectRoute()
        return False

    def deleteRoute(self, routeNum):
        """Deletes the route defined by routeNum"""
        if self.context == utils.Context.EDITOR_ROUTES:
            self.deselectRoute()
            del self._routes[routeNum]
            self.routesChanged.emit()

    @QtCore.pyqtSlot(int)
    def prepareRoute(self, signalId):
        """Prepares the route starting with the SignalItem given by signalId:
        - Checks that the route leads to another SignalItem, using the current
        directions of each PointsItem.
        - Set _preparedRoute to this route
        - Highlights the route if valid"""
        if self.context == utils.Context.EDITOR_ROUTES:
            si = self.trackItem(signalId)
            pos = routing.Position(si, si.previousItem, 0)
            directions = {}
            cur = pos.next()
            while not cur.trackItem.tiType.startswith("E"):
                ti = cur.trackItem
                if ti.tiType.startswith("P"):
                    directions[ti.tiId] = int(ti.pointsReversed)
                if ti.tiType.startswith("S"):
                    if ti.isOnPosition(cur):
                        self._preparedRoute = \
                                routing.Route(self, self._nextRouteId, si, ti)
                        self._nextRouteId += 1
                        for tiId, direction in directions.items():
                            self._preparedRoute.appendDirection(tiId, \
                                                                direction)
                        self._preparedRoute.createPositionsList()
                        self.selectedRoute = self._preparedRoute
                        return
                cur = cur.next()

    @QtCore.pyqtSlot(int)
    def selectRoute(self, routeNum):
        """Selects the route given by routeNum in the routes editor."""
        if self.context == utils.Context.EDITOR_ROUTES:
            route = self.routes[routeNum]
            self.selectedRoute = route
            self._preparedRoute = None

    @QtCore.pyqtSlot()
    def deselectRoute(self):
        """Desactivate the selected route in the routes editor"""
        if self.context == utils.Context.EDITOR_ROUTES:
            self.selectedRoute = None
            self._preparedRoute = None

    def getValidPosition(self):
        """Returns an arbitrary valid position on the scenery. Returns None,
        if no valid position has been found."""
        for ti in self._trackItems.values():
            if ti.tiType.startswith("L"):
                return routing.Position(ti, ti.previousItem, 0.0)
        return None

    @QtCore.pyqtSlot(int)
    def selectTrain(self, index):
        """Selects the train given by index in the train editor, and sets the
        displayedPosition on the train's head."""
        if self.context == utils.Context.EDITOR_TRAINS:
            train = self.trains[index]
            self._selectedTrain = train
            self.displayedPosition = train.trainHead

    @QtCore.pyqtSlot()
    def unselectTrains(self):
        """Unselect all selected trains, and the associated displayedPosition
        """
        self._selectedTrain = None
        self.displayedPosition = None

    @QtCore.pyqtSlot(routing.Position)
    def setSelectedTrainHead(self, position):
        """Sets the trainHead of the selectedTrain to position if valid"""
        if self.context == utils.Context.EDITOR_TRAINS:
            if self._selectedTrain is not None and \
               position is not None:
                self._selectedTrain.trainHead = position
                self.selectTrain(self.trains.index(self._selectedTrain))

    def addTrainType(self, code):
        """Adds an empty TrainType to the trainTypes list."""
        if self.context == utils.Context.EDITOR_TRAINTYPES:
            parameters = { \
                    "code":code, \
                    "description":"<Stock type description>", \
                    "maxspeed":"25.0", \
                    "stdaccel":"0.5", \
                    "stdbraking":"0.5", \
                    "emergbraking":"1.5", \
                    "tlength":"100"}
            self._trainTypes[code] = trains.TrainType(self, parameters)
            self.trainTypesChanged.emit()
            return True
        return False

    def deleteTrainType(self, code):
        """Deletes the trainType defined by code"""
        if self.context == utils.Context.EDITOR_TRAINTYPES:
            del self._trainTypes[code]
        self.trainTypesChanged.emit()

    def addService(self, code):
        """Adds an empty Service to the services list."""
        if self.context == utils.Context.EDITOR_SERVICES:
            parameters = { \
                    "servicecode":code, \
                    "description":"<Service description>", \
                    "nextservice":"", \
                    "autoreverse":0}
            self._services[code] = trains.Service(self, parameters)
            self.servicesChanged.emit()
            return True
        return False

    def deleteService(self, code):
        """Deletes the service defined by code"""
        if self.context == utils.Context.EDITOR_SERVICES:
            del self._services[code]
        self.servicesChanged.emit()

    def addServiceLine(self, service, index):
        """Adds a service line to service at the current index"""
        if self.context == utils.Context.EDITOR_SERVICES:
            parameters = {
                    "placecode":"",
                    "trackcode":"",
                    "scheduledarrivaltime":"00:00:00",
                    "scheduleddeparturetime":"00:00:00" ,
                    "stop":False}
            service.lines.insert(index, trains.ServiceLine(
                                                        service, parameters))
            self.serviceLinesChanged.emit()

    def deleteServiceLine(self, service, index):
        """Deletes the service line of service defined by index"""
        if self.context == utils.Context.EDITOR_SERVICES:
            del service.lines[index]
            self.serviceLinesChanged.emit()

    def setupTrainsFromServices(self):
        """Removes all trains instances and creates a train for each relevant
        service, that is each service which is not following another one (i.e
        a service which is not the nextService of another service)."""
        self._trains = []
        serviceList = list(self.services.keys())
        for s in self.services.values():
            if s.nextServiceCode is not None and \
               s.nextServiceCode != "":
                serviceList.remove(s.nextServiceCode)
        for sc in serviceList:
            train = self.addTrain()
            train.serviceCode = sc
            service = self.service(sc)
            placeCode, trackCode = service.getEntryPlaceData()
            entryLineItem = self.getLineItem(placeCode, trackCode)
            if entryLineItem is not None:
                if entryLineItem.nextItem.tiType.startswith("E") or \
                   entryLineItem.nextItem.tiType.startswith("SB"):
                    previousTI = entryLineItem.nextItem
                else:
                    previousTI = entryLineItem.previousItem
                position = routing.Position(
                                        entryLineItem,
                                        previousTI,
                                        max(0, entryLineItem.realLength - 1))
                initialSpeed = entryLineItem.maxSpeed
            else:
                position = self.getValidPosition()
                initialSpeed = 0
            train.trainHead = position
            train.initialSpeed = initialSpeed
            if service.lines[0].scheduledArrivalTimeStr != "":
                train.appearTimeStr = service.lines[0].scheduledArrivalTimeStr
            else:
                train.appearTimeStr = "00:00:00"

    def reverseSelectedTrain(self):
        """Reverses the selectedTrain direction."""
        if self.context == utils.Context.EDITOR_TRAINS:
            if self._selectedTrain is not None:
                reversedHead = self._selectedTrain.trainHead.reversed()
                self._selectedTrain.trainHead = reversedHead
                self.selectTrain(self.trains.index(self._selectedTrain))


    def addTrain(self):
        """Adds an empty train to the editor and returns that train"""
        if self.context == utils.Context.EDITOR_TRAINS:
            position = self.getValidPosition()
            if position is None:
                raise Exception("No valid position found. Check scenery.")
            parameters = {
                "servicecode": list(self.services.values())[0].serviceCode,
                "traintype": list(self.trainTypes.values())[0].code,
                "speed": 0.0,
                "accel": 0.0,
                "tiid": position.trackItem.tiId,
                "previoustiid": position.previousTI.tiId,
                "posonti": position.positionOnTI,
                "appeartime": "00:00:00"
               }
            train = trains.Train(self, parameters)
            self._trains.append(train)
            self.trainsChanged.emit()
            return train

    def deleteTrain(self, index):
        """Deletes the train assigned to serviceCode"""
        if self.context == utils.Context.EDITOR_TRAINS:
            del self.trains[index]
            self.trainsChanged.emit()

    @QtCore.pyqtSlot(int)
    def updateContext(self, tabNum):
        """Updates the context of the editor, depending on the tab selected
        and given by tabNum."""
        self.unselectTrains()

        if tabNum == 0:
            self._context = utils.Context.EDITOR_GENERAL
        elif tabNum == 1:
            self._context = utils.Context.EDITOR_SCENERY
        elif tabNum == 2:
            self._context = utils.Context.EDITOR_ROUTES
        elif tabNum == 3:
            self._context = utils.Context.EDITOR_TRAINTYPES
        elif tabNum == 4:
            self._context = utils.Context.EDITOR_SERVICES
        elif tabNum == 5:
            self._context = utils.Context.EDITOR_TRAINS


