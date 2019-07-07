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
        import ts2.scenery.lineitem
        if self._position is not None and \
           self.simulation.context == utils.Context.EDITOR_TRAINS:
            trackItem = self._position.trackItem
            if not isinstance(trackItem, ts2.scenery.lineitem.LineItem):
                raise Exception("Error: PositionGraphicsItem can be used only"
                                " for positions on LineItem and subclasses")
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
    """A ``Position`` object is a point on a :class:`~ts2.scenery.abstract.TrackItem`.

    A ``Position`` is defined as being :func:`~ts2.routing.position.Position.positionOnTI` meters away from the end of
    the ``TrackItem`` that is connected to ``TrackItem`` :func:`~ts2.routing.position.Position.previousTI`. Note that a
    Position has a direction, so that for any point on a TrackItem, there are
    two Positions that can be defined:

      - one starting from one end of the :class:`~ts2.scenery.abstract.TrackItem`
      - the other starting from the other end.

      You can get the other Position by calling :func:`~ts2.routing.position.Position.reversed`."""

    def __init__(self, trackItem=None, previousTI=None, positionOnTI=0.0,
                 parameters=None):
        """
        :param trackItem:
        :param previousTI:
        :param positionOnTI:
        :param parameters:
        """
        if parameters:
            self._parameters = parameters
            self._trackItem = None
            self._previousTI = None
            self._positionOnTI = 0.0
        else:
            self._parameters = None
            self._trackItem = trackItem
            self._previousTI = previousTI
            self._positionOnTI = positionOnTI

    def initialize(self, simulation):
        """Initialize position defined by parameters."""
        if not self._parameters:
            return
        params = self._parameters
        self._trackItem = simulation.trackItem(params['trackItem'])
        self._previousTI = simulation.trackItem(params['previousTI'])
        self._positionOnTI = params['positionOnTI']

    def for_json(self):
        """Dumps the position to JSON.

        :return: `dict` """
        return {
            "__type__": "Position",
            "trackItem": self.trackItem.tiId,
            "previousTI": self.previousTI.tiId,
            "positionOnTI": self.positionOnTI
        }

    @property
    def trackItem(self):
        """
        :return: :class:`~ts2.scenery.abstract.TrackItem` on which this ``Position`` is"""
        return self._trackItem

    @property
    def previousTI(self):
        """
        :return:  :class:`~ts2.scenery.abstract.TrackItem`  connected to this one from which to measure the
                  distance of the ``Position`` """
        return self._previousTI

    @property
    def positionOnTI(self):
        """
        :return: `float` with distance of the :class:`~ts2.routing.position.Position` from the
                end of the :class:`~ts2.scenery.abstract.TrackItem` connected
                to   :class:`~ts2.routing.position.Position.previousTI`"""
        return float(self._positionOnTI)

    def next(self, pos=0, direction=-1):
        """
        :param pos: metre position
        :param int direction:
        :return: A Position on the next :class:`~ts2.scenery.abstract.TrackItem` (i.e. the TrackItem
                 connected to this one which is not previousTI) at pos meters from
                 the connection of the next TrackItem to this one. By default,
                 pos is 0.
        :rtype: :class:`~ts2.routing.position.Position`
        """
        return Position(self._trackItem.getFollowingItem(self._previousTI,
                                                         direction),
                        self._trackItem,
                        pos)

    def previous(self, pos=None):
        """
        :param pos: metre position
        :param int direction:
        :return: a Position on the previous :class:`~ts2.scenery.abstract.TrackItem`  (i.e. previousTI),
                 running backwards, at pos meters from the end behind (i.e. the end
                 not connected to this TrackItem). By default, pos is equal to the
                 length of the previous Item, so that the position is on the
                 connection point with this TrackItem.
        :rtype: :class:`~ts2.routing.position.Position`
        """
        # try:
        if pos is None:
            pos = self._previousTI.realLength
        res = Position(self._previousTI,
                       self._previousTI.getFollowingItem(self._trackItem),
                       pos)
        # except AttributeError:
        #     res = Position()
        return res

    def distanceToPosition(self, p):
        """
        :param p:
        :type p: :class:`~ts2.routing.position.Position`
        :return: The distance between the current position and p. if p is
                 ahead of current position, otherwise zero
        :rtype: float
        """
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
        """
        :param p:
        :type p: :class:`~ts2.routing.position.Position`
        :return: a list of all the trackItems between this position and
                 position p including the trackItem of this position and the trackItem
                 of position p.
        :rtype: a ``list`` of :class:`~ts2.scenery.abstract.TrackItem`'s
        """
        til = []
        cur = self
        while cur.trackItem != p.trackItem and not cur.isOut():
            til.append(cur.trackItem)
            cur = cur.next()
        til.append(p.trackItem)
        return til

    def isOut(self):
        """
        :return: ``True`` if this position is out of the scenery, going outwards
                   i.e. on an :class:`~ts2.scenery.enditem.EndItem`  with a previous item that is not None.
        :rtype: bool
        """
        import ts2.scenery.enditem
        if isinstance(self.trackItem, ts2.scenery.enditem.EndItem) and \
                self.previousTI is not None:
            return True
        else:
            return False

    def isValid(self):
        """
        :return: ``True`` if this Position is valid.
        :rtype: bool
        """
        ## TODO This import here needs to go (pedro)
        import ts2.scenery.enditem
        import ts2.scenery.pointsitem
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
            if isinstance(self.trackItem, ts2.scenery.pointsitem.PointsItem) \
                    and self.trackItem.reverseItem == self.previousTI:
                return True
            if isinstance(self.trackItem, ts2.scenery.enditem.EndItem) and \
               self.previousTI is None:
                return True
            return False
        return True

    def isNull(self):
        """
        :return: ``True`` if this Position is Null.
        :rtype: bool
        """
        return (self.trackItem is None and
                self.previousTI is None and
                self.positionOnTI == 0)

    def reversed(self):
        """
        :return: a position that is physically on the exact same place, but
                 coming from the opposite direction
        :rtype: :class:`~ts2.routing.position.Position`
        """
        positionOnTI = self._trackItem.realLength - self._positionOnTI
        previousTI = self._trackItem.getFollowingItem(self._previousTI)
        return Position(self._trackItem, previousTI, positionOnTI)

    def __eq__(self, p):
        """
        :param p:
        :type p: :class:`~ts2.routing.position.Position`
        :return: `True` if p is the same Position as this one.
        :rtype: bool
        """
        return (self._trackItem == p.trackItem and
                self._previousTI == p.previousTI and
                self._positionOnTI == p.positionOnTI)

    def __ne__(self, p):
        """
        :param p:
        :type p: :class:`~ts2.routing.position.Position`
        :return: `True` if p is not the same Position as this one..
        :rtype: bool
        """
        return not (self == p)

    def __add__(self, length):
        """
        :param float length:  meters to add to this position
        :return: the position that is length meters ahead of this position.
        :rtype: :class:`~ts2.routing.position.Position`
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
        """Returns the position that is length meters behind this Position.

        :param float length: length in meters to add to this position
        :return: The new position
        :rtype: :class:`~ts2.routing.position.Position`
        """
        if self._positionOnTI - length > 0:
            return Position(self._trackItem,
                            self._previousTI,
                            self._positionOnTI - length)
        else:
            return (self.previous(self._previousTI.realLength) -
                    (length - self._positionOnTI))

    # noinspection PyMethodFirstArgAssignment
    def __iadd__(self, length):
        """Implements Position += length operator.

        :return: new position
        :rtype: :class:`~ts2.routing.position.Position`
        """
        self = self + length
        return self

    # noinspection PyMethodFirstArgAssignment
    def __isub__(self, length):
        """Implements Position -= length operator.

        :return: new position
        :rtype: :class:`~ts2.routing.position.Position`
        """
        self = self - length
        return self

    def __str__(self):
        """
        :return: a string representation of the position, which is
                 ``(trackItem.tiId, previousTI.tiId, positionOnTI)``
        :rtype: str
        """

        if self.trackItem is None and \
           self.previousTI is None and \
           self.positionOnTI == 0:
            return "<Null position>"
        if self.isValid():
            return "(%s, %s, %f)" % (self.trackItem.tiId,
                                     self.previousTI.tiId,
                                     self.positionOnTI)
        return "<Invalid position: %s, %s, %s>" % (self.trackItem,
                                                   self.previousTI,
                                                   self.positionOnTI)
