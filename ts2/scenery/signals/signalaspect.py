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


class SignalShape:
    """This class holds the possible representation shapes for signal lights.
    """
    NONE = 0
    CIRCLE = 1
    SQUARE = 2
    QUARTER_SW = 10
    QUARTER_NW = 11
    QUARTER_NE = 12
    QUARTER_SE = 13
    BAR_N_S = 20
    BAR_E_W = 21
    BAR_SW_NE = 22
    BAR_NW_SE = 23
    POLE_NS = 31
    POLE_NSW = 32
    POLE_SW = 33
    POLE_NE = 34
    POLE_NSE = 35


class SignalLineStyle:
    """This class holds the possible representation shapes for the line at
    the base of the signal.
    """
    LINE = 0
    BUFFER = 1


class Target:
    """This class defines when a speed limit associated with a signal aspect
    must be applied."""
    ASAP = 0
    BEFORE_THIS_SIGNAL = 1
    BEFORE_NEXT_SIGNAL = 2


class SignalAspect:
    """SignalAspect class represents an aspect of a signal, that is a
    combination of on and off lights with a meaning for the train driver."""

    def __init__(self, parameters):
        """Constructor for the SignalAspect class."""
        self.name = parameters["name"]
        self.lineStyle = parameters["lineStyle"]
        self.outerShapes = parameters["outerShapes"]
        self.outerColors = parameters["outerColors"]
        self.shapes = parameters["shapes"]
        self.shapesColors = parameters["shapesColors"]
        self.blink = parameters.get("blink") or [False] * 6
        self.actions = [tuple(x) for x in parameters["actions"]]

    def for_json(self):
        """Dumps this SignalAspect to JSON."""
        return {
            "__type__": "SignalAspect",
            "lineStyle": self.lineStyle,
            "outerShapes": self.outerShapes,
            "outerColors": self.outerColors,
            "shapes": self.shapes,
            "shapesColors": self.shapesColors,
            "actions": self.actions,
            "blink": self.blink
        }

    def meansProceed(self):
        """Returns true if this aspect is a proceed aspect, returns false if
        this aspect requires to stop."""
        if not self.actions:
            # No action means the driver discards the signal
            return True
        else:
            return self.actions[0] != (Target.ASAP, 0) \
                and self.actions[0] != (Target.BEFORE_THIS_SIGNAL, 0)

    def isBlinking(self):
        return any(b for b in self.blink)

    def drawAspect(self, p, linePen, shapePen, persistent=False, lightOn=True):
        """Draws the aspect on the given painter p. Draws the line with
        linePen and the shapes with shapePen."""
        if self.lineStyle == SignalLineStyle.BUFFER:
            p.setPen(shapePen)
            brush = QtGui.QBrush(Qt.SolidPattern)
            brush.setColor(Qt.darkGray)
            p.setBrush(brush)
            triangle = QtGui.QPolygonF()
            triangle << QtCore.QPointF(4, -4) \
                     << QtCore.QPointF(4, 4) \
                     << QtCore.QPointF(9, 0)
            p.drawPolygon(triangle)

        elif self.lineStyle == SignalLineStyle.LINE:
            p.setPen(linePen)
            p.drawLine(0, 0, 10, 0)

            # Draw the signal itself
            p.setPen(shapePen)
            brush = QtGui.QBrush(Qt.SolidPattern)
            for i in range(6):
                p.drawLine(2, 0, 2, -7)
                p.drawLine(2, -7, 8, -7)
                r = QtCore.QRectF((i // 2) * 8 + 8, -(i % 2) * 8 - 11, 8, 8)
                brush.setColor(QtGui.QColor(self.outerColors[i]))
                p.setBrush(brush)
                self.drawShape(p, self.outerShapes[i], r)
                if lightOn or not self.blink[i]:
                    brush.setColor(QtGui.QColor(self.shapesColors[i]))
                else:
                    brush.setColor(Qt.black)
                p.setBrush(brush)
                self.drawShape(p, self.shapes[i], r)

            # Draw persistent route marker
            if persistent:
                ppen = QtGui.QPen(Qt.white)
                ppen.setWidthF(2.5)
                ppen.setCapStyle(Qt.FlatCap)
                p.setPen(ppen)
                p.drawLine(6, -10, 6, -3)

    @staticmethod
    def drawShape(p, shape, rect):
        """Draws a signal aspect shape.

        :param p: The painter on which to draw the shape
        :param shape: The shape to draw
        :type shape: SignalShape
        :param rect: The rect inside which to draw the shape on the painter
        :type rect: QRectF
        """
        if shape == SignalShape.CIRCLE:
            p.drawEllipse(rect)
        elif shape == SignalShape.SQUARE:
            p.drawRect(rect)
        elif shape == SignalShape.QUARTER_NE:
            points = QtGui.QPolygonF()
            points \
                << rect.topLeft() \
                << rect.topRight() \
                << rect.bottomLeft()
            p.drawPolygon(points)
        elif shape == SignalShape.QUARTER_SE:
            points = QtGui.QPolygonF()
            points \
                << rect.topRight() \
                << rect.bottomRight() \
                << rect.topLeft()
            p.drawPolygon(points)
        elif shape == SignalShape.QUARTER_SW:
            points = QtGui.QPolygonF()
            points \
                << rect.bottomRight() \
                << rect.bottomLeft() \
                << rect.topRight()
            p.drawPolygon(points)
        elif shape == SignalShape.QUARTER_NW:
            points = QtGui.QPolygonF()
            points \
                << rect.bottomLeft() \
                << rect.topLeft() \
                << rect.bottomRight()
            p.drawPolygon(points)
        elif shape == SignalShape.BAR_N_S:
            tl = rect.topLeft() + QtCore.QPointF(1, 3)
            p.drawRect(QtCore.QRectF(tl, QtCore.QSizeF(6, 2)))
        elif shape == SignalShape.BAR_E_W:
            tl = rect.topLeft() + QtCore.QPointF(3, 1)
            p.drawRect(QtCore.QRectF(tl, QtCore.QSizeF(2, 6)))
        elif shape == SignalShape.BAR_NW_SE:
            edges = QtGui.QPolygonF()
            edges \
                << rect.topLeft() + QtCore.QPointF(1, 5.5) \
                << rect.topLeft() + QtCore.QPointF(2.5, 7) \
                << rect.topLeft() + QtCore.QPointF(7, 2.5) \
                << rect.topLeft() + QtCore.QPointF(5.5, 1)
            p.drawPolygon(edges)
        elif shape == SignalShape.BAR_SW_NE:
            edges = QtGui.QPolygonF()
            edges \
                << rect.topLeft() + QtCore.QPointF(1, 2.5) \
                << rect.topLeft() + QtCore.QPointF(5.5, 7) \
                << rect.topLeft() + QtCore.QPointF(7, 5.5) \
                << rect.topLeft() + QtCore.QPointF(2.5, 1)
            p.drawPolygon(edges)

        if (shape == SignalShape.POLE_NE or
                shape == SignalShape.POLE_NS or
                shape == SignalShape.POLE_NSE or
                shape == SignalShape.POLE_NSW):
            tm = QtCore.QPointF(rect.right(), rect.center().y())
            p.drawLine(rect.center(), tm)

        if (shape == SignalShape.POLE_NS or
                shape == SignalShape.POLE_NSE or
                shape == SignalShape.POLE_NSW or
                shape == SignalShape.POLE_SW):
            bm = QtCore.QPointF(rect.left(), rect.center().y())
            p.drawLine(rect.center(), bm)

        if (shape == SignalShape.POLE_NE or
                shape == SignalShape.POLE_NSE):
            rm = QtCore.QPointF(rect.center().x(), rect.bottom())
            p.drawLine(rect.center(), rm)

        if (shape == SignalShape.POLE_NSW or
                shape == SignalShape.POLE_SW):
            lm = QtCore.QPointF(rect.center().x(), rect.top())
            p.drawLine(rect.center(), lm)

    def boundingRect(self):
        """Return the boundingRect of this aspect."""
        return QtCore.QRectF(0, -20, 33, 24)
