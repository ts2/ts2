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

from Qt import QtGui, QtCore, QtWidgets, Qt

from ts2 import scenery
from ts2.editor import editor
from ts2.gui import widgets
import ts2.editor.views



class EditorWindow(QtWidgets.QMainWindow):
    """The EditorWindow class holds the main window of the editor"""

    def __init__(self, mainWindow):
        """Constructor for the EditorWindow class"""
        super().__init__(mainWindow)
        self.setGeometry(100, 100, 1024, 768)
        self.setWindowTitle(
            self.tr("ts2 - Train Signalling Simulation - Editor"))
        self._mainWindow = mainWindow

        # Editor
        self.editor = editor.Editor()
        self.editor.initialize(self)

        # Actions
        self.newAction = QtWidgets.QAction(self.tr("&New"), self)
        self.newAction.setShortcut(QtGui.QKeySequence.New)
        newActionTip = self.tr("Create a new simulation")
        self.newAction.setToolTip(newActionTip)
        self.newAction.setStatusTip(newActionTip)
        self.newAction.triggered.connect(self.closeSimulation)

        self.openAction = QtWidgets.QAction(self.tr("&Open..."), self)
        self.openAction.setShortcut(QtGui.QKeySequence.Open)
        openActionTip = self.tr("Open a simulation")
        self.openAction.setToolTip(openActionTip)
        self.openAction.setStatusTip(openActionTip)
        self.openAction.triggered.connect(self.loadSimulation)

        self.saveAction = QtWidgets.QAction(self.tr("&Save"), self)
        self.saveAction.setShortcut(QtGui.QKeySequence.Save)
        saveActionTip = self.tr("Save the current simulation")
        self.saveAction.setToolTip(saveActionTip)
        self.saveAction.setStatusTip(saveActionTip)
        self.saveAction.triggered.connect(self.saveSimulation)

        self.saveAsAction = QtWidgets.QAction(self.tr("&Save as..."), self)
        self.saveAsAction.setShortcut(QtGui.QKeySequence.SaveAs)
        saveAsActionTip = self.tr(
            "Save the current simulation with a different file name")
        self.saveAsAction.setToolTip(saveAsActionTip)
        self.saveAsAction.setStatusTip(saveAsActionTip)
        self.saveAsAction.triggered.connect(self.saveAsSimulation)

        self.closeAction = QtWidgets.QAction(self.tr("&Close"), self)
        self.closeAction.setShortcut(QtGui.QKeySequence.Close)
        closeActionTip = self.tr("Close the editor")
        self.closeAction.setToolTip(closeActionTip)
        self.closeAction.setStatusTip(closeActionTip)
        self.closeAction.triggered.connect(self.close)

        self.panToolAction = QtWidgets.QAction(self.tr("&Pan tool"), self)
        panToolActionTip = self.tr("Set the pan tool")
        self.panToolAction.setToolTip(panToolActionTip)
        self.panToolAction.setStatusTip(panToolActionTip)
        self.panToolAction.setCheckable(True)
        self.panToolAction.triggered.connect(self.setPanTool)

        self.selectionToolAction = QtWidgets.QAction(self.tr("&Selection tool"),
                                                     self)
        selectionToolActionTip = self.tr("Set the selection tool")
        self.selectionToolAction.setToolTip(selectionToolActionTip)
        self.selectionToolAction.setStatusTip(selectionToolActionTip)
        self.selectionToolAction.setCheckable(True)
        self.selectionToolAction.triggered.connect(self.setSelectionTool)

        self.toolActions = QtWidgets.QActionGroup(self)
        self.toolActions.addAction(self.panToolAction)
        self.toolActions.addAction(self.selectionToolAction)
        self.panToolAction.setChecked(True)

        self.copyAction = QtWidgets.QAction(self.tr("&Copy"), self)
        self.copyAction.setShortcut(QtGui.QKeySequence.Copy)
        copyActionTip = self.tr("Copy the current selection to the clipboard")
        self.copyAction.setToolTip(copyActionTip)
        self.copyAction.setStatusTip(copyActionTip)
        self.copyAction.triggered.connect(self.copyItems)

        self.pasteAction = QtWidgets.QAction(self.tr("&Paste"), self)
        self.pasteAction.setShortcut(QtGui.QKeySequence.Paste)
        pasteActionTip = self.tr("Paste the items of the clipboard")
        self.pasteAction.setToolTip(pasteActionTip)
        self.pasteAction.setStatusTip(pasteActionTip)
        self.pasteAction.triggered.connect(self.pasteItems)

        self.deleteAction = QtWidgets.QAction(self.tr("&Delete"), self)
        self.deleteAction.setShortcut(QtGui.QKeySequence.Delete)
        deleteActionTip = self.tr("Delete the selected items")
        self.deleteAction.setToolTip(deleteActionTip)
        self.deleteAction.setStatusTip(deleteActionTip)
        self.deleteAction.triggered.connect(self.deleteItems)

        self.selectAllAction = QtWidgets.QAction(self.tr("&Select All"), self)
        self.selectAllAction.setShortcut(QtGui.QKeySequence.SelectAll)
        selectAllActionTip = self.tr("Select all the items")
        self.selectAllAction.setToolTip(selectAllActionTip)
        self.selectAllAction.setStatusTip(selectAllActionTip)
        self.selectAllAction.triggered.connect(self.selectAll)

        self.aboutAction = QtWidgets.QAction(self.tr("&About TS2..."), self)
        aboutActionTip = self.tr("About TS2")
        self.aboutAction.setToolTip(aboutActionTip)
        self.aboutAction.setStatusTip(aboutActionTip)
        self.aboutAction.triggered.connect(self._mainWindow.showAboutBox)

        self.aboutQtAction = QtWidgets.QAction(self.tr("About Qt..."), self)
        aboutQtTip = self.tr("About Qt")
        self.aboutQtAction.setToolTip(aboutQtTip)
        self.aboutQtAction.setStatusTip(aboutQtTip)
        self.aboutQtAction.triggered.connect(QtWidgets.QApplication.aboutQt)

        # Menu
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeAction)
        self.editMenu = self.menuBar().addMenu(self.tr("&Edit"))
        self.editMenu.addAction(self.panToolAction)
        self.editMenu.addAction(self.selectionToolAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.copyAction)
        self.editMenu.addAction(self.pasteAction)
        self.editMenu.addAction(self.deleteAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.selectAllAction)
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAction)
        self.helpMenu.addAction(self.aboutQtAction)
        self.menuBar().setCursor(Qt.PointingHandCursor)
        self.updateMenus(0)

        # Status bar
        statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(statusBar)

        # Dock Widgets
        # >> TrackItems panel: TI Library
        self.toolsPanel = QtWidgets.QDockWidget(self.tr("Tools"), self)
        self.toolsPanel.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable
        )
        self.trackItemsLibraryView = QtWidgets.QGraphicsView(self)
        self.trackItemsLibraryView.setBackgroundBrush(QtGui.QBrush(Qt.black))
        self.trackItemsLibraryView.setInteractive(True)
        self.trackItemsLibraryView.setRenderHint(QtGui.QPainter.Antialiasing,
                                                 False)
        self.trackItemsLibraryView.setDragMode(
            QtWidgets.QGraphicsView.ScrollHandDrag
        )
        self.trackItemsLibraryView.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # >> TrackItems panel: layout
        toolBoard = QtWidgets.QWidget(self)
        toolGrid = QtWidgets.QVBoxLayout()
        toolGrid.addWidget(self.trackItemsLibraryView)
        toolGrid.setSpacing(5)
        toolBoard.setLayout(toolGrid)
        self.toolsPanel.setWidget(toolBoard)
        self.addDockWidget(Qt.RightDockWidgetArea, self.toolsPanel)

        # >> Properties panel
        self.propertiesPanel = QtWidgets.QDockWidget(self.tr("Properties"),
                                                     self)
        self.propertiesPanel.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable
        )
        self.propertiesView = ts2.editor.views.PropertiesView(self)
        self.propertiesPanel.setWidget(self.propertiesView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.propertiesPanel)

        # Central tab widget
        self.tabWidget = QtWidgets.QTabWidget(self)

        # General tab
        generalTab = QtWidgets.QWidget()
        titleLabel = QtWidgets.QLabel(self.tr("Simulation title: "),
                                      generalTab)
        self.titleTxt = QtWidgets.QLineEdit(generalTab)
        self.titleTxt.editingFinished.connect(self.updateTitle)
        descriptionLabel = QtWidgets.QLabel(self.tr("Description: "),
                                            generalTab)
        self.descriptionTxt = QtWidgets.QPlainTextEdit(generalTab)
        self.descriptionTxt.textChanged.connect(self.updateDescription)
        optionsLabel = QtWidgets.QLabel(self.tr("Options: "))
        self.optionsView = QtWidgets.QTableView(generalTab)
        fgrid = QtWidgets.QFormLayout()
        fgrid.addRow(titleLabel, self.titleTxt)
        fgrid.addRow(descriptionLabel, self.descriptionTxt)
        fgrid.addRow(optionsLabel, self.optionsView)
        generalTab.setLayout(fgrid)
        self.tabWidget.addTab(generalTab, self.tr("General"))

        # Scenery tab
        sceneryTab = QtWidgets.QWidget()
        self.sceneryView = QtWidgets.QGraphicsView(sceneryTab)
        self.sceneryView.setInteractive(True)
        self.sceneryView.setRenderHint(QtGui.QPainter.Antialiasing, False)
        self.sceneryView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.sceneryView.setAcceptDrops(True)
        self.sceneryView.setBackgroundBrush(QtGui.QBrush(Qt.black))
        self.unlockSceneryBtn = QtWidgets.QPushButton(self.tr("Unlock Scenery"),
                                                      sceneryTab)
        self.unlockSceneryBtn.setEnabled(False)
        self.validateSceneryBtn = QtWidgets.QPushButton(
            self.tr("Validate Scenery"), sceneryTab
        )
        self.validateSceneryBtn.clicked.connect(self.validateSceneryBtnClicked)
        self.zoomWidget = widgets.ZoomWidget(sceneryTab)
        self.zoomWidget.valueChanged.connect(self.zoom)
        hgrid = QtWidgets.QHBoxLayout()
        hgrid.addWidget(self.unlockSceneryBtn)
        hgrid.addWidget(self.validateSceneryBtn)
        hgrid.addStretch()
        hgrid2 = QtWidgets.QHBoxLayout()
        hgrid2.addWidget(self.zoomWidget)
        hgrid2.addStretch()
        vgrid = QtWidgets.QVBoxLayout()
        vgrid.addLayout(hgrid)
        vgrid.addWidget(self.sceneryView)
        vgrid.addLayout(hgrid2)
        sceneryTab.setLayout(vgrid)
        self.tabWidget.addTab(sceneryTab, self.tr("Scenery"))

        # Routes tab
        routesTab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        self.routesGraphicView = QtWidgets.QGraphicsView(routesTab)
        self.routesGraphicView.setInteractive(True)
        self.routesGraphicView.setRenderHint(QtGui.QPainter.Antialiasing,
                                             False)
        self.routesGraphicView.setDragMode(
            QtWidgets.QGraphicsView.ScrollHandDrag
        )
        self.routesGraphicView.setAcceptDrops(True)
        self.routesGraphicView.setBackgroundBrush(QtGui.QBrush(Qt.black))
        self.routesGraphicView.setSizePolicy(sizePolicy)
        self.addRouteBtn = QtWidgets.QPushButton(self.tr("Add Route"),
                                                 routesTab)
        self.addRouteBtn.clicked.connect(self.addRouteBtnClicked)
        self.delRouteBtn = QtWidgets.QPushButton(self.tr("Delete Route"),
                                                 routesTab)
        self.delRouteBtn.clicked.connect(self.delRouteBtnClicked)
        hgrid = QtWidgets.QHBoxLayout()
        hgrid.addWidget(self.addRouteBtn)
        hgrid.addWidget(self.delRouteBtn)
        hgrid.addStretch()
        self.routesView = ts2.editor.views.RoutesEditorView(routesTab)
        grid = QtWidgets.QVBoxLayout()
        grid.addWidget(self.routesGraphicView)
        grid.addLayout(hgrid)
        grid.addWidget(self.routesView)
        routesTab.setLayout(grid)
        routesTab.setEnabled(False)
        self.tabWidget.addTab(routesTab, self.tr("Routes"))
        self.routesTab = routesTab

        # Train types tab
        trainTypesTab = QtWidgets.QWidget()
        self.trainTypesView = \
            ts2.editor.views.TrainTypesEditorView(trainTypesTab)
        self.addTrainTypeBtn = QtWidgets.QPushButton(
            self.tr("Add new train type"), trainTypesTab
        )
        self.addTrainTypeBtn.clicked.connect(self.addTrainTypeBtnClicked)
        self.delTrainTypeBtn = QtWidgets.QPushButton(
            self.tr("Remove train type"), trainTypesTab
        )
        self.delTrainTypeBtn.clicked.connect(self.delTrainTypeBtnClicked)
        hgrid = QtWidgets.QHBoxLayout()
        hgrid.addWidget(self.addTrainTypeBtn)
        hgrid.addWidget(self.delTrainTypeBtn)
        hgrid.addStretch()
        grid = QtWidgets.QVBoxLayout()
        grid.addWidget(self.trainTypesView)
        grid.addLayout(hgrid)
        trainTypesTab.setLayout(grid)
        self.tabWidget.addTab(trainTypesTab, self.tr("Train types"))

        # Services tab
        servicesTab = QtWidgets.QWidget()
        self.exportServicesBtn = QtWidgets.QPushButton(
            self.tr("Export services as CSV file..."),
            servicesTab
        )
        self.exportServicesBtn.clicked.connect(self.exportServicesBtnClicked)
        self.importServicesBtn = QtWidgets.QPushButton(
            self.tr("Import services from CSV file..."),
            servicesTab
        )
        self.importServicesBtn.clicked.connect(self.importServicesBtnClicked)
        hgride = QtWidgets.QHBoxLayout()
        hgride.addWidget(self.exportServicesBtn)
        hgride.addWidget(self.importServicesBtn)
        hgride.addStretch()
        self.servicesView = ts2.editor.views.ServicesEditorView(servicesTab)
        self.addServiceBtn = QtWidgets.QPushButton(self.tr("Add new service"),
                                                   servicesTab)
        self.addServiceBtn.clicked.connect(self.addServiceBtnClicked)
        self.delServiceBtn = QtWidgets.QPushButton(self.tr("Remove service"),
                                                   servicesTab)
        self.delServiceBtn.clicked.connect(self.delServiceBtnClicked)
        hgrids = QtWidgets.QHBoxLayout()
        hgrids.addWidget(self.addServiceBtn)
        hgrids.addWidget(self.delServiceBtn)
        hgrids.addStretch()
        self.serviceLinesView = ts2.editor.views.ServiceLinesEditorView(
            servicesTab
        )
        self.serviceLinesView.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self.serviceLinesView.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self.appendServiceLineBtn = QtWidgets.QPushButton(
            self.tr("Append new line"), servicesTab
        )
        self.appendServiceLineBtn.clicked.connect(
            self.appendServiceLineBtnClicked
        )
        self.insertServiceLineBtn = QtWidgets.QPushButton(
            self.tr("Insert new line"), servicesTab
        )
        self.insertServiceLineBtn.clicked.connect(
            self.insertServiceLineBtnClicked
        )
        self.delServiceLineBtn = QtWidgets.QPushButton(self.tr("Remove line"),
                                                       servicesTab)
        self.delServiceLineBtn.clicked.connect(self.delServiceLineBtnClicked)
        hgridl = QtWidgets.QHBoxLayout()
        hgridl.addWidget(self.appendServiceLineBtn)
        hgridl.addWidget(self.insertServiceLineBtn)
        hgridl.addWidget(self.delServiceLineBtn)
        hgridl.addStretch()
        grid = QtWidgets.QVBoxLayout()
        grid.addLayout(hgride)
        grid.addWidget(self.servicesView)
        grid.addLayout(hgrids)
        grid.addWidget(self.serviceLinesView)
        grid.addLayout(hgridl)
        servicesTab.setLayout(grid)
        self.tabWidget.addTab(servicesTab, self.tr("Services"))

        # Train tab
        trainsTab = QtWidgets.QWidget()
        self.setupTrainsBtn = QtWidgets.QPushButton(
            self.tr("Setup trains from services"), trainsTab
        )
        self.setupTrainsBtn.clicked.connect(self.setupTrainsBtnClicked)

        hgride = QtWidgets.QHBoxLayout()
        hgride.addWidget(self.setupTrainsBtn)
        hgride.addStretch()
        self.trainsGraphicsView = ts2.editor.views.TrainsGraphicsView(
            trainsTab
        )
        self.reverseTrainBtn = QtWidgets.QPushButton(
            self.tr("Reverse train direction"), trainsTab
        )
        self.reverseTrainBtn.clicked.connect(self.reverseTrainBtnClicked)
        hgridr = QtWidgets.QHBoxLayout()
        hgridr.addWidget(self.reverseTrainBtn)
        hgridr.addStretch()
        self.trainsView = ts2.editor.views.TrainsEditorView(trainsTab)
        self.addTrainBtn = QtWidgets.QPushButton(self.tr("Add new train"),
                                                 trainsTab)
        self.addTrainBtn.clicked.connect(self.addTrainBtnClicked)
        self.delTrainBtn = QtWidgets.QPushButton(self.tr("Remove train"),
                                                 trainsTab)
        self.delTrainBtn.clicked.connect(self.delTrainBtnClicked)
        hgrid = QtWidgets.QHBoxLayout()
        hgrid.addWidget(self.addTrainBtn)
        hgrid.addWidget(self.delTrainBtn)
        hgrid.addStretch()
        grid = QtWidgets.QVBoxLayout()
        grid.addLayout(hgride)
        grid.addWidget(self.trainsGraphicsView)
        grid.addLayout(hgridr)
        grid.addWidget(self.trainsView)
        grid.addLayout(hgrid)
        trainsTab.setLayout(grid)
        self.tabWidget.addTab(trainsTab, self.tr("Trains"))

        self.setCentralWidget(self.tabWidget)

    def simulationConnect(self):
        """Connects the signals and slots to the simulation."""
        self.titleTxt.setText(self.editor.option("title"))
        self.descriptionTxt.setPlainText(self.editor.option("description"))
        self.optionsView.setModel(self.editor.optionsModel)
        self.sceneryView.setScene(self.editor.scene)
        self.trackItemsLibraryView.setScene(self.editor.libraryScene)
        self.routesGraphicView.setScene(self.editor.scene)
        self.routesView.setModel(self.editor.routesModel)
        self.trainTypesView.setModel(self.editor.trainTypesModel)
        servicesSortedModel = QtCore.QSortFilterProxyModel()
        servicesSortedModel.setSourceModel(self.editor.servicesModel)
        self.servicesView.setModel(servicesSortedModel)
        self.serviceLinesView.setModel(self.editor.serviceLinesModel)
        self.trainsGraphicsView.setScene(self.editor.scene)
        trainsSortedModel = QtCore.QSortFilterProxyModel()
        trainsSortedModel.setSourceModel(self.editor.trainsModel)
        self.trainsView.setModel(trainsSortedModel)

        # Signal connections
        self.tabWidget.currentChanged.connect(self.showHideDockWidgets)
        self.tabWidget.currentChanged.connect(self.updateMenus)
        self.editor.selectionChanged.connect(self.setPropertiesModel)
        self.tabWidget.currentChanged.connect(self.editor.updateContext)
        self.editor.sceneryIsValidated.connect(
            self.sceneryView.setDisabled
        )
        self.editor.sceneryIsValidated.connect(
            self.unlockSceneryBtn.setEnabled
        )
        self.editor.sceneryIsValidated.connect(
            self.validateSceneryBtn.setDisabled
        )
        self.editor.sceneryIsValidated.connect(self.routesTab.setEnabled)
        self.unlockSceneryBtn.clicked.connect(
            self.editor.invalidateScenery
        )
        self.routesView.routeSelected.connect(self.editor.selectRoute)
        self.servicesView.serviceSelected.connect(
            self.editor.serviceLinesModel.setServiceCode
        )
        self.trainsView.trainSelected.connect(self.editor.selectTrain)
        self.trainsView.trainsUnselected.connect(self.editor.unselectTrains)

        self.tabWidget.currentChanged.emit(self.tabWidget.currentIndex())

    def simulationDisconnect(self):
        """Disconnects all the signals of this editor."""
        signals = [
            self.editor.selectionChanged,
            self.tabWidget.currentChanged,
            self.editor.sceneryIsValidated,
            self.unlockSceneryBtn.clicked,
            self.routesView.routeSelected,
            self.servicesView.serviceSelected,
            self.trainsView.trainSelected,
            self.trainsView.trainsUnselected
        ]
        for signal in signals:
            try:
                signal.disconnect()
            except TypeError:
                pass

    closed = QtCore.pyqtSignal()

    def closeEvent(self, closeEvent):
        """Called when the editor window is closed. Emits the closed signal.
        """
        super().closeEvent(closeEvent)
        if closeEvent.isAccepted():
            choice = QtWidgets.QMessageBox.question(
                self,
                self.tr("Close editor"),
                self.tr("Do you want to save your changes ?"),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |
                QtWidgets.QMessageBox.Cancel
            )
            if choice == QtWidgets.QMessageBox.Yes:
                self.saveSimulation()
            if choice == QtWidgets.QMessageBox.Yes or \
               choice == QtWidgets.QMessageBox.No:
                self.closed.emit()
            else:
                closeEvent.ignore()

    @QtCore.pyqtSlot(int)
    def setPropertiesModel(self):
        """Sets the TrackPropertiesModel related to the selection on the
        properties view"""
        if len(self.editor.selectedItems) > 0:
            self.propertiesView.setModel(
                scenery.helper.TrackPropertiesModel(self.editor.selectedItems)
            )
        else:
            self.propertiesView.setModel(None)

    @QtCore.pyqtSlot()
    def loadSimulation(self):
        """Loads the simulation from the database"""
        # DEBUG
        # fileName = "C:\\Users\\nicolas\\Documents\\Progs\\GitHub\\ts2\\data\\drain.json"

        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
                           self,
                           self.tr("Open a simulation"),
                           QtCore.QDir.currentPath(),
                           self.tr("TS2 simulation files (*.ts2)"))
        if fileName != "":
            QtWidgets.qApp.setOverrideCursor(Qt.WaitCursor)
            self.simulationDisconnect()
            self.editor = editor.load(self, fileName)
            self.setWindowTitle(
                self.tr("ts2 - Train Signalling Simulation - Editor - %s")
                % fileName
            )
            self.simulationConnect()
            QtWidgets.qApp.restoreOverrideCursor()

    @QtCore.pyqtSlot()
    def saveSimulation(self):
        """Saves the simulation to the database"""
        if not self.editor.fileName:
            self.saveAsSimulation()
        QtWidgets.qApp.setOverrideCursor(Qt.WaitCursor)
        self.editor.save()
        QtWidgets.qApp.restoreOverrideCursor()

    @QtCore.pyqtSlot()
    def saveAsSimulation(self):
        """Saves the simulation to a different database"""
        # DEBUG
        # fileName = "/home/nicolas/Progs/GitHub/ts2/data/drain-save.ts2"
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                           self,
                           self.tr("Save the simulation as"),
                           QtCore.QDir.currentPath(),
                           self.tr("TS2 simulation files (*.ts2)"))
        if fileName != "":
            self.editor.fileName = fileName
            self.saveSimulation()

    @QtCore.pyqtSlot()
    def closeSimulation(self):
        """Closes the current simulation, and prepares for editing a new one
        """
        if self.editor.database is not None:
            if QtWidgets.QMessageBox.warning(
                self,
                self.tr("Simulation loaded"),
                self.tr("The current simulation will be closed.\n"
                        "Do you want to continue?"),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            ) == QtWidgets.QMessageBox.Yes:
                self.editor = editor.Editor()
                self.editor.initialize(self)

    @QtCore.pyqtSlot()
    def setPanTool(self):
        """Sets the pan tool."""
        self.sceneryView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    @QtCore.pyqtSlot()
    def setSelectionTool(self):
        """Sets the selection tool."""
        self.sceneryView.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

    @QtCore.pyqtSlot()
    def copyItems(self):
        """Copy the current selection to the clipboard."""
        self.editor.copyToClipboard()

    @QtCore.pyqtSlot()
    def pasteItems(self):
        """Paste the items of the clipboard on the scenery."""
        self.editor.pasteFromClipboard()

    @QtCore.pyqtSlot()
    def deleteItems(self):
        """Delete the items of the current selection."""
        if QtWidgets.QMessageBox.warning(
            self,
            self.tr("Delete items"),
            self.tr("Do you really want to delete all "
                    "the selected items?"),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        ) == QtWidgets.QMessageBox.Yes:
            self.editor.deleteSelection()

    @QtCore.pyqtSlot()
    def selectAll(self):
        """Select all the items on the scene."""
        self.editor.clearSelection()
        for tiId in self.editor.trackItems:
            self.editor.updateSelection(tiId, True)

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

    @QtCore.pyqtSlot(int)
    def updateMenus(self, index):
        """Updates the enabled menu actions depending on the selected tab."""
        if index == 1:
            # Scenery panel
            self.selectionToolAction.setEnabled(True)
            self.copyAction.setEnabled(True)
            self.pasteAction.setEnabled(True)
            self.deleteAction.setEnabled(True)
            self.selectAllAction.setEnabled(True)
        else:
            self.panToolAction.setChecked(True)
            self.selectionToolAction.setEnabled(False)
            self.copyAction.setEnabled(False)
            self.pasteAction.setEnabled(False)
            self.deleteAction.setEnabled(False)
            self.selectAllAction.setEnabled(False)

    @QtCore.pyqtSlot()
    def updateGeneralTab(self):
        """Updates the data in the general tab with the simulation options."""
        self.titleTxt.setText(self.editor.option("title"))
        self.descriptionTxt.setPlainText(self.editor.option("description"))

    @QtCore.pyqtSlot()
    def validateSceneryBtnClicked(self):
        """Validates the scenery by calling the editor to perform the task."""
        QtWidgets.qApp.setOverrideCursor(Qt.WaitCursor)
        self.editor.validateScenery()
        QtWidgets.qApp.restoreOverrideCursor()

    @QtCore.pyqtSlot()
    def delRouteBtnClicked(self):
        """Deletes the selected route in routesView when the delete route
        button is clicked."""
        rowIndexes = self.routesView.selectionModel().selectedRows()
        if len(rowIndexes) != 0:
            rowIndex = rowIndexes[0]
            model = self.editor.routesModel
            routeNum = model.data(rowIndex, 0)
            if QtWidgets.QMessageBox.question(
                self,
                self.tr("Delete route"),
                self.tr("Are you sure you want "
                        "to delete route %i?") % routeNum,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            ) == QtWidgets.QMessageBox.Yes:
                model.beginRemoveRows(QtCore.QModelIndex(), rowIndex.row(),
                                      rowIndex.row())
                self.editor.deleteRoute(routeNum)
                model.endRemoveRows()

    @QtCore.pyqtSlot()
    def addRouteBtnClicked(self):
        """Adds a route in routesView when the add route button is clicked."""
        model = self.editor.routesModel
        model.beginInsertRows(QtCore.QModelIndex(),
                              model.rowCount(), model.rowCount())
        if self.editor.addRoute():
            model.endInsertRows()
        else:
            QtWidgets.QMessageBox.warning(
                self,
                self.tr("Add route"),
                self.tr("No route added:\n"
                        "No route selected or a route between "
                        "these two signals already exists.")
            )

    @QtCore.pyqtSlot()
    def addTrainTypeBtnClicked(self):
        """Adds an empty stock type to the editor"""
        code, ok = QtWidgets.QInputDialog.getText(
            self,
            self.tr("Add train type"),
            self.tr("Enter new train type code:")
        )
        if ok:
            if code not in self.editor.trainTypes:
                model = self.editor.trainTypesModel
                model.beginInsertRows(QtCore.QModelIndex(),
                                      model.rowCount(), model.rowCount())
                self.editor.addTrainType(code)
                model.endInsertRows()
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    self.tr("Add train type"),
                    self.tr("Unable to add train type: \n"
                            "This train type code already exists.")
                )

    @QtCore.pyqtSlot()
    def delTrainTypeBtnClicked(self):
        """Removes the currently selected stock type from the simulation"""
        rowIndexes = self.trainTypesView.selectionModel().selectedRows()
        if len(rowIndexes) != 0:
            rowIndex = rowIndexes[0]
            model = self.editor.trainTypesModel
            code = model.data(rowIndex, 0)
            if QtWidgets.QMessageBox.question(
                self,
                self.tr("Delete train type"),
                self.tr("Are you sure you want "
                        "to delete train type %s?") % code,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            ) == QtWidgets.QMessageBox.Yes:
                model.beginRemoveRows(QtCore.QModelIndex(), rowIndex.row(),
                                      rowIndex.row())
                self.editor.deleteTrainType(code)
                model.endRemoveRows()

    @QtCore.pyqtSlot()
    def addServiceBtnClicked(self):
        """Adds an empty service to the editor"""
        code, ok = QtWidgets.QInputDialog.getText(
            self,
            self.tr("Add service"),
            self.tr("Enter new service code:")
        )
        if ok:
            if code not in self.editor.services:
                model = self.editor.servicesModel
                model.beginInsertRows(QtCore.QModelIndex(), model.rowCount(),
                                      model.rowCount())
                self.editor.addService(code)
                model.endInsertRows()
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    self.tr("Add service"),
                    self.tr("Unable to add service: \n"
                            "This service code already exists.")
                )

    @QtCore.pyqtSlot()
    def delServiceBtnClicked(self):
        """Removes the currently selected service from the simulation"""
        rowIndexes = self.servicesView.selectionModel().selectedRows()
        if len(rowIndexes) != 0:
            rowIndex = self.servicesView.model().mapToSource(rowIndexes[0])
            model = self.editor.servicesModel
            code = model.data(rowIndex, 0)
            if QtWidgets.QMessageBox.question(
                self,
                self.tr("Delete service"),
                self.tr("Are you sure you want "
                        "to delete service %s?") % code,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            ) == QtWidgets.QMessageBox.Yes:
                model.beginRemoveRows(QtCore.QModelIndex(), rowIndex.row(),
                                      rowIndex.row())
                self.editor.deleteService(code)
                model.endRemoveRows()

    @QtCore.pyqtSlot()
    def appendServiceLineBtnClicked(self):
        """Appends a service line to this service at the end of the list"""
        model = self.editor.serviceLinesModel
        service = model.service
        index = model.rowCount()
        model.beginInsertRows(QtCore.QModelIndex(), index, index)
        self.editor.addServiceLine(service, index)
        model.endInsertRows()

    @QtCore.pyqtSlot()
    def insertServiceLineBtnClicked(self):
        """Add a service line to this service after the currently selected"""
        model = self.editor.serviceLinesModel
        service = model.service
        index = 0
        if len(service.lines) != 0:
            rows = self.serviceLinesView.selectionModel().selectedRows()
            if len(rows) != 0:
                index = rows[0].row()
        model.beginInsertRows(QtCore.QModelIndex(), index, index)
        self.editor.addServiceLine(service, index)
        model.endInsertRows()

    @QtCore.pyqtSlot()
    def delServiceLineBtnClicked(self):
        """Removes the currently selected service line of this service"""
        service = self.serviceLinesView.model().service
        rowIndexes = self.serviceLinesView.selectionModel().selectedRows()
        if len(rowIndexes) != 0:
            rowIndex = rowIndexes
            model = self.editor.serviceLinesModel
            code = model.data(rowIndex, 0)
            if QtWidgets.QMessageBox.question(
                self,
                self.tr("Delete service"),
                self.tr("Are you sure you want "
                        "to delete the line at %s?") % code,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            ) == QtWidgets.QMessageBox.Yes:
                model.beginRemoveRows(QtCore.QModelIndex(), rowIndex.row(),
                                      rowIndex.row())
                self.editor.deleteServiceLine(service, rowIndex.row())
                model.endRemoveRows()

    @QtCore.pyqtSlot()
    def importServicesBtnClicked(self):
        """Calls an open file dialog for the user to select the file to import
        services from and asks the editor to actually do the import"""

        # ### DEBUG
        # fileName = "/home/nicolas/drain.csv"

        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.tr("Import services"),
            QtCore.QDir.currentPath(),
            self.tr("CSV files (*.csv)")
        )
        if fileName != "":
            if QtWidgets.QMessageBox.warning(
                self,
                self.tr("Import services"),
                self.tr("This will erase any existing service\n"
                        "Are you sure you want to continue?"),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            ) == QtWidgets.QMessageBox.Yes:
                QtWidgets.qApp.setOverrideCursor(Qt.WaitCursor)
                self.editor.importServicesFromFile(fileName)
                QtWidgets.qApp.restoreOverrideCursor()

    @QtCore.pyqtSlot()
    def exportServicesBtnClicked(self):
        """Calls a save file dialog for the user to give the filanme to which
        to export the services and asks the editor to actually do the export.
        """
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.tr("Export services"),
            QtCore.QDir.currentPath(),
            self.tr("CSV files (*.csv)")
        )
        if fileName != "":
            self.editor.exportServicesToFile(fileName)

    @QtCore.pyqtSlot()
    def setupTrainsBtnClicked(self):
        """Calls the editor to setup the trains list from the services list.
        """
        if QtWidgets.QMessageBox.warning(
            self,
            self.tr("Setup trains"),
            self.tr("This will erase any existing train, and will"
                    " create a train for each service that do not"
                    " follow another one.\n"
                    "Are you sure you want to continue?"),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        ) == QtWidgets.QMessageBox.Yes:
            QtWidgets.qApp.setOverrideCursor(Qt.WaitCursor)
            self.editor.setupTrainsFromServices()
            QtWidgets.qApp.restoreOverrideCursor()

    @QtCore.pyqtSlot()
    def reverseTrainBtnClicked(self):
        """Calls the editor to reverse the train direction (in fact the
        its trainHead direction)"""
        self.editor.reverseSelectedTrain()

    @QtCore.pyqtSlot()
    def addTrainBtnClicked(self):
        """Adds an empty train to the editor"""
        model = self.editor.trainsModel
        model.beginInsertRows(QtCore.QModelIndex(), model.rowCount(),
                              model.rowCount())
        self.editor.addTrain()
        model.endInsertRows()

    @QtCore.pyqtSlot()
    def delTrainBtnClicked(self):
        """Removes the currently selected train"""
        rowIndexes = self.trainsView.selectionModel().selectedRows()
        if len(rowIndexes) != 0:
            row = self.trainsView.model().mapToSource(rowIndexes[0]).row()
            model = self.editor.trainsModel
            if QtWidgets.QMessageBox.question(
                self,
                self.tr("Delete train"),
                self.tr("Are you sure you want "
                        "to delete train %i?") % row,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            ) == QtWidgets.QMessageBox.Yes:
                model.beginRemoveRows(QtCore.QModelIndex(), row, row)
                self.editor.deleteTrain(row)
                model.endRemoveRows()

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
        transform = QtGui.QTransform()
        transform.scale(percent/100, percent/100)
        self.sceneryView.setTransform(transform)

    @QtCore.pyqtSlot(int)
    def openReassignServiceWindow(self, trainId):
        """To conform to Mainwindow morphism."""
        pass
