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

class PlaceInfoModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._place = None

    def rowCount(self, parent = QtCore.QModelIndex()):
        if self._place is not None:
            return len(self._place.timetable) + 2
        else:
            return 0

    def columnCount (self, parent = QtCore.QModelIndex()):
        if self._place is not None:
            return 5
        else:
            return 0

    def data (self, index, role = Qt.DisplayRole):
        if self._place is not None and role == Qt.DisplayRole:
            if index.row() == 0:
                if index.column() == 0:
                    return self.tr("Station:")
                if index.column() == 1:
                    return self._place.placeName
            elif index.row() == 1:
                return ""
            else:
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
                        return self.tr("non-stop")
                    else:
                        return ""
        return None

    def headerData (self, column, orientation, role = Qt.DisplayRole):
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

    def flags (self, index):
        return Qt.ItemIsEnabled

    @property
    def place(self):
        return self._place

    @place.setter
    def place(self, place):
        self._place = place
        self.reset()

    @QtCore.pyqtSlot(str)
    def setPlace(self, place):
        self.place = place


class Place(TrackItem):
    """A Place is a place where trains will have a schedule (mainly station,
    but can also be a main junction for example)
    """
    def __init__(self, simulation, parameters):
        """Constructor for the Place class"""
        super().__init__(simulation, parameters)
        self._tiType = "A"
        self._placeCode = parameters["placecode"]
        self.updateBoundingRect()
        gi = TrackGraphicsItem(self)
        gi.setPos(self.realOrigin)
        gi.setCursor(Qt.PointingHandCursor)
        gi.setToolTip(self.toolTipText)
        gi.setZValue(0)
        self._gi = gi
        self._simulation.registerGraphicsItem(self._gi)
        self._timetable = []
        self._tracks = {}
        self.updateGraphics()

    selectedPlaceModel = PlaceInfoModel()

    properties = TrackItem.properties + [\
                                    TIProperty("placeCode", tr("Place code"))]

    def getSaveParameters(self):
        """Returns the parameters dictionary to save this TrackItem to the
        database"""
        parameters = super().getSaveParameters()
        parameters.update({"placecode":self.placeCode})
        return parameters

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

    def addTrack(self, li):
        self._tracks[li.trackCode] = li

    def addTimetable(self, sl):
        self._timetable.append(sl)
        #self._timetable.sort(key=lambda x: x.scheduledDepartureTime)

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
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            self._placeCode = value

    @property
    def name(self):
        """Returns the name of the Place"""
        return self._name

    @name.setter
    def name(self, value):
        """Setter function for the name property"""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            self._gi.prepareGeometryChange()
            self._name = value
            self._gi.setToolTip(self.toolTipText)
            self.updateBoundingRect()
            self.updateGraphics()

    def track(self, trackCode):
        return self._tracks[trackCode]

    def updateBoundingRect(self):
        """Updates the bounding rectangle of the graphics item"""
        tl = QtGui.QTextLayout(self._name)
        tl.beginLayout()
        line = tl.createLine()
        tl.endLayout()
        self._rect = tl.boundingRect()

    def graphicsBoundingRect(self):
        """This function is called by the owned TrackGraphicsItem to return
        its bounding rectangle"""
        if self.name is None or self.name == "":
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
        p.drawText(self._rect.bottomLeft(), self.name)

    @QtCore.pyqtSlot()
    def sortTimetable(self):
        """Sorts the timetable of the place."""
        self._timetable.sort(key=lambda x: x.scheduledDepartureTime)

