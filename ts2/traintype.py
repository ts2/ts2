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

from PyQt4.QtCore import *

class TrainType(QObject):
    """ TODO Document TrainType class"""
    
    def __init__(self, code, description, maxSpeed, stdAccel, stdBraking, emergBraking, length):
        super().__init__()
        self._code = code
        self._description = description
        self._maxSpeed = float(maxSpeed)
        self._stdAccel = float(stdAccel)
        self._stdBraking = float(stdBraking)
        self._emergBraking = float(emergBraking)
        self._length = float(length)

    @property
    def code(self):
        return self._code
    
    @property
    def description(self):
        return self._description
    
    @property
    def maxSpeed(self): 
        return self._maxSpeed
    
    @property
    def stdAccel(self):
        return self._stdAccel
    
    @property
    def stdBraking(self):
        return self._stdBraking
    
    @property
    def emergBraking(self):
        return self._emergBraking
    
    @property
    def length(self): 
        return self._length
    

