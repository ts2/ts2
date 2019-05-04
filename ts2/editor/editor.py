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

import copy
import zipfile

import simplejson as json

from Qt import QtCore, QtWidgets, Qt
from ts2 import __FILE_FORMAT__
from ts2 import simulation
from ts2 import utils, trains
from ts2.editor import editorscenebackground
from ts2.routing import position, route
from ts2.scenery import abstract, placeitem, lineitem, platformitem, \
    invisiblelinkitem, enditem, pointsitem, textitem
from ts2.scenery.signals import signalitem

translate = QtWidgets.qApp.translate


def json_hook(dct):
    """Hook method for json.load()."""
    if not dct.get('__type__'):
        return dct
    elif dct['__type__'] == "Simulation":
        return Editor(dct['options'], dct['trackItems'], dct['routes'],
                      dct['trainTypes'], dct['services'], dct['trains'],
                      dct['messageLogger'], dct['signalLibrary'])
    else:
        return simulation.json_hook(dct)


def load(editorWindow, jsonStream):
    """Loads the simulation from jsonStream and returns it as an Editor.

    The logic of loading is the following:
    1. We create the graph of objects from json.load(). When initialized,
    each object stores its JSON data.
    2. When all the objects are created, we call the initialize() method of the
    simulation which calls in turn the initialize() method of each object.
    This method will create all the missing links between the object and the
    simulation (and other objects)."""
    editor = json.load(jsonStream, object_hook=json_hook, encoding='utf-8')
    if not isinstance(editor, Editor):
        raise utils.FormatException(
            translate("simulation.load", "Loaded file is not a TS2 simulation")
        )
    editor.initialize(editorWindow)
    return editor


class WhiteLineItem(QtWidgets.QGraphicsLineItem):
    """Shortcut class to make a white line item and add to scene"""

    def __init__(self, x1, y1, x2, y2, parent, scene):
        """Constructor for the WhiteLineItem class"""
        super().__init__(x1, y1, x2, y2, parent)
        self.setPen(Qt.white)
        scene.addItem(self)
        self.update()


