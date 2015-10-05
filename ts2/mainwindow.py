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

import tempfile
import zipfile
import os
from urllib import request

from Qt import QtCore, QtGui, QtWidgets, Qt

from ts2 import simulation, utils
from ts2.gui import dialogs, trainlistview, servicelistview, widgets, opendialog
from ts2.scenery import placeitem
from ts2.editor import editorwindow
from ts2.utils import settings

from ts2 import __PROJECT_WWW__, __PROJECT_HOME__, __PROJECT_BUGS__, __ORG_CONTACT__, __VERSION__


class MainWindow(QtWidgets.QMainWindow):
    """MainWindow Class"""

    simulationLoaded = QtCore.pyqtSignal(simulation.Simulation)

    def __init__(self, debug=False, file=None):
        super().__init__()
        MainWindow._self = self

        settings.setDebug(debug)

        self.setObjectName("ts2_main_window")
        self.editorWindow = None
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle(self.tr("ts2 - Train Signalling Simulation") + " - %s" % __VERSION__)

        # Simulation
        self.simulation = None

        # Actions  ======================================
        self.openAction = QtWidgets.QAction(self.tr("&Open..."), self)
        self.openAction.setShortcut(QtGui.QKeySequence.Open)
        self.openAction.setToolTip(self.tr("Open a simulation or a "
                                           "previously saved game"))
        self.openAction.triggered.connect(self.onOpenSimulation)

        self.openRecentAction = QtWidgets.QAction(self.tr("Recent"), self)
        menu = QtWidgets.QMenu()
        self.openRecentAction.setMenu(menu)
        menu.triggered.connect(self.onRecent)

        self.saveGameAsAction = QtWidgets.QAction(self.tr("&Save game"), self)
        self.saveGameAsAction.setShortcut(QtGui.QKeySequence.SaveAs)
        self.saveGameAsAction.setToolTip(self.tr("Save the current game"))
        self.saveGameAsAction.triggered.connect(self.saveGame)
        self.saveGameAsAction.setEnabled(False)

        self.downloadAction = QtWidgets.QAction(
            self.tr("&Download simulations..."), self
        )
        self.downloadAction.setToolTip(
            self.tr("Download simulations from a server")
        )
        self.downloadAction.triggered.connect(self.downloadSimulations)

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

        self.editorAction = QtWidgets.QAction(self.tr("&Open"), self)
        self.editorAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+E")))
        self.editorAction.setToolTip(self.tr("Open the simulation editor"))
        self.editorAction.triggered.connect(self.openEditor)

        # Web Links
        self.actionGroupWwww = QtWidgets.QActionGroup(self)
        self.actionGroupWwww.triggered.connect(self.onWwwAction)

        self.aboutWwwHompage = QtWidgets.QAction(self.tr("&TS2 Homepage"), self)
        self.aboutWwwHompage.setProperty("url", __PROJECT_WWW__)
        self.actionGroupWwww.addAction(self.aboutWwwHompage)

        self.aboutWwwProject = QtWidgets.QAction(self.tr("&TS2 Project"), self)
        self.aboutWwwProject.setProperty("url", __PROJECT_HOME__)
        self.actionGroupWwww.addAction(self.aboutWwwProject)

        self.aboutWwwBugs = QtWidgets.QAction(self.tr("&TS2 Bugs && Feedback"), self)
        self.aboutWwwBugs.setProperty("url", __PROJECT_BUGS__)
        self.actionGroupWwww.addAction(self.aboutWwwBugs)

        # About
        self.aboutAction = QtWidgets.QAction(self.tr("&About TS2..."), self)
        self.aboutAction.setToolTip(self.tr("About TS2"))
        self.aboutAction.triggered.connect(self.showAboutBox)

        self.aboutQtAction = QtWidgets.QAction(self.tr("About Qt..."), self)
        self.aboutQtAction.setToolTip(self.tr("About Qt"))
        self.aboutQtAction.triggered.connect(QtWidgets.QApplication.aboutQt)

        # ===============================================
        # Menus

        # FileMenu
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.openRecentAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveGameAsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.downloadAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.propertiesAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAction)

        # Editor Menu
        self.editorMenu = self.menuBar().addMenu(self.tr("&Editor"))
        self.editorMenu.addAction(self.editorAction)
        
        # Help Menu
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutWwwHompage)
        self.helpMenu.addAction(self.aboutWwwProject)
        self.helpMenu.addAction(self.aboutWwwBugs)
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.aboutAction)
        self.helpMenu.addAction(self.aboutQtAction)

        self.menuBar().setCursor(Qt.PointingHandCursor)



        # ==============================================================
        # ToolBars

        # =========
        # Actions
        tbar, tbg = self._make_toolbar_group("Actions")
        self.addToolBar(tbar)
        tbg.addAction(self.openAction)
        tbg.addAction(self.editorAction)

        # =========
        # Speed
        tbar, tbg = self._make_toolbar_group("Speed")
        self.addToolBar(tbar)

        # Time factor spinBox
        self.timeFactorSpinBox = QtWidgets.QSpinBox(self)
        self.timeFactorSpinBox.setRange(1, 10)
        self.timeFactorSpinBox.setSingleStep(1)
        self.timeFactorSpinBox.setValue(1)
        self.timeFactorSpinBox.setSuffix("x")
        tbg.addWidget(self.timeFactorSpinBox)

        # =========
        # Zoom
        tbar, tbg = self._make_toolbar_group("Zoom")
        self.addToolBar(tbar)
        tbg.setMaximumWidth(300)

        self.zoomWidget = widgets.ZoomWidget(self)
        self.zoomWidget.setMaximumWidth(300)
        self.zoomWidget.valueChanged.connect(self.zoom)
        tbg.addWidget(self.zoomWidget)

        # =========
        # Score
        tbar, tbg = self._make_toolbar_group("Score")
        self.addToolBar(tbar)

        # Score display
        self.scoreDisplay = QtWidgets.QLCDNumber(self)
        self.scoreDisplay.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scoreDisplay.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scoreDisplay.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.scoreDisplay.setNumDigits(5)
        self.scoreDisplay.resize(70, 25)
        tbg.addWidget(self.scoreDisplay)

        # =========
        # Clock
        tbar, tbg = self._make_toolbar_group("Clock")
        self.addToolBar(tbar)

        # Pause button
        self.buttPause = QtWidgets.QToolButton(self)
        self.buttPause.setText( self.tr("Pause") )
        self.buttPause.setCheckable(True)
        self.buttPause.setAutoRaise(True)
        self.buttPause.setMaximumWidth(50)
        tbg.addWidget(self.buttPause)

        # Clock Widget
        self.clockWidget = widgets.ClockWidget(self)
        tbg.addWidget(self.clockWidget)


        # ====================
        # Sim Title
        tbar = QtWidgets.QToolBar()
        tbar.setFloatable(False)
        tbar.setMovable(False)
        self.addToolBar(tbar)
        self.lblTitle = QtWidgets.QLabel()
        lbl_sty = "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #fefefe, stop: 1 #CECECE);"
        lbl_sty += " color: #333333; font-size: 16pt; padding: 1px;"
        self.lblTitle.setStyleSheet(lbl_sty)
        self.lblTitle.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.lblTitle.setText("no sim loaded")
        sp = self.lblTitle.sizePolicy()
        sp.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.lblTitle.setSizePolicy(sp)
        tbar.addWidget(self.lblTitle)

        # ===============================================================
        # Dock Widgets

        # Train Info
        self.trainInfoPanel = QtWidgets.QDockWidget(
            self.tr("Train Information"), self
        )
        self.trainInfoPanel.setObjectName("train_information")
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

        # Service Info
        self.serviceInfoPanel = QtWidgets.QDockWidget(
            self.tr("Service Information"), self
        )
        self.serviceInfoPanel.setObjectName("service_information")
        self.serviceInfoPanel.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable
        )
        self.serviceInfoView = QtWidgets.QTreeView(self)
        self.serviceInfoView.setItemsExpandable(False)
        self.serviceInfoView.setRootIsDecorated(False)
        self.serviceInfoPanel.setWidget(self.serviceInfoView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.serviceInfoPanel)

        # Stations + Places Info
        self.placeInfoPanel = QtWidgets.QDockWidget(
            self.tr("Station Information"), self
        )
        self.placeInfoPanel.setObjectName("place_information")
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

        # Trains
        self.trainListPanel = QtWidgets.QDockWidget(self.tr("Trains"), self)
        self.trainListPanel.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable
        )
        self.trainListPanel.setObjectName("trains_panel")
        self.trainListView = trainlistview.TrainListView(self)
        self.simulationLoaded.connect(self.trainListView.setupTrainList)
        self.trainListPanel.setWidget(self.trainListView)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.trainListPanel)

        # Services
        self.serviceListPanel = QtWidgets.QDockWidget(self.tr("Services"), self)
        self.serviceListPanel.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable
        )
        self.serviceListPanel.setObjectName("services_panel")
        self.serviceListView = servicelistview.ServiceListView(self)
        self.simulationLoaded.connect(self.serviceListView.setupServiceList)
        self.serviceListPanel.setWidget(self.serviceListView)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.serviceListPanel)
        self.tabifyDockWidget(self.serviceListPanel, self.trainListPanel)

        # Message Logger
        self.loggerPanel = QtWidgets.QDockWidget(self.tr("Messages"), self)
        self.loggerPanel.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable |
                                     QtWidgets.QDockWidget.DockWidgetFloatable)
        self.loggerPanel.setObjectName("logger_panel")
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

        # ===========================================
        # Main Board
        self.board = QtWidgets.QWidget(self)

        # Canvas
        self.view = widgets.XGraphicsView(self.board)
        self.view.setInteractive(True)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing, False)
        self.view.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.view.setPalette(QtGui.QPalette(Qt.black))
        self.view.wheelChanged.connect(self.onWheelChanged)

        # Control Panel
        # Loaded with simulation
        self.panel = widgets.ControlBarWidget(self.board, self)
        self.panel.zoomChanged.connect(self.zoom)

        # Display
        self.grid = QtWidgets.QVBoxLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.addWidget(self.view)
        self.grid.addWidget(self.panel)
        self.grid.setSpacing(0)
        self.board.setLayout(self.grid)
        self.setCentralWidget(self.board)

        # Editor
        self.editorOpened = False

        self.refreshRecent()
        settings.restoreWindow(self)

        if file:
            self.loadSimulation(file)
        # DEBUG
        # self.onOpenSimulation()
        # self.loadSimulation()
        # self.openEditor()

    @staticmethod
    def instance():
        return MainWindow._self

    def onOpenSimulation(self):
        d = opendialog.OpenDialog(self)
        d.openFile.connect(self.loadSimulation)
        d.exec_()


    @QtCore.pyqtSlot(str)
    def loadSimulation(self, fileName=None):
        # ## DEBUG
        #if settings.debug:
        #   fileName = "C:\\Users\\nicolas\\Documents\\Progs\\GitHub\\ts2\\data\\drain.ts2"

        if not fileName:
            self.onOpenSimulation()
            return

        if fileName != "" or fileName != None:
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
                    settings.addRecent(fileName)
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
            self.lblTitle.setText( self.simulation.option("title") )
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
        self.simulation.timeChanged.connect(self.clockWidget.setTime)
        self.simulation.scorer.scoreChanged.connect(
            self.panel.scoreDisplay.display
        )
        self.panel.scoreDisplay.display(self.simulation.scorer.score)
        self.scoreDisplay.display(self.simulation.scorer.score)
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
                settings.addRecent(fileName)
                QtWidgets.QApplication.restoreOverrideCursor()

    @QtCore.pyqtSlot()
    def downloadSimulations(self):
        """Download simulations from a GitHub repository"""
        serverDialog = dialogs.DownloadSimulationsDialog(self)
        if serverDialog.exec() == QtWidgets.QDialog.Accepted:
            QtWidgets.qApp.setOverrideCursor(Qt.WaitCursor)
            url = "%s/archive/master.zip" % serverDialog.url.text().strip('/')
            response = request.urlopen(url)
            with tempfile.TemporaryFile() as tmpFile:
                tmpFile.write(response.read())
                with zipfile.ZipFile(tmpFile) as zipArchive:
                    for fileName in zipArchive.namelist():
                        fs = fileName.split('/', 1)
                        fn = fs[1] if len(fs) > 1 else fs[0]
                        if fileName.endswith(".ts2"):
                            fName = os.path.join(simulationsDirectory, fn)
                            os.makedirs(os.path.dirname(fName), exist_ok=True)
                            with open(fName, 'wb') as f:
                                f.write(zipArchive.read(fileName))
                        elif fileName.endswith(".tsl"):
                            fName = os.path.join(userDataDirectory,
                                                 os.path.basename(fileName))
                            with open(fName, 'wb') as f:
                                f.write(zipArchive.read(fileName))
                        elif fileName.endswith(".json"):
                            fName = os.path.join(simulationsDirectory,
                                                 fn.replace(".json", ".ts2"))
                            os.makedirs(os.path.dirname(fName), exist_ok=True)
                            with zipfile.ZipFile(fName, "w") as ts2Zip:
                                ts2Zip.writestr("simulation.json",
                                                zipArchive.read(fileName))

            QtWidgets.qApp.restoreOverrideCursor()

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
            "Copyright 2008-%s, NPi (%s)\n"
            "%s\n\n"
            "TS2 is licensed under the terms of the GNU GPL v2\n""") %
            (__VERSION__, QtCore.QDate.currentDate().year(), __ORG_CONTACT__,   __PROJECT_WWW__))
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

    def refreshRecent(self):
        """Reload the recent menu"""
        menu = self.openRecentAction.menu()
        menu.clear()
        act = []
        for fileName in settings.getRecent():
            if os.path.exists(fileName):
                act.append(menu.addAction(fileName))
        if act:
            self.onRecent(act[0])

    def onRecent(self, act):
        """Open a  recent item"""
        self.loadSimulation(fileName=act.text())

    def closeEvent(self, event):
        """Save window postions on close"""
        settings.saveWindow(self)
        settings.sync()
        super().closeEvent(event)

    def onWheelChanged(self, direction):
        """Handle scrollwheel on canvas"""
        percent = self.panel.zoomWidget.spinBox.value()
        self.panel.zoomWidget.spinBox.setValue(percent + (direction * 10))

        percent = self.zoomWidget.spinBox.value()
        self.zoomWidget.spinBox.setValue(percent + (direction * 10))

    def onWwwAction(self, act):
        url = act.property("url")
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def _make_toolbar_group(self, title):
        """Creates a toolbar containing a `ToolBarGroup`"""
        tbar = QtWidgets.QToolBar()
        tbar.setObjectName("tb_" + title )
        tbar.setFloatable(False)
        tbar.setMovable(True)

        tbg = widgets.ToolBarGroup(self, title=title)
        tbar.addWidget(tbg)
        return tbar, tbg


