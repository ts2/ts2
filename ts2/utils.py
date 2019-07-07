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

from Qt import QtCore
import simplejson

import ts2.xobjects.xsettings
settings = ts2.xobjects.xsettings.XSettings()
"""Settings instance"""


class Context:
    """Different context's"""
    GAME = 10
    """Game"""

    EDITORS = [20, 21, 22, 23, 24, 25]
    """Editor Modes list """

    EDITOR_GENERAL = 20
    """Editor General"""

    EDITOR_SCENERY = 21
    """Editor Scenery"""

    EDITOR_ROUTES = 22
    """Editor Routes"""

    EDITOR_TRAINTYPES = 23
    """Editor TrainTypes"""

    EDITOR_SERVICES = 24
    """Editor Services"""

    EDITOR_TRAINS = 25
    """Editor Trains"""


class FormatException(Exception):
    """File format exception."""
    def __init__(self, arg):
        """Constructor of the FormatException class."""
        super().__init__(arg)


class MissingDependencyException(Exception):
    """Exception raised when a dependency is missing (e.g. TSL file)."""
    def __init__(self, arg):
        """Constructor of the MissingDependencyException class."""
        super().__init__(arg)


def cumsum(lis):
    """Cumulated sum of a list

    :param: the list to cumulatively sum.
    :return: an iterator with each item being the cumulated sum of all the
             items of the original list up to this index.
    """
    summ = 0
    for x in lis:
        summ += x
        yield summ


class DurationProba(QtCore.QObject):
    """A DurationProba is a probability distribution for a duration in
    seconds. This class is used to have random delays of trains."""

    def __init__(self, data):
        """Constructor for the DurationProba class.

        :param data: A list of tuples (or its string representation). Each
                     tuple defines in order:
                     - A lower bound
                     - An upper bound
                     - A probability (in percent) of the value to be inside
                     the defined bounds.
                     e.g. [(0, 100, 80),(100, 500, 20)] means that when a value
                     will be yielded by `yieldValue` it will have 80% chance of
                     being between 0 and 100, and 20% chance of being between
                     100 and 500.

                     If a number N is given instead of a list of tuples then
                     this number will always be yielded
        """
        super().__init__()
        self._probaList = None
        if isinstance(data, str):
            try:
                self._probaList = eval(data)
            except SyntaxError:
                pass
        else:
            self._probaList = data

    def __str__(self):
        """
        :return: The string representation of the DurationProba.
        :rtype str:
        """
        return str(self._probaList)

    def list(self):
        """Returns the DurationProba list"""
        return self._probaList

    def isNull(self):
        """
        :return: True if the DurationProba instance has no data.
        :rtype bool:
        """
        return self._probaList is None

    def yieldValue(self):
        """Returns a random value in the bounds and probabilities given by
        this DurationProba instance.

        This is done in two steps:
        - First we take a random number to determine the segment (tuple) in
          which we should be according to our _probaList.
        - Then we take a second random number to get our value inside the
          selected segment (with even probability).
        """
        try:
            probas = list(cumsum([t[2] for t in self._probaList]))
            probas.insert(0, 0)
        except TypeError:
            # We have a value instead of a list
            return self._probaList
        except Exception as err:
            QtCore.qDebug(str(err))
            return None

        # First determine our segment
        r0 = 100 * random.random()
        seg = 0
        for i in range(len(probas) - 1):
            if probas[i] < r0 < probas[i+1]:
                break
            seg += 1
        else:
            # Out of range: returns max value
            return self._probaList[-1][1]

        # Then pick up a number inside our segment
        r1 = random.random()
        low, high, prob = self._probaList[seg]
        return r1 * (high - low) + low


def to_json(data):
    """Serialize data to a json string

    .. important:: Its advised to use this function as its is indented and
                   sorted and therefore a consistent output. This is for git and
                   versioning reasons, ie less deltas.
    """
    return simplejson.dumps(data, indent=4, sort_keys=True)


def from_json(json_str):
    """Load data from a json string"""
    return simplejson.loads(json_str)
