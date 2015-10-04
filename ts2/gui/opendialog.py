

from Qt import QtCore, QtWidgets, Qt

import ts2
from ts2.gui import servicelistview

translate = QtWidgets.qApp.translate

class OpenDialog(QtWidgets.QDialog):
    """Popup files for the user to open a sim"""

    def __init__(self, parent):
        """Constructor for the DownloadSimulationsDialog."""
        super().__init__(parent)
        self.setWindowTitle(
            self.tr("Open Dialog")
        )
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)

        containerLayout = QtWidgets.QVBoxLayout()
        self.setLayout(containerLayout)

        mainLayout = QtWidgets.QHBoxLayout()
        containerLayout.addLayout(mainLayout)

        # Tab Widget
        self.tabWidget = QtWidgets.QTabWidget()
        mainLayout.addWidget(self.tabWidget)

        # =====================================
        # Browse Sims
        self.browseWidget = QtWidgets.QWidget()
        self.browseLayout = QtWidgets.QVBoxLayout()
        self.browseWidget.setLayout(self.browseLayout)
        self.tabWidget.addTab(self.browseWidget, "Browse Local")

        tbBrowse = QtWidgets.QToolBar()
        self.browseLayout.addWidget(tbBrowse)

        self.txtUrl = QtWidgets.QLineEdit(self)
        self.txtUrl.setText(ts2.get_info().get('simulations_repo'))
        tbBrowse.addWidget(self.txtUrl)

        self.buttDownload = tbBrowse.addAction("Download", self.onDownload)


        self.treeSims = QtWidgets.QTreeWidget()
        self.browseLayout.addWidget(self.treeSims)


    def onDownload(self):

        print("onDownload")
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
