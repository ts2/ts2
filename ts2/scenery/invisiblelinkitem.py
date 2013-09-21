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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from ts2 import utils
from ts2.scenery import LineItem


class InvisibleLinkItem(LineItem):
    """InvisibleLinkItem behave like line items, but are not represented at
    all on the scenery. They are used to make links between lines or to
    represent bridges and tunnels.
    """
    def __init__(self, simulation, parameters):
        """Constructor for the InvisibleLinkItem class"""
        super().__init__(simulation, parameters)
        self._tiType = "LI"
        self._tli.hide()

    def graphicsPaint(self, p, options, widget):
        """This function is called by the owned TrackGraphicsItem to paint its
        painter. Draws nothing during the game."""
        if self._simulation.context == utils.Context.EDITOR_SCENERY:
            p.setPen(Qt.cyan)
            p.drawLine(self.line)
            self.drawConnectionRect(p, self.line.p1())
            self.drawConnectionRect(p, self.line.p2())

    @QtCore.pyqtSlot()
    def updateGraphics(self):
        self._gi.update()



