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

import sys
import traceback

from Qt import QtCore, QtWidgets, Qt

import ts2
from ts2.gui import servicelistview
from ts2.utils import settings

translate = QtWidgets.qApp.translate


class ExceptionDialog:
    """A Dialog box for displaying exception information
    """

    @staticmethod
    def popupException(parent, exception=None):
        """Displays a dialog with all the information about the exception and
        the traceback."""
        title = translate("ExceptionDialog", "Error")
        message = ""
        if exception is not None:
            message = str(exception) + "\n\n"
            message += message.join(traceback.format_tb(sys.exc_info()[2]))
        else:
            message += message.join(traceback.format_exc())
        if settings.debug:
            print(message)
        return QtWidgets.QMessageBox.critical(parent, title, message)


class PropertiesDialog(QtWidgets.QDialog):
    """Dialog box for editing simulation properties during the game."""

    def __init__(self, parent, simulation):
        """Constructor for the PropertiesDialog class."""
        super().__init__(parent)
        self.simulation = simulation
        self.setWindowTitle(self.tr("Simulation properties"))
        self.setMinimumWidth(500)

        titleLabel = QtWidgets.QLabel(self)
        titleLabel.setText("<u>" +
                           self.tr("Simulation title:") +
                           "</u>")
        titleText = QtWidgets.QLabel(simulation.option("title"), self)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(titleLabel)
        hlayout.addWidget(titleText)
        hlayout.addStretch()
        descriptionLabel = QtWidgets.QLabel(self)
        descriptionLabel.setText("<u>" +
                                 self.tr("Description:") +
                                 "</u>")
        descriptionText = QtWidgets.QTextEdit(self)
        descriptionText.setReadOnly(True)
        descriptionText.setText(simulation.option("description"))
        optionsLabel = QtWidgets.QLabel(self)
        optionsLabel.setText("<u>" + self.tr("Options:") + "</u>")
        tibOptionCB = QtWidgets.QCheckBox(self)
        tibOptionCB.stateChanged.connect(self.changeTIB)
        tibOptionCB.setChecked(
            int(simulation.option("trackCircuitBased")) != 0)
        optionLayout = QtWidgets.QFormLayout()
        optionLayout.addRow(self.tr("Play simulation with track circuits"),
                            tibOptionCB)
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(hlayout)
        layout.addWidget(descriptionLabel)
        layout.addWidget(descriptionText)
        layout.addWidget(optionsLabel)
        layout.addLayout(optionLayout)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        buttonBox.accepted.connect(self.accept)

    @QtCore.pyqtSlot(int)
    def changeTIB(self, checkState):
        """Changes the trackItemBased Option."""
        if checkState == Qt.Checked:
            self.simulation.setOption("trackCircuitBased", 1)
        else:
            self.simulation.setOption("trackCircuitBased", 0)


class ServiceAssignDialog(QtWidgets.QDialog):
    """TODO Document ServiceAssignDialog"""

    def __init__(self, parent, simulation):
        super().__init__(parent)
        self.setObjectName("service_assign_dialog")
        self.setWindowTitle(
            self.tr("Choose a service to assign to this train")
        )
        self.serviceListView = servicelistview.ServiceListView(self)
        self.serviceListView.setupServiceList(simulation)
        buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.serviceListView)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.resize(600, 300)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.serviceListView.doubleClicked.connect(self.accept)

        settings.restoreWindow(self)

    def getServiceCode(self):
        index = self.serviceListView.selectionModel().selection().indexes()[0]
        if index.isValid():
            return index.data()
        else:
            return ""

    @staticmethod
    def reassignServiceToTrain(simulation, trainId):
        """Reassigns a service to the train given by trainId by poping-up a
        reassignServiceDialog."""
        sad = ServiceAssignDialog(simulation.simulationWindow, simulation)
        if sad.exec_() == QtWidgets.QDialog.Accepted:
            newServiceCode = sad.getServiceCode()
            if newServiceCode != "":
                simulation.simulationWindow.webSocket.sendRequest("train", "setService",
                                                                  {'id': int(trainId), 'service': newServiceCode})

    def closeEvent(self, event):
        """Save window postions on close"""
        settings.saveWindow(self)
        settings.sync()
        super().closeEvent(event)


class SplitTrainDialog(QtWidgets.QDialog):
    """Popup window for the user to select where to split a train."""

    def __init__(self, parent, train):
        """Constructor for the SplitTrainDialog."""
        super().__init__(parent)
        self.setObjectName("split_train_dialog")
        self.setWindowTitle(
            self.tr("Split a train")
        )
        layout = QtWidgets.QVBoxLayout()

        label0 = QtWidgets.QLabel(self)
        label0.setText(train.trainType.elements[0].description)
        layout.addWidget(label0)
        self.radioButtons = []
        for element in train.trainType.elements[1:]:
            self.radioButtons.append(QtWidgets.QRadioButton(
                self.tr("Split here"), self)
            )
            layout.addWidget(self.radioButtons[-1])
            label = QtWidgets.QLabel(self)
            label.setText(element.description)
            layout.addWidget(label)
        self.radioButtons[0].setChecked(True)
        buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.setMinimumWidth(300)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        settings.restoreWindow(self)

    def getSplitIndex(self):
        """
        :return: The index of the selected radio button
        """
        for button in self.radioButtons:
            if button.isChecked():
                return self.radioButtons.index(button)
        return 0

    @staticmethod
    def getSplitIndexPopUp(train):
        """Pops up a split train dialog and returns the index at which to split
        the given train.
        :param train: The train instance to split
        """
        simWindow = train.simulation.simulationWindow
        std = SplitTrainDialog(simWindow, train)
        if std.exec_() == QtWidgets.QDialog.Accepted:
            train.splitTrain(std.getSplitIndex() + 1)

    def closeEvent(self, event):
        """Save window postions on close"""
        settings.saveWindow(self)
        settings.sync()
        super().closeEvent(event)


class DownloadSimulationsDialog(QtWidgets.QDialog):
    """Popup window for the user to select download server."""
    def __init__(self, parent):
        """Constructor for the DownloadSimulationsDialog."""
        super().__init__(parent)
        self.setWindowTitle(
            self.tr("Download simulations from server")
        )
        label = QtWidgets.QLabel(self)
        label.setText(self.tr("Download server: "))
        self.url = QtWidgets.QLineEdit(self)
        self.url.setText(ts2.get_info().get('simulations_repo'))
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(label)
        hlayout.addWidget(self.url)
        note = QtWidgets.QLabel(self)
        note.setText(self.tr("<em>The download server must be the url of a "
                             "valid GitHub repository.</em>"))
        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.addButton(self.tr("Download"),
                            QtWidgets.QDialogButtonBox.AcceptRole)
        buttonBox.addButton(self.tr("Cancel"),
                            QtWidgets.QDialogButtonBox.RejectRole)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addSpacing(5)
        vlayout.addWidget(note)
        vlayout.addSpacing(10)
        vlayout.addWidget(buttonBox)
        self.setLayout(vlayout)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
