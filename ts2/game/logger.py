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

from Qt import QtCore, QtGui, Qt


class Message(QtCore.QObject):
    """A Message instance holds all the data regarding one message emitted to
    the Message Logger of the simulation."""

    SOFTWARE_MSG = 0
    PLAYER_WARNING_MSG = 1
    SIMULATION_MSG = 2

    def __init__(self, parent, msgText, msgType=SIMULATION_MSG):
        """Constructor for the Message class."""
        super().__init__(parent)
        self.msgType = msgType
        self.msgText = msgText

    def __str__(self):
        """Returns the string representation of the message."""
        return self.msgText


class MessageLogger(QtCore.QAbstractTableModel):
    """A MessageLogger holds all messages that has been emitted to it and
    format them so that it can be used directly as a model for views."""

    def __init__(self, simulation):
        """Constructor for the MessageLogger class."""
        super().__init__(simulation)
        self.simulation = simulation
        self._messages = [Message(self, " ")]

    def addMessage(self, msgText, msgType=Message.SIMULATION_MSG):
        """Adds a message to the logger."""
        row = len(self._messages) - 1
        if msgType == Message.SIMULATION_MSG:
            msgText = \
                self.simulation.currentTime.toString("HH:mm - ") + msgText
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self._messages.insert(row, Message(self, msgText, msgType))
        self.endInsertRows()

    def rowCount(self, parent=None, *args, **kwargs):
        """Returns the number of rows of the model, corresponding to the
        number of messages in the logger."""
        return len(self._messages)

    def columnCount(self, parent=None, *args, **kwargs):
        """Returns the number of columns of the model"""
        return 1

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole:
            return str(self._messages[index.row()])
        elif role == Qt.FontRole:
            return QtGui.QFont("Courier new")
        elif role == Qt.BackgroundRole:
            return QtGui.QBrush(Qt.black)
        elif role == Qt.ForegroundRole:
            msgType = self._messages[index.row()].msgType
            if msgType == Message.SOFTWARE_MSG:
                return QtGui.QBrush(Qt.magenta)
            elif msgType == Message.PLAYER_WARNING_MSG:
                return QtGui.QBrush(Qt.cyan)
            elif msgType == Message.SIMULATION_MSG:
                return QtGui.QBrush(Qt.yellow)

    def headerData(self, column, orientation, role=Qt.DisplayRole):
        """Returns the column headers to display"""
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        return Qt.ItemIsEnabled
