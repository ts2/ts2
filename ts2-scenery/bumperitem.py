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

from signalitem import *
from PyQt4.QtSql import *

class BumperItem(SignalItem):
    def __init__(self, simulation, record):
        super().__init__(simulation, record)
        self._tiType = "SB"


    def drawSignal(self, p):
        """Draws the bumper on the painter given as parameter.
        This function is called by SignalGraphicsItem.paint.
        @param p The painter on which to draw the signal."""
        # Draw the berth
        linePen = self.getPen()
        textPen = self.getPen()
        textPen.setColor(Qt.white)
        if self.trainPresent:
            linePen.setColor(Qt.red)

        if self._trainServiceCode != "":
            # Train code to draw
            p.setPen(textPen)
            font = QFont("Courier new")
            font.setPixelSize(11)
            p.setFont(font)
            textOrigin = QPointF(23,6) if self.reverse() else QPointF(3,22)
            p.drawText(textOrigin, self._trainServiceCode.rightJustified(5))
        else:
            # No Train code => Draw Line
            p.setPen(linePen)
            if self.reverse():
                p.drawLine(20, 2, 60, 2) 
            else:
                p.drawLine(0, 18, 40, 18)

        if self.selected():
            linePen.setColor(Qt.cyan)

        # Draw the signal itself
        textPen.setWidth(1)
        brush = QBrush(Qt.SolidPattern)
        if self.signalHighlighted():
            textPen.setColor(Qt.white)
            brush.setColor(Qt.white)
        else:
            textPen.setColor(Qt.darkGray)
            brush.setColor(Qt.darkGray)
        p.setPen(textPen)
        p.setBrush(brush)

        if self.reverse():
            triangle = QPolygonF()
            triangle << QPointF(10,2) << QPointF(15,4) << QPointF(15, 0)
            p.drawPolygon(triangle)
        else:
            triangle = QPolygonF()
            triangle << QPointF(50, 18) << QPointF(45,20) << QPointF(45, 16)
            p.drawPolygon(triangle)


