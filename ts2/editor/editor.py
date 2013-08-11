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

from PyQt4 import QtGui, QtCore
from ts2.simulation import Simulation
from ts2.scenery import SignalItem, SignalTimerItem, LineItem, EndItem, \
                    PlatformItem, TrackItem, BumperItem, PointsItem
from ts2 import utils
from ts2.editor import EditorSceneBackground

class Editor(Simulation):
    """The Editor class holds all the logic behind the simulation editor."""
    
    def __init__(self, editorWindow):
        """Constructor for the Editor class"""
        super().__init__(editorWindow)
        self._scene = QtGui.QGraphicsScene(self)
        self._libraryScene = QtGui.QGraphicsScene()
        self._sceneBackground = EditorSceneBackground(self, 0, 0, 1024, 768)
        self._sceneBackground.setZValue(-100)
        self._scene.addItem(self._sceneBackground)
        self._nextId = 1
        self._grid = 5.0
        
        # Construct the library
        self.librarySignalItem = SignalItem(self, \
                {"tiid":-1, "name":"Signal", "x":15, "y":5, "reverse":0})
        self.librarySignalTimerItem = SignalTimerItem(self, \
                {"tiid":-2, "name":"Timer Signal", "x":80, "y":5, \
                 "reverse":0, "timersw":1.0, "timerwc":1.0})
        self.libraryPointsItem = PointsItem(self, \
                {"tiid":-3, "name":"Points", "x":45, "y":55, "xf":-5, \
                 "yf":0, "xn":5, "yn":0, "xr":5, "yr":-5})
        self.libraryBumperItem = BumperItem(self, \
                {"tiid":-4, "name":"Bumper", "x":90, "y":55, "reverse":0})
        self.libraryLineItem = LineItem(self, \
                {"tiid":-5, "name":"Line", "x":15, "y":105, "xf":70, \
                 "yf":105, "maxspeed":25.0, "reallength":0.0, \
                 "placecode":None, "trackcode":None})
        self.libraryPlatformItem = PlatformItem(self, \
                {"tiid":-6, "name":"Platform", "x":85, "y":105, "xf":145, \
                 "yf":105,  "xn":90, "yn":85, "xr":140, "yr":97, \
                 "maxspeed":25.0, "reallength":0.0, \
                 "placecode":None, "trackcode":None})
        self.libraryEndItem = EndItem(self, \
                {"tiid":-7, "name":"End", "x":45, "y":155})
    
    @property
    def libraryScene(self):
        """The pseudo-scene for the TrackItem "tool box" """
        return self._libraryScene
    
    def registerGraphicsItem(self, graphicItem):
        """Reimplemented from Simulation. Adds the graphicItem to the scene
        or to the libraryScene (if tiId <0)."""
        if hasattr(graphicItem, "trackItem") and \
           graphicItem.trackItem.tiId < 0:
            self._libraryScene.addItem(graphicItem)
        else:
            self._scene.addItem(graphicItem)

    def createRoute(self, siId, persistent):
        """Reimplemented from Simulation so as not to do anything"""
        pass
    
    def deleteRoute(self, siId):
        """Reimplemented from Simulation so as not to do anything"""
        pass
    
    @property
    def context(self):
        """Reimplemented from Simulation to return the EDITOR Context"""
        return utils.Context.EDITOR
    
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
            ti = LineItem(self, parameters)
        elif tiType == "LP":
            ti = PlatformItem(self, parameters)
        elif tiType == "S":
            ti = SignalItem(self, parameters)
        elif tiType == "SB":
            ti = BumperItem(self, parameters)
        elif tiType == "ST":
            ti = SignalTimerItem(self, parameters)
        elif tiType == "P":
            ti = PointsItem(self, parameters)
        elif tiType == "E":
            ti = EndItem(self, parameters)
        else:
            ti = TrackItem(self, parameters)
        self._trackItems[self._nextId] = ti
        self._nextId += 1
    
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
    