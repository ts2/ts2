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

import io
import os
import signal
import subprocess
import tempfile
import time
import zipfile
from os import path

import simplejson as json
import websocket

from Qt import QtCore, QtGui, QtWidgets, Qt
from ts2 import __PROJECT_WWW__, __PROJECT_HOME__, __PROJECT_BUGS__, \
    __ORG_CONTACT__, __VERSION__, utils
from ts2 import simulation
from ts2.editor import editorwindow
from ts2.gui import dialogs, trainlistview, servicelistview, widgets, \
    opendialog, settingsdialog
from ts2.scenery import placeitem
from ts2.utils import settings

WS_TIMEOUT = 10


class MainWindow(QtWidgets.QMainWindow):
    """MainWindow Class"""

    simulationLoaded = QtCore.pyqtSignal(simulation.Simulation)

    def __init__(self, args=None):
        super().__init__()
        MainWindow._self = self

        self.fileName = None
        self.simServer = args.server

        if args:
            settings.setDebug(args.debug)
            if args.file:
                # TODO absolute paths
                self.fileName = args.file

        self.setObjectName("ts2_main_window")
        self.editorWindow = None
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle(self.tr("ts2 - Train Signalling Simulation - %s")
                            % __VERSION__)

        # Simulation
        self.simulation = None
        self.webSocket = None
        self.serverPID = None
        if settings.debug:
            websocket.enableTrace(True)

        # Actions  ======================================
        self.openAction = QtWidgets.QAction(self.tr("&Open..."), self)
        self.openAction.setShortcut(QtGui.QKeySequence.Open)
        self.openAction.setToolTip(self.tr("Open a simulation or a "
                                           "previously saved game"))
        self.openAction.triggered.connect(self.onOpenSimulation)

        self.closeAction = QtWidgets.QAction(self.tr("&Close"))
        self.closeAction.setShortcut(QtGui.QKeySequence.Close)
        self.closeAction.setToolTip(self.tr("Close the current simulation"))
        self.closeAction.triggered.connect(self.simulationClose)

        self.openRecentAction = QtWidgets.QAction(self.tr("Recent"), self)
        menu = QtWidgets.QMenu()
        self.openRecentAction.setMenu(menu)
        menu.triggered.connect(self.onRecent)

        self.saveGameAsAction = QtWidgets.QAction(self.tr("&Save game"), self)
        self.saveGameAsAction.setShortcut(QtGui.QKeySequence.SaveAs)
        self.saveGameAsAction.setToolTip(self.tr("Save the current game"))
        self.saveGameAsAction.triggered.connect(self.saveGame)
        self.saveGameAsAction.setEnabled(False)

        # Properties
        self.propertiesAction = QtWidgets.QAction(self.tr("Sim &Properties..."),
                                                  self)
        self.propertiesAction.setShortcut(
            QtGui.QKeySequence(self.tr("Ctrl+P"))
        )
        self.propertiesAction.setToolTip(self.tr("Edit simulation properties"))
        self.propertiesAction.triggered.connect(self.openPropertiesDialog)
        self.propertiesAction.setEnabled(False)

        # Settings
        self.settingsAction = QtWidgets.QAction(self.tr("Settings..."),
                                                self)
        self.settingsAction.setToolTip(self.tr("User Settings"))
        self.settingsAction.triggered.connect(self.openSettingsDialog)

        self.quitAction = QtWidgets.QAction(self.tr("&Quit"), self)
        self.quitAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+Q")))
        self.quitAction.setToolTip(self.tr("Quit TS2"))
        self.quitAction.triggered.connect(self.close)

        self.editorAction = QtWidgets.QAction(self.tr("&Open Editor"), self)
        self.editorAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+E")))
        self.editorAction.setToolTip(self.tr("Open the simulation editor"))
        self.editorAction.triggered.connect(self.openEditor)

        self.editorCurrAction = QtWidgets.QAction(self.tr("&Edit"), self)
        self.editorCurrAction.setToolTip(self.tr("Open this sim in editor"))
        self.editorCurrAction.triggered.connect(self.onEditorCurrent)

        # Web Links
        self.actionGroupWwww = QtWidgets.QActionGroup(self)
        self.actionGroupWwww.triggered.connect(self.onWwwAction)

        self.aboutWwwHompage = QtWidgets.QAction(self.tr("&TS2 Homepage"), self)
        self.aboutWwwHompage.setProperty("url", __PROJECT_WWW__)
        self.actionGroupWwww.addAction(self.aboutWwwHompage)

        self.aboutWwwProject = QtWidgets.QAction(self.tr("&TS2 Project"), self)
        self.aboutWwwProject.setProperty("url", __PROJECT_HOME__)
        self.actionGroupWwww.addAction(self.aboutWwwProject)

        self.aboutWwwBugs = QtWidgets.QAction(self.tr("&TS2 Bugs && Feedback"),
                                              self)
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
        self.fileMenu.addAction(self.saveGameAsAction)
        self.fileMenu.addAction(self.closeAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.propertiesAction)
        self.fileMenu.addAction(self.settingsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAction)

        # Editor Menu
        self.editorMenu = self.menuBar().addMenu(self.tr("&Editor"))
        self.editorMenu.addAction(self.editorAction)
        self.editorMenu.addAction(self.editorCurrAction)

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
        tbar, tbg = self._make_toolbar_group(self.tr("Simulation"),
                                             bg="#dddddd")
        self.addToolBar(tbar)
        tbg.addAction(self.openAction)
        tbg.addAction(self.editorCurrAction)

        # =========
        # Speed
        tbar, tbg = self._make_toolbar_group(self.tr("Speed"), bg="#aaaaaa")
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
        tbar, tbg = self._make_toolbar_group(self.tr("Zoom"), bg="white")
        self.addToolBar(tbar)
        tbg.setMaximumWidth(300)

        self.zoomWidget = widgets.ZoomWidget(self)
        self.zoomWidget.valueChanged.connect(self.zoom)
        tbg.addWidget(self.zoomWidget)

        # =========
        # Score
        tbar, tbg = self._make_toolbar_group(self.tr("Penalty"), bg="#dddddd")
        self.addToolBar(tbar)

        # Score display
        self.scoreDisplay = QtWidgets.QLCDNumber(self)
        self.scoreDisplay.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scoreDisplay.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scoreDisplay.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.scoreDisplay.setNumDigits(5)
        self.scoreDisplay.setMinimumHeight(30)
        tbg.addWidget(self.scoreDisplay)

        # =========
        # Clock
        tbar, tbg = self._make_toolbar_group(self.tr("Clock"), fg="Yellow",
                                             bg="#444444")
        self.addToolBar(tbar)

        # Pause button
        self.buttPause = QtWidgets.QToolButton(self)
        self.buttPause.setText(self.tr("Pause"))
        self.buttPause.setCheckable(True)
        self.buttPause.setAutoRaise(True)
        self.buttPause.setMaximumWidth(50)
        self.buttPause.setChecked(True)
        tbg.addWidget(self.buttPause)

        # Clock Widget
        self.clockWidget = widgets.ClockWidget(self)
        tbg.addWidget(self.clockWidget)

        # ====================
        # Sim Title
        tbar = QtWidgets.QToolBar()
        tbar.setObjectName("toolbar_label_title")
        tbar.setFloatable(False)
        tbar.setMovable(False)
        self.addToolBar(tbar)

        self.lblTitle = QtWidgets.QLabel()
        lbl_sty = "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0," \
                  " stop: 0 #fefefe, stop: 1 #CECECE);"
        lbl_sty += " color: #333333; font-size: 16pt; padding: 1px;"
        self.lblTitle.setStyleSheet(lbl_sty)
        self.lblTitle.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lblTitle.setText("no sim loaded")
        tbar.addWidget(self.lblTitle)
        tbar.layout().setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)

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

        sty = "background-color: #444444; color: white; padding: 2px;" \
              " font-size: 10pt"
        wid = QtWidgets.QScrollArea()
        self.serviceInfoPanel.setWidget(wid)
        grid = QtWidgets.QGridLayout()
        wid.setLayout(grid)
        self.lblServiceInfoCode = QtWidgets.QLabel()
        self.lblServiceInfoCode.setStyleSheet(sty)
        self.lblServiceInfoCode.setText("")
        self.lblServiceInfoCode.setMaximumWidth(100)
        grid.addWidget(self.lblServiceInfoCode, 0, 0)
        self.lblServiceInfoDescription = QtWidgets.QLabel()
        self.lblServiceInfoDescription.setText("")
        self.lblServiceInfoDescription.setStyleSheet(sty)
        self.lblServiceInfoDescription.setScaledContents(False)
        grid.addWidget(self.lblServiceInfoDescription, 0, 1)
        self.serviceInfoView = QtWidgets.QTreeView(self)
        self.serviceInfoView.setItemsExpandable(False)
        self.serviceInfoView.setRootIsDecorated(False)
        grid.addWidget(self.serviceInfoView, 1, 0, 1, 2)
        self.serviceInfoPanel.setWidget(wid)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 4)
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
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
        wid = QtWidgets.QScrollArea()
        self.placeInfoPanel.setWidget(wid)
        hb = QtWidgets.QVBoxLayout()
        wid.setLayout(hb)
        self.lblPlaceInfoName = QtWidgets.QLabel()
        self.lblPlaceInfoName.setStyleSheet(sty)
        self.lblPlaceInfoName.setText("")
        hb.addWidget(self.lblPlaceInfoName)

        self.placeInfoView = QtWidgets.QTreeView(self)
        self.placeInfoView.setItemsExpandable(False)
        self.placeInfoView.setRootIsDecorated(False)
        self.placeInfoView.setModel(placeitem.Place.selectedPlaceModel)
        hb.addWidget(self.placeInfoView)

        hb.setSpacing(0)
        hb.setContentsMargins(0, 0, 0, 0)

        self.placeInfoPanel.setWidget(wid)
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

        # Display
        self.grid = QtWidgets.QVBoxLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.addWidget(self.view)
        self.grid.setSpacing(0)
        self.board.setLayout(self.grid)
        self.setCentralWidget(self.board)

        # Editor
        self.editorOpened = False
        self.setControlsDisabled(True)

        self.refreshRecent()
        settings.restoreWindow(self)

        if args and args.file:
            if args.edit:
                self.openEditor(args.file)
                # else:
                # here we call after window is shown
        QtCore.QTimer.singleShot(100, self.onAfterShow)

    @staticmethod
    def instance():
        return MainWindow._self

    @QtCore.pyqtSlot()
    def onAfterShow(self):
        """Fires a few moments after window shows"""
        if not settings.b(settings.INITIAL_SETUP, False):
            self.openSettingsDialog()

        if not self.fileName and settings.b(settings.LOAD_LAST, False):
            actions = self.openRecentAction.menu().actions()
            if actions:
                self.fileName = actions[0].text()

        if self.fileName:
            self.loadSimulation(self.fileName)

    def onOpenSimulation(self):
        d = opendialog.OpenDialog(self)
        d.openFile.connect(self.loadSimulation)
        d.connectToServer.connect(self.connectToServer)
        d.exec_()

    @QtCore.pyqtSlot(str)
    def loadSimulation(self, fileName=None):
        """This is where the simulation server is spawn"""
        if fileName:
            self.fileName = fileName
            if zipfile.is_zipfile(fileName):
                with zipfile.ZipFile(fileName) as zipArchive:
                    zipArchive.extract("simulation.json", path=tempfile.gettempdir())
                fileName = path.join(tempfile.gettempdir(), "simulation.json")

            QtWidgets.qApp.setOverrideCursor(Qt.WaitCursor)
            logLevel = "info"
            if settings.debug:
                logLevel = "dbug"

            if not self.simServer:
                cmd = settings.serverLoc
            else:
                cmd = self.simServer

            self.simulationClose()
            try:
                serverCmd = subprocess.Popen([cmd, "-loglevel", logLevel, fileName])
            except FileNotFoundError:
                QtWidgets.qApp.restoreOverrideCursor()
                QtWidgets.QMessageBox.critical(self, "Configuration Error",
                                               "ts2-sim-server executable not found in the server directory.\n"
                                               "Go to File->Options to download it")
                raise
            except OSError as e:
                QtWidgets.qApp.restoreOverrideCursor()
                dialogs.ExceptionDialog.popupException(self, e)
                raise
            self.serverPID = serverCmd.pid
            settings.addRecent(self.fileName)
            time.sleep(1)
            QtWidgets.qApp.restoreOverrideCursor()
            self.connectToServer("localhost", "22222")
        else:
            self.onOpenSimulation()

    def connectToServer(self, host, port):
        QtWidgets.qApp.setOverrideCursor(Qt.WaitCursor)
        self.webSocket = WebSocketController("ws://%s:%s/ws" % (host, port), self)
        self.webSocket.connectionReady.connect(self.simulationLoad)

    @QtCore.pyqtSlot()
    def simulationLoad(self):
        def load_sim(data):
            simData = json.dumps(data)
            self.simulation = simulation.load(self, io.StringIO(simData))
            self.lblTitle.setText(self.simulation.option("title"))
            self.setWindowTitle(self.tr(
                "ts2 - Train Signalling Simulator - %s") % self.simulation.option("title"))
            self.simulationConnectSignals()
            self.webSocket.sendRequest("server", "renotify")
            self.simulationLoaded.emit(self.simulation)

            self.refreshRecent()
            self.setControlsDisabled(False)

            QtWidgets.QApplication.restoreOverrideCursor()

        self.webSocket.sendRequest("simulation", "dump", callback=load_sim)

    def simulationConnectSignals(self):
        """Connects the signals and slots to the simulation."""

        # Set models
        self.trainInfoView.setModel(self.simulation.selectedTrainModel)
        self.serviceInfoView.setModel(self.simulation.selectedServiceModel)
        self.loggerView.setModel(self.simulation.messageLogger)
        # Set scene
        self.view.setScene(self.simulation.scene)
        # TrainListView
        self.trainListView.trainSelected.connect(
            self.simulation.trainSelected
        )
        self.simulation.trainSelected.connect(
            self.simulation.selectedTrainModel.setTrainByTrainId
        )
        self.simulation.trainSelected.connect(
            self.serviceListView.updateServiceSelection
        )
        self.trainListView.trainSelected.connect(self.centerViewOnTrain)
        # ServiceListView
        self.serviceListView.serviceSelected.connect(
            self.simulation.selectedServiceModel.setServiceCode
        )
        self.serviceListView.serviceSelected.connect(
            self.onServiceSelected
        )
        # TrainInfoView
        self.simulation.trainStatusChanged.connect(
            self.trainInfoView.model().update
        )
        self.simulation.timeChanged.connect(
            self.trainInfoView.model().updateSpeed
        )
        # Place view
        placeitem.Place.selectedPlaceModel.modelReset.connect(
            self.onPlaceSelected
        )
        # MessageLogger
        self.simulation.messageLogger.rowsInserted.connect(
            self.loggerView.scrollToBottom
        )
        # Panel
        self.simulation.timeChanged.connect(self.clockWidget.setTime)
        self.simulation.simulationPaused.connect(self.checkPauseButton)
        self.simulation.scorer.scoreChanged.connect(
            self.scoreDisplay.display
        )
        self.scoreDisplay.display(self.simulation.scorer.score)
        self.simulation.timeFactorChanged.connect(self.timeFactorSpinBox.setValue)
        self.buttPause.toggled.connect(self.simulation.pause)
        self.timeFactorSpinBox.valueChanged.connect(
            self.simulation.setTimeFactor
        )
        self.timeFactorSpinBox.setValue(
            int(self.simulation.option("timeFactor"))
        )

        # Menus
        self.saveGameAsAction.setEnabled(True)
        self.propertiesAction.setEnabled(True)

    def simulationDisconnect(self):
        """Disconnects the simulation for deletion."""
        # Unset models
        self.trainListView.setModel(None)
        self.trainInfoView.setModel(None)
        self.serviceInfoView.setModel(None)
        self.serviceListView.setModel(None)
        self.loggerView.setModel(None)
        self.placeInfoView.setModel(None)
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
        # Panel
        try:
            self.simulation.timeChanged.disconnect()
        except TypeError:
            pass
        try:
            self.simulation.simulationPaused.disconnect()
        except TypeError:
            pass
        try:
            self.simulation.scorer.scoreChanged.disconnect()
        except TypeError:
            pass
        self.scoreDisplay.display(0)
        try:
            self.simulation.timeFactorChanged.disconnect()
        except TypeError:
            pass
        try:
            self.buttPause.toggled.disconnect()
        except TypeError:
            pass
        try:
            self.timeFactorSpinBox.valueChanged.disconnect()
        except TypeError:
            pass
        self.timeFactorSpinBox.setValue(1)
        self.buttPause.setChecked(True)

        # Menus
        self.saveGameAsAction.setEnabled(False)
        self.propertiesAction.setEnabled(False)
        # Clock
        self.clockWidget.setTime(QtCore.QTime())

        self.webSocket.removeHandlers()

    def simulationClose(self):
        if self.simulation is not None:
            self.simulationDisconnect()
            self.simulation = None
            self.fileName = None
            if self.serverPID:
                os.kill(self.serverPID, signal.SIGTERM)
                self.serverPID = None
            self.setControlsDisabled(True)

    @QtCore.pyqtSlot()
    def saveGame(self):
        """Saves the current game to file."""
        if self.simulation is not None:
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

    @QtCore.pyqtSlot(int)
    def zoom(self, percent):
        transform = QtGui.QTransform()
        transform.scale(percent / 100, percent / 100)
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
                                    (__VERSION__,
                                     QtCore.QDate.currentDate().year(),
                                     __ORG_CONTACT__,
                                     __PROJECT_WWW__))
        if self.editorOpened:
            self.editorWindow.activateWindow()

    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenu(self, pos):
        if self.sender() == self.trainInfoView:
            train = self.trainInfoView.model().train
            if train is not None:
                train.showTrainActionsMenu(self.trainInfoView,
                                           self.trainInfoView.mapToGlobal(pos))

    @QtCore.pyqtSlot()
    def onEditorCurrent(self):
        if self.fileName:
            self.openEditor(fileName=self.fileName)

    @QtCore.pyqtSlot()
    def openEditor(self, fileName=None):
        """This slot opens the editor window if it is not already opened"""
        if not self.editorOpened:
            self.editorWindow = editorwindow.EditorWindow(self, fileName=fileName)
            self.editorWindow.simulationConnect()
            self.editorWindow.closed.connect(self.onEditorClosed)
            self.editorOpened = True
            self.editorWindow.show()
        else:
            self.editorWindow.activateWindow()

    @QtCore.pyqtSlot()
    def onEditorClosed(self):
        self.editorOpened = False

    @QtCore.pyqtSlot(bool)
    def checkPauseButton(self, paused):
        self.buttPause.setChecked(paused)

    @QtCore.pyqtSlot()
    def openPropertiesDialog(self):
        """Pops-up the simulation properties dialog."""
        if self.simulation is not None:
            propertiesDialog = dialogs.PropertiesDialog(self, self.simulation)
            propertiesDialog.exec_()

    @QtCore.pyqtSlot(str)
    def openReassignServiceWindow(self, trainId):
        """Opens the reassign service window."""
        if self.simulation is not None:
            dialogs.ServiceAssignDialog.reassignServiceToTrain(
                self.simulation, trainId
            )

    @QtCore.pyqtSlot(str)
    def openSplitTrainWindow(self, trainId):
        """Opens the split train dialog window."""
        if self.simulation is not None:
            dialogs.SplitTrainDialog.getSplitIndexPopUp(
                self.simulation.trains[trainId]
            )

    def refreshRecent(self):
        """Reload the recent menu"""
        menu = self.openRecentAction.menu()
        menu.clear()
        act = []
        for fileName in settings.getRecent():
            if not fileName:
                continue
            if os.path.exists(fileName):
                act.append(menu.addAction(fileName))

    def onRecent(self, act):
        """Open a  recent item"""
        self.loadSimulation(fileName=act.iconText())

    def closeEvent(self, event):
        """Save window postions on close"""
        settings.saveWindow(self)
        settings.sync()
        self.simulationClose()
        if self.webSocket:
            self.webSocket.wsThread.exit()
        super().closeEvent(event)

    def onWheelChanged(self, direction):
        """Handle scrollwheel on canvas, sent from
        :class:`~ts2.gui.widgets.XGraphicsView` """
        percent = self.zoomWidget.spinBox.value()
        self.zoomWidget.spinBox.setValue(percent + (direction * 10))

    def onWwwAction(self, act):
        url = act.property("url")
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def _make_toolbar_group(self, title, bg=None, fg=None):
        """Creates a toolbar containing a `ToolBarGroup`"""
        tbar = QtWidgets.QToolBar()
        tbar.setObjectName("toolbar_" + title)
        tbar.setFloatable(False)
        tbar.setMovable(True)

        tbg = widgets.ToolBarGroup(self, title=title, bg=bg, fg=fg)
        tbar.addWidget(tbg)
        return tbar, tbg

    def onServiceSelected(self, serviceCode):
        serv = self.simulation.service(serviceCode)
        self.lblServiceInfoCode.setText(serviceCode)
        self.lblServiceInfoDescription.setText(serv.description)

    def onPlaceSelected(self):
        place = placeitem.Place.selectedPlaceModel.place
        if place:
            self.lblPlaceInfoName.setText(place.name)

    def setControlsDisabled(self, state):
        if not state and self.fileName:
            self.editorCurrAction.setDisabled(False)
        else:
            self.editorCurrAction.setDisabled(True)
        self.zoomWidget.setDisabled(state)
        self.timeFactorSpinBox.setDisabled(state)
        self.buttPause.setDisabled(state)
        self.clockWidget.setDisabled(state)

    def openSettingsDialog(self):
        d = settingsdialog.SettingsDialog(self)
        d.exec_()

    def centerViewOnTrain(self, trainId):
        """Centers the graphics view on the given train."""
        if self.simulation:
            train = self.simulation.trains[int(trainId)]
            if train.isOnScenery():
                trackItem = train.trainHead.trackItem
                self.view.centerOn(trackItem.graphicsItem)


