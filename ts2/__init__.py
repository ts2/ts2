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

###############################################################
# Please try and not include any imports here
# As this file may be loaded in any enviroment
# such as a packager, docs compile etc
###############################################################


__VERSION__ = "0.7.9"
__SERVER_VERSION__ = "0.7.7"
__FILE_FORMAT__ = "0.7"
__APP_SHORT__ = "ts2"
__APP_LONG__ = "Train Signalling Simulation"
__APP_DESCRIPTION__ = "A railway simulation game where you have to dispatch trains across an area and keep them on " \
                      "schedule"

__ORG_NAME__ = "TS2 Team"
__ORG_CONTACT__ = "npiganeau@github.com"

__PROJECT_DOMAIN__ = "ts2.github.io"
__PROJECT_WWW__ = "http://ts2.github.io/"
__PROJECT_HOME__ = "https://github.com/ts2"
__PROJECT_BUGS__ = "https://github.com/ts2/ts2/issues"
__PROJECT_API_DOCS__ = "http://docs-ts2.rhcloud.com/"

__SIMULATIONS_REPO__ = "https://github.com/ts2/ts2-data"
__SERVER_REPO__ = "https://github.com/ts2/ts2-sim-server"


PLATFORMS_MAP = {
    'linux': 'Linux',
    'win32': 'Windows',
    'darwin': 'Darwin',
}


def get_info():
    """ts2 info

    :rtype: `dict`
    """
    return dict(
        version=__VERSION__,
        server_version=__SERVER_VERSION__,
        app_short=__APP_SHORT__,
        app_long=__APP_LONG__,
        app_description=__APP_DESCRIPTION__,
        project_domain=__PROJECT_DOMAIN__,
        project_www=__PROJECT_WWW__,
        project_home=__PROJECT_HOME__,
        project_bugs=__PROJECT_BUGS__,
        project_api_docs=__PROJECT_API_DOCS__,
        simulations_repo=__SIMULATIONS_REPO__,
        server_repo=__SERVER_REPO__,
    )
