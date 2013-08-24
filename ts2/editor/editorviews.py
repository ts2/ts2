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

class RoutesEditorView(QtGui.QTableView):
    """Table view with specific options for editing routes in the editor
    """
    def __init__(self, parent):
        """Constructor for the RoutesEditorView class"""
        super().__init__(parent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, \
                                       QtGui.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        self.setSizePolicy(sizePolicy)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    
    routeSelected = QtCore.pyqtSignal(int)
    
    def selectionChanged(self, selected, deselected):
        """Called when the user changes the selection. Emits the routeSelected
        signal"""
        super().selectionChanged(selected, deselected)
        index = selected.indexes()[0]
        if index.isValid():
            self.routeSelected.emit(index.data())



class TrainTypesEditorView(QtGui.QTableView):
    """Table view with specific options for editing trainTypes in the editor
    """
    def __init__(self, parent):
        """Constructor for the RoutesEditorView class"""
        super().__init__(parent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, \
                                       QtGui.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        self.setSizePolicy(sizePolicy)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    

    
    