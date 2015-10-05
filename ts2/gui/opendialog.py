
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
    description = 1
    file_name = 2
    file_path = 3

class TAB:
    browse = 0
    recent = 1
    filesystem = 2


class OpenDialog(QtWidgets.QDialog):
    """Popup files for the user to open a sim"""

    def __init__(self, parent, tab=0):
        """Constructor for the DownloadSimulationsDialog."""
        super().__init__(parent)
        self.setWindowTitle(
            self.tr("Open Dialog")
        )
        self.setMinimumWidth(800)
        self.setMinimumHeight(800)

        containerLayout = QtWidgets.QVBoxLayout()
        containerLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(containerLayout)
        containerLayout.addSpacing(10)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        containerLayout.addLayout(mainLayout)

        # Tab Widget
        self.tabWidget = QtWidgets.QTabWidget()
        mainLayout.addWidget(self.tabWidget)

        # =====================================
        # Browse Sims
        self.browseWidget = QtWidgets.QWidget()
        self.browseLayout = QtWidgets.QVBoxLayout()
        self.browseLayout.setContentsMargins(0, 0, 0, 0)
        self.browseWidget.setLayout(self.browseLayout)
        self.tabWidget.addTab(self.browseWidget, "Downloaded")

        tbBrowse = QtWidgets.QToolBar()
        self.browseLayout.addWidget(tbBrowse)

        self.txtUrl = QtWidgets.QLineEdit(self)
        self.txtUrl.setText(ts2.get_info().get('simulations_repo'))
        tbBrowse.addWidget(self.txtUrl)

        self.buttDownload = tbBrowse.addAction("Download", self.onDownload)


        self.treeSims = QtWidgets.QTreeWidget()
        self.browseLayout.addWidget(self.treeSims)
        hitem = self.treeSims.headerItem()
        hitem.setText(C.name, "Name")
        hitem.setText(C.description, "Description")
        hitem.setText(C.file_name, "File")
        hitem.setText(C.file_path, "Path")
        self.treeSims.setColumnHidden(C.file_path, True)
        self.treeSims.itemDoubleClicked.connect(self.onTreeSimsItemDblClicked)


        # =====================================
        # Recent
        #self.recentWidget = QtWidgets.QWidget()
        #self.recentLayout = QtWidgets.QVBoxLayout()
        #self.recentLayout.setContentsMargins(0, 0, 0, 0)
        #self.recentWidget.setLayout(self.browseLayout)


        self.treeRecent = QtWidgets.QTreeWidget()
        self.tabWidget.addTab(self.treeRecent, "Recent")

        #self.recentLayout.addWidget(self.treeSims)
        hitem = self.treeRecent.headerItem()
        #hitem.setText(C.name, "Name")
        #hitem.setText(C.description, "Description")
        #hitem.setText(C.file_name, "File")
        hitem.setText(0, "Path")
        #self.treeRecent.setColumnHidden(C.file_path, True)
        self.treeRecent.itemDoubleClicked.connect(self.onTreeRecentItemDblClicked)


        # =====================================
        # Browse
        self.fileModel = QtWidgets.QFileSystemModel()
        print(QtCore.QDir.homePath())


        self.treeFiles = QtWidgets.QTreeView()
        self.treeFiles.setModel(self.fileModel)

        self.fileModel.setRootPath( QtCore.QDir.homePath() )

        self.tabWidget.addTab(self.treeFiles, "Browse")

        # =================================
        # Bottom status
        self.statusBar = widgets.StatusBar()
        containerLayout.addWidget(self.statusBar)
        if settings.debug:
            self.statusBar.showMessage(settings.simulationsDir)

        self.onRefreshSims()

    def onDownload(self):

        #print("onDownload")
        QtWidgets.qApp.setOverrideCursor(Qt.WaitCursor)

        if settings.debug:
            url = "http://localhost/~ts2/ts2-data-master.zip"
        else:
            url = "%s/archive/master.zip" % self.txtUrl.text().strip('/')

        self.statusBar.showBusy(True)
        self.statusBar.showMessage("Requesting %s" % url)

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
        self.onRefreshSims()


    def onRefreshSims(self):

        self.statusBar.showMessage("Loading")
        self.treeSims.clear()

        ts2_files = []
        for root, dirnames, filenames in os.walk(settings.simulationsDir):
            for filename in fnmatch.filter(filenames, '*.ts2'):
                ts2_files.append(os.path.join(root, filename))


        for file_path in ts2_files:
            with zipfile.ZipFile(file_path, "r") as zippy:

                # wtf, confused why bytes returned
                bytes =  zippy.read("simulation.json")
                data = json.loads( bytes.decode() )
                nfo = data['options']

                item = QtWidgets.QTreeWidgetItem()
                item.setText(C.name, nfo['title'])
                item.setText(C.description, nfo['description'])
                item.setText(C.file_name, os.path.basename(file_path))
                item.setText(C.file_path, file_path)
                self.treeSims.addTopLevelItem(item)

        self.treeSims.resizeColumnToContents(C.name)
        self.statusBar.showMessage("")

    def onTreeSimsItemDblClicked(self, item):
        print(item)
        file_path = item.text(C.file_path)

    def onTreeRecentItemDblClicked(self, item):
        file_path = item.text(0)

