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
from PyQt4.Qt import Qt
from ts2 import utils
from ts2.scenery import placeitem, helper, abstract

translate = QtGui.QApplication.translate

class PlatformItem(abstract.ResizableItem):
    """Platform items are represented as a colored rectangle on the scene to
    symbolise the platform. This colored rectangle permits user interaction.
    """
    def __init__(self, simulation, parameters):
        """Constructor for the PlatformItem class"""
        super().__init__(simulation, parameters)
        self.tiType = "ZP"
        x1 = parameters["x"]
        x2 = parameters["xf"]
        y1 = parameters["y"]
        y2 = parameters["yf"]
        self._end = QtCore.QPointF(x2, y2)
        self._placeCode = parameters["placecode"]
        trackCode = parameters["trackcode"]
        self._place = simulation.place(self._placeCode)
        if self._place is not None:
            self._trackCode = trackCode
            self._place.addTrack(self)
        else:
            self._trackCode = ""
        pgi = helper.TrackGraphicsItem(self)
        pgi.setPos(self.origin)
        pgi.setCursor(Qt.PointingHandCursor)
        pgi.setToolTip(self.toolTipText)
        pgi.setZValue(0)
        self._gi[0] = pgi
        self.simulation.registerGraphicsItem(pgi)
        self.platformSelected.connect(
                                placeitem.Place.selectedPlaceModel.setPlace)


    properties = [helper.TIProperty("tiTypeStr", translate("PlatformItem",
                                                            "Type"), True),
                  helper.TIProperty("tiId", translate("PlatformItem",
                                                       "id"), True),
                  helper.TIProperty("name", translate("PlatformItem",
                                                       "Name")),
                  helper.TIProperty("originStr", translate("PlatformItem",
                                                            "Point 1")),
                  helper.TIProperty("endStr", translate("PlatformItem",
                                                         "Point 2")),
                  helper.TIProperty("placeCode", translate("PlatformItem",
                                                            "Place code")),
                  helper.TIProperty("trackCode", translate("PlatformItem",
                                                            "Track code"))]

    platformSelected = QtCore.pyqtSignal(placeitem.Place)

    def getSaveParameters(self):
        """Returns the parameters dictionary to save this TrackItem to the
        database"""
        parameters = super().getSaveParameters()
        parameters.update({
                            "xf": self.end.x(),
                            "yf": self.end.y(),
                            "placecode": self.placeCode,
                            "trackcode": self.trackCode
                          })
        return parameters

    ### Properties #####################################################

    @property
    def toolTipText(self):
        """Returns the string to show on the tool tip"""
        if self._place is not None:
            return self.tr("%s\nPlatform %s") % \
                                  (self._place.placeName, self.trackCode)
        elif self.tiId < 0:
            return "Platform"
        else:
            return ""

    @property
    def placeCode(self):
        """Returns the place code corresponding to this LineItem."""
        return self._placeCode

    @placeCode.setter
    def placeCode(self, value):
        """Setter function for the placeCode property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            place = self.simulation.place(value)
            if place is not None:
                self._placeCode = value
                self._place = place
                self._place.addTrack(self)
            else:
                self._placeCode = ""

    @property
    def trackCode(self):
        """Returns the track code corresponding to this LineItem. The
        trackCode enables to identify each line in a place (typically a
        station)"""
        return self._trackCode

    @trackCode.setter
    def trackCode(self, value):
        """Setter function for the trackCode property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if self._place is not None:
                self._trackCode = value
            else:
                self._trackCode = ""

    ### Graphics Methods ##############################################

    def graphicsPaint(self, painter, options, itemId, widget):
        """This function is called by the owned TrackGraphicsItem to paint its
        painter. Draws the rectangle."""
        x1 = self.origin.x()
        y1 = self.origin.y()
        x2 = self.end.x()
        y2 = self.end.y()
        painter.setPen(QtGui.QPen(QtGui.QColor("#88ffbb")))
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#88ffbb")))
        painter.drawRect(0, 0, x2 - x1, y2 - y1)
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.drawConnectionRect(painter, QtCore.QPointF(0, 0))
            self.drawConnectionRect(painter, QtCore.QPointF(x2 - x1, y2 - y1))

    def graphicsMousePressEvent(self, e, itemId):
        """Reimplemented from TrackItem.graphicsMousePressEvent to handle the
        mousePressEvent of the owned TrackGraphicsItem.
        It processes mouse clicks on the platform and emits the signal
        platformSelected."""
        super().graphicsMousePressEvent(e, itemId)
        pos = e.buttonDownPos(Qt.LeftButton)
        if e.button() == Qt.LeftButton:
            if self.simulation.context == utils.Context.GAME:
                self.platformSelected.emit(self._place)
        self.updateGraphics()
