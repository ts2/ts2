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

from trackitem import *
from simulation import *
from PyQt4.QtSql import *

BIG = 1000000000

class EndItem(TrackItem):
    """ TODO Document EndItem class"""
    
    def __init__(self, simulation, record):
        super().__init__(simulation, record)
        self._tiType = "E"
        self._realLength = BIG
        self._end = QPointF(-1,-1)
        self._gi = QGraphicsLineItem(0,0,0,0,None)
        simulation.registerGraphicsItem(self._gi)

    def getFollowingItem(self, precedingItem, direction = -1):
        if precedingItem == self._previousItem:
            return None
        else:
            return self._previousItem

