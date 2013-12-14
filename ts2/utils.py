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

from PyQt4 import QtCore

TS2_VERSION = "0.4.0"
TS2_FILE_FORMAT = 0.4

def recordToDict(record):
    """This helper function returns a dictionary from a QSqlRecord"""
    retDict = {}
    for i in range(record.count()):
        if not isinstance(record.value(i), QtCore.QPyNullVariant):
            retDict[record.fieldName(i)] = record.value(i)
        else:
            retDict[record.fieldName(i)] = None
    return retDict


class Context():
    """This class holds the different contexts for ts2."""
    GAME = 10
    EDITORS = [20, 21, 22, 23, 24, 25]
    EDITOR_GENERAL = 20
    EDITOR_SCENERY = 21
    EDITOR_ROUTES = 22
    EDITOR_TRAINTYPES = 23
    EDITOR_SERVICES = 24
    EDITOR_TRAINS = 25


class FormatException(Exception):
    """Exception class for file format exception."""
    def __init__(self, arg):
        """Constructor of the Exception class."""
        super().__init__(arg)
