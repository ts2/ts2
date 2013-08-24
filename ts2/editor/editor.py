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
from PyQt4.Qt import Qt
from ts2.simulation import Simulation
from ts2 import scenery, utils
from ts2.editor import EditorSceneBackground
from ts2.route import Route, RoutesModel
from ts2.traintype import TrainType, TrainTypesModel
from ts2.position import Position

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


class Editor(Simulation):
    """The Editor class holds all the logic behind the simulation editor.
    """    
    def __init__(self, editorWindow):
        """Constructor for the Editor class"""
        super().__init__(editorWindow)
        self._context = utils.Context.EDITOR_GENERAL
        self._libraryScene = QtGui.QGraphicsScene(0, 0, 200, 250, self)
        self._sceneBackground = EditorSceneBackground(self, 0, 0, 1024, 768)
        self._sceneBackground.setZValue(-100)
        self._scene.addItem(self._sceneBackground)
        self.drawToolBox()
        self._sceneryValidated = False
        self._routesModel = RoutesModel(self)
        self._trainTypesModel = TrainTypesModel(self)
        self._database = None
        self._nextId = 1
        self._nextRouteId = 1
        self._nextTrainTypeId = 1
        self._grid = 5.0
        self._preparedRoute = None
        self._selectedRoute = None
        
    sceneryIsValidated = QtCore.pyqtSignal(bool)
    routesChanged = QtCore.pyqtSignal()
    trainTypesChanged = QtCore.pyqtSignal()
    
    def drawToolBox(self):
        """Construct the library tool box"""
        # Lines
        WhiteLineItem(0, 0, 0, 300, None, self._libraryScene)
        WhiteLineItem(100, 0, 100, 250, None, self._libraryScene)
        WhiteLineItem(200, 0, 200, 300, None, self._libraryScene)
        WhiteLineItem(0, 0, 200, 0, None, self._libraryScene)
        WhiteLineItem(0, 50, 200, 50, None, self._libraryScene)
        WhiteLineItem(0, 100, 200, 100, None, self._libraryScene)
        WhiteLineItem(0, 150, 200, 150, None, self._libraryScene)
        WhiteLineItem(0, 200, 200, 200, None, self._libraryScene)
        WhiteLineItem(0, 250, 200, 250, None, self._libraryScene)
        WhiteLineItem(0, 300, 200, 300, None, self._libraryScene)
        # Items
        self.librarySignalItem = scenery.SignalItem(self, \
                {"tiid":-1, "name":"Signal", "x":20, "y":30, "reverse":0})
        self.librarySignalTimerItem = scenery.SignalTimerItem(self, \
                {"tiid":-2, "name":"Timer Signal", "x":120, "y":30, \
                 "reverse":0, "timersw":1.0, "timerwc":1.0})
        self.libraryPointsItem = scenery.PointsItem(self, \
                {"tiid":-3, "name":"Points", "x":50, "y":75, "xf":-5, \
                 "yf":0, "xn":5, "yn":0, "xr":5, "yr":-5})
        self.libraryBumperItem = scenery.BumperItem(self, \
                {"tiid":-4, "name":"Bumper", "x":120, "y":75, "reverse":0})
        self.libraryLineItem = scenery.LineItem(self, \
                {"tiid":-5, "name":"Line", "x":20, "y":125, "xf":80, \
                 "yf":125, "maxspeed":25.0, "reallength":0.0, \
                 "placecode":None, "trackcode":None})
        self.libraryPlatformItem = scenery.PlatformItem(self, \
                {"tiid":-6, "name":"Platform", "x":120, "y":135, "xf":180, \
                 "yf":135,  "xn":125, "yn":120, "xr":175, "yr":130, \
                 "maxspeed":25.0, "reallength":0.0, \
                 "placecode":None, "trackcode":None})
        self.libraryEndItem = scenery.EndItem(self, \
                {"tiid":-7, "name":"End", "x":50, "y":175})
        self.libraryPlaceItem = scenery.Place(self, \
                {"tiid":-8, "name":"PLACE", "placecode":"", "x":132, "y":180})
        self.libraryBinItem = TrashBinItem(self, self._libraryScene, \
                                                      QtCore.QPointF(86, 260))
    
    @property
    def libraryScene(self):
        """The pseudo-scene for the TrackItem "tool box" """
        return self._libraryScene
    
    @property
    def routesModel(self):
        """Returns the routesModel of this editor instance"""
        return self._routesModel
    
    @property
    def trainTypesModel(self):
        """Returns the trainTypesModel of this editor"""
        return self._trainTypesModel
    
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

    def reload(self, fileName):
        """Load or reload all the data of the simulation from the database."""
        conn = sqlite3.connect(fileName)
        conn.row_factory = sqlite3.Row
        self.createAllTrackItems(conn)
        self._nextId = max(self._trackItems.keys()) + 1
        if self.validateScenery():
            self.loadRoutes(conn)
            self._nextRouteId = max(self._routes.keys()) + 1
            self.routesChanged.emit()
        self.loadTrainTypes(conn)
        try:
            self._nextTrainTypeId = max(self._trainTypes.keys()) + 1
        except:
            pass
        self.trainTypesChanged.emit()
        #self.loadServices()
        #self.loadTrains()

    def save(self):
        """Saves the data of the simulation to the database"""
        # Set up database
        conn = sqlite3.connect(self._database)
        self.saveTrackItems(conn)
        self.saveRoutes(conn)
        self.saveTrainTypes(conn)
        conn.close()
        
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
        conn.execute("CREATE TABLE routes (" \
                            "routenum INTEGER PRIMARY KEY," \
                            "beginsignal INTEGER," \
                            "endsignal INTEGER," \
                            "initialstate INTEGER)" \
                    )
        for route in self._routes.values():
            query = "INSERT INTO routes "\
                    "(routenum, beginsignal, endsignal, initialstate) "\
                    "VALUES " \
                    "(:routenum, :beginsignal, :endsignal, :initialstate)"
            parameters = { \
                    "routenum":route.routeNum, \
                    "beginsignal":route.beginSignal.tiId, \
                    "endsignal":route.endSignal.tiId, \
                    "initialstate":route.initialState \
                         }
            conn.execute(query, parameters)
        
        # Save the directions
        conn.execute("DROP TABLE IF EXISTS directions")
        conn.execute("CREATE TABLE directions (" \
                        "routenum INTEGER," \
                        "tiid INTEGER," \
                        "direction INTEGER)" \
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
        conn.execute("CREATE TABLE traintypes (" \
                            "code VARCHAR(10)," \
                            "description VARCHAR(200)," \
                            "maxspeed DOUBLE," \
                            "stdaccel DOUBLE," \
                            "stdbraking DOUBLE," \
                            "emergbraking DOUBLE," \
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
        options."""
        options = {"timeFactor": 1.0}
        return options[key]
    
    def createTrackItem(self, tiType, pos, posEnd = None):
        """Creates a TrackItem of type type at the position pos"""
        pos = QtCore.QPointF(round(pos.x() / self.grid) * self.grid, \
                             round(pos.y() / self.grid) * self.grid)
        if posEnd is None:
            if tiType.startswith("P"):
                posEnd = QtCore.QPointF(-5, 0)
            elif tiType.startswith("L"):
                posEnd = pos + QtCore.QPointF(60, 0)
            else:
                posEnd = QtCore.QPointF(0, 0)
        parameters = { \
                    "tiid": self._nextId, \
                    "name": "%i" % self._nextId, \
                    "titype":tiType, \
                    "x": pos.x(), \
                    "y": pos.y(), \
                    "xf": posEnd.x(), \
                    "yf": posEnd.y(), \
                    "xn": 5, \
                    "yn": 0, \
                    "xr": 5, \
                    "yr": -5, \
                    "reverse": 0, \
                    "timersw": 1.0, \
                    "timerwc": 1.0, \
                    "maxspeed": 25.0, \
                    "reallength": 0.0, \
                    "placecode":None, \
                    "trackcode":None}
                
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
        elif tiType == "A":
            ti = scenery.Place(self, parameters)
        else:
            ti = scenery.TrackItem(self, parameters)
        self.makeTrackItemSignalSlotConnections(ti)
        self._trackItems[self._nextId] = ti
        ti.trackItemClicked.emit(int(self._nextId))
        self._nextId += 1
    
    def makeTrackItemSignalSlotConnections(self, ti):
        """Makes all signal-slot connections for TrackItem ti"""
        if ti.tiType.startswith("S"):
            ti.signalSelected.connect(self.prepareRoute)
            ti.signalUnselected.connect(self.deselectRoute)
        
    
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
        ti.trackItemClicked.emit(int(tiId))
        
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
            pos = Position(si, si.previousItem, 0)
            directions = {}
            cur = pos.next()
            while not cur.trackItem.tiType.startswith("E"):
                ti = cur.trackItem
                if ti.tiType.startswith("P"):
                    directions[ti.tiId] = int(ti.pointsReversed)
                if ti.tiType.startswith("S"):
                    if ti.isOnPosition(cur):
                        self._preparedRoute = \
                                        Route(self, self._nextRouteId, si, ti)
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

    def addTrainType(self):
        """Adds an empty TrainType to the trainTypes list."""
        if self.context == utils.Context.EDITOR_TRAINTYPES:
            code = str(self._nextTrainTypeId)
            parameters = { \
                    "code":code, \
                    "description":"<Stock type description>", \
                    "maxspeed":"25.0", \
                    "stdaccel":"0.5", \
                    "stdbraking":"0.5", \
                    "emergbraking":"1.5", \
                    "tlength":"100"}
            self._trainTypes[code] = TrainType(self, parameters)
            self._nextTrainTypeId += 1
            self.trainTypesChanged.emit()
            return True
        return False
    
    def deleteTrainType(self, code):
        """Deletes the route defined by routeNum"""
        if self.context == utils.Context.EDITOR_TRAINTYPES:
            del self._trainTypes[code]
        self.trainTypesChanged.emit()
 
    @QtCore.pyqtSlot(int)
    def updateContext(self, tabNum):
        """Updates the context of the editor, depending on the tab selected 
        and given by tabNum."""
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
        
    