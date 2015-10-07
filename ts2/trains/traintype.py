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

import copy
from Qt import QtCore, Qt

from ts2 import utils


class TrainTypesModel(QtCore.QAbstractTableModel):
    """Model for TrainType class used in the editor
    """
    def __init__(self, editor):
        """Constructor for the TrainTypesModel class"""
        super().__init__(editor)
        self._editor = editor
        
    def rowCount(self, parent=None, *args, **kwargs):
        """Returns the number of rows of the model, corresponding to the 
        number of rolling stock types."""
        return len(self._editor.trainTypes)
    
    def columnCount(self, parent=None, *args, **kwargs):
        """Returns the number of columns of the model"""
        return 7
    
    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole or role == Qt.EditRole:
            trainTypes = list(self._editor.trainTypes.values())
            if index.column() == 0:
                return str(trainTypes[index.row()].code)
            elif index.column() == 1:
                return trainTypes[index.row()].description
            elif index.column() == 2:
                return trainTypes[index.row()].maxSpeed
            elif index.column() == 3:
                return trainTypes[index.row()].stdAccel
            elif index.column() == 4:
                return trainTypes[index.row()].stdBraking
            elif index.column() == 5:
                return trainTypes[index.row()].emergBraking
            elif index.column() == 6:
                return trainTypes[index.row()].length
        return None
    
    def setData(self, index, value, role=None):
        """Updates data when modified in the view"""
        if role == Qt.EditRole:
            code = index.sibling(index.row(), 0).data()
            if index.column() == 1:
                self._editor.trainTypes[code].description = value
            elif index.column() == 2:
                self._editor.trainTypes[code].maxSpeed = value
            elif index.column() == 3:
                self._editor.trainTypes[code].stdAccel = value
            elif index.column() == 4:
                self._editor.trainTypes[code].stdBraking = value
            elif index.column() == 5:
                self._editor.trainTypes[code].emergBraking = value
            elif index.column() == 6:
                self._editor.trainTypes[code].length = value
            else:
                return False
            self.dataChanged.emit(index, index)
            return True
        return False
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Returns the header labels"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return self.tr("Code")
            elif section == 1:
                return self.tr("Description")
            elif section == 2:
                return self.tr("Max speed (m/s)")
            elif section == 3:
                return self.tr("Std acceleration (m/s2)")
            elif section == 4:
                return self.tr("Std braking (m/s2)")
            elif section == 5:
                return self.tr("Emerg. braking (m/s2)")
            elif section == 6:
                return self.tr("Length (m)")
        return None
    
    def flags(self, index):
        """Returns the flags of the model"""
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() != 0:
            flags |= Qt.ItemIsEditable
        return flags


class TrainType:
    """The ``TrainType`` class holds information relating to rolling stock types.
    """
    def __init__(self, parameters):
        """Constructor for the TrainType class"""
        self._code = str(parameters["code"])
        self._description = parameters["description"]
        self._maxSpeed = float(parameters["maxSpeed"])
        self._stdAccel = float(parameters["stdAccel"])
        self._stdBraking = float(parameters["stdBraking"])
        self._emergBraking = float(parameters["emergBraking"])
        self._length = float(parameters["length"])
        self.simulation = None

    def initialize(self, simulation):
        """Initializes the simulation variable once it is loaded."""
        self.simulation = simulation

    def for_json(self):
        """Dumps this trainType to JSON"""
        return {
            "__type__": "TrainType",
            "code": self.code,
            "description": self.description,
            "maxSpeed": self.maxSpeed,
            "stdAccel": self.stdAccel,
            "stdBraking": self.stdBraking,
            "emergBraking": self.emergBraking,
            "length": self.length
        }

    @property
    def code(self):
        """Returns the unique code of this rolling stock type"""
        return self._code
    
    @code.setter
    def code(self, value):
        """Setter function for the code property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINTYPES:
            self._code = value
    
    @property
    def description(self):
        """Returns the description of this rolling stock type"""
        return self._description
    
    @description.setter
    def description(self, value):
        """Setter function for the description property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINTYPES:
            self._description = value
    
    @property
    def maxSpeed(self):
        """Returns the maximum speed that this rolling stock type is capable,
        in m/s"""
        return self._maxSpeed
    
    @maxSpeed.setter
    def maxSpeed(self, value):
        """Setter function for the maxSpeed property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINTYPES:
            self._maxSpeed = value
    
    @property
    def stdAccel(self):
        """Returns the standard acceleration of this rolling stock type, in
        m/s2"""
        return self._stdAccel
    
    @stdAccel.setter
    def stdAccel(self, value):
        """Setter function for the stdAccel property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINTYPES:
            self._stdAccel = value
    
    @property
    def stdBraking(self):
        """Returns the standard braking of this rolling stock type, in
        m/s2. The standard braking is the normal rate at which speed will be 
        reduced when approaching a speed limit, a station, a signal, etc."""
        return self._stdBraking
    
    @stdBraking.setter
    def stdBraking(self, value):
        """Setter function for the stdBraking property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINTYPES:
            self._stdBraking = value
    
    @property
    def emergBraking(self):
        """Returns the emergency braking of this rolling stock type, in
        m/s2. Emergency braking is the maximum rate at which a train can 
        reduce its speed in case of a danger ahead."""
        return self._emergBraking
    
    @emergBraking.setter
    def emergBraking(self, value):
        """Setter function for the emergBraking property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINTYPES:
            self._emergBraking = value
    
    @property
    def length(self):
        """Returns the length of this rolling stock type in meters"""
        return self._length
    
    @length.setter
    def length(self, value):
        """Setter function for the length property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINTYPES:
            self._length = value
