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

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

class ServicesDelegate(QtGui.QStyledItemDelegate):
    """ServicesDelegate is a delegate that provides a combo box for 
    selecting a Service.
    """
    
    def createEditor(self, parent, option, index):
        """Creates the editor, i.e. a combo box for selecting a service."""
        simulation = index.model().simulation
        comboBox = QtGui.QComboBox(parent)
        comboBox.setModel(simulation.serviceListModel)
        comboBox.setModelColumn(0)
        return comboBox
    
    def setEditorData(self, editor, index):
        """Sets the values from the model in the combo box"""
        simulation = index.model().simulation
        serviceCode = index.model().data(index, Qt.EditRole)
        startSearchIndex = simulation.serviceListModel.index(0, 0)
        serviceIndexes = simulation.serviceListModel.match(
                                                startSearchIndex, 
                                                Qt.DisplayRole, 
                                                serviceCode, 
                                                1, 
                                                Qt.MatchExactly|Qt.MatchWrap)
        if len(serviceIndexes) > 0:
            serviceIndex = serviceIndexes[0].row()
        else:
            serviceIndex = 0
        editor.setCurrentIndex(serviceIndex)
    
    def setModelData(self, editor, model, index):
        """Sets the values from the combo box to the model after editing"""
        serviceCode = editor.currentText()
        model.setData(index, serviceCode, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Sets the editor geometry."""
        editor.setGeometry(option.rect)


        
class TrainTypesDelegate(QtGui.QStyledItemDelegate):
    """TrainTypesDelegate is a delegate that provides a combo box for 
    selecting a TrainType.
    """
    
    def createEditor(self, parent, option, index):
        """Creates the editor, i.e. a combo box for selecting a train type."""
        simulation = index.model().simulation
        comboBox = QtGui.QComboBox(parent)
        comboBox.setModel(simulation.trainTypesModel)
        comboBox.setModelColumn(0)
        return comboBox
    
    def setEditorData(self, editor, index):
        """Sets the values from the model in the combo box"""
        simulation = index.model().simulation
        code = index.model().data(index, Qt.EditRole)
        startSearchIndex = simulation.trainTypesModel.index(0, 0)
        trainTypeIndexes = simulation.trainTypesModel.match(
                                                startSearchIndex, 
                                                Qt.DisplayRole, 
                                                code, 
                                                1, 
                                                Qt.MatchExactly|Qt.MatchWrap)
        if len(trainTypeIndexes) > 0:
            trainTypeIndex = trainTypeIndexes[0].row()
        else:
            trainTypeIndex = 0
        editor.setCurrentIndex(trainTypeIndex)
    
    def setModelData(self, editor, model, index):
        """Sets the values from the combo box to the model after editing"""
        code = editor.currentText()
        model.setData(index, code, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Sets the editor geometry."""
        editor.setGeometry(option.rect)
        
        
    