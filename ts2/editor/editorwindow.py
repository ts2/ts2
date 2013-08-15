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

from PyQt4 import QtGui, QtCore, QtSql
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
        self._mainWindow = mainWindow
        
        # Editor
        self.editor = Editor(self)
        self.editor.itemSelected.connect(self.setPropertiesModel)

        # Actions
        self.newAction = QtGui.QAction(self.tr("&New"), self)
        self.newAction.setShortcut(QtGui.QKeySequence.New)
        newActionTip = self.tr("Create a new simulation")
        self.newAction.setToolTip(newActionTip)
        self.newAction.setStatusTip(newActionTip)
        self.newAction.triggered.connect(self.closeSimulation)
        
        self.openAction = QtGui.QAction(self.tr("&Open..."), self)
        self.openAction.setShortcut(QtGui.QKeySequence.Open)
        openActionTip = self.tr("Open a simulation")
        self.openAction.setToolTip(openActionTip)
        self.openAction.setStatusTip(openActionTip)
        self.openAction.triggered.connect(self.loadSimulation)
        
        self.saveAction = QtGui.QAction(self.tr("&Save"), self)
        self.saveAction.setShortcut(QtGui.QKeySequence.Save)
        saveActionTip = self.tr("Save the current simulation")
        self.saveAction.setToolTip(saveActionTip)
        self.saveAction.setStatusTip(saveActionTip)
        self.saveAction.triggered.connect(self.saveSimulation)

        self.saveAsAction = QtGui.QAction(self.tr("&Save as..."), self)
        self.saveAsAction.setShortcut(QtGui.QKeySequence.SaveAs)
        saveAsActionTip = self.tr( \
                    "Save the current simulation with a different file name")
        self.saveAsAction.setToolTip(saveAsActionTip)
        self.saveAsAction.setStatusTip(saveAsActionTip)
        self.saveAsAction.triggered.connect(self.saveAsSimulation)

        self.closeAction = QtGui.QAction(self.tr("&Close"), self)
        self.closeAction.setShortcut(QtGui.QKeySequence.Close)
        closeActionTip = self.tr("Close the editor")
        self.closeAction.setToolTip(closeActionTip)
        self.closeAction.setStatusTip(closeActionTip)
        self.closeAction.triggered.connect(self.close)
        
        self.aboutAction = QtGui.QAction(self.tr("&About TS2..."), self)
        aboutActionTip = self.tr("About TS2")
        self.aboutAction.setToolTip(aboutActionTip)
        self.aboutAction.setStatusTip(aboutActionTip)
        self.aboutAction.triggered.connect(self._mainWindow.showAboutBox)

        self.aboutQtAction = QtGui.QAction(self.tr("About Qt..."), self)
        aboutQtTip = self.tr("About Qt")
        self.aboutQtAction.setToolTip(aboutQtTip)
        self.aboutQtAction.setStatusTip(aboutQtTip)
        self.aboutQtAction.triggered.connect(QtGui.QApplication.aboutQt)

        # Menu
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeAction)
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAction)
        self.helpMenu.addAction(self.aboutQtAction)
        self.menuBar().setCursor(Qt.PointingHandCursor)
       
        # Status bar
        statusBar = QtGui.QStatusBar()
        self.setStatusBar(statusBar)
       
        # Dock Widgets
        # >> TrackItems panel: TI Library
        self.toolsPanel = QtGui.QDockWidget(self.tr("Tools"), self)
        self.toolsPanel.setFeatures( \
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
        # >> TrackItems panel: layout           
        toolBoard = QtGui.QWidget(self)
        toolGrid = QtGui.QVBoxLayout()
        toolGrid.addWidget(self._trackItemsLibraryView)
        toolGrid.setMargin(0)
        toolGrid.setSpacing(5)
        toolBoard.setLayout(toolGrid)
        self.toolsPanel.setWidget(toolBoard)
        self.addDockWidget(Qt.RightDockWidgetArea, self.toolsPanel)

        # >> Properties panel
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
        board = QtGui.QWidget(self)

        # Canvas
        self._view = QtGui.QGraphicsView(self.editor.scene, board)
        self._view.setInteractive(True)
        self._view.setRenderHint(QtGui.QPainter.Antialiasing, False)
        self._view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self._view.setAcceptDrops(True)
        self._view.setBackgroundBrush(QtGui.QBrush(Qt.black))

        # Display
        grid = QtGui.QVBoxLayout()
        grid.addWidget(self._view)
        #self.grid.addWidget(self.panel)
        grid.setMargin(0)
        grid.setSpacing(0)
        board.setLayout(grid)
        self.setCentralWidget(board)
        
        #### DEBUG
        #self.loadSimulation()

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
        
    @QtCore.pyqtSlot()
    def loadSimulation(self):
        """Loads the simulation from the database"""
        #### DEBUG 
        #fileName = "/home/nicolas/Progs/GitHub/ts2/data/drain.ts2"

        fileName = QtGui.QFileDialog.getOpenFileName(\
                           self,\
                           self.tr("Open a simulation"),\
                           QtCore.QDir.currentPath(),\
                           self.tr("TS2 simulation files (*.ts2)"))
        if fileName != "":
            self.editor.database = fileName
            self.editor.reload(fileName)
            self.setWindowTitle( \
                self.tr("ts2 - Train Signalling Simulation - Editor - %s") % \
                                                                    fileName)
    
    @QtCore.pyqtSlot()
    def saveSimulation(self):
        """Saves the simulation to the database"""
        if self.editor.database is None:
            self.saveAsSimulation()
        self.editor.save()

    @QtCore.pyqtSlot()
    def saveAsSimulation(self):
        """Saves the simulation to a different database"""
        #### DEBUG
        #fileName = "/home/nicolas/Progs/GitHub/ts2/data/drain-save.ts2"
        fileName = QtGui.QFileDialog.getSaveFileName(\
                           self,\
                           self.tr("Save the simulation as"),\
                           QtCore.QDir.currentPath(),\
                           self.tr("TS2 simulation files (*.ts2)"))
        if fileName != "":
            self.editor.database = fileName
            self.saveSimulation()

    @QtCore.pyqtSlot()
    def closeSimulation(self):
        """Closes the current simulation, and prepares for editing a new one
        """
        if self.editor.database is not None:
            if QtGui.QMessageBox.warning(self, \
                    "Simulation loaded", \
                    """The current simulation will be closed.\n
Do you want to continue?""", \
                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) \
                            == QtGui.QMessageBox.Yes:
                self.editor.initialize()


    
