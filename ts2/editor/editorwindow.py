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
from PyQt4.Qt import Qt
from ts2.editor import Editor
from ts2.scenery import TrackItem, TrackPropertiesModel

class EditorWindow(QtGui.QMainWindow):
    """The EditorWindow class holds the main window of the editor"""
    
    def __init__(self, mainWindow):
        """Constructor for the EditorWindow class"""
        super().__init__(mainWindow)
        self.setGeometry(100, 100, 1024, 768)
        self.setWindowTitle( \
                        self.tr("ts2 - Train Signalling Simulation - Editor"))
        
        # Editor
        self.editor = Editor(self)
        self.editor.itemSelected.connect(self.setPropertiesModel)
        
        # Dock Widgets
        self.trackItemsPanel = QtGui.QDockWidget(self.tr("Track items"), self)
        self.trackItemsPanel.setFeatures( \
                                QtGui.QDockWidget.DockWidgetMovable| \
                                QtGui.QDockWidget.DockWidgetFloatable)
        self._trackItemsLibraryView = \
                                QtGui.QGraphicsView(self.editor.libraryScene)
        self._trackItemsLibraryView.setBackgroundBrush(QtGui.QBrush(Qt.black))
        self._trackItemsLibraryView.setInteractive(True)
        self._trackItemsLibraryView.setRenderHint( \
                                QtGui.QPainter.Antialiasing, False)
        self._trackItemsLibraryView.setDragMode( \
                                QtGui.QGraphicsView.ScrollHandDrag)
        self._trackItemsLibraryView.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.trackItemsPanel.setWidget(self._trackItemsLibraryView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.trackItemsPanel)

        self.propertiesPanel = QtGui.QDockWidget(self.tr("Properties"), self)
        self.propertiesPanel.setFeatures(
                                    QtGui.QDockWidget.DockWidgetMovable| \
                                    QtGui.QDockWidget.DockWidgetFloatable)
        self._propertiesView = QtGui.QTreeView(self)
        self._propertiesView.setItemsExpandable(False)
        self._propertiesView.setRootIsDecorated(False)
        self._propertiesView.setHeaderHidden(False)
        self.propertiesPanel.setWidget(self._propertiesView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.propertiesPanel)

        # board
        self.board = QtGui.QWidget(self)

        # Canvas
        self._view = QtGui.QGraphicsView(self.editor.scene, self.board)
        self._view.setInteractive(True)
        self._view.setRenderHint(QtGui.QPainter.Antialiasing, False)
        self._view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self._view.setAcceptDrops(True)
        self._view.setBackgroundBrush(QtGui.QBrush(Qt.black))

        # Display
        self.grid = QtGui.QVBoxLayout()
        self.grid.addWidget(self._view)
        #self.grid.addWidget(self.panel)
        self.grid.setMargin(0)
        self.grid.setSpacing(0)
        self.board.setLayout(self.grid)
        self.setCentralWidget(self.board)

    closed = QtCore.pyqtSignal()
    
    def closeEvent(self, closeEvent):
        """Called when the editor window is closed. Emits the closed signal.
        """
        super().closeEvent(closeEvent)
        if closeEvent.isAccepted():
            self.closed.emit()

    @QtCore.pyqtSlot(int)
    def setPropertiesModel(self, tiId):
        """Sets the TrackPropertiesModel related to trackItem on the 
        properties view"""
        ti = self.editor.trackItem(tiId)
        self._propertiesView.setModel(TrackPropertiesModel(ti))
