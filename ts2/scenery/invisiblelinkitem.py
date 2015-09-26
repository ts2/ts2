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

from Qt import Qt

from ts2 import utils
from ts2.scenery import lineitem


class InvisibleLinkItem(lineitem.LineItem):
    """InvisibleLinkItem behave like line items, but are not represented at
    all on the scenery. They are used to make links between lines or to
    represent bridges and tunnels.
    """
    def __init__(self, parameters):
        """Constructor for the InvisibleLinkItem class"""
        super().__init__(parameters)
        for tli in self._tli:
            tli.hide()

    # ## Methods ########################################################

    def updateTrain(self):
        """Does nothing as this is an invisible link."""
        pass

    # ## Graphics Methods ###############################################

    def graphicsPaint(self, p, options, itemId, widget=None):
        """This function is called by the owned TrackGraphicsItem to paint its
        painter. Draws nothing during the game."""
        super(lineitem.LineItem, self).graphicsPaint(p, options, itemId, widget)
        if self.simulation.context == utils.Context.EDITOR_SCENERY:
            if self.selected:
                p.setPen(Qt.magenta)
            else:
                p.setPen(Qt.cyan)
            p.drawLine(self.line)
            self.drawConnectionRect(p, self.line.p1())
            self.drawConnectionRect(p, self.line.p2())
