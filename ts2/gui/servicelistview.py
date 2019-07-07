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

from Qt import QtCore, QtWidgets

from ts2 import simulation


class ServiceListView(QtWidgets.QTreeView):
    """TODO Document ServiceListView"""

    def __init__(self, parent):
        super().__init__(parent)
        self.simulation = None
        self.setItemsExpandable(False)
        self.setRootIsDecorated(False)
        self.setHeaderHidden(False)

    serviceSelected = QtCore.pyqtSignal(str)

    @QtCore.pyqtSlot(str)
    def updateServiceSelection(self, trainId):
        """Update the selection by selecting the service of the train given by
        trainId. """
        if self.simulation is not None:
            serviceCode = self.simulation.trains[int(trainId)].serviceCode
            for i in range(self.model().rowCount()):
                index = self.model().index(i, 0)
                if self.model().data(index) == serviceCode:
                    self.selectionModel().select(
                        index,
                        QtCore.QItemSelectionModel.Rows |
                        QtCore.QItemSelectionModel.ClearAndSelect
                    )

    @QtCore.pyqtSlot(simulation.Simulation)
    def setupServiceList(self, sim):
        """Updates the service list view."""
        self.simulation = sim
        # if self.model() is None:
        model = self.simulation.serviceListModel
        model.updateModel()
        self.setModel(model)
        self.setSortingEnabled(True)
        for i in range(0, 4):
            self.resizeColumnToContents(i)
        self.header().setStretchLastSection(False)
        self.header().setSortIndicatorShown(False)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    @QtCore.pyqtSlot(QtCore.QItemSelection, QtCore.QItemSelection)
    def selectionChanged(self, selected, deselected):
        """This function is called when a line is selected in the
        serviceListView.
        It emits the serviceSelected signal for others to connect to."""
        super().selectionChanged(selected, deselected)
        if selected.indexes():
            index = selected.indexes()[0]
            if index.isValid():
                self.serviceSelected.emit(index.data())
