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

from Qt import QtCore, Qt

from ts2.scenery import abstract, helper
from ts2 import utils

BIG = 1000000000


class EndItem(abstract.TrackItem):
    """End items are invisible items to which the free ends of other
    trackitems must be connected to prevent the simulation from crashing.

    End items are defined by:

    - their titype which is “E”
    - and their position (x, y)
    - They are single point items
    """
    def __init__(self, parameters):
        """
        :param dict paramaters:
        """
        super().__init__(parameters)
        self._realLength = BIG
        egi = helper.TrackGraphicsItem(self)
        egi.setPos(self.origin)
        self._gi[0] = egi

    def initialize(self, simulation):
        """Initialize the item after all items are loaded."""
        super().initialize(simulation)
        if self.simulation.context in utils.Context.EDITORS:
            self._gi[0].setCursor(Qt.PointingHandCursor)

    def for_json(self):
        """Dumps this end item to JSON."""
        jsonData = super().for_json()
        jsonData.update({
            "nextTiId": None
        })
        return jsonData

    def _getEnd(self):
        """
        :return: a point far away of the scene
        :rtype: ``QPointF``
        """
        return QtCore.QPointF(-BIG, -BIG)

    end = property(_getEnd)

    def getFollowingItem(self, precedingItem, direction=-1):
        """
        Reimplemented from :class:`~ts2.scenery.abstract.TrackItem` . :func:`~ts2.scenery.abstract.TrackItem.getFollowingItem`

        :return: ``None`` if going to the free end
        :rtype: ``None`` or :class:`~ts2.scenery.abstract.TrackItem`
        """
        if precedingItem == self._previousItem:
            return None
        else:
            return self._previousItem

    def graphicsBoundingRect(self, itemId):
        """Reimplemented from :class:`~ts2.scenery.abstract.TrackItem` . :func:`~ts2.scenery.abstract.TrackItem.graphicsBoundingRect`

        :return: The bounding rectangle of the owned :class:`~ts2.scenery.helper.TrackGraphicsItem`.
        :rtype: ``QRectF``
        """
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if self.tiId.startswith("__EDITOR__"):
                # Toolbox itemId
                return QtCore.QRectF(-50, -25, 100, 50)
            else:
                return QtCore.QRectF(-5, -5, 10, 10)
        else:
            return super().graphicsBoundingRect(itemId)

    def graphicsPaint(self, p, options, itemId, widget=0):
        """ Reimplemented from TrackItem.graphicsPaint"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            pen = self.getPen()
            if self.selected:
                pen.setColor(Qt.magenta)
            else:
                pen.setColor(Qt.cyan)
            p.setPen(pen)
            p.drawEllipse(-1.5, -1.5, 3, 3)
            self.drawConnectionRect(p, QtCore.QPointF(0, 0))
