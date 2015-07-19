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

from Qt import QtGui, QtCore, QtWidgets, Qt

from ts2 import utils


class PositionGraphicsItem(QtWidgets.QGraphicsPolygonItem):
    """This class is a graphics representation of a position to be put on a
    scene.
    """
    def __init__(self, simulation, position=None, parent=None):
        """Constructor for the PositionGraphicsItem class"""
        super().__init__(parent)
        self.simulation = simulation
        self._position = position
        self._leftToRightPolygon = QtGui.QPolygonF()
        self._leftToRightPolygon << QtCore.QPointF(-5, -5) \
                                 << QtCore.QPointF(0, 0) \
                                 << QtCore.QPointF(-5, 5) \
                                 << QtCore.QPointF(-5, -5)
        self._rightToLeftPolygon = QtGui.QPolygonF()
        self._rightToLeftPolygon << QtCore.QPointF(5, -5) \
                                 << QtCore.QPointF(0, 0) \
                                 << QtCore.QPointF(5, 5) \
                                 << QtCore.QPointF(5, -5)
        self._currentPolygon = self._leftToRightPolygon
        self.setPen(QtGui.QPen(Qt.yellow))
        self.setBrush(QtGui.QBrush(Qt.yellow))
        self.setZValue(100)
        self.updatePosition()

    @property
    def position(self):
        """Returns the position this PositionGraphicsItem represents"""
        return self._position

    @position.setter
    def position(self, value):
        """Setter function for the position property"""
        self._position = value
        self.updatePosition()

    def updatePosition(self):
        """Updates the position of this PositionGraphicsItem according to its
        Position."""
        if self._position is not None and \
           self.simulation.context == utils.Context.EDITOR_TRAINS:
            trackItem = self._position.trackItem
            if not trackItem.tiType.startswith("L"):
                raise Exception("Error: PositionGraphicsItem can be used only"
                                "for positions on LineItem and subclasses")
            pos1 = trackItem.sceneLine.pointAt(
                self._position.positionOnTI /
                self._position.trackItem.realLength
            )
            pos2 = trackItem.sceneLine.pointAt(
                1 - (self._position.positionOnTI /
                     self._position.trackItem.realLength)
            )
            if trackItem.sceneLine.dx() > 0:
                # line is from left to right
                if trackItem.previousItem == self._position.previousTI:
                    # previousTI is on the left
                    self._currentPolygon = self._leftToRightPolygon
                    pos = pos1
                else:
                    # previousTI is on the right
                    self._currentPolygon = self._rightToLeftPolygon
                    pos = pos2
            else:
                # line is from right to left
                if trackItem.previousItem == self._position.previousTI:
                    # previousTI is on the right
                    self._currentPolygon = self._rightToLeftPolygon
                    pos = pos2
                else:
                    # previousTI is on the left
                    self._currentPolygon = self._leftToRightPolygon
                    pos = pos1
            self.setPos(pos)
            self.setPolygon(self._currentPolygon)
            self.update()
            self.show()
        else:
            self.hide()


