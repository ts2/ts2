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
from PyQt4.QtCore import Qt

from ts2 import scenery
import ts2.gui.dialogs
import ts2.editor.views


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
        self.editor = ts2.editor.Editor(self)
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
        self.trackItemsLibraryView = \
                                QtGui.QGraphicsView(self.editor.libraryScene)
        self.trackItemsLibraryView.setBackgroundBrush(QtGui.QBrush(Qt.black))
        self.trackItemsLibraryView.setInteractive(True)
        self.trackItemsLibraryView.setRenderHint( \
                                QtGui.QPainter.Antialiasing, False)
        self.trackItemsLibraryView.setDragMode( \
                                QtGui.QGraphicsView.ScrollHandDrag)
        self.trackItemsLibraryView.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # >> TrackItems panel: layout
        toolBoard = QtGui.QWidget(self)
        toolGrid = QtGui.QVBoxLayout()
        toolGrid.addWidget(self.trackItemsLibraryView)
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
        self.propertiesView = ts2.editor.views.PropertiesView(self)
        self.propertiesPanel.setWidget(self.propertiesView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.propertiesPanel)

        # Central tab widget
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.currentChanged.connect(self.showHideDockWidgets)
        self.tabWidget.currentChanged.connect(self.editor.updateContext)

        # General tab
        generalTab = QtGui.QWidget()
        titleLabel = QtGui.QLabel(self.tr("Simulation title: "), generalTab)
        self.titleTxt = QtGui.QLineEdit(generalTab)
        self.titleTxt.editingFinished.connect(self.updateTitle)
        descriptionLabel = QtGui.QLabel(self.tr("Description: "), generalTab)
        self.descriptionTxt = QtGui.QPlainTextEdit(generalTab)
        self.descriptionTxt.textChanged.connect(self.updateDescription)
        self.editor.optionsChanged.connect(self.updateGeneralTab)
        optionsLabel = QtGui.QLabel(self.tr("Options: "))
        self.optionsView = QtGui.QTableView(generalTab)
        self.optionsView.setModel(self.editor.optionsModel)
        self.editor.optionsChanged.connect(self.optionsView.model().reset)
        fgrid = QtGui.QFormLayout()
        fgrid.addRow(titleLabel, self.titleTxt)
        fgrid.addRow(descriptionLabel, self.descriptionTxt)
        fgrid.addRow(optionsLabel, self.optionsView)
        generalTab.setLayout(fgrid)
        self.tabWidget.addTab(generalTab, self.tr("General"))

        # Scenery tab
        sceneryTab = QtGui.QWidget()
        self.sceneryView = QtGui.QGraphicsView(self.editor.scene, sceneryTab)
        self.sceneryView.setInteractive(True)
        self.sceneryView.setRenderHint(QtGui.QPainter.Antialiasing, False)
        self.sceneryView.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.sceneryView.setAcceptDrops(True)
        self.sceneryView.setBackgroundBrush(QtGui.QBrush(Qt.black))
        self.editor.sceneryIsValidated.connect(\
                                    self.sceneryView.setDisabled)
        self.unlockSceneryBtn = QtGui.QPushButton(\
                                    self.tr("Unlock Scenery"), sceneryTab)
        self.unlockSceneryBtn.setEnabled(False)
        self.unlockSceneryBtn.clicked.connect(\
                                    self.editor.invalidateScenery)
        self.editor.sceneryIsValidated.connect(\
                                    self.unlockSceneryBtn.setEnabled)
        self.validateSceneryBtn = QtGui.QPushButton(\
                                    self.tr("Validate Scenery"), sceneryTab)
        self.validateSceneryBtn.clicked.connect(\
                                    self.validateSceneryBtnClicked)
        self.editor.sceneryIsValidated.connect(\
                                    self.validateSceneryBtn.setDisabled)
        self.zoomSlider = QtGui.QSlider(Qt.Horizontal, sceneryTab)
        self.zoomSlider.setRange(10, 200)
        self.zoomSlider.setValue(100)
        self.zoomSlider.valueChanged.connect(self.zoom)
        hgrid = QtGui.QHBoxLayout()
        hgrid.addWidget(self.unlockSceneryBtn)
        hgrid.addWidget(self.validateSceneryBtn)
        hgrid.addStretch()
        hgrid2 = QtGui.QHBoxLayout()
        hgrid2.addWidget(QtGui.QLabel(self.tr("Zoom: "), sceneryTab))
        hgrid2.addWidget(self.zoomSlider)
        hgrid2.addStretch()
        vgrid = QtGui.QVBoxLayout()
        vgrid.addLayout(hgrid)
        vgrid.addWidget(self.sceneryView)
        vgrid.addLayout(hgrid2)
        sceneryTab.setLayout(vgrid)
        self.tabWidget.addTab(sceneryTab, self.tr("Scenery"))

        # Routes tab
        routesTab = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        self.routesGraphicView = QtGui.QGraphicsView(self.editor.scene,
                                                     routesTab)
        self.routesGraphicView.setInteractive(True)
        self.routesGraphicView.setRenderHint(QtGui.QPainter.Antialiasing,
                                              False)
        self.routesGraphicView.setDragMode(
                                        QtGui.QGraphicsView.ScrollHandDrag)
        self.routesGraphicView.setAcceptDrops(True)
        self.routesGraphicView.setBackgroundBrush(QtGui.QBrush(Qt.black))
        self.routesGraphicView.setSizePolicy(sizePolicy)
        self.addRouteBtn = QtGui.QPushButton(
                                self.tr("Add Route"), routesTab)
        self.addRouteBtn.clicked.connect(self.addRouteBtnClicked)
        self.delRouteBtn = QtGui.QPushButton(
                                self.tr("Delete Route"), routesTab)
        self.delRouteBtn.clicked.connect(self.delRouteBtnClicked)
        hgrid = QtGui.QHBoxLayout()
        hgrid.addWidget(self.addRouteBtn)
        hgrid.addWidget(self.delRouteBtn)
        hgrid.addStretch()
        self.routesView = ts2.editor.views.RoutesEditorView(routesTab)
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
        self.tabWidget.addTab(routesTab, self.tr("Routes"))

        # Train types tab
        trainTypesTab = QtGui.QWidget()
        self.trainTypesView = ts2.editor.views.TrainTypesEditorView(
                                                                trainTypesTab)
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
        self.tabWidget.addTab(trainTypesTab, self.tr("Train types"))

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
        self.servicesView = ts2.editor.views.ServicesEditorView(servicesTab)
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
        self.tabWidget.addTab(servicesTab, self.tr("Services"))

        # Train tab
        trainsTab = QtGui.QWidget()
        self.setupTrainsBtn = QtGui.QPushButton(
                                self.tr("Setup trains from services"),
                                trainsTab)
        self.setupTrainsBtn.clicked.connect(
                                self.setupTrainsBtnClicked)

        hgride = QtGui.QHBoxLayout()
        hgride.addWidget(self.setupTrainsBtn)
        hgride.addStretch()
        self.trainsGraphicsView = ts2.editor.views.TrainsGraphicsView(
                                                self.editor.scene, trainsTab)
        self.reverseTrainBtn = QtGui.QPushButton(
                                self.tr("Reverse train direction"),
                                trainsTab)
        self.reverseTrainBtn.clicked.connect(self.reverseTrainBtnClicked)
        hgridr = QtGui.QHBoxLayout()
        hgridr.addWidget(self.reverseTrainBtn)
        hgridr.addStretch()
        self.trainsView = ts2.editor.views.TrainsEditorView(trainsTab)
        self.trainsView.setModel(self.editor.trainsModel)
        self.trainsView.trainSelected.connect(self.editor.selectTrain)
        self.trainsView.trainsUnselected.connect(self.editor.unselectTrains)
        self.editor.trainsChanged.connect(self.trainsView.model().reset)
        self.editor.trainsChanged.connect(
                                self.trainsView.resizeColumnsToContents)
        self.addTrainBtn = QtGui.QPushButton(self.tr("Add new train"),
                                             trainsTab)
        self.addTrainBtn.clicked.connect(self.addTrainBtnClicked)
        self.delTrainBtn = QtGui.QPushButton(self.tr("Remove train"),
                                             trainsTab)
        self.delTrainBtn.clicked.connect(self.delTrainBtnClicked)
        hgrid = QtGui.QHBoxLayout()
        hgrid.addWidget(self.addTrainBtn)
        hgrid.addWidget(self.delTrainBtn)
        hgrid.addStretch()
        grid = QtGui.QVBoxLayout()
        grid.addLayout(hgride)
        grid.addWidget(self.trainsGraphicsView)
        grid.addLayout(hgridr)
        grid.addWidget(self.trainsView)
        grid.addLayout(hgrid)
        trainsTab.setLayout(grid)
        self.tabWidget.addTab(trainsTab, self.tr("Trains"))

        self.setCentralWidget(self.tabWidget)


    closed = QtCore.pyqtSignal()

    def closeEvent(self, closeEvent):
        """Called when the editor window is closed. Emits the closed signal.
        """
        super().closeEvent(closeEvent)
        if closeEvent.isAccepted():
            choice = QtGui.QMessageBox.question(
                            self,
                            self.tr("Close editor"),
                            self.tr("Do you want to save your changes ?"),
                            QtGui.QMessageBox.Yes|QtGui.QMessageBox.No|
                            QtGui.QMessageBox.Cancel)
            if choice == QtGui.QMessageBox.Yes:
                self.saveSimulation()
            if choice == QtGui.QMessageBox.Yes or \
               choice == QtGui.QMessageBox.No:
                self.closed.emit()
            else:
                closeEvent.ignore()

    @QtCore.pyqtSlot(int)
    def setPropertiesModel(self, tiId):
        """Sets the TrackPropertiesModel related to trackItem on the
        properties view"""
        ti = self.editor.trackItem(tiId)
        self.propertiesView.setModel(scenery.TrackPropertiesModel(ti))

    @QtCore.pyqtSlot()
    def loadSimulation(self):
        """Loads the simulation from the database"""
        #### DEBUG
        #fileName = "/home/nicolas/Progs/GitHub/ts2/data/drain.ts2"

        fileName = QtGui.QFileDialog.getOpenFileName(
                           self,
                           self.tr("Open a simulation"),
                           QtCore.QDir.currentPath(),
                           self.tr("TS2 simulation files (*.ts2)"))
        if fileName != "":
            self.setCursor(Qt.WaitCursor)
            self.editor.database = fileName
            self.editor.reload(fileName)
            self.setWindowTitle(
                    self.tr("ts2 - Train Signalling Simulation - Editor - %s")
                    % fileName)
            self.setCursor(Qt.ArrowCursor)

    @QtCore.pyqtSlot()
    def saveSimulation(self):
        """Saves the simulation to the database"""
        if self.editor.database is None:
            self.saveAsSimulation()
        self.setCursor(Qt.WaitCursor)
        try:
            self.editor.save()
        except Exception as e:
            ts2.gui.dialogs.ExceptionDialog.popupException(self, e)
        self.setCursor(Qt.ArrowCursor)

    @QtCore.pyqtSlot()
    def saveAsSimulation(self):
        """Saves the simulation to a different database"""
        # DEBUG
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
    def updateGeneralTab(self):
        """Updates the data in the general tab with the simulation options."""
        self.titleTxt.setText(self.editor.option("title"))
        self.descriptionTxt.setPlainText(self.editor.option("description"))

    @QtCore.pyqtSlot()
    def validateSceneryBtnClicked(self):
        """Validates the scenery by calling the editor to perform the task."""
        self.setCursor(Qt.WaitCursor)
        self.editor.validateScenery()
        self.setCursor(Qt.ArrowCursor)

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

    @QtCore.pyqtSlot()
    def setupTrainsBtnClicked(self):
        """Calls the editor to setup the trains list from the services list.
        """
        if QtGui.QMessageBox.warning(
                        self,
                        self.tr("Setup trains"),
                        self.tr("This will erase any existing train, and will"
                                " create a train for each service that do not"
                                " follow another one.\n"
                                "Are you sure you want to continue?"),
                        QtGui.QMessageBox.Yes|QtGui.QMessageBox.No
                                        ) == QtGui.QMessageBox.Yes:
            self.editor.setupTrainsFromServices()

    @QtCore.pyqtSlot()
    def reverseTrainBtnClicked(self):
        """Calls the editor to reverse the train direction (in fact the
        its trainHead direction)"""
        self.editor.reverseSelectedTrain()

    @QtCore.pyqtSlot()
    def addTrainBtnClicked(self):
        """Adds an empty train to the editor"""
        self.editor.addTrain()

    @QtCore.pyqtSlot()
    def delTrainBtnClicked(self):
        """Removes the currently selected train"""
        rows = self.trainsView.selectionModel().selectedRows()
        if len(rows) != 0:
            row = rows[0].row()
            if QtGui.QMessageBox.question(
                        self,
                        self.tr("Delete train"),
                        self.tr("Are you sure you want "
                                "to delete train %i?") % row,
                        QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) \
                                == QtGui.QMessageBox.Yes:
                self.editor.deleteTrain(row)

    @QtCore.pyqtSlot()
    def updateTitle(self):
        """Updates the title in the options hash when input is modified."""
        self.editor.setOption("title", self.titleTxt.text())

    @QtCore.pyqtSlot()
    def updateDescription(self):
        """Updates the description in the options hash when input is modified.
        """
        self.editor.setOption("description",
                              self.descriptionTxt.toPlainText())

    @QtCore.pyqtSlot(int)
    def zoom(self, percent):
        self.sceneryView.setMatrix(QtGui.QMatrix(percent/100, 0, 0,
                                                 percent/100, 0, 0))


