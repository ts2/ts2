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
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from trackitem import *

class PointsGraphicsItem(QGraphicsItem):
    """@brief Graphical item for points
    This class is the graphics of a PointsItem on the scene. Each instance belongs to a PointsItem which is defined in the constructor.
    @author Nicolas Piganeau"""
    def __init__(self, scene, pointsItem, parent = None):
        """Constructor for the PointsGraphicsItem class.
        @param signalItem Pointer to the PointsItem to which this PointsGraphicsItem belongs to.
        """
        super().__init__(parent, scene)
        self._pointsItem = pointsItem
        self.setZValue(100)

    def boundingRect(self):
        """Returns the bounding rectangle of the PointsGraphicsItem.
        See QGraphicsItem::boundingRect() for more info."""
        return QRectF(0,0,10,10)

    def paint(self, painter, option, widget = None ):
        """Painting function for the PointsGraphicsItem.
        This function asks for the owning PointsItem to paint its painter."""
        self._pointsItem.drawPoints(painter)

    mouseClicked = pyqtSignal(QGraphicsSceneMouseEvent)

    def mouseReleaseEvent(self, event):
        """mouseReleaseEvent function, called when the PointsGraphicsItem is clicked. This function simply
        emits the signal mouseClicked, which can be caught by the owning PointsItem."""
        self.mouseClicked.emit(event)


class PointsItem(TrackItem):
    """PointsItem Class
    TODO Document the class"""
    def __init__(self, simulation, record):
        """Constructor for the PointsItem class"""
        super().__init__(simulation, record)
        self._tiType = "P"
        x = record.value("x")
        y = record.value("y")
        cpx = record.value("xf")
        cpy = record.value("yf")
        npx = record.value("xn")
        npy = record.value("yn")
        rpx = record.value("xr")
        rpy = record.value("yr")
        self._commonPoint = QPointF(cpx, cpy) + self.middle
        self._normalPoint = QPointF(npx, npy) + self.middle
        self._reversePoint = QPointF(rpx, rpy) + self.middle
        self._realOrigin = QPointF(x,y) + QPointF(-5,-5)
        self._origin = QPointF(x,y) + QPointF(cpx, cpy)
        self._end = QPointF(x,y) + QPointF(npx, npy)
        self._pointsReversed = False
        self._reverseItem = None
        pgi = PointsGraphicsItem(simulation.scene, self)
        pgi.setPos(self._realOrigin)
        pgi.setCursor(Qt.PointingHandCursor)
        pgi.setToolTip(self.tr("Points no: %i") % self.tiId)
        self._gi = pgi
        self.updateGraphics()

    @property
    def size(self):
        return QSizeF(10,10)

    @property
    def realOrigin(self):
        return self._realOrigin

    @property
    def pointsReversed(self):
        return self._pointsReversed

    @pointsReversed.setter
    def pointsReversed(self, rev):
        self._pointsReversed = True if rev else False
        
    @property
    def middle(self):
        return QPointF(5,5)

    @property
    def reversePoint(self):
        return self._reversePoint

    @property
    def commonItem(self):
        return self._previousItem

    @property
    def normalItem(self):
        return self._nextItem

    @property
    def reverseItem(self):
        return self._reverseItem

    @reverseItem.setter
    def reverseItem(self, ti):
        """Sets the _reverseItem variable which points to the next TrackItem in the
        reverse direction. For common direction, _previousItem is used and for
        normal direction, _nextItem is used.
        @param ti Pointer to the TrackItem to set"""
        self._reverseItem = ti


    def drawPoints(self, p):
        """Draws the points on the painter given as parameter.
        This function is called by PointsGraphicsItem.paint.
        @param p The painter on which to draw the signal."""
        pen = self.getPen()
        if self.trainPresent():
            pen.setColor(Qt.red)
        p.setPen(pen)

        p.drawLine(self._commonPoint, self.middle)
        if not self.pointsReversed:
            p.drawLine(self._normalPoint, self.middle)
        else:
            p.drawLine(self._reversePoint, self.middle)

    def getFollowingItem(self, precedingItem, direction = -1):
        """Overload of TrackItem.getFollowingItem for PointsItem, including the direction
        @param precedingItem The TrackItem we come from
        @param direction The direction of the points (0 => normal, positive => reverse,
        negative => according to self._pointsReversed)"""
        if precedingItem == self.commonItem:
            if direction < 0:
                return self.reverseItem if self.pointsReversed else self.normalItem
            elif direction == 0:
                return self.normalItem
            else:
                return self.reverseItem
        else:
            return self.commonItem

    def setActiveRoute(self, r, previous):
        """ Sets the active route information (see TrackItem.setActiveRoute()).
        Here, this function also changes the points direction."""
        if r.direction(self.tiId) == 0:
            self._pointsReversed = False
        else:
            self._pointsReversed = True
        super().setActiveRoute(r, previous)

