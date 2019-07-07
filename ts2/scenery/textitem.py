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

from Qt import QtGui, QtCore, QtWidgets, Qt

from ts2.scenery import abstract, helper
from ts2 import utils

translate = QtWidgets.qApp.translate


class TextItem(abstract.TrackItem):
    """A TextItem is a prop to display simple text on the layout
    """
    def __init__(self, parameters):
        """Constructor for the TextItem class"""
        super().__init__(parameters)
        self._rect = QtCore.QRectF()
        self.updateBoundingRect()
        gi = helper.TrackGraphicsItem(self)
        gi.setPos(self.origin)
        gi.setToolTip(self.toolTipText)
        gi.setZValue(0)
        self._gi[0] = gi

    def initialize(self, simulation):
        """Initialize the item after all items are loaded."""
        if simulation.context in utils.Context.EDITORS:
            self._gi[0].setCursor(Qt.PointingHandCursor)
        else:
            self._gi[0].setCursor(Qt.ArrowCursor)
        super().initialize(simulation)

    @staticmethod
    def getProperties():
        return [
            helper.TIProperty("tiTypeStr", translate("TextItem", "Type"), True),
            helper.TIProperty("tiId", translate("TextItem", "id"), True),
            helper.TIProperty("text", translate("TextItem", "Text")),
            helper.TIProperty("originStr", translate("TextItem", "Point 1"))
        ]

    @property
    def text(self):
        """Returns the text to display"""
        return self._name

    @text.setter
    def text(self, value):
        """Setter function for the text property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.graphicsItem.prepareGeometryChange()
            self._name = value
            self.graphicsItem.setToolTip(self.toolTipText)
            self.updateBoundingRect()
            self.updateGraphics()

    def updateBoundingRect(self):
        """Updates the bounding rectangle of the graphics item"""
        tl = QtGui.QTextLayout(self.text)
        tl.beginLayout()
        tl.createLine()
        tl.endLayout()
        self._rect = tl.boundingRect()

    def graphicsBoundingRect(self, itemId):
        """This function is called by the owned TrackGraphicsItem to return
        its bounding rectangle"""
        if self.text is None or self.text == "":
            return super().boundingRect()
        else:
            if self.tiId.startswith("__EDITOR__"):
                # Toolbox item
                return QtCore.QRectF(-36, -15, 100, 50)
            else:
                return self._rect

    def graphicsPaint(self, p, options, itemId, widget=None):
        """This function is called by the owned TrackGraphicsItem to paint its
        painter."""
        super().graphicsPaint(p, options, itemId, widget)
        pen = self.getPen()
        pen.setWidth(0)
        pen.setColor(Qt.white)
        p.setPen(pen)
        p.drawText(self._rect.bottomLeft(), self.text)
