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
import zipfile

from Qt import QtCore, QtGui, QtWidgets, Qt

from ts2 import simulation, utils
from ts2.gui import dialogs, trainlistview, servicelistview, widgets
from ts2.scenery import placeitem
from ts2.editor import editorwindow


class MainWindow(QtWidgets.QMainWindow):
    """ TODO Document MainWindow Class"""

    def __init__(self):
        super().__init__()
        MainWindow._self = self
        self.editorWindow = None
        self.setWindowState(Qt.WindowMaximized)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle(self.tr("ts2 - Train Signalling Simulation"))

        # Simulation
        self.simulation = None

        # Actions
        self.openAction = QtWidgets.QAction(self.tr("&Open..."), self)
        self.openAction.setShortcut(QtGui.QKeySequence.Open)
        self.openAction.setToolTip(self.tr("Open a simulation or a "
                                           "previously saved game"))
        self.openAction.triggered.connect(self.loadSimulation)

        self.saveGameAsAction = QtWidgets.QAction(self.tr("&Save game as..."),
                                                  self)
        self.saveGameAsAction.setShortcut(QtGui.QKeySequence.SaveAs)
        self.saveGameAsAction.setToolTip(self.tr("Save the current game"))
        self.saveGameAsAction.triggered.connect(self.saveGame)
        self.saveGameAsAction.setEnabled(False)

        self.propertiesAction = QtWidgets.QAction(self.tr("&Properties..."),
                                                  self)
        self.propertiesAction.setShortcut(
            QtGui.QKeySequence(self.tr("Ctrl+P"))
        )
        self.propertiesAction.setToolTip(self.tr("Edit simulation properties"))
        self.propertiesAction.triggered.connect(self.openPropertiesDialog)
        self.propertiesAction.setEnabled(False)

        self.quitAction = QtWidgets.QAction(self.tr("&Quit"), self)
        self.quitAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+Q")))
        self.quitAction.setToolTip(self.tr("Quit TS2"))
        self.quitAction.triggered.connect(self.close)

        self.editorAction = QtWidgets.QAction(self.tr("&Editor"), self)
        self.editorAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+E")))
        self.editorAction.setToolTip(self.tr("Open the simulation editor"))
        self.editorAction.triggered.connect(self.openEditor)

        self.aboutAction = QtWidgets.QAction(self.tr("&About TS2..."), self)
        self.aboutAction.setToolTip(self.tr("About TS2"))
        self.aboutAction.triggered.connect(self.showAboutBox)

        self.aboutQtAction = QtWidgets.QAction(self.tr("About Qt..."), self)
        self.aboutQtAction.setToolTip(self.tr("About Qt"))
        self.aboutQtAction.triggered.connect(QtWidgets.QApplication.aboutQt)

        # Menu
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveGameAsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.propertiesAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAction)
        self.editorMenu = self.menuBar().addAction(self.editorAction)
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAction)
        self.helpMenu.addAction(self.aboutQtAction)
        self.menuBar().setCursor(Qt.PointingHandCursor)

        # Dock Widgets
        self.trainInfoPanel = QtWidgets.QDockWidget(
            self.tr("Train Information"), self
        )
        self.trainInfoPanel.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable
        )
        self.trainInfoView = QtWidgets.QTreeView(self)
        self.trainInfoView.setItemsExpandable(False)
        self.trainInfoView.setRootIsDecorated(False)
        self.trainInfoView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.trainInfoView.customContextMenuRequested.connect(
            self.showContextMenu
        )
        self.trainInfoPanel.setWidget(self.trainInfoView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.trainInfoPanel)

        self.serviceInfoPanel = QtWidgets.QDockWidget(
            self.tr("Service Information"), self
        )
        self.serviceInfoPanel.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable
        )
        self.serviceInfoView = QtWidgets.QTreeView(self)
        self.serviceInfoView.setItemsExpandable(False)
        self.serviceInfoView.setRootIsDecorated(False)
        self.serviceInfoPanel.setWidget(self.serviceInfoView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.serviceInfoPanel)

        self.placeInfoPanel = QtWidgets.QDockWidget(
            self.tr("Station Information"), self
        )
        self.placeInfoPanel.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable
        )
        self.placeInfoView = QtWidgets.QTreeView(self)
        self.placeInfoView.setItemsExpandable(False)
        self.placeInfoView.setRootIsDecorated(False)
        self.placeInfoView.setModel(placeitem.Place.selectedPlaceModel)
        self.placeInfoPanel.setWidget(self.placeInfoView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.placeInfoPanel)

        self.trainListPanel = QtWidgets.QDockWidget(self.tr("Trains"), self)
        self.trainListPanel.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable
        )
        self.trainListView = trainlistview.TrainListView(self)
        self.simulationLoaded.connect(self.trainListView.setupTrainList)
        self.trainListPanel.setWidget(self.trainListView)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.trainListPanel)

        self.serviceListPanel = QtWidgets.QDockWidget(self.tr("Services"), self)
        self.serviceListPanel.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable
        )
        self.serviceListView = servicelistview.ServiceListView(self)
        self.simulationLoaded.connect(self.serviceListView.setupServiceList)
        self.serviceListPanel.setWidget(self.serviceListView)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.serviceListPanel)
        self.tabifyDockWidget(self.serviceListPanel, self.trainListPanel)

        self.loggerPanel = QtWidgets.QDockWidget(self.tr("Messages"), self)
        self.loggerPanel.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable |
                                     QtWidgets.QDockWidget.DockWidgetFloatable)
        self.loggerView = QtWidgets.QTreeView(self)
        self.loggerView.setItemsExpandable(False)
        self.loggerView.setRootIsDecorated(False)
        self.loggerView.setHeaderHidden(True)
        self.loggerView.setPalette(QtGui.QPalette(Qt.black))
        self.loggerView.setVerticalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerItem
        )
        self.loggerPanel.setWidget(self.loggerView)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.loggerPanel)

        # board
        self.board = QtWidgets.QWidget(self)

        # Canvas
        self.view = QtWidgets.QGraphicsView(self.board)
        self.view.setInteractive(True)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing, False)
        self.view.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.view.setPalette(QtGui.QPalette(Qt.black))

        # Panel
        # Loaded with simulation
        self.panel = widgets.Panel(self.board, self)
        self.panel.zoomChanged.connect(self.zoom)

        # Display
        self.grid = QtWidgets.QVBoxLayout()
        self.grid.addWidget(self.view)
        self.grid.addWidget(self.panel)
        self.grid.setSpacing(0)
        self.board.setLayout(self.grid)
        self.setCentralWidget(self.board)

        # Editor
        self.editorOpened = False

        # DEBUG
        # self.loadSimulation()
        # self.openEditor()

    simulationLoaded = QtCore.pyqtSignal(simulation.Simulation)

    @staticmethod
    def instance():
        return MainWindow._self

    @QtCore.pyqtSlot()
    def loadSimulation(self):
        # ## DEBUG
        # fileName = "C:\\Users\\nicolas\\Documents\\Progs\\GitHub\\ts2\\data\\drain.ts2"

        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.tr("Open a simulation"),
            QtCore.QDir.currentPath(),
            self.tr("TS2 files (*.ts2 *.tsg);;"
                    "TS2 simulation files (*.ts2);;"
                    "TS2 saved game files (*.tsg)"))
        if fileName != "":
            QtWidgets.qApp.setOverrideCursor(Qt.WaitCursor)

            if self.simulation is not None:
                self.simulationDisconnect()
                self.simulation = None
            # try:
            if zipfile.is_zipfile(fileName):
                with zipfile.ZipFile(fileName) as zipArchive:
                    with zipArchive.open("simulation.json") as file:
                        self.simulation = simulation.load(self, file)
            else:
                with open(fileName) as file:
                    self.simulation = simulation.load(self, file)
            # except utils.FormatException as err:
            #     QtWidgets.QMessageBox.critical(
            #         self,
            #         self.tr("Bad version of TS2 simulation file"),
            #         str(err),
            #         QtWidgets.QMessageBox.Ok
            #     )
            #     self.simulation = None
            # except:
            #     dialogs.ExceptionDialog.popupException(self)
            #     self.simulation = None
            # else:
            self.setWindowTitle(self.tr(
                "ts2 - Train Signalling Simulation - %s") % fileName)
            self.simulationConnect()
            self.simulationLoaded.emit(self.simulation)
            QtWidgets.QApplication.restoreOverrideCursor()

    def simulationConnect(self):
        """Connects the signals and slots to the simulation."""
        # Set models
        self.trainInfoView.setModel(self.simulation.selectedTrainModel)
        self.serviceInfoView.setModel(self.simulation.selectedServiceModel)
        self.loggerView.setModel(self.simulation.messageLogger)
        # Set scene
        self.view.setScene(self.simulation.scene)
        # TrainListView
        self.simulation.trainSelected.connect(
            self.trainListView.updateTrainSelection
        )
        self.trainListView.trainSelected.connect(
            self.simulation.selectedTrainModel.setTrainByServiceCode
        )
        self.trainListView.trainSelected.connect(
            self.serviceListView.updateServiceSelection
        )
        # ServiceListView
        self.serviceListView.serviceSelected.connect(
            self.simulation.selectedServiceModel.setServiceCode
        )
        # TrainInfoView
        self.simulation.trainStatusChanged.connect(
            self.trainInfoView.model().update
        )
        self.simulation.timeChanged.connect(
            self.trainInfoView.model().updateSpeed
        )
        # MessageLogger
        self.simulation.messageLogger.rowsInserted.connect(
            self.loggerView.scrollToBottom
        )
        # Panel
        self.simulation.timeChanged.connect(self.panel.clock.setTime)
        self.simulation.scorer.scoreChanged.connect(
            self.panel.scoreDisplay.display
        )
        self.panel.scoreDisplay.display(self.simulation.scorer.score)
        # Menus
        self.saveGameAsAction.setEnabled(True)
        self.propertiesAction.setEnabled(True)

    def simulationDisconnect(self):
        """Disconnects the simulation for deletion."""
        # Unset models
        self.trainInfoView.setModel(None)
        self.serviceInfoView.setModel(None)
        self.loggerView.setModel(None)
        # Unset scene
        self.view.setScene(None)
        # Disconnect signals
        try:
            self.simulation.trainSelected.disconnect()
        except TypeError:
            pass
        try:
            self.trainListView.trainSelected.disconnect()
        except TypeError:
            pass
        try:
            self.serviceListView.serviceSelected.disconnect()
        except TypeError:
            pass
        try:
            self.simulation.trainStatusChanged.disconnect()
        except TypeError:
            pass
        try:
            self.simulation.timeChanged.disconnect()
        except TypeError:
            pass
        try:
            self.simulation.messageLogger.rowsInserted.disconnect()
        except TypeError:
            pass
        try:
            self.simulation.scorer.scoreChanged.disconnect()
        except TypeError:
            pass
        # Menus
        self.saveGameAsAction.setEnabled(False)
        self.propertiesAction.setEnabled(False)

    @QtCore.pyqtSlot()
    def saveGame(self):
        """Saves the current game to file."""
        if self.simulation is not None:
            self.panel.pauseButton.click()
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                self.tr("Save the simulation as"),
                QtCore.QDir.homePath(),
                self.tr("TS2 game files (*.tsg)")
            )
            if fileName != "":
                QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
                # try:
                self.simulation.saveGame(fileName)
                # except:
                #     dialogs.ExceptionDialog.popupException(self)
                QtWidgets.QApplication.restoreOverrideCursor()

    @QtCore.pyqtSlot(int)
    def zoom(self, percent):
        transform = QtGui.QTransform()
        transform.scale(percent/100, percent/100)
        self.view.setTransform(transform)

    @QtCore.pyqtSlot()
    def showAboutBox(self):
        """Shows the about box"""
        QtWidgets.QMessageBox.about(self, self.tr("About TS2"), self.tr(
            "TS2 is a train signalling simulation.\n\n"
            "Version %s\n\n"
            "Copyright 2008-2013, NPi (npi@users.sourceforge.net)\n"
            "http://ts2.sourceforge.net\n\n"
            "TS2 is licensed under the terms of the GNU GPL v2\n""") %
            utils.TS2_VERSION)
        if self.editorOpened:
            self.editorWindow.activateWindow()

    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenu(self, pos):
        if self.sender() == self._trainInfoView:
            train = self.trainInfoView.model().train
            if train is not None:
                train.showTrainActionsMenu(self.trainInfoView,
                                           self.trainInfoView.mapToGlobal(pos))

    @QtCore.pyqtSlot()
    def openEditor(self):
        """This slot opens the editor window if it is not already opened"""
        if not self.editorOpened:
            self.editorWindow = editorwindow.EditorWindow(self)
            self.editorWindow.simulationConnect()
            self.editorWindow.closed.connect(self.editorIsClosed)
            self.editorOpened = True
            self.editorWindow.show()
        else:
            self.editorWindow.activateWindow()

    @QtCore.pyqtSlot()
    def editorIsClosed(self):
        self.editorOpened = False

    @QtCore.pyqtSlot()
    def openPropertiesDialog(self):
        """Pops-up the simulation properties dialog."""
        if self.simulation is not None:
            paused = self.panel.pauseButton.isChecked()
            if not paused:
                self.panel.pauseButton.click()
            propertiesDialog = dialogs.PropertiesDialog(self, self.simulation)
            propertiesDialog.exec_()
            if not paused:
                self.panel.pauseButton.click()

    @QtCore.pyqtSlot(int)
    def openReassignServiceWindow(self, trainId):
        """Opens the reassign service window."""
        if self.simulation is not None:
            dialogs.ServiceAssignDialog.reassignServiceToTrain(
                self.simulation, trainId
            )
