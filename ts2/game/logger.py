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
from ts2 import utils


class Message(QtCore.QObject):
    """A Message instance holds all the data regarding one message emitted to
    the Message Logger of the simulation."""

    SOFTWARE_MSG = 0
    PLAYER_WARNING_MSG = 1
    SIMULATION_MSG = 2

    def __init__(self, parameters):
        """Constructor for the Message class.
        :param parameters: dictionary to build the message. Should have a
        'msgType' and a 'msgText' keys.
        :type parameters: dict
        """
        super().__init__()
        self.msgType = parameters['msgType']
        self.msgText = parameters['msgText']

    def __str__(self):
        """Returns the string representation of the message."""
        return self.msgText

    def for_json(self):
        """Dumps this message to JSON."""
        return {
            "__type__": "Message",
            "msgType": self.msgType,
            "msgText": self.msgText
        }


class MessageLogger(QtCore.QAbstractTableModel):
    """A MessageLogger holds all messages that has been emitted to it and
    format them so that it can be used directly as a model for views."""

    def __init__(self, parameters):
        """Constructor for the MessageLogger class."""
        super().__init__()
        self._messages = parameters.get('messages', []) + [Message(
            {'msgType': Message.SIMULATION_MSG, 'msgText': " "}
        )]
        self.simulation = None

    def initialize(self, simulation):
        """Initializes the message logger once everything is loaded."""
        self.simulation = simulation

    def for_json(self):
        """Dumps the messages to JSON."""
        messages = []
        if self.simulation.context == utils.Context.GAME:
            messages = self._messages
        return {
            "__type__": "MessageLogger",
            "messages": messages
        }

    def addMessage(self, msgText, msgType=Message.SIMULATION_MSG):
        """Adds a message to the logger."""
        row = len(self._messages) - 1
        if msgType == Message.SIMULATION_MSG:
            msgText = \
                self.simulation.currentTime.toString("HH:mm - ") + msgText
        msgData = {
            'msgType': msgType,
            'msgText': msgText
        }
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self._messages.insert(row, Message(msgData))
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
