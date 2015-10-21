
import os
import tempfile
import zipfile
import fnmatch
from urllib import request

from Qt import QtCore, QtWidgets, Qt
import json

import ts2
from ts2.utils import settings
from ts2.gui import widgets

translate = QtWidgets.qApp.translate


class C:
    name = 0
    file_name = 1
    description = 2
    file_path = 3


class NAV:
    sims = 0
    recent = 1
    filesystem = 2


class OpenDialog(QtWidgets.QDialog):
    """Open sim file dialog"""

    openFile = QtCore.pyqtSignal(str)

    def __init__(self, parent, tab=0):
        """Constructor for the OpenDialog."""
        super().__init__(parent)
        self.setWindowTitle(
            self.tr("Open Simulation")
        )
        self.setMinimumWidth(800)
        self.setMinimumHeight(800)

        m = 5
        containerLayout = QtWidgets.QHBoxLayout()
        containerLayout.setContentsMargins(m, m, m, m)
        self.setLayout(containerLayout)

        # ========================================
        # Left Bar + navigation
        self.leftBar = QtWidgets.QVBoxLayout()
        self.leftBar.setContentsMargins(0, 0, 0, 0)
        containerLayout.addLayout(self.leftBar)

        self.buttGroup = QtWidgets.QButtonGroup()
        self.buttGroup.setExclusive(True)

        self.leftBar.addWidget(self._make_nav_button(self.tr("Sims"), NAV.sims))
        self.leftBar.addWidget(
            self._make_nav_button(self.tr("Recent"), NAV.recent)
        )
        self.leftBar.addWidget(
            self._make_nav_button(self.tr("Browse"), NAV.filesystem)
        )
        self.leftBar.addStretch(20)

        # ==================================================================================
        # Stack widget for main
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        containerLayout.addLayout(mainLayout)

        self.stackWidget = QtWidgets.QStackedWidget()
        mainLayout.addWidget(self.stackWidget, 200)

        # =================
        # Downloaded Sims
        self.downloadWidget = QtWidgets.QWidget()
        self.downloadLayout = QtWidgets.QVBoxLayout()
        self.downloadLayout.setContentsMargins(0, 0, 0, 0)
        self.downloadWidget.setLayout(self.downloadLayout)
        self.stackWidget.addWidget(self.downloadWidget)

        tbBrowse = QtWidgets.QToolBar()
        self.downloadLayout.addWidget(tbBrowse)

        self.txtUrl = QtWidgets.QLineEdit(self)
        self.txtUrl.setText(ts2.get_info().get('simulations_repo'))
        tbBrowse.addWidget(self.txtUrl)

        self.buttDownload = tbBrowse.addAction("Download", self.onDownload)

        self.treeSims = QtWidgets.QTreeWidget()
        self.downloadLayout.addWidget(self.treeSims)
        hitem = self.treeSims.headerItem()
        hitem.setText(C.name, "Name")
        hitem.setText(C.description, "Description")
        hitem.setText(C.file_name, "File")
        hitem.setText(C.file_path, "Path")
        self.treeSims.setColumnHidden(C.file_path, True)
        self.treeSims.header().setStretchLastSection(True)
        self.treeSims.itemDoubleClicked.connect(self.onTreeSimsItemDblClicked)

        # =====================================
        # Recent

        self.treeRecent = QtWidgets.QTreeWidget()
        self.stackWidget.addWidget(self.treeRecent)

        hitem = self.treeRecent.headerItem()
        hitem.setText(0, "Path")

        self.treeRecent.itemDoubleClicked.connect(
            self.onTreeRecentItemDblClicked
        )

        # =====================================
        # Browse
        self.filesModel = QtWidgets.QFileSystemModel()
        self.filesModel.setRootPath(QtCore.QDir.homePath())
        self.filesModel.setNameFilters(["*.ts2", "*.json"])

        self.treeFiles = QtWidgets.QTreeView()
        self.treeFiles.setModel(self.filesModel)

        self.stackWidget.addWidget(self.treeFiles)

        self.treeFiles.doubleClicked.connect(
            self.onTreeBrowseItemDblClicked
        )

        # =================================
        # Bottom status
        self.statusBar = widgets.StatusBar()
        mainLayout.addWidget(self.statusBar, 0)
        if settings.debug:
            self.statusBar.showMessage(settings.simulationsDir)

        self.buttGroup.buttonToggled.connect(self.onNavButtClicked)
        self.buttGroup.button(tab).setChecked(True)

    def onDownload(self):
        """Downloads zip when Download button clicked"""
        QtWidgets.qApp.setOverrideCursor(Qt.WaitCursor)

        if settings.debug:
            url = "http://localhost/~ts2/ts2-data-master.zip"
        else:
            url = "%s/archive/master.zip" % self.txtUrl.text().strip('/')

        self.statusBar.showBusy(True)
        self.statusBar.showMessage("Requesting %s" % url)
        self.buttDownload.setDisabled(True)

        response = request.urlopen(url)

        with tempfile.TemporaryFile() as tmpFile:
            tmpFile.write(response.read())
            with zipfile.ZipFile(tmpFile) as zipArchive:
                for fileName in zipArchive.namelist():
                    fs = fileName.split('/', 1)
                    fn = fs[1] if len(fs) > 1 else fs[0]
                    if fileName.endswith(".ts2"):
                        fName = os.path.join(settings.simulationsDir, fn)
                        os.makedirs(os.path.dirname(fName), exist_ok=True)
                        with open(fName, 'wb') as f:
                            f.write(zipArchive.read(fileName))

                    elif fileName.endswith(".tsl"):
                        fName = os.path.join(settings.userDataDir,
                                             os.path.basename(fileName))
                        with open(fName, 'wb') as f:
                            f.write(zipArchive.read(fileName))

                    elif fileName.endswith(".json"):
                        fName = os.path.join(settings.simulationsDir,
                                             fn.replace(".json", ".ts2"))
                        os.makedirs(os.path.dirname(fName), exist_ok=True)
                        with zipfile.ZipFile(fName, "w") as ts2Zip:
                            ts2Zip.writestr("simulation.json",
                                            zipArchive.read(fileName))

        QtWidgets.qApp.restoreOverrideCursor()

        self.statusBar.showBusy(False)
        self.statusBar.showMessage("Download done", timeout=2)
        self.buttDownload.setDisabled(False)
        self.onRefreshSims()

    def onNavButtClicked(self, butt):

        idx = self.buttGroup.id(butt)

        if idx == NAV.sims:
            self.onRefreshSims()

        elif idx == NAV.recent:
            self.onRefreshRecent()

        self.stackWidget.setCurrentIndex(idx)

    def onRefreshSims(self):
        """Reloads the simulations dir"""
        self.statusBar.showMessage("Loading")
        self.treeSims.clear()

        ts2_files = {}
        for root, dirnames, filenames in os.walk(settings.simulationsDir):
            for filename in fnmatch.filter(filenames, '*.ts2'):
                d = root.split(QtCore.QDir.separator())[-1]
                if d not in ts2_files:
                    ts2_files[d] = []
                ts2_files[d].append(os.path.join(root, filename))

        for folder in sorted(ts2_files.keys()):
            pitem = QtWidgets.QTreeWidgetItem()
            pitem.setText(C.name, folder)
            pitem.setFirstColumnSpanned(True)
            self.treeSims.addTopLevelItem(pitem)
            for file_path in ts2_files[folder]:
                with zipfile.ZipFile(file_path, "r") as zippy:

                    # wtf, confused why bytes returned
                    bytesData = zippy.read("simulation.json")
                    data = json.loads(bytesData.decode())
                    nfo = data['options']

                    item = QtWidgets.QTreeWidgetItem(pitem)
                    item.setText(C.name, nfo['title'])
                    item.setText(C.description, nfo['description'])
                    item.setText(C.file_name, os.path.basename(file_path))
                    item.setText(C.file_path, file_path)
            pitem.setExpanded(True)

        self.treeSims.resizeColumnToContents(C.name)
        self.statusBar.showMessage("")

    def onRefreshRecent(self):
        """Reloads the recent items"""
        self.treeRecent.clear()
        for fn in settings.getRecent():
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, fn)
            self.treeRecent.addTopLevelItem(item)

    def onTreeSimsItemDblClicked(self, item):
        if self.treeSims.indexOfTopLevelItem(item) != -1:
            return
        filePath = item.text(C.file_path)
        self.openFile.emit(filePath)
        self.accept()

    def onTreeRecentItemDblClicked(self, item):
        filePath = item.text(0)
        self.openFile.emit(filePath)
        self.accept()

    def onTreeBrowseItemDblClicked(self, index):
        filePath = index.model().filePath(index)
        if filePath.endswith(".ts2") or filePath.endswith(".json") or \
                filePath.endswith(".tsg"):
            self.openFile.emit(filePath)
            self.accept()

    def _make_nav_button(self, txt, idx):
        butt = QtWidgets.QToolButton()
        butt.setText(txt)
        butt.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        butt.setCheckable(True)
        butt.setStyleSheet("font-weight: bold; text-align: center;"
                           " font-size: 14pt;")
        butt.setFixedWidth(100)
        butt.setAutoRaise(True)
        self.buttGroup.addButton(butt, idx)
        return butt
