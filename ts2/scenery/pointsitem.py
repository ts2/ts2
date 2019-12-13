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

from Qt import QtCore, QtWidgets, Qt

from ts2 import utils
from ts2.scenery import helper, abstract

translate = QtWidgets.qApp.translate


def getEndNames():
    """
    :return: a list of point end names TODO
    """
    return [
        translate("PointsItem", "N"),
        translate("PointsItem", "NE"),
        translate("PointsItem", "E"),
        translate("PointsItem", "SE"),
        translate("PointsItem", "S"),
        translate("PointsItem", "SW"),
        translate("PointsItem", "W"),
        translate("PointsItem", "NW")
    ]


def getEndValues():
    """
    :return: a list of values TODO
    """
    return [(0, -5), (5, -5), (5, 0), (5, 5),
            (0, 5), (-5, 5), (-5, 0), (-5, -5)]


class PointsItem(abstract.TrackItem):
    """A ``PointsItem`` is a three-way junction.

    The three ends and called:

    - common end
    - normal end
    - reverse end

    .. code-block:: bash

                            ____________ reverse
                           /
        common ___________/______________normal

    - Trains can go from common end to normal or reverse ends depending on the
      state of the points.
    - They cannot go from normal end to reverse end.
    - Usually, the normal end is aligned with the common end and the reverse end
      is sideways, but this is not mandatory.
    """

    def __init__(self, parameters):
        """
        :param dict paramaters:
        """
        self._commonEnd = QtCore.QPointF()
        self._normalEnd = QtCore.QPointF()
        self._reverseEnd = QtCore.QPointF()
        self._center = QtCore.QPointF()
        self._pairedTiId = ""
        super().__init__(parameters)
        self._pointsReversed = False
        self._reverseItem = None
        self.defaultZValue = 60
        pgi = helper.TrackGraphicsItem(self)
        pgi.setPos(self._center)
        pgi.setZValue(self.defaultZValue)
        pgi.setCursor(Qt.PointingHandCursor)
        pgi.setToolTip(self.toolTipText)
        self._gi[0] = pgi

    def updateFromParameters(self, parameters):
        super(PointsItem, self).updateFromParameters(parameters)
        x = parameters.get("x", 0.0)
        y = parameters.get("y", 0.0)
        cpx = parameters.get("xf", 0.0)
        cpy = parameters.get("yf", 0.0)
        npx = parameters.get("xn", 0.0)
        npy = parameters.get("yn", 0.0)
        rpx = parameters.get("xr", 0.0)
        rpy = parameters.get("yr", 0.0)
        self._commonEnd = QtCore.QPointF(cpx, cpy)
        self._normalEnd = QtCore.QPointF(npx, npy)
        self._reverseEnd = QtCore.QPointF(rpx, rpy)
        self._center = QtCore.QPointF(x, y)
        self._pairedTiId = parameters.get("pairedTiId", "")

    def initialize(self, simulation):
        """Initialize the item after all items are loaded."""
        params = self._parameters
        self._reverseItem = simulation.trackItem(params.get('reverseTiId'))
        super().initialize(simulation)

    def updateData(self, msg):
        if "reversed" in msg:
            self.pointsReversed = msg["reversed"]
        super(PointsItem, self).updateData(msg)

    @staticmethod
    def getProperties():
        """
        :return: List of ptoperties
        :rtype: list
        """
        return abstract.TrackItem.getProperties() + [
            helper.TIProperty("commonEndTuple",
                              translate("PointsItem", "Common End"),
                              False,
                              "enum",
                              getEndNames(),
                              getEndValues()),
            helper.TIProperty("normalEndTuple",
                              translate("PointsItem", "Normal End"),
                              False,
                              "enum",
                              getEndNames(),
                              getEndValues()),
            helper.TIProperty("reverseEndTuple",
                              translate("PointsItem", "Reverse End"),
                              False,
                              "enum",
                              getEndNames(),
                              getEndValues()),
            helper.TIProperty("pairedTiId", translate("PointsItem",
                                                      "Coupled Points"))
        ]

    def for_json(self):
        """Dumps this points item to JSON."""
        jsonData = super().for_json()
        if self.reverseItem is not None:
            reverseTiId = self.reverseItem.tiId
        else:
            reverseTiId = None
        jsonData.update({
            "x": self._center.x(),
            "y": self._center.y(),
            "xf": self._commonEnd.x(),
            "yf": self._commonEnd.y(),
            "xn": self._normalEnd.x(),
            "yn": self._normalEnd.y(),
            "xr": self._reverseEnd.x(),
            "yr": self._reverseEnd.y(),
            "pairedTiId": self._pairedTiId,
            "reverseTiId": reverseTiId
        })
        return jsonData

    # ## Properties #####################################################

    # Ends in scene coordinates
    def _getOrigin(self):
        """
        :return: the origin point of the PointsItem, which is actually the
                 **common end** in the scene coordinates
        :rtype: ``QPointF``
        """
        return self.center + self.commonEnd

    def _setOrigin(self, pos):
        """Setter function for the origin property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            grid = self.simulation.grid
            x = round((pos.x() - self.commonEnd.x()) / grid) * grid
            y = round((pos.y() - self.commonEnd.y()) / grid) * grid
            self._center = QtCore.QPointF(x, y)
            self.graphicsItem.setPos(self.center)
            self.updateGraphics()

    def _getEnd(self):
        """
        :return: the origin point of the PointsItem, which is actually the
                 **normal end** in the scene coordinates
        :rtype: ``QPointF``
        """
        return self.center + self.normalEnd

    def _getReverse(self):
        """
        :return: the reverse point of the PointsItem, which is actually the
                 **reverse end** in the scene coordinates
        :rtype: ``QPointF``
        """
        return self.center + self.reverseEnd

    def _getCenter(self):
        """
        :return: the center point of the PointsItemn the scene's coordinates.
        :rtype: ``QPointF``
        """
        return self._center

    origin = property(_getOrigin, _setOrigin)
    end = property(_getEnd)
    reverse = property(_getReverse)
    center = property(_getCenter)

    # Ends in item's coordinates

    def _getCommonEnd(self):
        """
        :return: the **common end** point in the item's coordinates
        :rtype: ``QPointF``
        """
        return self._commonEnd

    def _setCommonEnd(self, value):
        """Setter for the commonEndStr property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.graphicsItem.prepareGeometryChange()
            self._commonEnd = QtCore.QPointF(value)
            self.updateGraphics()

    def _getNormalEnd(self):
        """
        :return: the **normal end** in the item's coordinates.
        :rtype: ``QPointF``
        """
        return self._normalEnd

    def _setNormalEnd(self, value):
        """Setter for the commonEndStr property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.graphicsItem.prepareGeometryChange()
            self._normalEnd = QtCore.QPointF(value)
            self.updateGraphics()

    def _getReverseEnd(self):
        """
        :return: the **reverse end** in the item's coordinates.
        :rtype: ``QPointF``
        """
        return self._reverseEnd

    def _setReverseEnd(self, value):
        """Setter for the commonEndStr property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.graphicsItem.prepareGeometryChange()
            self._reverseEnd = QtCore.QPointF(value)
            self.updateGraphics()

    def _getMiddle(self):
        """
        :return: the central poin of the PointsItem, in the item's coordinates.
        :rtype: ``QPointF``
        """
        return QtCore.QPointF(0, 0)

    commonEnd = property(_getCommonEnd, _setCommonEnd)
    normalEnd = property(_getNormalEnd, _setNormalEnd)
    reverseEnd = property(_getReverseEnd, _setReverseEnd)
    middle = property(_getMiddle)

    commonEndTuple = property(abstract.qPointFTupler("commonEnd"),
                              abstract.qPointFDetupler("commonEnd"))
    normalEndTuple = property(abstract.qPointFTupler("normalEnd"),
                              abstract.qPointFDetupler("normalEnd"))
    reverseEndTuple = property(abstract.qPointFTupler("reverseEnd"),
                               abstract.qPointFDetupler("reverseEnd"))

    # Other properties

    def _getPairedTiId(self):
        """
        :return: the conflict trackitem ID.
        :rtype: str
        """
        return self._pairedTiId

    def _setPairedTiId(self, value):
        """Setter function for the conflictTiId property."""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if value:
                self._pairedTiId = value
                pairedItem = self.simulation.trackItem(value)
                if pairedItem:
                    pairedItem._pairedTiId = self.tiId
            else:
                pairedItem = self.simulation.trackItem(self._pairedTiId)
                if pairedItem:
                    pairedItem._pairedTiId = ""
                self._pairedTiId = ""

    pairedTiId = property(_getPairedTiId, _setPairedTiId)

    @property
    def pointsReversed(self):
        """
        :return: ``True`` if the points are reversed, otherwise ``False``
        :rtype: bool
        """
        return self._pointsReversed

    @pointsReversed.setter
    def pointsReversed(self, rev):
        """Setter function for the pointsReversed property"""
        self._pointsReversed = True if rev else False

    @property
    def commonItem(self):
        """
        :return: the item linked to the **common end** of this PointsItem,
        :rtype: :class:`~ts2.scenery.abstract.TrackItem`
        """
        return self._previousItem

    @property
    def normalItem(self):
        """
        :return: the TrackItem linked to the **normal end** of this PointsItem,
        :rtype: :class:`~ts2.scenery.abstract.TrackItem`
        """
        return self._nextItem

    @property
    def reverseItem(self):
        """
        :return: the TrackItem linked to the **reverse end** of this PointsItem,
        :rtype: :class:`~ts2.scenery.abstract.TrackItem`
        """
        return self._reverseItem

    @reverseItem.setter
    def reverseItem(self, ti):
        """Setter for the reverseItem property"""
        self._reverseItem = ti

    @property
    def toolTipText(self):
        """
        :return: text to show on the tool tip
        :rtype: str
        """
        return self.tr("Points no: %s" % self.name)

    # ## Methods ########################################################

    def getFollowingItem(self, precedingItem, direction=-1):
        """Overload of TrackItem.getFollowingItem for PointsItem, including the direction

        :param precedingItem: The TrackItem we come from
        :param direction: The direction of the points

                          - 0 => normal
                          - positive => reverse
                          - negative => according to ``self._pointsReversed``
        """
        if precedingItem == self.commonItem:
            if direction < 0:
                return \
                    self.reverseItem if self.pointsReversed else self.normalItem
            elif direction == 0:
                return self.normalItem
            else:
                return self.reverseItem
        elif precedingItem == self.normalItem or \
                precedingItem == self.reverseItem:
            return self.commonItem
        else:
            raise Exception("Items not linked: %s and %s" %
                            (self.tiId, precedingItem.tiId))

    # ## Graphics methods ###############################################

    def graphicsPaint(self, p, options, itemId, widget=None):
        """Draws the points on the painter given as parameter.
        This function is called by PointsGraphicsItem.paint.
        @param p The painter on which to draw the signal."""
        pen = self.getPen()

        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            p.setPen(pen)
            p.drawLine(self.commonEnd, self.middle)
            pen.setWidth(2)
            p.setPen(pen)
            p.drawLine(self.normalEnd, self.middle)
            pen.setWidth(1)
            p.setPen(pen)
            p.drawLine(self.reverseEnd, self.middle)

            # Draw the connection rects
            self.drawConnectionRect(p, self.commonEnd)
            self.drawConnectionRect(p, self.normalEnd)
            self.drawConnectionRect(p, self.reverseEnd)
        else:
            if self.trainPresent():
                pen.setColor(Qt.red)
            p.setPen(pen)
            p.drawLine(self.commonEnd, self.middle)
            if self.pointsReversed:
                p.drawLine(self.reverseEnd, self.middle)
            else:
                p.drawLine(self.normalEnd, self.middle)

    def graphicsBoundingRect(self, itemId):
        """This function is called by the owned TrackGraphicsItem to return
        its bounding rectangle. Reimplemented from TrackItem"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if self.tiId.startswith("__EDITOR__"):
                # Toolbox item
                return QtCore.QRectF(-50, -25, 100, 50)
            else:
                return QtCore.QRectF(-10, -10, 20, 20)
        else:
            return QtCore.QRectF(-5, -5, 10, 10)

    def graphicsMousePressEvent(self, event, itemId):
        """This function is called by the owned TrackGraphicsItem to handle
        its mousePressEvent. In the PointsItem class, this function reverses
        the points."""
        super().graphicsMousePressEvent(event, itemId)
        if self.simulation.context == utils.Context.EDITOR_ROUTES:
            if self.pointsReversed:
                self.pointsReversed = False
            else:
                self.pointsReversed = True
            self.updateGraphics()
