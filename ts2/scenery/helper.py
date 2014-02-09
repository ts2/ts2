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

translate = QtCore.QCoreApplication.translate

class TrackGraphicsItem(QtGui.QGraphicsItem):
    """@brief Graphical item of a trackItem
    This class is the graphics of a TrackItem on the scene. Each instance
    belongs to a trackItem which is defined in the constructor and which
    is responsible for all actions related to this graphical item."""
    def __init__(self, trackItem, parent = None):
        """Constructor for the TrackGraphicsItem Class"""
        super().__init__(parent)
        self.trackItem = trackItem
        self.setZValue(0)

    def boundingRect(self):
        """Returns the bounding rectangle of the TrackGraphicsItem.
        See QGraphicsItem::boundingRect() for more info.
        Actually calls the graphicsBoundingRect() function of the owning
        trackItem"""
        return self.trackItem.graphicsBoundingRect()

    def shape(self):
        """Returns the shape of this item as a QPainterPath in local
        coordinates."""
        shape = super().shape()
        return self.trackItem.graphicsShape(shape)

    def paint(self, painter, option, widget = 0):
        """Painting function for the SignalGraphicsItem.
        This function calls the graphicsPaint function of the owning TrackItem
        to paint its painter."""
        #pen = QtGui.QPen(Qt.red)
        #painter.setPen(pen)
        #painter.drawPath(self.shape())
        self.trackItem.graphicsPaint(painter, option, widget)

    def mousePressEvent(self, event):
        """Event handler for mouse pressed.
        This function calls the graphicsMousePressEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsMousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Event handler for mouse pressed.
        This function calls the graphicsMousePressEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsMouseMoveEvent(event)

    def dragEnterEvent(self, event):
        """Event handler for when drag enters the item.
        This function calls the graphicsDragEnterEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsDragEnterEvent(event)

    def dragLeaveEvent(self, event):
        """Event handler for when drag leaves the item.
        This function calls the graphicsDragLeaveEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsDragLeaveEvent(event)

    def dropEvent(self, event):
        """Event handler for drop event on this item.
        This function calls the graphicsDropEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsDropEvent(event)



class TrackPropertiesModel(QtCore.QAbstractTableModel):
    """This class is a model for accessing TrackItem properties in the editor
    """
    def __init__(self, trackItem):
        """Constructor for the TrackPropertiesModel class"""
        super().__init__()
        self._trackItem = trackItem
        self.simulation = trackItem.simulation

    def rowCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of rows of the model, corresponding to the
        number of properties."""
        return len(self._trackItem.properties)

    def columnCount(self, parent = QtCore.QModelIndex()):
        """Returns the number of columns of the model, i.e. 2, one for the
        property name, and one for the property value."""
        return 2

    def data(self, index, role = Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 0:
                return self._trackItem.properties[index.row()].display
            elif index.column() == 1:
                return getattr(self._trackItem,
                               self._trackItem.properties[index.row()].name)
        return None

    def setData(self, index, value, role = Qt.EditRole):
        """Sets the data to the model"""
        if role == Qt.EditRole:
            if index.column() == 1:
                setattr(self._trackItem,
                        self._trackItem.properties[index.row()].name,
                        value)
                self.dataChanged.emit(index, index)
                return True
        return False

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        """Returns the header labels"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return self.tr("Property")
            elif section == 1:
                return self.tr("Value")
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        retFlag = Qt.ItemIsEnabled
        if not self._trackItem.properties[index.row()].readOnly and \
            index.column() == 1:
                retFlag |= Qt.ItemIsEditable | Qt.ItemIsSelectable
        return retFlag


class TIProperty():
    """This class holds a TrackItem property that can be edited by the editor
    """
    def __init__(self, name, display, readOnly = False):
        """Constructor for the TIProperty class"""
        self._name = name
        self._display = display
        self._readOnly = readOnly

    @property
    def name(self):
        """The name of the property. This name must be the name of a python
        property of the TrackItem"""
        return self._name

    @property
    def display(self):
        """The property name to display in the editor"""
        return self._display

    @property
    def readOnly(self):
        """Returns True if the property can not be modified in the editor"""
        return bool(self._readOnly)


