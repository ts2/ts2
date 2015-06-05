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

# append the parent to the diretory
HERE_PATH =  os.path.abspath( os.path.dirname( __file__ ))
if sys.path.count(HERE_PATH) == 0:
	sys.path.insert(0, HERE_PATH)

__VERSION__ = "0.4.1"
__FILE_FORMAT__ = 0.4
__APP_SHORT__ = "ts2"
__APP_LONG__ = "Train Signalling Simulation #2"
__APP_DESCRIPTION__ = "A railway simulation game where you have to dispatch trains across an area and keep them on schedule"

__ORG_NAME__ = "ts2 team"
__ORG_CONTACT__ = "npiganeau"

__PROJECT_DOMAIN__ = "ts2.sourceforge.net"
__PROJECT_WWW__ = "http://ts2.sourceforge.net/"
__PROJECT_HOME__ = "https://github.com/npiganeau/ts2"


def get_info():
	return dict(
		version = __VERSION__,
		
		app_short = __APP_SHORT__,
		app_long = __APP_LONG__,
		app_description = __APP_DESCRIPTION__,
		
		project_domain = __PROJECT_DOMAIN__,
		project_www = __PROJECT_WWW__,
		project_home = __PROJECT_HOME__
	)




#__all__ = ['bumperitem','clock','enditem','lineitem','mainwindow','panel', \
           #'place','platformitem','pointsitem','position','route','service', \
           #'serviceassigndialog','servicelistview','signalitem','signaltimeritem', \
           #'simulation','trackitem','train','trainlistview','traintype','utils']
