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

from Qt import QtCore


class Scorer(QtCore.QObject):
    """A scorer calculates the score of the player during the simulation."""

    def __init__(self, simulation,):
        """Constructor class for the Scorer class."""
        super().__init__(simulation)
        self.simulation = simulation
        self._score = 0

    scoreChanged = QtCore.pyqtSignal(int)

    @property
    def score(self):
        """Returns the current score."""
        return self._score

    @score.setter
    def score(self, value):
        """Setter function for the score property."""
        oldScore = self._score
        self._score = int(value)
        if self._score != oldScore:
            self.scoreChanged.emit(value)
