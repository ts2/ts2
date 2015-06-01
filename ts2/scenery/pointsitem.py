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

from Qt import QtCore, QtGui, Qt

from ts2 import utils
from ts2.scenery import TrackItem, TrackGraphicsItem, TIProperty

class PointsItem(TrackItem):
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
        self._tiType = "P"
        x = parameters["x"]
        y = parameters["y"]
        cpx = parameters["xf"]
        cpy = parameters["yf"]
        npx = parameters["xn"]
        npy = parameters["yn"]
        rpx = parameters["xr"]
        rpy = parameters["yr"]
        self._commonEnd = QtCore.QPointF(cpx, cpy) + self.middle
        self._normalEnd = QtCore.QPointF(npx, npy) + self.middle
        self._reverseEnd = QtCore.QPointF(rpx, rpy) + self.middle
        self._center = QtCore.QPointF(x,y)
        #self._origin =  QtCore.QPointF(cpx, cpy)
        #self._end = QtCore.QPointF(x,y) + QtCore.QPointF(npx, npy)
        self._pointsReversed = False
        self._reverseItem = None
        pgi = TrackGraphicsItem(self)
        pgi.setPos(self.realOrigin)
        pgi.setZValue(100)
        pgi.setCursor(Qt.PointingHandCursor)
        pgi.setToolTip(self.toolTipText)
        self._gi = pgi
        self._simulation.registerGraphicsItem(self._gi)
        self.updateGraphics()

    properties = TrackItem.properties + [\
                            TIProperty("commonEndStr", "Common End"), \
                            TIProperty("normalEndStr", "Normal End"), \
                            TIProperty("reverseEndStr", "Reverse End")]

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
                                "xf":(self._commonEnd - self.middle).x(),
                                "yf":(self._commonEnd - self.middle).y(),
                                "xn":(self._normalEnd - self.middle).x(),
                                "yn":(self._normalEnd - self.middle).y(),
                                "xr":(self._reverseEnd - self.middle).x(),
                                "yr":(self._reverseEnd - self.middle).y(),
                                "rtiid":reverseTiId})
        return parameters

    @property
    def origin(self):
        """Returns the origin QPointF of the PointsItem, which is actually the
        common end in the scene coordinates"""
        return self._center + self._commonEnd - self.middle

    @property
    def end(self):
        """Returns the origin QPointF of the PointsItem, which is actually the
        normal end in the scene coordinates"""
        return self._center + self._normalEnd - self.middle

    @property
    def reverse(self):
        """Returns the reverse QPointF in the scene coordinates"""
        return self._center + self._reverseEnd - self.middle

    @property
    def realOrigin(self):
        """Returns the realOrigin QPointF of the TrackItem. The realOrigin is
        the position of the top left corner of the bounding rectangle of the
        TrackItem. Reimplemented in PointsItem"""
        return self._center - self.middle

    @realOrigin.setter
    def realOrigin(self, pos):
        """Setter function for the realOrigin property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            grid = self.simulation.grid
            x = round((pos.x() + 5.0) / grid) * grid
            y = round((pos.y() + 5.0) / grid) * grid
            self._center = QtCore.QPointF(x, y)
            self._gi.setPos(self.realOrigin)
            self.updateGraphics()

    @property
    def pointsReversed(self):
        """Returns true if the points are reversed, false otherwise"""
        return self._pointsReversed

    @pointsReversed.setter
    def pointsReversed(self, rev):
        """Setter function for the pointsReversed property"""
        self._pointsReversed = True if rev else False

    @property
    def middle(self):
        """Returns the central QPointF of the PointsItem, in the item's
        coordinates"""
        return QtCore.QPointF(5,5)

    @property
    def commonEndStr(self):
        """Returns a string representation of the connecting point situated at
        the common end of this PointsItem, in the items centered coordinates
        """
        cep = self._commonEnd - self.middle
        return "(%i,%i)" % (cep.x(), cep.y())

    @commonEndStr.setter
    def commonEndStr(self, value):
        """Setter for the commonEndStr property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            x, y = eval(value.strip('()'))
            self._gi.prepareGeometryChange()
            self._commonEnd = QtCore.QPointF(x, y) + self.middle
            self.updateGraphics()

    @property
    def normalEndStr(self):
        """Returns a string representation of the connecting point situated at
        the normal end of this PointsItem, in the items centered coordinates
        """
        nep = self._normalEnd - self.middle
        return "(%i,%i)" % (nep.x(), nep.y())

    @normalEndStr.setter
    def normalEndStr(self, value):
        """Setter for the normalEndStr property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            x, y = eval(value.strip('()'))
            self._gi.prepareGeometryChange()
            self._normalEnd = QtCore.QPointF(x, y) + self.middle
            self.updateGraphics()

    @property
    def reverseEndStr(self):
        """Returns a string representation of the connecting point situated at
        the reverse end of this PointsItem, in the items centered coordinates
        """
        rep = self._reverseEnd - self.middle
        return "(%i,%i)" % (rep.x(), rep.y())

    @reverseEndStr.setter
    def reverseEndStr(self, value):
        """Setter for the reverseEndStr property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            x, y = eval(value.strip('()'))
            self._gi.prepareGeometryChange()
            self._reverseEnd = QtCore.QPointF(x, y) + self.middle
            self.updateGraphics()

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

    def graphicsPaint(self, p, options, widget = 0):
        """Draws the points on the painter given as parameter.
        This function is called by PointsGraphicsItem.paint.
        @param p The painter on which to draw the signal."""
        pen = self.getPen()
        if self.trainPresent():
            pen.setColor(Qt.red)
        p.setPen(pen)

        p.drawLine(self._commonEnd, self.middle)
        if self.pointsReversed or \
           self._simulation.context == utils.Context.EDITOR_SCENERY:
            p.drawLine(self._reverseEnd, self.middle)
        if (not self.pointsReversed) or \
             (self._simulation.context == utils.Context.EDITOR_SCENERY):
            p.drawLine(self._normalEnd, self.middle)

        # Draw the connection rects
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.drawConnectionRect(p, self._commonEnd)
            self.drawConnectionRect(p, self._normalEnd)
            self.drawConnectionRect(p, self._reverseEnd)


    def graphicsBoundingRect(self):
        """This function is called by the owned TrackGraphicsItem to return
        its bounding rectangle. Reimplemented from TrackItem"""
        return QtCore.QRectF(0,0,10,10)

    def graphicsMousePressEvent(self, event):
        """This function is called by the owned TrackGraphicsItem to handle
        its mousePressEvent. In the PointsItem class, this function reverses
        the points."""
        super().graphicsMousePressEvent(event)
        if self.simulation.context == utils.Context.EDITOR_ROUTES:
            if self.pointsReversed:
                self.pointsReversed = False
            else:
                self.pointsReversed = True
            self.updateGraphics()

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
            self._pointsReversed = False
        else:
            self._pointsReversed = True
        super().setActiveRoute(r, previous)

