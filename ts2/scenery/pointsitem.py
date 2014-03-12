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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from ts2 import utils
from ts2.scenery import helper, abstract

translate = QtCore.QCoreApplication.translate

class PointsItem(abstract.TrackItem):
    """A points item is a three-way junction.
    We call the three ends: common end, normal end and reverse end.
    Trains can go from common end to normal or reverse ends depending on the
    state of the points. They cannot go from normal end to reverse end.
    Usually, the normal end is aligned with the common end and the reverse end
    is sideways, but this is not mandatory.
    """
    def __init__(self, simulation, parameters):
        """Constructor for the PointsItem class"""
        super().__init__(simulation, parameters)
        self.tiType = "P"
        x = parameters["x"]
        y = parameters["y"]
        cpx = parameters["xf"]
        cpy = parameters["yf"]
        npx = parameters["xn"]
        npy = parameters["yn"]
        rpx = parameters["xr"]
        rpy = parameters["yr"]
        self._commonEnd = QtCore.QPointF(cpx, cpy)
        self._normalEnd = QtCore.QPointF(npx, npy)
        self._reverseEnd = QtCore.QPointF(rpx, rpy)
        self._center = QtCore.QPointF(x,y)
        self._pointsReversed = False
        self._reverseItem = None
        self.defaultZValue = 60
        pgi = helper.TrackGraphicsItem(self)
        pgi.setPos(self._center)
        pgi.setZValue(self.defaultZValue)
        pgi.setCursor(Qt.PointingHandCursor)
        pgi.setToolTip(self.toolTipText)
        self._gi[0] = pgi
        self.simulation.registerGraphicsItem(pgi)
        self.updateGraphics()

    endNames = [translate("PointsItem", "N"),
                translate("PointsItem","NE"),
                translate("PointsItem","E"),
                translate("PointsItem","SE"),
                translate("PointsItem","S"),
                translate("PointsItem","SW"),
                translate("PointsItem","W"),
                translate("PointsItem","NW")]
    endValues = [(0, -5), (5, -5), (5, 0), (5, 5),
                 (0, 5), (-5, 5), (-5, 0), (-5, -5)]

    properties = abstract.TrackItem.properties + [
                            helper.TIProperty("commonEndTuple",
                                              translate("PointsItem",
                                                        "Common End"),
                                              False, "pointsEnd"),
                            helper.TIProperty("normalEndTuple",
                                              translate("PointsItem",
                                                        "Normal End"),
                                              False, "pointsEnd"),
                            helper.TIProperty("reverseEndTuple",
                                              translate("PointsItem",
                                                        "Reverse End"),
                                              False, "pointsEnd")]

    def getSaveParameters(self):
        """Returns the parameters dictionary to save this TrackItem to the
        database"""
        parameters = super().getSaveParameters()
        if self.reverseItem is not None:
            reverseTiId = self.reverseItem.tiId
        else:
            reverseTiId = None
        parameters.update({
                                "x":self._center.x(),
                                "y":self._center.y(),
                                "xf":self._commonEnd.x(),
                                "yf":self._commonEnd.y(),
                                "xn":self._normalEnd.x(),
                                "yn":self._normalEnd.y(),
                                "xr":self._reverseEnd.x(),
                                "yr":self._reverseEnd.y(),
                                "rtiid":reverseTiId})
        return parameters

    ### Properties #####################################################

    # Ends in scene coordinates
    def _getOrigin(self):
        """Returns the origin QPointF of the PointsItem, which is actually the
        common end in the scene coordinates"""
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
        """Returns the origin QPointF of the PointsItem, which is actually the
        normal end in the scene coordinates"""
        return self.center + self.normalEnd

    def _getReverse(self):
        """Returns the reverse QPointF in the scene coordinates"""
        return self.center + self.reverseEnd

    def _getCenter(self):
        """Returns the central QPointF of the PointsItem, in the scene's
        coordinates."""
        return self._center

    origin = property(_getOrigin, _setOrigin)
    end = property(_getEnd)
    reverse = property(_getReverse)
    center = property(_getCenter)

    # Ends in item's coordinates

    def _getCommonEnd(self):
        """Returns the common end in the item's coordinates."""
        return self._commonEnd

    def _setCommonEnd(self, value):
        """Setter for the commonEndStr property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.graphicsItem.prepareGeometryChange()
            self._commonEnd = QtCore.QPointF(value)
            self.updateGraphics()

    def _getNormalEnd(self):
        """Returns the normal end in the item's coordinates."""
        return self._normalEnd

    def _setNormalEnd(self, value):
        """Setter for the commonEndStr property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.graphicsItem.prepareGeometryChange()
            self._normalEnd = QtCore.QPointF(value)
            self.updateGraphics()

    def _getReverseEnd(self):
        """Returns the reverse end in the item's coordinates."""
        return self._reverseEnd

    def _setReverseEnd(self, value):
        """Setter for the commonEndStr property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.graphicsItem.prepareGeometryChange()
            self._reverseEnd = QtCore.QPointF(value)
            self.updateGraphics()

    def _getMiddle(self):
        """Returns the central QPointF of the PointsItem, in the item's
        coordinates."""
        return QtCore.QPointF(0, 0)

    commonEnd = property(_getCommonEnd, _setCommonEnd)
    normalEnd = property(_getNormalEnd, _setNormalEnd)
    reverseEnd = property(_getReverseEnd, _setReverseEnd)
    middle = property(_getMiddle)

    commonEndTuple = property(abstract.TrackItem.qPointFTupler("commonEnd"),
                            abstract.TrackItem.qPointFDetupler("commonEnd"))
    normalEndTuple = property(abstract.TrackItem.qPointFTupler("normalEnd"),
                            abstract.TrackItem.qPointFDetupler("normalEnd"))
    reverseEndTuple = property(abstract.TrackItem.qPointFTupler("reverseEnd"),
                            abstract.TrackItem.qPointFDetupler("reverseEnd"))

    # Other properties

    @property
    def pointsReversed(self):
        """Returns true if the points are reversed, false otherwise"""
        return self._pointsReversed

    @pointsReversed.setter
    def pointsReversed(self, rev):
        """Setter function for the pointsReversed property"""
        self._pointsReversed = True if rev else False

    @property
    def commonItem(self):
        """Returns the TrackItem linked to the common end of this PointsItem,
        """
        return self._previousItem

    @property
    def normalItem(self):
        """Returns the TrackItem linked to the normal end of this PointsItem,
        """
        return self._nextItem

    @property
    def reverseItem(self):
        """Returns the TrackItem linked to the reverse end of this PointsItem
        """
        return self._reverseItem

    @reverseItem.setter
    def reverseItem(self, ti):
        """Setter for the reverseItem property"""
        self._reverseItem = ti

    @property
    def toolTipText(self):
        """Returns the string to show on the tool tip"""
        return self.tr("Points no: %s" % self.name)

    ### Methods ########################################################

    def getFollowingItem(self, precedingItem, direction = -1):
        """Overload of TrackItem.getFollowingItem for PointsItem, including
        the direction
        @param precedingItem The TrackItem we come from
        @param direction The direction of the points
        (0 => normal, positive => reverse, negative => according to
        self._pointsReversed)"""
        if precedingItem == self.commonItem:
            if direction < 0:
                return self.reverseItem if self.pointsReversed \
                       else self.normalItem
            elif direction == 0:
                return self.normalItem
            else:
                return self.reverseItem
        else:
            return self.commonItem

    def setActiveRoute(self, r, previous):
        """Sets the active route information (see TrackItem.setActiveRoute()).
        Here, this function also changes the points direction."""
        if r.direction(self.tiId) == 0:
            self.pointsReversed = False
        else:
            self.pointsReversed = True
        super().setActiveRoute(r, previous)

    ### Graphics methods ###############################################

    def graphicsPaint(self, p, options, itemId, widget = 0):
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
            if self.tiId < 0:
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

