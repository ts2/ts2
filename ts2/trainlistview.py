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
from PyQt4.QtGui import *
from ts2.simulation import Simulation
from ts2 import trains

class TrainListView(QTreeView):
    """ TODO Document TrainListView class"""

    def __init__(self, parent, simulation):
        super().__init__(parent)
        self._simulation = simulation
        self.setItemsExpandable(False)
        self.setRootIsDecorated(False)
        self.setHeaderHidden(False)
        self.setSortingEnabled(True)
        self._simulation.simulationLoaded.connect(self.setupTrainList)

    trainSelected = pyqtSignal(int)

    @pyqtSlot(int)
    def updateTrainSelection(self, trainId):
        index = self.model().index(trainId, 0)
        self.selectionModel().select(index,
                                     QItemSelectionModel.Rows|
                                     QItemSelectionModel.ClearAndSelect)

    @pyqtSlot()
    def setupTrainList(self):
        if self.model() is None:
            #trainsSortedModel = QSortFilterProxyModel()
            #trainsSortedModel.setSourceModel()
            self.setModel(self._simulation.trainListModel)
            self.header().setStretchLastSection(False)
            self.header().setSortIndicatorShown(False)
            self.setSelectionBehavior(QAbstractItemView.SelectRows)
            self._simulation.trainStatusChanged.connect(self.model().update)
            #self._simulation.timeChanged.connect(self.model().update)
            #self.trainSelected.connect(self._simulation.selectedTrainModel.setTrainByServiceCode)


    def contextMenuEvent(self, event):
        index = self.selectionModel().selection().indexes()[0]
        if index.isValid():
            train = self._simulation.trains[index.row()]
            train.showTrainActionsMenu(self, event.globalPos())

    @pyqtSlot(QItemSelection, QItemSelection)
    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)
        if len(selected.indexes()) > 0:
            index = selected.indexes()[0]
            if index.isValid():
                self.trainSelected.emit(index.row())

