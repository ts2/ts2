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
from ts2 import utils
from ts2.scenery import abstract, helper

translate = QtWidgets.qApp.translate


class PlacesModel(QtCore.QAbstractTableModel):
    """Model listing places to be used in item delegates."""

    def __init__(self, editor):
        super().__init__()
        self._editor = editor

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._editor.places)

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        placeCodes = list(self._editor.places.keys())
        if role == Qt.DisplayRole:
            return placeCodes[index.row()]


class Place(abstract.TrackItem):
    """A Place is a place where trains will have a schedule (mainly station,
    but can also be a main junction for example)
    """

    def __init__(self, parameters):
        """Constructor for the Place class"""
        self._placeCode = ""
        super().__init__(parameters)
        self.simulation = None
        self._rect = QtCore.QRectF()
        self.updateBoundingRect()
        gi = helper.TrackGraphicsItem(self)
        gi.setPos(self._origin)
        gi.setCursor(Qt.PointingHandCursor)
        gi.setToolTip(self.toolTipText)
        gi.setZValue(self.defaultZValue)
        self._gi[0] = gi
        self._timetable = []
        self._tracks = {}

    def updateFromParameters(self, parameters):
        super(Place, self).updateFromParameters(parameters)
        self._placeCode = parameters.get("placeCode", "")

    @staticmethod
    def getProperties():
        return abstract.TrackItem.getProperties() + [
            helper.TIProperty("placeCode", translate("Place", "Place code"))
        ]

    def for_json(self):
        """Dumps this place item to JSON."""
        jsonData = super().for_json()
        jsonData.update({"placeCode": self.placeCode})
        return jsonData

    # ## Properties ###################################################

    def _setName(self, value):
        """Setter function for the name property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self.graphicsItem.prepareGeometryChange()
            self._name = value
            self.graphicsItem.setToolTip(self.toolTipText)
            self.updateBoundingRect()
            self.updateGraphics()

    name = property(abstract.TrackItem._getName, _setName)

    @property
    def placeName(self):
        return self.name

    @property
    def timetable(self):
        return self._timetable

    @property
    def placeCode(self):
        """Returns the place code of this place"""
        return self._placeCode

    @placeCode.setter
    def placeCode(self, value):
        """Setter function for the placeCode property"""
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            self._placeCode = value

    # ## Methods #######################################################

    def addTrack(self, li):
        self._tracks[li.trackCode] = li

    def addTimetable(self, sl):
        self._timetable.append(sl)
        self._timetable.sort(key=lambda x: x.scheduledDepartureTime)

    def track(self, trackCode):
        return self._tracks[trackCode]

    def updateBoundingRect(self):
        """Updates the bounding rectangle of the graphics item"""
        tl = QtGui.QTextLayout(self._name)
        tl.beginLayout()
        tl.createLine()
        tl.endLayout()
        self._rect = tl.boundingRect()

    @QtCore.pyqtSlot()
    def sortTimetable(self):
        """Sorts the timetable of the place."""
        self._timetable.sort(key=lambda x: x.scheduledDepartureTime)

    # ## Graphics Methods ##############################################

    def graphicsBoundingRect(self, itemId):
        """This function is called by the owned TrackGraphicsItem to return
        its bounding rectangle"""
        if self.name is None or self.name == "":
            return super().boundingRect()
        else:
            if self.tiId.startswith("__EDITOR__"):
                # Toolbox item
                return QtCore.QRectF(-32, -15, 100, 50)
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
        p.drawText(self._rect.bottomLeft(), self.name)


class PlaceInfoModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._place = None

    def rowCount(self, parent=None, *args, **kwargs):
        if self._place is not None:
            return len(self._place.timetable)
        else:
            return 0

    def columnCount(self, parent=None, *args, **kwargs):
        if self._place is not None:
            return 5
        else:
            return 0

    def data(self, index, role=Qt.DisplayRole):
        if self._place is not None and role == Qt.DisplayRole:
            line = self._place.timetable[index.row() - 2]
            if index.column() == 0:
                return line.scheduledDepartureTime
            elif index.column() == 1:
                return line.service.serviceCode
            elif index.column() == 2:
                return line.service.exitPlaceName
            elif index.column() == 3:
                return line.trackCode
            elif index.column() == 4:
                if not line.mustStop:
                    return self.tr("Non-stop")
                else:
                    return ""
        return None

    def headerData(self, column, orientation, role=Qt.DisplayRole):
        if self._place is not None \
                and orientation == Qt.Horizontal \
                and role == Qt.DisplayRole:
            if column == 0:
                return self.tr("Time")
            elif column == 1:
                return self.tr("Code")
            elif column == 2:
                return self.tr("Destination")
            elif column == 3:
                return self.tr("Platform")
            elif column == 4:
                return self.tr("Remarks")
            else:
                return ""
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled

    @property
    def place(self):
        return self._place

    @place.setter
    def place(self, place):
        self.setPlace(place)

    @QtCore.pyqtSlot(Place)
    def setPlace(self, place):
        self.beginResetModel()
        self._place = place
        self.endResetModel()


Place.selectedPlaceModel = PlaceInfoModel()
