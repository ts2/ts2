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

class TrackItem(QObject):

    def __init__(self, simulation, record):
        super().__init__()
        self._simulation = simulation
        self._tiId = record.value("tiid").toInt()
        self._name = record.value("name").toString()
        self._tiType = "0"
        self._nextItem = None
        self._previousItem = None
        self._activeRoute = None
        self._activeRoutePreviousItem = None
        self._selected = false
        x = record.value("x").toDouble()
        y = record.value("y").toDouble()
        self._origin = QPointF(x, y)
        self._end = _origin
        self._realLength = 1.0
        self._trainHead = -1
        self._trainTail = -1
        self._place = None
        self._conflictTrackItem = None
        self._gi = QGraphicsItem()

    @pyqtProperty(QPointF)
    def origin(self):
        return self._origin
    
    @pyqtProperty(QPointF)
    def end(self):
        return self._end

    @pyqtProperty(str)
    def name(self):
        return self._name
    
    @pyqtProperty(int)
    def tiId(self):
        return self._tiId
    
    @pyqtProperty(str)
    def tiType(self): 
        return self._tiType
    
    @pyqtProperty(Simulation)
    def simulation(self): 
        return self._simulation
    
    @pyqtProperty(QGraphicsItem)
    def graphicsItem(self): 
        return self._gi

    @pyqtProperty(bool)
    def highlighted(self): 
        if self._activeRoute is None:
            return false
        else:
            return true
    
    @pyqtProperty(bool)
    def selected(self):
        return self._selected

    @pyqtProperty(float)
    def realLength(self):
        return self._realLength
    
    @pyqtProperty(Place)
    def place(self):
        return self._place

    @pyqtProperty(TrackItem)
    def nextItem(self):
        return self._nextItem

    @nextItem.setter
    def setNextItem(self, ni): 
        if self._nextItem is None:
            self._nextItem = ni
    
    @pyqtProperty(TrackItem)
    def previousItem(self):
        return self._previousItem
    
    @previousItem.setter
    def setPreviousItem(self, pi):
        if self._previousItem is None:
            self._previousItem = pi

    def getFollowingItem(self, precedingItem, direction = -1):
        """Returns the following TrackItem linked to this one, knowing we come from precedingItem
        @param precedingItem TrackItem where we come from (along a route)
        @return Either _nextItem or _previousItem,depending which way we come from.
        """
        if precedingItem == self._previousItem:
            return self._nextItem
        elif precedingItem == self._nextItem:
            return self._previousItem
        else:
            return None
    
    @pyqtProperty(Route)
    def activeRoute(self):
        return self._activeRoute

    @pyqtProperty(TrackItem)
    def activeRoutePreviousItem(self):
        return self._activeRoutePreviousItem
    
    def setActiveRoute(self, r, previous):
        """Sets the activeRoute and activeRoutePreviousItem informations. It is called upon Route
        activation. These information are used when other routes are activated in order to check
        the potential conflicts.
        @param r The newly active Route on this TrackItem.
        @param previous The previous TrackItem on this route (to know the direction)."""
        self._activeRoute = r
        self._activeRoutePreviousItem = previous
        self.updateGraphics()

    def resetActiveRoute(self):
        """Resets the activeRoute and activeRoutePreviousItem informations. It is called upon route
        desactivation."""
        self._activeRoute = None
        self._activeRoutePreviousItem = None
        self.updateGraphics()

    def setTrainHead(self, pos, prevTI = None):
        """Sets the trainHead indication on this TrackItem. The trainHead indication enables the
        drawing of a Train on this TrackItem.
        @param pos is the position of the trainHead in metres. Set to -1 if no Train head on this
        TrackItem
        @param prevTI To define the direction of the train, prevTI is a pointer to the previous
        TrackItem where the Train comes from.
        """
        if pos == -1:
            self._trainHead = -1
        else:
            if prevTI == self._previousItem:
                self._trainHead = pos
            else:
                self._trainHead = self._realLength - pos
        self.updateGraphics()


    def setTrainTail(self, pos, prevTI = None):
        """Same as setTrainHead() but with the trainTail information."""
        if pos == -1:
            self._trainTail = -1
        else:
            if prevTI == self._previousItem:
                self._trainTail = pos
            else:
                self._trainTail = self._realLength - pos
        self.updateGraphics()
    
    def trainPresent(self):
        if self._trainHead != -1 or self._trainTail != -1:
            return true
        else:
            return false
    
    def isOnPosition(self, p):
        if p.trackItem() == self:
            return true
        else:
            return false
    
    def trainHeadActions(self, serviceCode):
        pass
    
    def trainTailActions(self, serviceCode):
        if self.activeRoute() is not None:
            if not self.activeRoute().isPersistent():
                beginSignalNextRoute = self.activeRoute().beginSignal().nextActiveRoute()
                if beginSignalNextRoute is None or beginSignalNextRoute != self.activeRoute():
                    self.activeRoutePreviousItem().resetActiveRoute()
                    self.updateGraphics()

    @pyqtProperty(TrackItem)
    def conflictTI(self):
        return self._conflictTrackItem
    
    @conflictTI.setter
    def setConflictTI(self, ti):
        self._conflictTrackItem = ti

    def __eq__(self, ti):
        if self._tiId == ti._tiId:
            return true
        else:
            return false
            
    def __ne__(self, ti):
        if self._tiId == ti._tiId:
            return true
        else:
            return false

    def updateGraphics(self):
        self._gi.update()

    def getPen(self):
        pen = QPen()
        pen.setWidth(3)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        if highlighted():
            pen.setColor(Qt.white)
        else:
            pen.setColor(Qt.darkGray)
        return pen


