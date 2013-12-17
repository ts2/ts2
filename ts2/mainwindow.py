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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

from ts2 import simulation, scenery, utils, editor
from ts2.gui import dialogs, trainlistview, servicelistview, widgets


class MainWindow(QtGui.QMainWindow):
    """ TODO Document MainWindow Class"""

    def __init__(self):
        super().__init__()
        MainWindow._self = self
        self.setWindowState(Qt.WindowMaximized)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle(self.tr("ts2 - Train Signalling Simulation"))

        # Simulation
        self.simulation = simulation.Simulation(self)

        # Actions
        self.openAction = QtGui.QAction(self.tr("&Open..."), self)
        self.openAction.setShortcut(QtGui.QKeySequence.Open)
        self.openAction.setToolTip(self.tr("Open a simulation"))
        self.openAction.triggered.connect(self.loadSimulation)

        self.quitAction = QtGui.QAction(self.tr("&Quit"), self)
        self.quitAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+Q")))
        self.quitAction.setToolTip(self.tr("Quit TS2"))
        self.quitAction.triggered.connect(self.close)

        self.editorAction = QtGui.QAction(self.tr("&Editor"), self)
        self.editorAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+E")))
        self.editorAction.setToolTip(self.tr("Open the simulation editor"))
        self.editorAction.triggered.connect(self.openEditor)

        self.aboutAction = QtGui.QAction(self.tr("&About TS2..."), self)
        self.aboutAction.setToolTip(self.tr("About TS2"))
        self.aboutAction.triggered.connect(self.showAboutBox)

        self.aboutQtAction = QtGui.QAction(self.tr("About Qt..."), self)
        self.aboutQtAction.setToolTip(self.tr("About Qt"))
        self.aboutQtAction.triggered.connect(QtGui.QApplication.aboutQt)

        # Menu
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAction)
        self.editorMenu = self.menuBar().addAction(self.editorAction)
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAction)
        self.helpMenu.addAction(self.aboutQtAction)
        self.menuBar().setCursor(Qt.PointingHandCursor)

        # Dock Widgets
        self.trainInfoPanel = QtGui.QDockWidget(self.tr("Train Information"),
                                                self)
        self.trainInfoPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable|
                                        QtGui.QDockWidget.DockWidgetFloatable)
        self._trainInfoView = QtGui.QTreeView(self)
        self._trainInfoView.setItemsExpandable(False)
        self._trainInfoView.setRootIsDecorated(False)
        self._trainInfoView.setModel(self.simulation.selectedTrainModel)
        self._trainInfoView.setContextMenuPolicy(Qt.CustomContextMenu)
        self._trainInfoView.customContextMenuRequested.connect(
                                        self.showContextMenu)
        self.simulation.trainStatusChanged.connect(
                                        self._trainInfoView.model().update)
        self.trainInfoPanel.setWidget(self._trainInfoView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.trainInfoPanel)

        self.serviceInfoPanel = QtGui.QDockWidget(
                                            self.tr("Service Information"),
                                            self)
        self.serviceInfoPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable|
                                        QtGui.QDockWidget.DockWidgetFloatable)
        self._serviceInfoView = QtGui.QTreeView(self)
        self._serviceInfoView.setItemsExpandable(False)
        self._serviceInfoView.setRootIsDecorated(False)
        self._serviceInfoView.setModel(self.simulation.selectedServiceModel)
        self.serviceInfoPanel.setWidget(self._serviceInfoView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.serviceInfoPanel)

        self.placeInfoPanel = QtGui.QDockWidget(
                                        self.tr("Station Information"), self)
        self.placeInfoPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable|
                                        QtGui.QDockWidget.DockWidgetFloatable)
        self._placeInfoView = QtGui.QTreeView(self)
        self._placeInfoView.setItemsExpandable(False)
        self._placeInfoView.setRootIsDecorated(False)
        self._placeInfoView.setModel(scenery.Place.selectedPlaceModel)
        self.placeInfoPanel.setWidget(self._placeInfoView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.placeInfoPanel)

        self.trainListPanel = QtGui.QDockWidget(self.tr("Trains"), self)
        self.trainListPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable|
                                        QtGui.QDockWidget.DockWidgetFloatable)
        self._trainListView = trainlistview.TrainListView(
                                                    self, self.simulation)
        self._trainListView.trainSelected.connect(
                    self.simulation.selectedTrainModel.setTrainByServiceCode)
        self.simulation.trainSelected.connect(
                    self._trainListView.updateTrainSelection)
        self.trainListPanel.setWidget(self._trainListView)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.trainListPanel)

        self.serviceListPanel = QtGui.QDockWidget(self.tr("Services"), self)
        self.serviceListPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable|
                                        QtGui.QDockWidget.DockWidgetFloatable)
        self._serviceListView = servicelistview.ServiceListView(
                                                    self, self.simulation)
        self._serviceListView.serviceSelected.connect(
                        self.simulation.selectedServiceModel.setServiceCode)
        self._trainListView.trainSelected.connect(
                        self._serviceListView.updateServiceSelection)
        self.serviceListPanel.setWidget(self._serviceListView)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.serviceListPanel)
        self.tabifyDockWidget(self.serviceListPanel, self.trainListPanel)

        self.loggerPanel = QtGui.QDockWidget(self.tr("Messages"), self)
        self.loggerPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable|
                                        QtGui.QDockWidget.DockWidgetFloatable)
        self.loggerView = QtGui.QTreeView(self)
        self.loggerView.setItemsExpandable(False)
        self.loggerView.setRootIsDecorated(False)
        self.loggerView.setHeaderHidden(True)
        self.loggerView.setPalette(QtGui.QPalette(Qt.black))
        self.loggerView.setVerticalScrollMode(
                                        QtGui.QAbstractItemView.ScrollPerItem)
        self.simulation.messageLogger.rowsInserted.connect(
                                            self.loggerView.scrollToBottom)
        self.loggerView.setModel(self.simulation.messageLogger)
        self.loggerPanel.setWidget(self.loggerView)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.loggerPanel)

        # board
        self.board = QtGui.QWidget(self)

        # Canvas
        self._view = QtGui.QGraphicsView(self.simulation.scene, self.board)
        self._view.setInteractive(True)
        self._view.setRenderHint(QtGui.QPainter.Antialiasing, False)
        self._view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self._view.setBackgroundBrush(QtGui.QBrush(Qt.black))

        # Panel
        self.panel = widgets.Panel(self.board, self.simulation);
        self.simulation.timeChanged.connect(self.panel.clock.setTime)
        self.panel.zoomChanged.connect(self.zoom)

        # Display
        self.grid = QtGui.QVBoxLayout()
        self.grid.addWidget(self._view)
        self.grid.addWidget(self.panel)
        self.grid.setMargin(0)
        self.grid.setSpacing(0)
        self.board.setLayout(self.grid)
        self.setCentralWidget(self.board)

        # Editor
        self.editorOpened = False

        # DEBUG
        #self.loadSimulation()
        #self.openEditor()

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

    @QtCore.pyqtSlot()
    def loadSimulation(self):
        ### DEBUG
        #fileName = "/home/nicolas/Progs/GitHub/ts2/data/drain.ts2";

        fileName = QtGui.QFileDialog.getOpenFileName(
                           self,
                           self.tr("Open a simulation"),
                           QtCore.QDir.currentPath(),
                           self.tr("TS2 simulation files (*.ts2)"))
        if fileName != "":
            QtGui.QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                self.simulation.reload(fileName)
            except utils.FormatException as err:
                QtGui.QMessageBox.critical(self,
                             self.tr("Bad version of TS2 simulation file"),
                             str(err),
                             QtGui.QMessageBox.Ok)
            except Exception as err:
                gui.dialogs.ExceptionDialog.popupException(self, err)
            else:
                self.setWindowTitle(self.tr(
                        "ts2 - Train Signalling Simulation - %s") % fileName)
            QtGui.QApplication.restoreOverrideCursor()

    @QtCore.pyqtSlot(int)
    def zoom(self, percent):
        self._view.setMatrix(QtGui.QMatrix(percent/100, 0, 0,
                                           percent/100, 0, 0))

    @QtCore.pyqtSlot()
    def showAboutBox(self):
        """Shows the about box"""
        QtGui.QMessageBox.about(self, self.tr("About TS2"), self.tr(
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
            train = self._trainInfoView.model().train
            if train is not None:
                train.showTrainActionsMenu(self._trainInfoView,
                                        self._trainInfoView.mapToGlobal(pos))

    @QtCore.pyqtSlot()
    def openEditor(self):
        """This slot opens the editor window if it is not already opened"""
        if not self.editorOpened:
            self.editorWindow = editor.EditorWindow(self)
            self.editorWindow.closed.connect(self.editorIsClosed)
            self.editorOpened = True
            self.editorWindow.show()
        else:
            self.editorWindow.activateWindow()


    @QtCore.pyqtSlot()
    def editorIsClosed(self):
        self.editorOpened = False
