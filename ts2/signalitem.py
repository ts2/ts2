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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from ts2.trackitem import *
from ts2.route import *

class SignalState:

    CLEAR = 0
    WARNING = 50
    STOP = 100

class SignalGraphicsItem(QGraphicsItem):
    """@brief Graphical item for signals
    This class is the graphics of a SignalItem on the scene.
    Each instance belongs to a SignalItem which is defined in the constructor.
    @author Nicolas Piganeau"""

    def __init__(self, signalItem, parent = None):
        """Constructor for the SignalGraphicsItem class.
        @param signalItem Pointer to the SignalItem to which this
        SignalGraphicsItem belongs to."""
        super().__init__(parent)
        self._signalItem = signalItem
        self.setZValue(100)

    def boundingRect(self):
        """Returns the bounding rectangle of the SignalGraphicsItem.
        See QGraphicsItem::boundingRect() for more info."""
        return QRectF(0, 0, 60, 25)

    def paint(self, painter, option, widget = 0):
        """Painting function for the SignalGraphicsItem.
        This function asks for the owning SignalItem to paint its painter."""
        self._signalItem.drawSignal(painter)

    def mousePressEvent(self, event):
        """mousePressEvent function, called when the signalGraphicsItem is
        clicked. This function calls the select function of the owning
        SignalItem."""
        self._signalItem.select(event)


