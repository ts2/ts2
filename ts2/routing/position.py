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

class Position:
    """Class Position
    TODO Document Position class"""

    def __init__(self, trackItem = None, previousTI = None, positionOnTI = 0.0):
        self._trackItem = trackItem
        self._previousTI = previousTI
        self._positionOnTI = positionOnTI

    @property
    def trackItem(self):
        return self._trackItem

    @property
    def previousTI(self):
        return self._previousTI

    @property
    def positionOnTI(self):
        return float(self._positionOnTI)

    def next(self, pos = 0, direction = -1):
        return Position(self._trackItem.getFollowingItem(self._previousTI, direction),\
                        self._trackItem, \
                        pos)
    
    def previous(self, pos = None):
        if pos is None:
            pos = self._previousTI.realLength
        return Position(self._previousTI,\
                        self._previousTI.getFollowingItem(self._trackItem),\
                        pos)

    def distanceToPosition(self, p):
        """Returns the distance between the current position and p if p is ahead of 
        current position. Returns 0 otherwise."""
        res = 0.0
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
        """Returns a list of all the trackItems between this position and position p.
        including the trackItem of this position and the trackItem of position p."""
        til = []
        cur = self
        while cur.trackItem != p.trackItem and not cur.isOut():
            til.append(cur.trackItem)
            cur = cur.next()
        til.append(p.trackItem)
        return til

    def isOut(self):
        if self.trackItem.tiType.startswith("E"):
            return True
        else:
            return False

    def reverse(self):
        """Returns a position that is physically on the exact same place, but
        coming from the opposite direction"""
       	self._positionOnTI = self._trackItem.realLength - self._positionOnTI
        self._previousTI = self._trackItem.getFollowingItem(self._previousTI)
        return Position(self._trackItem, self._previousTI, self._positionOnTI)

    def __eq__(self, p):
        return (self._trackItem == p.trackItem \
            and self._previousTI == p.previousTI \
            and self._positionOnTI == p.positionOnTI)

    def __ne__(self, p):
        return not (self == p)

    def __add__(self, length):
        if self._positionOnTI + length < self._trackItem.realLength:
            return Position(self._trackItem, \
                            self._previousTI, \
                            self._positionOnTI + length)
        else:
            return self.next() + (length + self._positionOnTI - self._trackItem.realLength)

    def __sub__(self, length):
        if (self._positionOnTI - length > 0):
            return Position(self._trackItem, \
                            self._previousTI, \
                            self._positionOnTI - length)
        else:
            return self.previous(self._previousTI.realLength) - \
                   (length - self._positionOnTI)

    def __iadd__(self, length):
        self = self + length
        return self

    def __isub__(self, length):
        self = self - length
        return self
    
