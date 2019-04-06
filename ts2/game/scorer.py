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

    def __init__(self, simulation):
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

    @property
    def wrongDestinationPenalty(self):
        """Returns the number of penalty points for leading a train in a wrong
        destination."""
        wdp = self.simulation.option("wrongDestinationPenalty")
        if wdp is not None and wdp != "":
            return int(wdp)
        else:
            return 100

    @property
    def latePenalty(self):
        """Returns the number of penalty points for each minute each train is
        late at each station."""
        lp = self.simulation.option("latePenalty")
        if lp is not None and lp != "":
            return int(lp)
        else:
            return 1

    @property
    def wrongPlatformPenalty(self):
        """Returns the number of penalty points for leading a train onto a
        wrong platform."""
        wpp = self.simulation.option("wrongPlatformPenalty")
        if wpp is not None and wpp != "":
            return int(wpp)
        else:
            return 5

    @QtCore.pyqtSlot(str)
    def trainArrivedAtStation(self, trainId):
        """Updates the score when a train arrives at a station."""
        train = self.simulation.trains[int(trainId)]
        serviceLine = train.currentService.lines[train.nextPlaceIndex]
        place = train.trainHead.trackItem.place
        plannedPlatform = serviceLine.trackCode
        actualPlatform = train.trainHead.trackItem.trackCode
        if actualPlatform != plannedPlatform:
            self.score += self.wrongPlatformPenalty
            self.simulation.messageLogger.addMessage(
                self.tr("Train %s arrived at station %s on platform %s instead"
                        " of %s") % (train.serviceCode, place.placeName,
                                     actualPlatform, plannedPlatform)
            )
        scheduledArrivalTime = serviceLine.scheduledArrivalTime
        currentTime = self.simulation.currentTime
        secondsLate = abs(scheduledArrivalTime.secsTo(currentTime))
        if secondsLate // 60 > 0:
            minutesLateByPlayer = ((secondsLate // 60) -
                                   (train.initialDelay // 60))
            self.score += max(self.latePenalty * minutesLateByPlayer, 0)
            self.simulation.messageLogger.addMessage(
                self.tr("Train %s arrived %i minutes late at station %s "
                        "(%+i minutes)") %
                (train.serviceCode, secondsLate // 60, place.placeName,
                 minutesLateByPlayer)
            )
        else:
            self.simulation.messageLogger.addMessage(
                self.tr("Train %s arrived on time at station %s") %
                (train.serviceCode, place.placeName)
            )

    @QtCore.pyqtSlot(str)
    def trainExitedArea(self, trainId):
        """Updates the score when the train exits the area."""
        train = self.simulation.trains[int(trainId)]
        if train.nextPlaceIndex is not None:
            self.score += self.wrongDestinationPenalty
            self.simulation.messageLogger.addMessage(
                self.tr("Train %s badly routed") % train.serviceCode)
