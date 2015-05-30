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

import os
import sys

HERE_PATH =  os.path.abspath( os.path.dirname( __file__ ))
if sys.path.count(HERE_PATH) == 0:
	sys.path.insert(0, HERE_PATH)

#print("YES", HERE_PATH)


#__all__ = ['bumperitem','clock','enditem','lineitem','mainwindow','panel', \
           #'place','platformitem','pointsitem','position','route','service', \
           #'serviceassigndialog','servicelistview','signalitem','signaltimeritem', \
           #'simulation','trackitem','train','trainlistview','traintype','utils']
