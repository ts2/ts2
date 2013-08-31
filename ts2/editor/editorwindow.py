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
from ts2.editor import Editor, RoutesEditorView, TrainTypesEditorView, \
    ServicesEditorView
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

        # Central tab widget
        self._tabWidget = QtGui.QTabWidget(self)
        self._tabWidget.currentChanged.connect(self.showHideDockWidgets)
        self._tabWidget.currentChanged.connect(self.editor.updateContext)

        # General tab
        widget = QtGui.QWidget()
        self._tabWidget.addTab(widget, self.tr("General"))

        # Scenery tab
        sceneryTab = QtGui.QWidget()
        self._sceneryView = QtGui.QGraphicsView(self.editor.scene, sceneryTab)
        self._sceneryView.setInteractive(True)
        self._sceneryView.setRenderHint(QtGui.QPainter.Antialiasing, False)
        self._sceneryView.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self._sceneryView.setAcceptDrops(True)
        self._sceneryView.setBackgroundBrush(QtGui.QBrush(Qt.black))
        self.editor.sceneryIsValidated.connect(\
                                    self._sceneryView.setDisabled)
        self._unlockSceneryBtn = QtGui.QPushButton(\
                                    self.tr("Unlock Scenery"), sceneryTab)
        self._unlockSceneryBtn.setEnabled(False)
        self._unlockSceneryBtn.clicked.connect(\
                                    self.editor.invalidateScenery)
        self.editor.sceneryIsValidated.connect(\
                                    self._unlockSceneryBtn.setEnabled)
        self._validateSceneryBtn = QtGui.QPushButton(\
                                    self.tr("Validate Scenery"), sceneryTab)
        self._validateSceneryBtn.clicked.connect(\
                                    self.editor.validateScenery)
        self.editor.sceneryIsValidated.connect(\
                                    self._validateSceneryBtn.setDisabled)
        hgrid = QtGui.QHBoxLayout()
        hgrid.addWidget(self._unlockSceneryBtn)
        hgrid.addWidget(self._validateSceneryBtn)
        hgrid.addStretch()
        vgrid = QtGui.QVBoxLayout()
        vgrid.addLayout(hgrid)
        vgrid.addWidget(self._sceneryView)
        sceneryTab.setLayout(vgrid)
        self._tabWidget.addTab(sceneryTab, self.tr("Scenery"))
        
        # Routes tab
        routesTab = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, \
                                       QtGui.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        self.routesGraphicView = QtGui.QGraphicsView(self.editor.scene, \
                                                      routesTab)
        self.routesGraphicView.setInteractive(True)
        self.routesGraphicView.setRenderHint(QtGui.QPainter.Antialiasing, \
                                              False)
        self.routesGraphicView.setDragMode( \
                                        QtGui.QGraphicsView.ScrollHandDrag)
        self.routesGraphicView.setAcceptDrops(True)
        self.routesGraphicView.setBackgroundBrush(QtGui.QBrush(Qt.black))
        self.routesGraphicView.setSizePolicy(sizePolicy)
        self.addRouteBtn = QtGui.QPushButton(\
                                self.tr("Add Route"), routesTab)
        self.addRouteBtn.clicked.connect(self.addRouteBtnClicked)
        self.delRouteBtn = QtGui.QPushButton(
                                self.tr("Delete Route"), routesTab)
        self.delRouteBtn.clicked.connect(self.delRouteBtnClicked)
        hgrid = QtGui.QHBoxLayout()
        hgrid.addWidget(self.addRouteBtn)
        hgrid.addWidget(self.delRouteBtn)
        hgrid.addStretch()
        self.routesView = RoutesEditorView(routesTab)
        self.routesView.setModel(self.editor.routesModel)
        self.routesView.routeSelected.connect(self.editor.selectRoute)
        self.editor.routesChanged.connect(self.routesView.model().reset)
        grid = QtGui.QVBoxLayout()
        grid.addWidget(self.routesGraphicView)
        grid.addLayout(hgrid)
        grid.addWidget(self.routesView)
        routesTab.setLayout(grid)
        routesTab.setEnabled(False)
        self.editor.sceneryIsValidated.connect(routesTab.setEnabled)
        self._tabWidget.addTab(routesTab, self.tr("Routes"))
        
        # Train types tab
        trainTypesTab = QtGui.QWidget()
        self.trainTypesView = TrainTypesEditorView(trainTypesTab)
        self.trainTypesView.setModel(self.editor.trainTypesModel)
        self.editor.trainTypesChanged.connect( \
                                self.trainTypesView.model().reset)
        self.editor.trainTypesChanged.connect( \
                                self.trainTypesView.resizeColumnsToContents)
        self.addTrainTypeBtn = QtGui.QPushButton( \
                                self.tr("Add new train type"), trainTypesTab)
        self.addTrainTypeBtn.clicked.connect(self.addTrainTypeBtnClicked)
        self.delTrainTypeBtn = QtGui.QPushButton( \
                                self.tr("Remove train type"), trainTypesTab)
        self.delTrainTypeBtn.clicked.connect(self.delTrainTypeBtnClicked)
        hgrid = QtGui.QHBoxLayout()
        hgrid.addWidget(self.addTrainTypeBtn)
        hgrid.addWidget(self.delTrainTypeBtn)
        hgrid.addStretch()
        grid = QtGui.QVBoxLayout()
        grid.addWidget(self.trainTypesView)
        grid.addLayout(hgrid)
        trainTypesTab.setLayout(grid)
        self._tabWidget.addTab(trainTypesTab, self.tr("Train types"))
        
        # Services tab
        servicesTab = QtGui.QWidget()
        self.exportServicesBtn = QtGui.QPushButton(
                                self.tr("Export services as CSV file..."), 
                                servicesTab)
        self.exportServicesBtn.clicked.connect(
                                self.exportServicesBtnClicked)
        self.importServicesBtn = QtGui.QPushButton(
                                self.tr("Import services from CSV file..."), 
                                servicesTab)
        self.importServicesBtn.clicked.connect(
                                self.importServicesBtnClicked)
        hgride = QtGui.QHBoxLayout()
        hgride.addWidget(self.exportServicesBtn)
        hgride.addWidget(self.importServicesBtn)
        hgride.addStretch()
        self.servicesView = ServicesEditorView(servicesTab)
        self.servicesView.setModel(self.editor.servicesModel)
        self.editor.servicesChanged.connect(self.servicesView.model().reset)
        self.editor.servicesChanged.connect( 
                                self.servicesView.resizeColumnsToContents)
        self.addServiceBtn = QtGui.QPushButton( 
                                self.tr("Add new service"), servicesTab)
        self.addServiceBtn.clicked.connect( 
                                self.addServiceBtnClicked)
        self.delServiceBtn = QtGui.QPushButton( 
                                self.tr("Remove service"), servicesTab)
        self.delServiceBtn.clicked.connect( 
                                self.delServiceBtnClicked)
        hgrids = QtGui.QHBoxLayout()
        hgrids.addWidget(self.addServiceBtn)
        hgrids.addWidget(self.delServiceBtn)
        hgrids.addStretch()
        self.serviceLinesView = QtGui.QTableView()
        self.serviceLinesView.setSelectionBehavior( 
                                QtGui.QAbstractItemView.SelectRows)
        self.serviceLinesView.setSelectionMode( 
                                QtGui.QAbstractItemView.SingleSelection)
        self.serviceLinesView.setModel(self.editor.serviceLinesModel)
        self.servicesView.serviceSelected.connect(
                                self.editor.serviceLinesModel.setServiceCode)
        self.editor.serviceLinesChanged.connect( 
                                self.serviceLinesView.model().reset)
        self.editor.serviceLinesChanged.connect( 
                                self.serviceLinesView.resizeColumnsToContents)
        self.appendServiceLineBtn = QtGui.QPushButton( 
                                self.tr("Append new line"), servicesTab)
        self.appendServiceLineBtn.clicked.connect(
                                self.appendServiceLineBtnClicked)
        self.insertServiceLineBtn = QtGui.QPushButton( 
                                self.tr("Insert new line"), servicesTab)
        self.insertServiceLineBtn.clicked.connect(
                                self.insertServiceLineBtnClicked)
        self.delServiceLineBtn = QtGui.QPushButton( 
                                self.tr("Remove line"), servicesTab)
        self.delServiceLineBtn.clicked.connect(
                                self.delServiceLineBtnClicked)
        hgridl = QtGui.QHBoxLayout()
        hgridl.addWidget(self.appendServiceLineBtn)
        hgridl.addWidget(self.insertServiceLineBtn)
        hgridl.addWidget(self.delServiceLineBtn)
        hgridl.addStretch()
        grid = QtGui.QVBoxLayout()
        grid.addLayout(hgride)
        grid.addWidget(self.servicesView)
        grid.addLayout(hgrids)
        grid.addWidget(self.serviceLinesView)
        grid.addLayout(hgridl)
        servicesTab.setLayout(grid)
        self._tabWidget.addTab(servicesTab, self.tr("Services"))
        
        # Train tab
        trainsTab = QtGui.QWidget()
        self._trainsView = QtGui.QTableView(trainsTab)
        grid = QtGui.QVBoxLayout()
        grid.addWidget(self._trainsView)
        trainsTab.setLayout(grid)
        self._tabWidget.addTab(trainsTab, self.tr("Trains"))
        
        self.setCentralWidget(self._tabWidget)
        
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
        fileName = "/home/nicolas/Progs/GitHub/ts2/data/drain.ts2"

        #fileName = QtGui.QFileDialog.getOpenFileName(
                           #self,
                           #self.tr("Open a simulation"),
                           #QtCore.QDir.currentPath(),
                           #self.tr("TS2 simulation files (*.ts2)"))
        if fileName != "":
            self.editor.database = fileName
            self.editor.reload(fileName)
            self.setWindowTitle(
                    self.tr("ts2 - Train Signalling Simulation - Editor - %s") 
                    % fileName)
    
    @QtCore.pyqtSlot()
    def saveSimulation(self):
        """Saves the simulation to the database"""
        if self.editor.database is None:
            self.saveAsSimulation()
        self.setCursor(Qt.WaitCursor)
        self.editor.save()
        self.setCursor(Qt.ArrowCursor)

    @QtCore.pyqtSlot()
    def saveAsSimulation(self):
        """Saves the simulation to a different database"""
        #### DEBUG
        #fileName = "/home/nicolas/Progs/GitHub/ts2/data/drain-save.ts2"
        fileName = QtGui.QFileDialog.getSaveFileName(
                           self,
                           self.tr("Save the simulation as"),
                           QtCore.QDir.currentPath(),
                           self.tr("TS2 simulation files (*.ts2)"))
        if fileName != "":
            self.editor.database = fileName
            self.saveSimulation()

    @QtCore.pyqtSlot()
    def closeSimulation(self):
        """Closes the current simulation, and prepares for editing a new one
        """
        if self.editor.database is not None:
            if QtGui.QMessageBox.warning(
                    self, 
                    self.tr("Simulation loaded"), 
                    self.tr("The current simulation will be closed.\n"
                            "Do you want to continue?"), 
                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) \
                            == QtGui.QMessageBox.Yes:
                self.editor.initialize()

    @QtCore.pyqtSlot(int)
    def showHideDockWidgets(self, index):
        """Hides or Show the dock widgets depending on the selected tab"""
        if index == 1:
            # Scenery panel
            self.toolsPanel.show()
            self.propertiesPanel.show()
        else:
            self.toolsPanel.hide()
            self.propertiesPanel.hide()
        
    @QtCore.pyqtSlot()
    def delRouteBtnClicked(self):
        """Deletes the selected route in routesView when the delete route
        button is clicked."""
        rows = self.routesView.selectionModel().selectedRows()
        if len(rows) != 0:
            row = rows[0]
            routeNum = self.routesView.model().data(row, 0)
            if QtGui.QMessageBox.question( 
                        self, 
                        self.tr("Delete route"), 
                        self.tr("Are you sure you want " 
                                "to delete route %i?") % routeNum, 
                        QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) \
                                == QtGui.QMessageBox.Yes:
                self.editor.deleteRoute(routeNum)
        
    @QtCore.pyqtSlot()
    def addRouteBtnClicked(self):
        """Adds a route in routesView when the add route button is clicked."""
        if not self.editor.addRoute():
            QtGui.QMessageBox.warning( 
                        self, 
                        self.tr("Add route"), 
                        self.tr("No route added:\n"
                                "No route selected or a route between "
                                "these two signals already exists."))
                        
    @QtCore.pyqtSlot()
    def addTrainTypeBtnClicked(self):
        """Adds an empty stock type to the editor"""
        code, ok = QtGui.QInputDialog.getText( 
                        self, 
                        self.tr("Add train type"), 
                        self.tr("Enter new train type code:"))
        if ok:
            if code not in self.editor.trainTypes:
                self.editor.addTrainType(code)
            else:
                QtGui.QMessageBox.warning( 
                            self, 
                            self.tr("Add train type"), 
                            self.tr("Unable to add train type: \n"
                                    "This train type code already exists."))
    
    @QtCore.pyqtSlot()
    def delTrainTypeBtnClicked(self):
        """Removes the currently selected stock type from the simulation"""
        rows = self.trainTypesView.selectionModel().selectedRows()
        if len(rows) != 0:
            row = rows[0]
            code = self.trainTypesView.model().data(row, 0)
            if QtGui.QMessageBox.question( 
                        self, 
                        self.tr("Delete train type"), 
                        self.tr("Are you sure you want " 
                                "to delete train type %s?") % code, 
                        QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) \
                                == QtGui.QMessageBox.Yes:
                self.editor.deleteTrainType(code)
        
    @QtCore.pyqtSlot()
    def addServiceBtnClicked(self):
        """Adds an empty service to the editor"""
        code, ok = QtGui.QInputDialog.getText( 
                        self, 
                        self.tr("Add service"), 
                        self.tr("Enter new service code:"))
        if ok:
            if code not in self.editor.services:
                self.editor.addService(code)
            else:
                QtGui.QMessageBox.warning( 
                            self, 
                            self.tr("Add service"), 
                            self.tr("Unable to add service: \n"
                                    "This service code already exists."))
    
    @QtCore.pyqtSlot()
    def delServiceBtnClicked(self):
        """Removes the currently selected service from the simulation"""
        rows = self.servicesView.selectionModel().selectedRows()
        if len(rows) != 0:
            row = rows[0]
            code = self.servicesView.model().data(row, 0)
            if QtGui.QMessageBox.question( 
                        self, 
                        self.tr("Delete service"), 
                        self.tr("Are you sure you want " 
                                "to delete service %s?") % code, 
                        QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) \
                                == QtGui.QMessageBox.Yes:
                self.editor.deleteService(code)
        
    @QtCore.pyqtSlot()
    def appendServiceLineBtnClicked(self):
        """Appends a service line to this service at the end of the list"""
        service = self.serviceLinesView.model().service
        index = self.serviceLinesView.model().rowCount()
        self.editor.addServiceLine(service, index)
    
    @QtCore.pyqtSlot()
    def insertServiceLineBtnClicked(self):
        """Add a service line to this service after the currently selected"""
        service = self.serviceLinesView.model().service
        index = 0
        if len(service.lines) != 0:
            rows = self.serviceLinesView.selectionModel().selectedRows()
            if len(rows) != 0:
                index = rows[0].row()
        self.editor.addServiceLine(service, index)
    
    @QtCore.pyqtSlot()
    def delServiceLineBtnClicked(self):
        """Removes the currently selected service line of this service"""
        service = self.serviceLinesView.model().service
        rows = self.serviceLinesView.selectionModel().selectedRows()
        if len(rows) != 0:
            row = rows[0]
            code = self.serviceLinesView.model().data(row, 0)
            if QtGui.QMessageBox.question( 
                                self, 
                                self.tr("Delete service"), 
                                self.tr("Are you sure you want " 
                                        "to delete the line at %s?") % code, 
                                QtGui.QMessageBox.Yes|QtGui.QMessageBox.No
                                         ) == QtGui.QMessageBox.Yes:
                self.editor.deleteServiceLine(service, row.row())
    
    @QtCore.pyqtSlot()
    def importServicesBtnClicked(self):
        """Calls an open file dialog for the user to select the file to import
        services from and asks the editor to actually do the import"""
        
        # ### DEBUG
        #fileName = "/home/nicolas/drain.csv"
        
        fileName = QtGui.QFileDialog.getOpenFileName(
                                self,
                                self.tr("Import services"),
                                QtCore.QDir.currentPath(),
                                self.tr("CSV files (*.csv)"))
        if fileName != "":
            if QtGui.QMessageBox.warning(
                            self,
                            self.tr("Import services"),
                            self.tr("This will erase any existing service\n"
                                    "Are you sure you want to continue?"),
                            QtGui.QMessageBox.Yes|QtGui.QMessageBox.No
                                         ) == QtGui.QMessageBox.Yes:
                self.editor.importServicesFromFile(fileName)
    
    @QtCore.pyqtSlot()
    def exportServicesBtnClicked(self):
        """Calls a save file dialog for the user to give the filanme to which
        to export the services and asks the editor to actually do the export.
        """
        fileName = QtGui.QFileDialog.getSaveFileName(
                                self,
                                self.tr("Export services"),
                                QtCore.QDir.currentPath(),
                                self.tr("CSV files (*.csv)"))
        if fileName != "":
            self.editor.exportServicesToFile(fileName)