class Position:
    """A Position object is a point on a TrackItem.

    A Position is defined as being positionOnTI meters away from the end of
    the TrackItem that is connected to TrackItem previousTI. Note that a
    Position has a direction, so that for any point on a TrackItem, there are
    two Positions that can be defined: one starting from one end of the
    TrackItem, the other starting from the other end. You can get the
    other Position by calling reversed()."""

    def __init__(self, trackItem=None, previousTI=None, positionOnTI=0.0):
        """Constructor for the Position class"""
        self._trackItem = trackItem
        self._previousTI = previousTI
        self._positionOnTI = positionOnTI

    def for_json(self):
        """Dumps the position to JSON."""
        return {
            "__type__": "Position",
            "trackItem": self.trackItem.tiId,
            "previousTI": self.previousTI.tiId,
            "positionOnTI": self.positionOnTI
        }

    @property
    def trackItem(self):
        """The TrackItem on which this Position is"""
        return self._trackItem

    @property
    def previousTI(self):
        """The TrackItem connected to this one from which to measure the
        distance of the Position"""
        return self._previousTI

    @property
    def positionOnTI(self):
        """Distance of the Position from the end of the TrackItem connected to
        previousTI"""
        return float(self._positionOnTI)

    def next(self, pos=0, direction=-1):
        """Returns a Position on the next TrackItem.

        Returns a Position on the next TrackItem (i.e. the TrackItem
        connected to this one which is not previousTI) at pos meters from
        the connection of the next TrackItem to this one. By default,
        pos is 0."""
        return Position(self._trackItem.getFollowingItem(self._previousTI,
                                                         direction),
                        self._trackItem,
                        pos)

    def previous(self, pos=None):
        """Returns a Position on the previous TrackItem.

        Returns a Position on the previous TrackItem (i.e. previousTI),
        running backwards, at pos meters from the end behind (i.e. the end
        not connected to this TrackItem). By default, pos is equal to the
        length of the previous Item, so that the position is on the
        connection point with this TrackItem."""
        if pos is None:
            pos = self._previousTI.realLength
        return Position(self._previousTI,
                        self._previousTI.getFollowingItem(self._trackItem),
                        pos)

    def distanceToPosition(self, p):
        """Returns the distance between the current position and p if p is
        ahead of current position. Returns 0 otherwise."""
        if self.trackItem != p.trackItem:
            res = self.trackItem.realLength - self.positionOnTI
            cur = self.next()
            while cur.trackItem != p.trackItem:
                if cur.trackItem is None:
                    return -1
                res += cur.trackItem.realLength
                cur = cur.next()
            res += p.positionOnTI
        else:
            res = p.positionOnTI - self.positionOnTI
        return max(res, 0)

    def trackItemsToPosition(self, p):
        """Returns a list of all the trackItems between this position and
        position p including the trackItem of this position and the trackItem
        of position p."""
        til = []
        cur = self
        while cur.trackItem != p.trackItem and not cur.isOut():
            til.append(cur.trackItem)
            cur = cur.next()
        til.append(p.trackItem)
        return til

    def isOut(self):
        """Returns True if this position is out of the scenery, i.e. on an
        EndItem."""
        if self.trackItem.tiType.startswith("E"):
            return True
        else:
            return False

    def isValid(self):
        """Returns True if this Position is valid."""
        if self.isNull():
            # A null position is valid
            return True
        if self.trackItem is None:
            return False
        if self.positionOnTI > self.trackItem.realLength or \
           self.positionOnTI < 0:
            return False
        if self.trackItem.nextItem != self.previousTI and \
           self.trackItem.previousItem != self.previousTI:
            if self.trackItem.tiType.startswith("P") and \
               self.trackItem.reverseItem == self.previousTI:
                return True
            if self.trackItem.tiType.startswith("E") and \
               self.previousTI is None:
                return True
            return False
        return True

    def isNull(self):
        """Returns True if this Position is Null."""
        return (self.trackItem is None and
                self.previousTI is None and
                self.positionOnTI == 0)

    def reversed(self):
        """Returns a position that is physically on the exact same place, but
        coming from the opposite direction"""
        positionOnTI = self._trackItem.realLength - self._positionOnTI
        previousTI = self._trackItem.getFollowingItem(self._previousTI)
        return Position(self._trackItem, previousTI, positionOnTI)

    def __eq__(self, p):
        """Returns True if p is the same Position as this one."""
        return (self._trackItem == p.trackItem
                and self._previousTI == p.previousTI
                and self._positionOnTI == p.positionOnTI)

    def __ne__(self, p):
        """Returns True if p is not the same Position as this one."""
        return not (self == p)

    def __add__(self, length):
        """Returns the position that is length meters ahead of this
        position.
        :rtype : Position
        :param length: length in meters to add to this position
        :return: The new position
        """
        if self._positionOnTI + length < self._trackItem.realLength:
            return Position(self._trackItem,
                            self._previousTI,
                            self._positionOnTI + length)
        else:
            return self.next() + (length +
                                  self._positionOnTI -
                                  self._trackItem.realLength)

    def __sub__(self, length):
        """Returns the position that is length meters behind this
        Position.
        :rtype : Position
        :param length: length in meters to add to this position
        :return: The new position
        """
        if self._positionOnTI - length > 0:
            return Position(self._trackItem,
                            self._previousTI,
                            self._positionOnTI - length)
        else:
            return (self.previous(self._previousTI.realLength) -
                    (length - self._positionOnTI))

    def __iadd__(self, length):
        """Implements Position += length operator.
        :rtype : Position
        """
        self = self + length
        return self

    def __isub__(self, length):
        """Implements Position -= length operator.
        :rtype : Position
        """
        self = self - length
        return self

    def __str__(self):
        """Returns the string representation of the position, which is
        "(trackItem.tiId, previousTI.tiId, positionOnTI)"."""
        if self.trackItem is None and \
           self.previousTI is None and \
           self.positionOnTI == 0:
            return "<Null position>"
        return "(%i, %i, %f)" % (self.trackItem.tiId,
                                 self.previousTI.tiId,
                                 self.positionOnTI)
