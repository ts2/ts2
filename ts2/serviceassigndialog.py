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
from service import *
from servicelistview import *

class ServiceAssignDialog(QDialog):
    """TODO Document ServiceAssignDialog"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Choose a service to assign to this train"))
        self._serviceListView = ServiceListView(self, parent.simulation)
        self._serviceListView.setupServiceList()
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        layout = QVBoxLayout()
        layout.addWidget(self._serviceListView)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.resize(600, 300)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getServiceCode(self):
        index = self._serviceListView.selectionModel().selection().indexes()[0]
        if index.isValid():
            return index.data()
        else:
            return ""

