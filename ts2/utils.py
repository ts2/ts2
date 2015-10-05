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

import random
import os.path

from Qt import QtCore
import simplejson

import ts2.xobjects.xsettings


settings = ts2.xobjects.xsettings.XSettings()
"""Settings instance"""


class Context:
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


def cumsum(lis):
    """Returns a list with the cumulated sum of lis."""
    summ = 0
    for x in lis:
        summ += x
        yield summ

"""
def _getUserDataDirectory():

    homeDir = os.path.expanduser("~")
    if os.path.commonprefix((homeDir, os.getcwd())):
        return os.getcwd()
    else:
        os.makedirs(os.path.join(homeDir, ".ts2", "data"), exist_ok=True)
        os.makedirs(os.path.join(homeDir, ".ts2", "simulations"), exist_ok=True)
        return os.path.join(homeDir, ".ts2")


simulationsDirectory = os.path.join(_getUserDataDirectory(), "simulations")
userDataDirectory = os.path.join(_getUserDataDirectory(), "data")
"""

class DurationProba(QtCore.QObject):
    """A DurationProba is a probability distribution for a duration in
    seconds."""

    def __init__(self, data):
        """Constructor for the DurationProba class."""
        super().__init__()
        self._probaList = None
        if isinstance(data, str):
            try:
                self._probaList = eval(data)
            except:
                pass
        else:
            self._probaList = data

    def __str__(self):
        """Returns the string representation of the DurationProba."""
        return str(self._probaList)

    def isNull(self):
        """Returns true if the DurationProba instance has no data."""
        return self._probaList is None

    def yieldValue(self):
        """Returns a random value in the bounds and probabilities given by
        this DurationProba instance."""
        try:
            probas = list(cumsum([t[2] for t in self._probaList]))
            probas.insert(0, 0)
        except TypeError:
            return self._probaList
        except Exception as err:
            QtCore.qDebug(str(err))
            return None
        r0 = 100 * random.random()
        seg = 0
        for i in range(len(probas) - 1):
            if probas[i] < r0 < probas[i+1]:
                break
            seg += 1
        else:
            # Out of range: returns max value
            return self._probaList[-1][1]
        r1 = random.random()
        low, high, prob = self._probaList[seg]
        return r1 * (high - low) + low

##==============================================
def to_json(data):
    """Serialize data to a json string

    .. important:: Its advised to use this function as its is indented and sorted and therefore
                   a consistent output. This is for git and versioning reasons, ie less deltas.
    """
    return simplejson.dumps(data, indent=4, sort_keys=True)

def from_json(json_str):
    """Load data from a json string"""
    return simplejson.loads(json_str)