def wsOnMessage(ws, message):
    if settings.debug:
        print("< %s" % message)
    ws.onMessage(message)


def wsOnError(ws, error):
    print("WS Error", error)


def wsOnClose(ws):
    QtCore.qDebug("WS Closed")
    ws.connectionClosed.emit()


class WebSocketConnection(websocket.WebSocketApp, QtCore.QObject):

    def __init__(self, controller, url):
        websocket.WebSocketApp.__init__(self, url, on_message=wsOnMessage, on_error=wsOnError, on_close=wsOnClose)
        QtCore.QObject.__init__(self)
        self.controller = controller
        self.ready = False

    messageReceived = QtCore.pyqtSignal(str)
    connectionReady = QtCore.pyqtSignal()
    connectionClosed = QtCore.pyqtSignal()

    def onMessage(self, message):
        self.messageReceived.emit(message)


class WebSocketController(QtCore.QObject):

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self._requests = []
        self._callbacks = {}
        self._handlers = {}
        self._counter = 1
        self.conn = WebSocketConnection(self, url)
        self.conn.messageReceived.connect(self.executeCallback)
        self.conn.connectionReady.connect(self.connectionReady)
        self.conn.connectionClosed.connect(self.onClosed)

        def login(w):
            def setReady(msg):
                if msg["status"] == "OK":
                    w.connectionReady.emit()
                else:
                    raise Exception("Error while connecting to simulation server", msg["message"])

            w.controller.sendRequest("server", "register", {"type": "client", "token": "client-secret"},
                                     callback=setReady)

        self.conn.on_open = login
        self.wsThread = WebSocketThread(self.conn)
        self.wsThread.start()

    connectionReady = QtCore.pyqtSignal()

    def sendRequest(self, obj, action, params=None, callback=None):
        """Send a websocket request. Response will be handled by given callback.
        :param obj: server object to call
        :param action: server action to execute
        :param params: parameters to send for action as dict
        :param callback: function taking a msg dict as argument
        """
        data = {
            "id": self._counter,
            "object": obj,
            "action": action,
            "params": params,
        }
        msg = json.dumps(data)
        if settings.debug:
            print("> %s" % data)
        self.conn.send(msg)
        self._callbacks[self._counter] = callback
        self._counter += 1

    @QtCore.pyqtSlot(str)
    def executeCallback(self, message):
        """Call the callback with the given id and remove it from the registry.
        :param message: raw JSON message received
        """
        msg = json.loads(message)
        if msg["msgType"] == "response":
            msgID = msg["id"]
            msgData = msg["data"]
            if msgID not in self._callbacks:
                if settings.debug:
                    print("msgID not in registry: %s" % msgID)
                return
            if self._callbacks[msgID]:
                self._callbacks[msgID](msgData)
            del self._callbacks[msgID]
        elif msg["msgType"] == "notification":
            msgData = msg["data"]
            if self._handlers.get(msgData["name"]):
                hData = self._handlers[msgData["name"]]
                hData[1](hData[0], msgData["object"])

    def registerHandler(self, eventName, sim, handler):
        self.sendRequest("server", "addListener", params={"event": "%s" % eventName})
        self._handlers[eventName] = (sim, handler)

    def removeHandlers(self):
        for eventName in self._handlers.keys():
            self.sendRequest("server", "removeListener", params={"event": "%s" % eventName})
            self._handlers = {}

    def onClosed(self):
        QtWidgets.QApplication.restoreOverrideCursor()
        mainWindow = self.parent()
        if not mainWindow.fileName:
            # Only notify if we are connected to a network simulation
            QtWidgets.QMessageBox.critical(
                mainWindow,
                mainWindow.tr("Connection closed"),
                mainWindow.tr("The server closed the connection to the simulation."),
                QtWidgets.QMessageBox.Ok
            )
        mainWindow.simulationClose()


class WebSocketThread(QtCore.QThread):

    def __init__(self, ws, parent=None):
        super(WebSocketThread, self).__init__(parent)
        self.websocket = ws

    def run(self):
        self.websocket.run_forever()
