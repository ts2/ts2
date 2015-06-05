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


from ts2.Qt import QtGui, QtCore, Qt
from ts2.scenery import SignalItem
from ts2 import utils

class NonReturnItem(SignalItem):
    """The NonReturnItem is an invisible item used to prevent trains from
    taking a track in an non authorized direction, and making a mess of the
    simulation. It behaves like a signal that is always set to STOP."""

    def __init__(self, simulation, parameters):
        """Constructor for the NonReturnItem class"""
        super().__init__(simulation, parameters)
        self._tiType = "SN"


    def graphicsPaint(self, p, options, widget):
        """ Reimplemented from TrackItem.graphicsPaint to
        draw the non return item on the owned TrackGraphicsItem"""
        # Draw the berth
        linePen = self.getPen()
        textPen = self.getPen()
        textPen.setColor(Qt.white)
        if self.trainPresent():
            linePen.setColor(Qt.red)

        if self.trainId is not None and \
           self.simulation.context == utils.Context.GAME:
            # Train code to draw
            p.setPen(textPen)
            font = QtGui.QFont("Courier new")
            font.setPixelSize(11)
            p.setFont(font)
            textOrigin = QtCore.QPointF(23,6) if self.reverse \
                    else QtCore.QPointF(3,22)
            p.drawText(textOrigin, self.trainServiceCode.rjust(5))
        else:
            # No Train code => Draw Line
            p.setPen(linePen)
            if self.reverse:
                p.drawLine(20, 2, 60, 2)
            else:
                p.drawLine(0, 18, 40, 18)

        # Draw the line at the base of the invisible signal
        p.setPen(linePen)
        if self.reverse:
            p.drawLine(0, 2, 20, 2)
        else:
            p.drawLine(40, 18, 60, 18)


        # Draw the direction if in the editor
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            p.setPen(QtGui.QPen(Qt.cyan))
            p.setBrush(QtGui.QBrush(Qt.cyan))
            if self.reverse:
                triangle = QtGui.QPolygonF()
                triangle << QtCore.QPointF(15, 2) \
                         << QtCore.QPointF(10, 6) \
                         << QtCore.QPointF(10, -2)
                p.drawPolygon(triangle)
            else:
                triangle = QtGui.QPolygonF()
                triangle << QtCore.QPointF(45, 18) \
                         << QtCore.QPointF(50, 22) \
                         << QtCore.QPointF(50, 14)
                p.drawPolygon(triangle)

        # Draw the connection rects
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if self.reverse:
                self.drawConnectionRect(p, QtCore.QPointF(0, 2))
                self.drawConnectionRect(p, QtCore.QPointF(60, 2))
            else:
                self.drawConnectionRect(p, QtCore.QPointF(0, 18))
                self.drawConnectionRect(p, QtCore.QPointF(60, 18))


