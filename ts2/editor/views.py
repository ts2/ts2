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

from Qt import QtCore, QtWidgets, Qt


from ts2.editor import delegates

class RoutesEditorView(QtWidgets.QTableView):
    """Table view with specific options for editing routes in the editor
    """
    def __init__(self, parent):
        """Constructor for the RoutesEditorView class"""
        super().__init__(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, \
                                       QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        self.setSizePolicy(sizePolicy)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    routeSelected = QtCore.pyqtSignal(int)

    def selectionChanged(self, selected, deselected):
        """Called when the user changes the selection. Emits the routeSelected
        signal"""
        super().selectionChanged(selected, deselected)
        index = selected.indexes()[0]
        if index.isValid():
            self.routeSelected.emit(index.data())



class TrainTypesEditorView(QtWidgets.QTableView):
    """Table view with specific options for editing trainTypes in the editor
    """
    def __init__(self, parent):
        """Constructor for the TrainTypesEditorView class"""
        super().__init__(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, \
                                       QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        self.setSizePolicy(sizePolicy)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

class PropertiesView(QtWidgets.QTableView):
    """Table view with specific options for editing track items properties in
    the editor
    """
    def __init__(self, parent):
        """Constructor for the PropertiesView class"""
        super().__init__(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, \
                                       QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        self.setSizePolicy(sizePolicy)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)


class ServicesEditorView(QtWidgets.QTableView):
    """Table view with specific options for editing services in the editor
    """
    def __init__(self, parent):
        """Constructor for the ServicesEditorView class"""
        super().__init__(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, \
                                       QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        self.setSizePolicy(sizePolicy)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    serviceSelected = QtCore.pyqtSignal(str)

    def selectionChanged(self, selected, deselected):
        """Called when the user changes the selection. Emits the
        serviceSelected signal"""
        super().selectionChanged(selected, deselected)
        index = selected.indexes()[0]
        if index.isValid():
            self.serviceSelected.emit(index.data())

class TrainsEditorView(QtWidgets.QTableView):
    """Table view with specific options for editing trains in the editor
    """
    def __init__(self, parent):
        """Constructor for the TrainsEditorView class"""
        super().__init__(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, \
                                       QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        self.setSizePolicy(sizePolicy)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        servicesDelegate = delegates.ServicesDelegate(self)
        trainTypesDelegate = delegates.TrainTypesDelegate(self)
        self.setItemDelegateForColumn(1, servicesDelegate)
        self.setItemDelegateForColumn(2, trainTypesDelegate)

    trainSelected = QtCore.pyqtSignal(int)
    trainsUnselected = QtCore.pyqtSignal()

    def selectionChanged(self, selected, deselected):
        """Called when the user changes the selection. Emits the
        trainSelected signal"""
        super().selectionChanged(selected, deselected)
        index = selected.indexes()[0]
        if index.isValid():
            self.trainSelected.emit(self.model().index(index.row(), 0).data())


class TrainsGraphicsView(QtWidgets.QGraphicsView):
    """Graphics view with specific options for editing train positions in the
    editor
    """
    def __init__(self, scene, parent):
        """Constructor for the TrainsGraphicsView class"""
        super().__init__(scene, parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, \
                                       QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        self.setInteractive(True)
        self.setRenderHint(QtWidgets.QPainter.Antialiasing, False)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setAcceptDrops(True)
        self.setBackgroundBrush(QtWidgets.QBrush(Qt.black))
        self.setSizePolicy(sizePolicy)