class OptionsModel(QtCore.QAbstractTableModel):
    """Model for editing options in the editor.
    """

    def __init__(self, editor):
        """Constructor for the OptionsModel class"""
        super().__init__()
        self._editor = editor

    def rowCount(self, parent=None, *args, **kwargs):
        """Returns the number of rows of the model, corresponding to the
        number of real options."""
        return self._editor.realOptionsLength

    def columnCount(self, parent=None, *args, **kwargs):
        """Returns the number of columns of the model"""
        return 2

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole or role == Qt.EditRole:
            optionKeys = list(self._editor.realOptions.keys())
            optionValues = list(self._editor.realOptions.values())
            if index.column() == 0:
                return optionKeys[index.row()]
            elif index.column() == 1:
                return str(optionValues[index.row()])
        return None

    def setData(self, index, value, role=None):
        """Updates data when modified in the view"""
        if role == Qt.EditRole:
            if index.column() == 1:
                optionKey = str(index.sibling(index.row(), 0).data())
                self._editor.setOption(optionKey, value)
                return True
        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
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

    def __init__(self, options=None, trackItems=None, routes=None,
                 trainTypes=None, services=None, trns=None, messageLogger=None,
                 signalLibrary=None, fileName=None):
        """Constructor for the Editor class"""
        options = options or simulation.BUILTIN_OPTIONS
        trackItems = trackItems or {}
        routes = routes or {}
        trainTypes = trainTypes or {}
        services = services or {}
        trns = trns or []
        messageLogger = messageLogger or {"messages": []}
        if signalLibrary:
            signalitem.SignalLibrary.update(signalitem.signalLibraryDict, signalLibrary)
        signalLibrary = signalitem.signalLibraryDict
        super().__init__(options, trackItems, routes, trainTypes, services,
                         trns, messageLogger, signalLibrary)

        self._context = utils.Context.EDITOR_GENERAL
        self._libraryScene = QtWidgets.QGraphicsScene(0, 0, 200, 250, self)
        self._sceneBackground = editorscenebackground.EditorSceneBackground(
            self, 0, 0, 800, 600
        )
        self._sceneBackground.setZValue(-100)
        self._scene.addItem(self._sceneBackground)

        # Lines
        WhiteLineItem(0, 0, 0, 300, None, self._libraryScene)
        WhiteLineItem(100, 0, 100, 300, None, self._libraryScene)
        WhiteLineItem(200, 0, 200, 300, None, self._libraryScene)
        WhiteLineItem(0, 0, 200, 0, None, self._libraryScene)
        WhiteLineItem(0, 50, 200, 50, None, self._libraryScene)
        WhiteLineItem(0, 100, 200, 100, None, self._libraryScene)
        WhiteLineItem(0, 150, 200, 150, None, self._libraryScene)
        WhiteLineItem(0, 200, 200, 200, None, self._libraryScene)
        WhiteLineItem(0, 250, 200, 250, None, self._libraryScene)
        WhiteLineItem(0, 300, 200, 300, None, self._libraryScene)

        # Items
        self.librarySignalItem = signalitem.SignalItem({
            "tiId": "__EDITOR__1", "name": "Signal", "x": 65, "y": 25, "reverse": 0,
            "xn": 20, "yn": 30, "signalType": "UK_3_ASPECTS", "activeAspect": "UK_DANGER", "maxSpeed": 0.0,
            "routesSetParams": "{}", "trainNotPresentParams": "{}"
        })
        self.libraryLineItem = lineitem.LineItem({
            "tiId": "__EDITOR__5", "name": "Line", "x": 120, "y": 25, "xf": 180, "yf": 25,
            "maxSpeed": 0.0, "realLength": 1.0, "placeCode": None,
            "trackCode": None
        })
        self.libraryPointsItem = pointsitem.PointsItem({
            "tiId": "__EDITOR__3", "name": "Points", "maxSpeed": 0.0, "x": 50, "y": 75,
            "xf": -5, "yf": 0, "xn": 5, "yn": 0, "xr": 5, "yr": -5
        })
        self.libraryPlatformItem = platformitem.PlatformItem({
            "tiId": "__EDITOR__6", "name": "Platform", "x": 120, "y": 65, "xf": 180,
            "yf": 85, "maxSpeed": 0.0, "realLength": 1.0, "placeCode": None,
            "trackCode": None
        })
        self.libraryPlaceItem = placeitem.Place({
            "tiId": "__EDITOR__8", "name": "PLACE", "placeCode": "", "maxSpeed": 0.0,
            "x": 132, "y": 115, "xf": 0, "yf": 0
        })
        self.libraryEndItem = enditem.EndItem({
            "tiId": "__EDITOR__7", "name": "End", "maxSpeed": 0.0, "x": 50, "y": 125,
            "xf": 0, "yf": 0
        })
        self.libraryTextItem = textitem.TextItem({
            "tiId": "__EDITOR__11", "name": "TEXT", "x": 36, "y": 165, "maxSpeed": 0.0,
            "realLength": 1.0
        })
        self.libraryInvisibleLinkItem = invisiblelinkitem.InvisibleLinkItem({
            "tiId": "__EDITOR__10", "name": "Invisible link", "x": 120, "y": 175,
            "xf": 180, "yf": 175, "maxSpeed": 0.0, "realLength": 1.0,
            "placeCode": None, "trackCode": None
        })

        # Setup Models
        self._routesModel = route.RoutesModel(self)
        self._trainTypesModel = trains.TrainTypesModel(self)
        self._servicesModel = trains.ServicesModel(self)
        self._serviceLinesModel = trains.ServiceLinesModel(self)
        self._trainsModel = trains.TrainsModel(self)
        self._optionsModel = OptionsModel(self)
        self._placesModel = placeitem.PlacesModel(self)

        self._sceneryValidated = False
        self.fileName = fileName
        self._nextId = 1
        self._nextRouteId = 1
        self._grid = 5.0
        self._preparedRoute = None
        self._selectedRoute = None
        self._selectedTrain = None
        self._selectedItems = []
        self._clipbooard = []

        self._displayedPositionGI = position.PositionGraphicsItem(self)
        self.registerGraphicsItem(self._displayedPositionGI)
        self.trainsChanged.connect(self.unselectTrains)
        self.scene.selectionChanged.connect(self.updateSelection)

    def initialize(self, editorWindow):
        """Initialize the simulation."""
        self.simulationWindow = editorWindow
        self.signalLibrary.initialize()

        self.updatePlaces()
        for ti in self.trackItems.values():
            ti.initialize(self)
        self.adjustSceneBackground()
        try:
            self._nextId = max([int(x) for x in self._trackItems.keys()]) + 1
        except ValueError:
            self._nextId = 1

        # Initialize library items
        self.librarySignalItem.initialize(self)
        self.libraryLineItem.initialize(self)
        self.libraryPointsItem.initialize(self)
        self.libraryPlatformItem.initialize(self)
        self.libraryPlaceItem.initialize(self)
        self.libraryEndItem.initialize(self)
        self.libraryTextItem.initialize(self)
        self.libraryInvisibleLinkItem.initialize(self)

        if self.validateScenery():
            for rte in self.routes.values():
                rte.initialize(self)
            try:
                self._nextRouteId = max([int(x) for x in self._routes.keys()]) + 1
            except ValueError:
                self._nextRouteId = 1
        for trainType in self.trainTypes.values():
            trainType.initialize(self)
        for service in self.services.values():
            service.initialize(self)
        for train in self.trains:
            train.initialize(self)
        self._trains.sort(key=lambda x: x.currentService.lines and
                                        x.currentService.lines[0].scheduledDepartureTimeStr or
                                        x.currentService.serviceCode)
        self.messageLogger.initialize(self)

        self._scene.update()

    sceneryIsValidated = QtCore.pyqtSignal(bool)
    trainsChanged = QtCore.pyqtSignal()

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
    def placesModel(self):
        """Returns the PlacesModel of this editor."""
        return self._placesModel

    @property
    def selectedRoute(self):
        """Returns the selected route in the route editor."""
        return self._selectedRoute

    @selectedRoute.setter
    def selectedRoute(self, value):
        """Setter function for the selectedRoute property"""
        if self._selectedRoute is not None:
            self._selectedRoute.unhighlight()
        self._selectedRoute = value
        if self._selectedRoute is not None:
            self._selectedRoute.highlight()

    @property
    def selectedItems(self):
        """Returns the list of the selected items on the scene."""
        return self._selectedItems

    @property
    def displayedPosition(self):
        """Returns the position that is currently selected in this editor"""
        return self._displayedPositionGI.position

    @displayedPosition.setter
    def displayedPosition(self, pos):
        """Setter function for the displayedPosition property"""
        if self.context == utils.Context.EDITOR_TRAINS:
            self._displayedPositionGI.position = pos

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

    def place(self, placeCode):
        """Returns the place defined by placeCode. Reimplemented from
        Simulation so as not to rely on the places dictionary."""
        if placeCode is not None and placeCode != "":
            for ti in self._trackItems.values():
                if isinstance(ti, placeitem.Place) \
                        and ti.placeCode == placeCode:
                    return ti
        return None

    def checkSimulation(self):
        """Checks that the simulation is valid.

        :return : a tuple (ok, message) where ok is True if the simulation is
                  valid, and False otherwise. If the simulation is not valid,
                  message describes the error.
        """
        if not self.checkTrackItemsLinks():
            return False, self.tr("Invalid simulation: Not all items are "
                                  "linked or end items are missing.")
        for ti in self.trackItems.values():
            try:
                ti.setupTriggers()
            except utils.FormatException as err:
                return False, str(err)
        return True, ""

    def save(self):
        """Saves the data of the simulation to the database"""
        # Set up file format version
        self.setOption("version", __FILE_FORMAT__)

        if self.fileName.endswith(".ts2"):
            with zipfile.ZipFile(self.fileName, "w") as zipArchive:
                zipArchive.writestr("simulation.json",
                                    json.dumps(self, separators=(',', ':'),
                                               for_json=True, encoding='utf-8'),
                                    compress_type=zipfile.ZIP_BZIP2)
        else:
            with open(self.fileName, 'w') as f:
                json.dump(self, f, separators=(', ', ': '), indent=4,
                          sort_keys=True, for_json=True, encoding='utf-8')

    def exportServicesToFile(self, fileName):
        """Exports the services to the file with the given fileName in ts2
        services CSV format"""
        file = open(fileName, "w", encoding="utf-8")
        file.write("serviceCode;description;nextServiceCode;autoReverse;")
        file.write("plannedTrainType;")
        file.write("places=>;placeCode;scheduledArrivalTime;")
        file.write("scheduledDepartureTime;trackCode;mustStop\n")
        for service in self.services.values():
            file.write("\"%s\";" % service.serviceCode)
            file.write("\"%s\";" % service.description)
            file.write("\"%s\";" % service.nextServiceCode)
            file.write("%s;" % service.autoReverse)
            file.write("\"%s\";" % service.plannedTrainType)

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
        allowedHeaders = [
            "serviceCode", "description", "nextServiceCode", "autoReverse",
            "plannedTrainType", "places=>", "placeCode", "scheduledArrivalTime",
            "scheduledDepartureTime", "trackCode", "mustStop"
        ]
        file = open(fileName, "r", encoding="utf-8")
        headers = file.readline().split(";")
        headers = [h.strip('" \n') for h in headers]
        lineHeaders = []
        placesIndex = 0
        inPlaces = False
        for header in headers:
            # We have empty headers over service line columns
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
                serviceParameters["__type__"] = "Service"
                lineLength = len(lineHeaders)
                serviceLines = []
                for i in range((len(params) - placesIndex - 1) // lineLength):
                    startIndex = placesIndex + 1 + i * lineLength
                    endIndex = startIndex + lineLength + 1
                    lineParameters = dict(zip(lineHeaders,
                                              params[startIndex:endIndex]))
                    lineParameters["__type__"] = "ServiceLine"
                    if lineParameters["placeCode"]:
                        serviceLines.append(lineParameters)
                serviceParameters["lines"] = serviceLines
                serviceCode = serviceParameters["serviceCode"]
                jsonStr = json.dumps(serviceParameters, encoding='utf-8')
                self.services[serviceCode] = json.loads(
                    jsonStr, object_hook=json_hook, encoding='utf-8'
                )
                self.services[serviceCode].initialize(self)
        file.close()

    def registerGraphicsItem(self, graphicItem):
        """Adds the graphicItem to the scene or to the libraryScene.

        Reimplemented from Simulation.
        :param graphicItem: The graphic Item to add to the scene or library
        scene (if tiId < 0)
        :type graphicItem: QtCore.QGraphicsItem
        """
        if hasattr(graphicItem, "trackItem") and \
                graphicItem.trackItem.tiId.startswith("__EDITOR__"):
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

    def createTrackItem(self, tiType, pos, posEnd=None):
        """Creates a TrackItem of type type at the position pos.

        :param tiType: The type of the TrackItem to create (class name)
        :type tiType: str
        :param pos: the position at which to create the item
        :type pos: QtCore.QPointF
        :param posEnd: the position of the other end of the item (when
        applicable)
        :type posEnd: QtCore.QPointF
        """
        pos = QtCore.QPointF(round(pos.x() / self.grid) * self.grid,
                             round(pos.y() / self.grid) * self.grid)
        if posEnd is None:
            if tiType == "PointsItem":
                posEnd = QtCore.QPointF(-5, 0)
            elif tiType == "LineItem" or tiType == "InvisibleLinkItem":
                posEnd = pos + QtCore.QPointF(60, 0)
            elif tiType == "PlatformItem":
                posEnd = pos + QtCore.QPointF(60, 20)
            else:
                posEnd = QtCore.QPointF(0, 0)
        parameters = {
            "tiId": str(self._nextId),
            "name": "%i" % self._nextId,
            "x": pos.x(),
            "y": pos.y(),
            "xf": posEnd.x(),
            "yf": posEnd.y(),
            "xn": 5,
            "yn": 0,
            "xr": 5,
            "yr": -5,
            "reverse": 0,
            "maxSpeed": 0.0,
            "realLength": 1.0,
            "placeCode": None,
            "trackCode": None,
            "signalType": "UK_3_ASPECTS",
            "activeAspect": "UK_DANGER",
            "routesSetParams": "{}",
            "trainNotPresentParams": "{}"
        }

        if tiType == "LineItem":
            ti = lineitem.LineItem(parameters)
        elif tiType == "PlatformItem":
            ti = platformitem.PlatformItem(parameters)
        elif tiType == "InvisibleLinkItem":
            ti = invisiblelinkitem.InvisibleLinkItem(parameters)
        elif tiType == "SignalItem":
            parameters.update({"xn": pos.x() - 45, "yn": pos.y() + 5})
            ti = signalitem.SignalItem(parameters)
        elif tiType == "PointsItem":
            ti = pointsitem.PointsItem(parameters)
        elif tiType == "EndItem":
            ti = enditem.EndItem(parameters)
        elif tiType == "Place":
            ti = placeitem.Place(parameters)
        elif tiType == "TextItem":
            ti = textitem.TextItem(parameters)
        else:
            ti = abstract.TrackItem(parameters)
        ti.initialize(self)
        self.expandBackgroundTo(ti)
        self._trackItems[self._nextId] = ti
        self._nextId += 1
        self.updateSelection()
        return ti

    def deleteTrackItem(self, tiId):
        """Delete the TrackItem given by tiId."""
        tiId = int(tiId)
        self._trackItems[tiId].removeAllGraphicsItems()
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

        Also moves the other trackItems that are currently selected.

        :param pos: position where to move the trackItem
        :type pos: QtCore.QPointF
        :param clickPos: is the position in the item's coordinates on which the
        mouse was clicked. it is used only if point has "origin" in its name.
        point is the property of the TrackItem that will be modified."""
        if len(self.selectedItems) > 1:
            point = "origin"
        trackItem = self.trackItem(int(tiId))
        if point.endswith("rigin"):
            pos -= clickPos
        pos = QtCore.QPointF(round(pos.x() / self.grid) * self.grid,
                             round(pos.y() / self.grid) * self.grid)
        translation = pos - getattr(trackItem, point)
        for ti in self.selectedItems:
            currentPos = getattr(ti, point)
            setattr(ti, point, currentPos + translation)
            self.expandBackgroundTo(ti)
        # ti.trackItemClicked.emit(int(tiId))

    def expandBackgroundTo(self, trackItem):
        """Expands the EditorSceneBackground to 300px around the given
        TrackItem, if it is not already the case."""
        tl = trackItem.graphicsItem.boundingRect().topLeft() + \
             trackItem.graphicsItem.pos() + QtCore.QPointF(-300, -300)
        br = trackItem.graphicsItem.boundingRect().bottomRight() + \
             trackItem.graphicsItem.pos() + QtCore.QPointF(300, 300)
        rect = self._sceneBackground.rect()
        if not rect.contains(tl):
            rect.setLeft(min(tl.x(), rect.left()))
            rect.setTop(min(tl.y(), rect.top()))
        if not rect.contains(br):
            rect.setRight(max(br.x(), rect.right()))
            rect.setBottom(max(br.y(), rect.bottom()))
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
        self.updatePlaces()
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
        """Adds the route that is selected on the scene to the routes.

        .. todo:: Maybe this should return Error string or None
        """
        if self.context == utils.Context.EDITOR_ROUTES:
            if (self._preparedRoute is not None) and \
                    (self._preparedRoute not in self._routes.values()):
                routeNum = self._preparedRoute.routeNum
                self._routes[routeNum] = self._preparedRoute
                self.deselectRoute()
                return True
        self.deselectRoute()
        return False

    def deleteRoute(self, routeNum):
        """Deletes the route defined by routeNum"""
        if self.context == utils.Context.EDITOR_ROUTES:
            self.deselectRoute()
            del self._routes[routeNum]

    @QtCore.pyqtSlot(str)
    def prepareRoute(self, signalId):
        """Prepares the route starting with the SignalItem given by
        _selectedSignal and ending at signalId. Sets _selectedSignal to signalId
        if it is not set. Preparation means:
        - Check that the route leads to signalId, using the current directions
        of each PointsItem.
        - Set _preparedRoute to this route
        - Highlights the route if valid"""
        if self.context == utils.Context.EDITOR_ROUTES:
            si = self.trackItem(signalId)
            if self._selectedSignal is None or self._selectedSignal == si:
                # First signal selected
                self._selectedSignal = si
            else:
                pos = position.Position(self._selectedSignal,
                                        self._selectedSignal.previousItem, 0)
                directions = {}
                cur = pos.next()
                while not isinstance(cur.trackItem, enditem.EndItem):
                    ti = cur.trackItem
                    if isinstance(ti, pointsitem.PointsItem):
                        directions[ti.tiId] = int(ti.pointsReversed)
                    if ti == si:
                        if ti.isOnPosition(cur):
                            self._preparedRoute = route.Route({
                                "routeNum": str(self._nextRouteId),
                                "beginSignal": self._selectedSignal.tiId,
                                "endSignal": signalId,
                                "directions": directions,
                                "initialState": 0
                            })
                            self._preparedRoute.initialize(self)
                            self.selectedRoute = self._preparedRoute
                            self._nextRouteId += 1
                            self._selectedSignal = None
                            si.unselect()
                            return
                    cur = cur.next()

    @QtCore.pyqtSlot(str)
    def selectRoute(self, routeNum):
        """Selects the route given by routeNum in the routes editor."""
        if self.context == utils.Context.EDITOR_ROUTES:
            self.selectedRoute = self.routes[routeNum]
            self._preparedRoute = None

    @QtCore.pyqtSlot()
    def deselectRoute(self):
        """Desactivate the selected route in the routes editor"""
        if self.context == utils.Context.EDITOR_ROUTES:
            self._selectedSignal = None
            self.selectedRoute = None
            self._preparedRoute = None

    def getValidPosition(self):
        """Returns an arbitrary valid position on the scenery. Returns None,
        if no valid position has been found."""
        for ti in self._trackItems.values():
            if isinstance(ti, lineitem.LineItem):
                return position.Position(ti, ti.previousItem, 0.0)
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

    @QtCore.pyqtSlot(position.Position)
    def setSelectedTrainHead(self, pos):
        """Sets the trainHead of the selectedTrain to position if valid"""
        if self.context == utils.Context.EDITOR_TRAINS:
            if self._selectedTrain is not None and pos is not None:
                self._selectedTrain.trainHead = pos
                self.selectTrain(self.trains.index(self._selectedTrain))

    def addTrainType(self, code):
        """Adds an empty TrainType to the trainTypes list."""
        if self.context == utils.Context.EDITOR_TRAINTYPES:
            parameters = {
                "code": code,
                "description": "<Stock type description>",
                "maxSpeed": 25.0,
                "stdAccel": 0.5,
                "stdBraking": 0.5,
                "emergBraking": 1.5,
                "length": 100
            }
            self._trainTypes[code] = trains.TrainType(parameters)
            self._trainTypes[code].initialize(self)
            return True
        return False

    def deleteTrainType(self, code):
        """Deletes the trainType defined by code"""
        if self.context == utils.Context.EDITOR_TRAINTYPES:
            del self._trainTypes[code]

    def addService(self, code):
        """Adds an empty Service to the services list."""
        if self.context == utils.Context.EDITOR_SERVICES:
            parameters = {
                "serviceCode": code,
                "description": "<Service description>",
                "nextServiceCode": "",
                "autoReverse": 0
            }
            self._services[code] = trains.Service(parameters)
            self._services[code].initialize(self)
            return True
        return False

    def deleteService(self, code):
        """Deletes the service defined by code"""
        if self.context == utils.Context.EDITOR_SERVICES:
            del self._services[code]

    def addServiceLine(self, service, index):
        """Adds a service line to service at the current index"""
        if self.context == utils.Context.EDITOR_SERVICES:
            parameters = {
                "placeCode": "",
                "scheduledArrivalTime": "00:00:00",
                "scheduledDepartureTime": "00:00:00",
                "trackCode": "",
                "mustStop": 0
            }
            serviceLine = trains.ServiceLine(parameters)
            serviceLine.initialize(service)
            service.lines.insert(index, serviceLine)

    def deleteServiceLine(self, service, index):
        """Deletes the service line of service defined by index"""
        if self.context == utils.Context.EDITOR_SERVICES:
            del service.lines[index]

    def setupTrainsFromServices(self):
        """Removes all trains instances and creates a train for each relevant
        service, that is each service which is not following another one (i.e
        a service which is not the nextService of another service)."""
        self._trains = []
        serviceList = list(self.services.keys())
        for s in self.services.values():
            if s.nextServiceCode is not None and \
                    s.nextServiceCode != "":
                try:
                    serviceList.remove(s.nextServiceCode)
                except ValueError:
                    QtCore.qDebug("nextServiceCode: %s does not exist" %
                                  s.nextServiceCode)
        for sc in serviceList:
            train = self.addNewTrain()
            train.serviceCode = sc
            service = self.service(sc)
            placeCode, trackCode = service.getEntryPlaceData()
            entryLineItem = self.getLineItem(placeCode, trackCode)
            if entryLineItem is not None:
                if isinstance(entryLineItem.nextItem, enditem.EndItem):
                    previousTI = entryLineItem.nextItem
                else:
                    previousTI = entryLineItem.previousItem
                pos = position.Position(entryLineItem, previousTI,
                                        max(0, entryLineItem.realLength - 1))
                initialSpeed = entryLineItem.maxSpeed
            else:
                pos = self.getValidPosition()
                initialSpeed = 0
            train.trainHead = pos
            train.initialSpeed = initialSpeed
            train.trainTypeCode = service.plannedTrainType
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

    def addNewTrain(self):
        """Adds an empty train to the editor and returns that train"""
        if self.context == utils.Context.EDITOR_TRAINS:
            pos = self.getValidPosition()
            if pos is None:
                raise Exception("No valid position found. Check scenery.")
            parameters = {
                "serviceCode": list(self.services.values())[0].serviceCode,
                "trainTypeCode": list(self.trainTypes.values())[0].code,
                "speed": 0.0,
                "trainHead": pos,
                "appearTime": "00:00:00",
                "initialDelay": self.option("defaultDelayAtEntry"),
                "initialSpeed": 0,
            }
            train = trains.Train(parameters)
            train.initialize(self)
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

        # QtCore.qDebug(">> List of selected TI")
        # for ti in self.selectedItems:
        # QtCore.qDebug("TI selected: %i" %ti.tiId )
        # QtCore.qDebug("> List of selected GI")
        # for gi in self.scene.selectedItems():
        # QtCore.qDebug("GI selected: %i:%i" %
        #               (gi.trackItem.tiId, gi.itemId ))
        # QtCore.qDebug("---------")

    @QtCore.pyqtSlot()
    def updateSelection(self):
        """Updates the trackItem selection."""
        selectedItems = self.selectedItems.copy()
        for ti in selectedItems:
            self.removeItemFromSelection(ti)

        # Synchronise trackItem selection with graphicsItem selection
        for gi in self.scene.selectedItems():
            self.addItemToSelection(gi.trackItem)

    def addItemToSelection(self, ti, selected=True):
        """Add the trackItem ti to the selection if selected is True and
        remove it if it is False."""
        if selected:
            ti.selected = True
            if ti not in self.selectedItems:
                self.selectedItems.append(ti)
        else:
            ti.selected = False
            if ti in self.selectedItems:
                self.selectedItems.remove(ti)
        self.selectionChanged.emit()

    def removeItemFromSelection(self, ti):
        """Remove the trackItem ti from the selection."""
        self.addItemToSelection(ti, False)

    @QtCore.pyqtSlot()
    def clearSelection(self):
        """Clears the graphicsItem selection so that the trackItem selection
        will get updated."""
        self.scene.clearSelection()

    @QtCore.pyqtSlot()
    def copyToClipboard(self):
        """Copy the current selection to the clipboard"""
        self._clipbooard = copy.copy(self.selectedItems)

    @QtCore.pyqtSlot()
    def pasteFromClipboard(self):
        """Paste the items of the clipboard on the scene."""
        if len(self._clipbooard) == 0:
            return
        if len(self.selectedItems) > 0:
            refPos = self._selectedItems[0].end
        else:
            refPos = QtCore.QPointF(0, 0)
        translation = refPos + QtCore.QPointF(100, 100) - \
                      self._clipbooard[0].origin
        for ti in self._clipbooard:
            newTi = self.createTrackItem(ti.tiTypeStr,
                                         ti.origin + translation,
                                         ti.end + translation)
            newTi.maxSpeed = ti.maxSpeed
            newTi._realLength = ti.realLength
            if isinstance(newTi, signalitem.SignalItem):
                newTi.signalTypeStr = ti.signalTypeStr
                newTi.reverse = ti.reverse
                newTi.origin = ti.origin + translation
            elif isinstance(ti, pointsitem.PointsItem):
                newTi.commonEnd = ti.commonEnd
                newTi.normalEnd = ti.normalEnd
                newTi.reverseEnd = ti.reverseEnd
                newTi.origin = ti.origin + translation

    @QtCore.pyqtSlot()
    def deleteSelection(self):
        """Delete all the items of the current selection."""
        for ti in self.selectedItems.copy():
            self.removeItemFromSelection(ti)
            self.deleteTrackItem(ti.tiId)
