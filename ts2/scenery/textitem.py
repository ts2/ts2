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
from PyQt4.QtCore import Qt
from ts2.scenery import TrackItem, TIProperty, TrackGraphicsItem
from ts2 import utils

tr = QtCore.QObject().tr


class TextItem(TrackItem):
    """A TextItem is a prop to display simple text on the layout
    """
    def __init__(self, simulation, parameters):
        """Constructor for the TextItem class"""
        super().__init__(simulation, parameters)
        self._tiType = "ZT"
        self._name = parameters["name"]
        self.updateBoundingRect()
        gi = TrackGraphicsItem(self)
        gi.setPos(self.realOrigin)
        gi.setToolTip(self.toolTipText)
        gi.setZValue(0)
        if simulation.context in utils.Context.EDITORS:
            gi.setCursor(Qt.PointingHandCursor)
        else:
            gi.setCursor(Qt.ArrowCursor)
        self._gi = gi
        self._simulation.registerGraphicsItem(self._gi)
        self.updateGraphics()

    properties = [TIProperty("tiTypeStr", tr("Type"), True),
                  TIProperty("tiId", tr("id"), True),
                  TIProperty("text", tr("Text")),
                  TIProperty("originStr", tr("Point 1"))]

    @property
    def origin(self):
        """Returns the origin QPointF of the TrackItem. The origin is
        the right end of the track represented on the SignalItem if the
        signal is reversed, the left end otherwise"""
        return self._origin

    @origin.setter
    def origin(self, value):
        """Setter function for the origin property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            self.realOrigin = value - self._rect.bottomLeft()

    @property
    def realOrigin(self):
        """Returns the realOrigin QPointF of the TrackItem. The realOrigin is
        the position of the top left corner of the bounding rectangle of the
        TrackItem. Reimplemented in Place"""
        return self.origin - self._rect.bottomLeft()

    @realOrigin.setter
    def realOrigin(self, pos):
        """Setter function for the realOrigin property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            grid = self.simulation.grid
            x = round((pos.x() + self._rect.bottomLeft().x()) / grid) * grid
            y = round((pos.y() + self._rect.bottomLeft().y()) / grid) * grid
            self._origin = QtCore.QPointF(x, y)
            self._gi.setPos(self.realOrigin)
            self.updateGraphics()

    @property
    def text(self):
        """Returns the text to display"""
        return self._name

    @text.setter
    def text(self, value):
        """Setter function for the text property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            self._gi.prepareGeometryChange()
            self._name = value
            self._gi.setToolTip(self.toolTipText)
            self.updateBoundingRect()
            self.updateGraphics()

    def updateBoundingRect(self):
        """Updates the bounding rectangle of the graphics item"""
        tl = QtGui.QTextLayout(self.text)
        tl.beginLayout()
        line = tl.createLine()
        tl.endLayout()
        self._rect = tl.boundingRect()

    def graphicsBoundingRect(self):
        """This function is called by the owned TrackGraphicsItem to return
        its bounding rectangle"""
        if self.text is None or self.text == "":
            return super().boundingRect()
        else:
            return self._rect

    def graphicsPaint(self, p, options, widget = 0):
        """This function is called by the owned TrackGraphicsItem to paint its
        painter."""
        pen = self.getPen()
        pen.setWidth(0)
        pen.setColor(Qt.white)
        p.setPen(pen)
        p.drawText(self._rect.bottomLeft(), self.text)