class SignalItem(TrackItem):
    """ @brief Logical item for signals
    This class holds the logics of a basic signal (CLEAR, WARNING, STOP).
    A signal is the item from and to which routes are created.
    Each instance owns a SignalGraphicsItem which is the graphical item drawn on the scene.
    @author Nicolas Piganeau"""

    def __init__(self, simulation, record):
        """ Constructor for the SignalItem class.
        trainSelected is  lists of the slots to which the 
        corresponding signals will be connected to"""
        super().__init__(simulation, record)
        reverse = record.value("reverse")
        if reverse:
            self._end = self._origin + QPointF(-60, 0)
        else:
            self._end = self._origin + QPointF(60, 0)
        self._tiType = "S"
        self._selected = False
        self._reverse = reverse
        self._signalState = SignalState.STOP
        self._previousActiveRoute = None
        self._nextActiveRoute = None
        self._trainServiceCode = ""
        self._signalPos = 0
        sgi = SignalGraphicsItem(self)
        sgi.setPos(self.realOrigin)
        sgi.setCursor(Qt.PointingHandCursor)
        sgi.setToolTip(self.tr("Signal: %s") % self.name)
        self._gi = sgi
        simulation.registerGraphicsItem(self._gi)
        self.updateGraphics()
        self.signalSelected.connect(simulation.createRoute)
        self.signalUnselected.connect(simulation.deleteRoute)
        self.trainSelected.connect(simulation.simulationWindow.trainListView.updateTrainSelection)

    signalSelected = pyqtSignal(int, bool)
    signalUnselected = pyqtSignal(int)
    trainSelected = pyqtSignal(str)

    @property
    def reverse(self):
        return self._reverse

    @property
    def highlighted(self):
        return (self._activeRoute is not None or self.signalHighlighted)

    @property
    def signalHighlighted(self):
        return self._nextActiveRoute is not None or self._previousActiveRoute is not None

    @property
    def realOrigin(self):
        if self._reverse:
            return self.end + QPointF(0,-2)
        else:
            return self.origin + QPointF(0,-18)

    @property
    def size(self):
        return QSizeF(60, 20)

    @property
    def signalState(self):
        return self._signalState

    @property
    def signalPos(self):
        return self._signalPos
  
    @property
    def previousActiveRoute(self):
        return self._previousActiveRoute

    @property
    def nextActiveRoute(self):
        return self._nextActiveRoute

    @nextActiveRoute.setter 
    def nextActiveRoute(self, route):
        """ Sets the nextActiveRoute information."""
        self._nextActiveRoute = route
        self.updateSignalState()

    def isOnPosition(self, p):
        """ Checks that the signalItem is on the position p,
        i.e. the trackItem and direction are the same
        @param p the position
        @return Returns true if the signalItem is on position p"""
        if p.trackItem == self and p.previousTI == self.previousItem:
            return True
        else:
            return False

    def select(self, e):
        """ This function is called by mousePressEvent of the owned SignalGraphicsItem.
        It processes mouse clicks on the signal. If the It emits the signals signalSelected,
        trainSelected, or signalUnselected depending on the case."""
        if e.button() == Qt.LeftButton:
            if (self._reverse and e.pos().x() <= 20) or \
               (not self._reverse and e.pos().x() > 40):
                # The signal itself is selected
                self._selected = True;
                persistent = (e.modifiers() == Qt.ShiftModifier)
                self.signalSelected.emit(self.tiId, persistent);
            else:
                # The train code is selected
                self.trainSelected.emit(self._trainServiceCode)
        elif e.button() == Qt.RightButton:
            if (self._reverse and e.pos().x() <= 20) or \
               (not self._reverse and e.pos().x() > 40):
                # The signal itself is right-clicked
                self._selected = False
                self.signalUnselected.emit(self.tiId)
            else:
                # The train code is right-clicked 
                train = self._simulation.train(self._trainServiceCode)
                if train is not None:
                    train.showTrainActionsMenu(self._simulation.simulationWindow.view, e.screenPos())
        self.updateGraphics()

    def drawSignal(self, p):
        """ Draws the signal on the painter given as parameter.
        This function is called by SignalGraphicsItem::paint.
        @param p The painter on which to draw the signal."""
        # Draws the berth
        linePen = self.getPen()
        textPen = self.getPen()
        textPen.setColor(Qt.white)
        if self.trainPresent():
            linePen.setColor(Qt.red)
        if self._trainServiceCode != "":
            # Draw Train code
            p.setPen(textPen)
            font = QFont("Courier new")
            font.setPixelSize(11)
            p.setFont(font)
            textOrigin = QPointF(23,6) if self.reverse else QPointF(3,22)
            p.drawText(textOrigin, self._trainServiceCode.rjust(5))
        else:
            # No Train code => Draw Line
            p.setPen(linePen)
            if self.reverse:
                p.drawLine(20, 2, 60, 2)
            else:
                p.drawLine(0, 18, 40, 18)

        # draw the line at the base of the signal
        if self.selected:
            linePen.setColor(Qt.cyan)
        p.setPen(linePen)
        if self.reverse:
            p.drawLine(0, 2, 20, 2)
        else:
            p.drawLine(40, 18, 60, 18)

        # Draw the signal itself
        textPen.setWidth(0)
        if self.signalHighlighted:
            textPen.setColor(Qt.white)
        else:
            textPen.setColor(Qt.darkGray)
        p.setPen(textPen)
        brush = QBrush(Qt.SolidPattern)
        if self._signalState == SignalState.CLEAR:
            brush.setColor(Qt.green)
        elif self._signalState == SignalState.WARNING:
            brush.setColor(Qt.yellow)
        elif self._signalState == SignalState.STOP:
            brush.setColor(Qt.red)
        else:
            brush.setColor(Qt.black)
        p.setBrush(brush)
        if self.reverse:
            r = QRect(7, 7, 8, 8)
            p.drawLine(18, 2, 18, 11);
            p.drawLine(18, 11, 15, 11);
            p.drawEllipse(r);
            if self._nextActiveRoute is not None and self._nextActiveRoute.persistent:
                # Draw persistent route rectangle marker
                brush.setColor(Qt.white)
                p.setBrush(brush)
                p.drawRect(1,5,4,3)
        else:
            r = QRect(45, 5, 8, 8)
            p.drawLine(42, 18, 42, 9)
            p.drawLine(42, 9, 45, 9)
            p.drawEllipse(r)
            if self._nextActiveRoute is not None and self._nextActiveRoute.persistent:
                # Draw persistent route rectangle marker
                brush.setColor(Qt.white)
                p.setBrush(brush)
                p.drawRect(55,12,4,3)
     
    def resetNextActiveRoute(self):
        """Resets the nextActiveRoute information."""
        self._nextActiveRoute = None
        self.updateSignalState()

    @previousActiveRoute.setter
    def previousActiveRoute(self, route):
        """Sets the previousActiveRoute information."""
        self._previousActiveRoute = route
        self.updateSignalState()

    def resetPreviousActiveRoute(self):
        """Reset the previousActiveRoute information."""
        self._previousActiveRoute = None
        self.updateSignalState()

    @property
    def trainServiceCode(self):
        """Returns the trainServiceCode of this signal. This is for display only."""
        return self._trainServiceCode

    @trainServiceCode.setter
    def trainServiceCode(self, code):
        """Sets the trainServiceCode of this signal to the given code. This is for display only."""
        self._trainServiceCode = code
        self.updateGraphics()

    def resetTrainServiceCode(self):
        """Resets the trainServiceCode of this signal."""
        self._trainServiceCode = ""
        self.updateGraphics()

    def trainsAhead(self):
        """ Returns true if there is a train ahead of this signalItem and before
        the next signalItem"""
        pos = Position(self._nextItem, self, 0)
        while not pos.trackItem.tiType.startswith("E"):
            if pos.trackItem.tiType.startswith("S") and \
            pos.trackItem.isOnPosition(pos):
                # We have met the next signal in the same direction without finding any train
                break
            if pos.trackItem.trainPresent():
                return True
            pos = pos.next()
        return False

    def trainHeadActions(self, serviceCode):
        """Actions to be performed when the train head reaches this signal.
        Pushes the train code to the next signal."""
        if self.nextActiveRoute is not None:
            self.nextActiveRoute.endSignal.trainServiceCode = self.trainServiceCode
            self.resetTrainServiceCode()            
        super().trainHeadActions(serviceCode)

    def trainTailActions(self, serviceCode):
        """Actions that are to be done when a train tail reaches this signal.
        It deals with desactivating this signal."""
        if self.activeRoute is not None and \
           self.activeRoutePreviousItem != self.previousItem:
            # The line is highlighted by an opposite direction route => usual TI
            super().trainTailActions(serviceCode)
        else:
            self.resetActiveRoute() # For cleaning purposes, activeRoute is not used in this direction
            if self.previousActiveRoute is not None and not self.previousActiveRoute.persistent:
                beginSignalNextRoute = self.previousActiveRoute.beginSignal.nextActiveRoute
                if beginSignalNextRoute is None or \
                   beginSignalNextRoute != self.previousActiveRoute:
                    # Only reset previous route if the user did not reactivate it in the meantime
                    self.previousItem.resetActiveRoute()
                    self.resetPreviousActiveRoute()
            if self.nextActiveRoute is not None and not self.nextActiveRoute.persistent:
                self.resetNextActiveRoute()
            self.updateSignalState()

    @pyqtSlot()
    def unselect(self):
        """Unselect the signal."""
        self._selected = False
        self.updateGraphics()

    @pyqtSlot()
    def updateSignalState(self):
        """Update the signal state."""
        if self._nextActiveRoute is None or self.trainsAhead():
            self._signalState = SignalState.STOP
        else:
            if self._nextActiveRoute.endSignal.signalState == SignalState.CLEAR:
                self._signalState = SignalState.CLEAR
            elif self._nextActiveRoute.endSignal.signalState == SignalState.WARNING:
                self._signalState = SignalState.CLEAR
            elif self._nextActiveRoute.endSignal.signalState == SignalState.STOP:
                self._signalState = SignalState.WARNING
            else:
                self._signalState = SignalState.STOP
        if self._previousActiveRoute is not None:
            self._previousActiveRoute.beginSignal.updateSignalState()
        self.updateGraphics()
