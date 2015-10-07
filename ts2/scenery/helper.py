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

translate = QtCore.QCoreApplication.translate


class TrackGraphicsItem(QtWidgets.QGraphicsItem):
    """Graphical item of a trackItem

    This class is the graphics of a :class:`~ts2.scenery.abstract.TrackItem` on the scene. Each instance
    belongs to a trackItem which is defined in the constructor and which
    is responsible for all actions related to this graphical item."""
    def __init__(self, trackItem, itemId=0):
        """
        :param trackItem: The object to draw for
        :type trackItem: :class:`~ts2.scenery.abstract.TrackItem`
        :param itemId: Id of this item
        :type int:
        """
        super().__init__()
        self.trackItem = trackItem
        self.itemId = itemId
        self.setZValue(0)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

    def boundingRect(self):
        """
        :return: The bounding rectangle of this ``TrackGraphicsItem``.
                 See ``QGraphicsItem::boundingRect()`` for more info.
                 Actually calls the graphicsBoundingRect() function of the owning trackItem
        :rtype: ``QRectF``
        """
        return self.trackItem.graphicsBoundingRect(self.itemId)

    def shape(self):
        """Returns the shape of this item as a QPainterPath in local
        coordinates."""
        shape = super().shape()
        return self.trackItem.graphicsShape(shape, self.itemId)

    def paint(self, painter, option, widget=None):
        """Painting function for the SignalGraphicsItem.
        This function calls the graphicsPaint function of the owning TrackItem
        to paint its painter."""
        self.trackItem.graphicsPaint(painter, option, self.itemId, widget)
        # pen = QtGui.QPen(Qt.red)
        # painter.setPen(pen)
        # painter.drawPath(self.shape())

    def mousePressEvent(self, event):
        """Event handler for mouse pressed.
        This function calls the graphicsMousePressEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsMousePressEvent(event, self.itemId)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Event handler for mouse pressed.
        This function calls the graphicsMousePressEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsMouseMoveEvent(event, self.itemId)

    def dragEnterEvent(self, event):
        """Event handler for when drag enters the item.
        This function calls the graphicsDragEnterEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsDragEnterEvent(event, self.itemId)

    def dragLeaveEvent(self, event):
        """Event handler for when drag leaves the item.
        This function calls the graphicsDragLeaveEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsDragLeaveEvent(event, self.itemId)

    def dropEvent(self, event):
        """Event handler for drop event on this item.
        This function calls the graphicsDropEvent function of the owning
        TrackItem to handle the event"""
        self.trackItem.graphicsDropEvent(event, self.itemId)


class TrackPropertiesModel(QtCore.QAbstractTableModel):
    """This class is a model for accessing TrackItem properties in the editor
    """
    def __init__(self, trackItems):
        """Constructor for the TrackPropertiesModel class"""
        super().__init__()
        self.trackItems = trackItems
        self.simulation = trackItems[0].simulation
        self.multiType = False
        tiType = type(self.trackItems[0])
        for ti in self.trackItems:
            if type(ti) != tiType:
                self.multiType = True
                break

    def rowCount(self, parent=None, *args):
        """Returns the number of rows of the model, corresponding to the
        number of properties."""
        if self.multiType:
            return len(self.trackItems[0].multiProperties)
        else:
            return len(self.trackItems[0].properties)

    def columnCount(self, parent=None, *args):
        """Returns the number of columns of the model, i.e. 2, one for the
        property name, and one for the property value."""
        return 2

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if self.multiType:
                prop = self.trackItems[0].multiProperties[index.row()]
            else:
                prop = self.trackItems[0].properties[index.row()]
            if index.column() == 0:
                return prop.display
            elif index.column() == 1:
                value = getattr(self.trackItems[0], prop.name)
                for ti in self.trackItems:
                    if getattr(ti, prop.name) != value:
                        value = ""
                        break
                if prop.propType == "enum":
                    index = prop.enumValues.index(value)
                    return prop.enumNames[index]
                else:
                    return value
        return None

    def setData(self, index, value, role=Qt.EditRole):
        """Sets the data to the model"""
        if role == Qt.EditRole:
            if index.column() == 1:
                for ti in self.trackItems:
                    if self.multiType:
                        setattr(ti,
                                ti.multiProperties[index.row()].name,
                                value)
                    else:
                        setattr(ti, ti.properties[index.row()].name, value)
                self.dataChanged.emit(index, index)
                return True
        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
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
        if self.multiType:
            prop = self.trackItems[0].multiProperties[index.row()]
        else:
            prop = self.trackItems[0].properties[index.row()]
        if not prop.readOnly and index.column() == 1:
                retFlag |= Qt.ItemIsEditable | Qt.ItemIsSelectable
        return retFlag


class TIProperty:
    """This class holds a TrackItem property that can be edited in the editor
    """
    def __init__(self, name, display, readOnly=False, propType="str",
                 enumNames=None, enumValues=None):
        """Constructor for the TIProperty class"""
        self.name = name
        self.display = display
        self.readOnly = readOnly
        self.propType = propType
        self.enumNames = enumNames
        self.enumValues = enumValues
