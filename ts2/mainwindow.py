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
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from simulation import *
from servicelistview import ServiceListView
from trainlistview import *
from panel import *
from ressources_rc import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        MainWindow._self = self
        self.setWindowState(Qt.WindowMaximized)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle(self.tr("ts2 - Train Signalling Simulation"))
        
        # Simulation
        self.simulation = Simulation(self)
        
        # Actions
        self.openAction = QAction(self.tr("&Open..."), self)
        self.openAction.setShortcut(QKeySequence.Open)
        self.openAction.setToolTip(self.tr("Open a simulation"))
        self.openAction.triggered.connect(self.loadSimulation)
        
        self.quitAction = QAction(self.tr("&Quit"), self)
        self.quitAction.setShortcut(QKeySequence(self.tr("Ctrl+Q")))
        self.quitAction.setToolTip(self.tr("Quit TS2"))
        self.quitAction.triggered.connect(self.close)

        self.aboutAction = QAction(self.tr("&About TS2..."), self)
        self.aboutAction.setToolTip(self.tr("About TS2"))
        self.aboutAction.triggered.connect(self.showAboutBox)

        self.aboutQtAction = QAction(self.tr("About Qt..."), self)
        self.aboutQtAction.setToolTip(self.tr("About Qt"))
        self.aboutQtAction.triggered.connect(QApplication.aboutQt)

        # Menu
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAction)
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAction)
        self.helpMenu.addAction(self.aboutQtAction)
        self.menuBar().setCursor(Qt.PointingHandCursor)
        
        # Dock Widgets
        self.trainInfoPanel = QDockWidget(self.tr("Train Information"), self)
        self.trainInfoPanel.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self._trainInfoView = QTreeView(self)
        self._trainInfoView.setItemsExpandable(False)
        self._trainInfoView.setRootIsDecorated(False)
        self._trainInfoView.setModel(self.simulation.selectedTrainModel)
        self._trainInfoView.setContextMenuPolicy(Qt.CustomContextMenu)
        self._trainInfoView.customContextMenuRequested.connect(self.showContextMenu)
        self.trainInfoPanel.setWidget(self._trainInfoView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.trainInfoPanel)

        self.serviceInfoPanel = QDockWidget(self.tr("Service Information"), self)
        self.serviceInfoPanel.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self._serviceInfoView = QTreeView(self)
        self._serviceInfoView.setItemsExpandable(False)
        self._serviceInfoView.setRootIsDecorated(False)
        self._serviceInfoView.setModel(self.simulation.selectedServiceModel)
        self.serviceInfoPanel.setWidget(self._serviceInfoView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.serviceInfoPanel)

        self.placeInfoPanel = QDockWidget(self.tr("Station Information"), self)
        self.placeInfoPanel.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self._placeInfoView = QTreeView(self)
        self._placeInfoView.setItemsExpandable(False)
        self._placeInfoView.setRootIsDecorated(False)
        self._placeInfoView.setModel(Place.selectedPlaceModel)
        self.placeInfoPanel.setWidget(self._placeInfoView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.placeInfoPanel)

        self.trainListPanel = QDockWidget(self.tr("Trains"), self)
        self.trainListPanel.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self._trainListView = TrainListView(self, self.simulation)
        self.trainListPanel.setWidget(self._trainListView)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.trainListPanel)

        self.serviceListPanel = QDockWidget(self.tr("Services"), self)
        self.serviceListPanel.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self._serviceListView = ServiceListView(self, self.simulation)
        self._trainListView.trainSelected.connect(self._serviceListView.updateServiceSelection)
        self.serviceListPanel.setWidget(self._serviceListView)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.serviceListPanel)

        # board
        self.board = QWidget(self)

        # Canvas
        self._view = QGraphicsView(self.simulation.scene, self.board)
        self._view.setInteractive(True)
        self._view.setRenderHint(QPainter.Antialiasing, False)
        self._view.setDragMode(QGraphicsView.ScrollHandDrag)
        self._view.setBackgroundBrush(QBrush(Qt.black))

        # Panel
        self.panel = Panel(self.board, self.simulation);
        self.simulation.timeChanged.connect(self.panel.clock.setTime)
        self.panel.zoomChanged.connect(self.zoom)

        # Display
        self.grid = QVBoxLayout()
        self.grid.addWidget(self._view)
        self.grid.addWidget(self.panel)
        self.grid.setMargin(0)
        self.grid.setSpacing(0)
        self.board.setLayout(self.grid)
        self.setCentralWidget(self.board)
        
        # DEBUG 
        #self.loadSimulation()
 
    @property
    def trainInfoView(self):
        return self._trainInfoView

    @property
    def serviceInfoView(self):
        return self._serviceInfoView
    
    @property
    def placeInfoView(self):
        return self._placeInfoView
    
    @property
    def trainListView(self):
        return self._trainListView

    @property
    def view(self):
        return self._view

    @staticmethod
    def instance():
        return MainWindow._self
    
    @pyqtSlot()
    def loadSimulation(self):
        QSqlDatabase.database().close()
        ### DEBUG 
        #fileName = "/home/nicolas/Progs/GitHub/ts2/data/drain.ts2";

        fileName = QFileDialog.getOpenFileName(\
                           self,\
                           self.tr("Open a simulation"),\
                           QDir.currentPath(),\
                           self.tr("TS2 simulation files (*.ts2)"))
        if fileName != "":
            qDebug("Simulation loading")
            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setHostName("localhost")
            self.db.setDatabaseName(fileName)
            self.db.open()
            self.simulation.reload()
            qDebug("Simulation loaded")
    
    @pyqtSlot(int)
    def zoom(self, percent):
        self._view.setMatrix(QMatrix(percent/100, 0, 0, percent/100, 0, 0))
    
    @pyqtSlot()
    def showAboutBox(self):
        QMessageBox.about(self, "About TS2", """TS2 is a train signalling simulation.\n
Version 0.3 (beta 2)\n
Copyright 2008-2013, NPi (npi@users.sourceforge.net)
http://ts2.sourceforge.net""")

    @pyqtSlot(QPoint)
    def showContextMenu(self, pos):
        if self.sender() == self._trainInfoView:
            train = self._trainInfoView.model().train
            if train is not None:
                train.showTrainActionsMenu(self._trainInfoView, self._trainInfoView.mapToGlobal(pos))

