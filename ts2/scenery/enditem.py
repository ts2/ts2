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

from ts2.scenery import TrackItem, TrackGraphicsItem, TIProperty
from ts2 import utils
from PyQt4 import QtCore
from PyQt4.QtCore import Qt

BIG = 1000000000

class EndItem(TrackItem):
    """End items are invisible items to which the free ends of other
    trackitems must be connected to prevent the simulation from crashing TS2.
    End items are defined by their titype which is “E” and their position
    (x, y). They are single point items.
    """
    def __init__(self, simulation, parameters):
        """Constructor for the EndItem class"""
        super().__init__(simulation, parameters)
        self._tiType = "E"
        self._realLength = BIG
        egi = TrackGraphicsItem(self)
        egi.setPos(self.realOrigin)
        if self._simulation.context in utils.Context.EDITORS:
            egi.setCursor(Qt.PointingHandCursor)
        self._gi = egi
        simulation.registerGraphicsItem(self._gi)

    @property
    def end(self):
        """Returns a point far away of the scene"""
        return QtCore.QPointF(-BIG, -BIG)

    @property
    def realOrigin(self):
        return self._origin

    @realOrigin.setter
    def realOrigin(self, pos):
        """Setter function for the realOrigin property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            grid = self._simulation.grid
            x = round((pos.x() + 3.0) / grid) * grid
            y = round((pos.y() + 3.0) / grid) * grid
            self._origin = QtCore.QPointF(x, y)
            self._gi.setPos(self.realOrigin)
            self.updateGraphics()

    def getFollowingItem(self, precedingItem, direction = -1):
        """Reimplemented from TrackItem to return None if going to the free
        end."""
        if precedingItem == self._previousItem:
            return None
        else:
            return self._previousItem

    def graphicsBoundingRect(self):
        """Reimplemented from TrackItem.graphicsBoundingRect to return the
        bounding rectangle of the owned TrackGraphicsItem."""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            return QtCore.QRectF(-5, -5, 10, 10)
        else:
            return super().graphicsBoundingRect()

    def graphicsPaint(self, p, options, widget):
        """ Reimplemented from TrackItem.graphicsPaint"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            pen = self.getPen()
            pen.setColor(Qt.cyan)
            p.setPen(pen)
            p.drawEllipse(-1.5, -1.5, 3, 3)
            self.drawConnectionRect(p, QtCore.QPointF(0, 0))
