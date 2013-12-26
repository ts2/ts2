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

import sys
import traceback

from PyQt4 import QtGui, QtCore

from ts2.gui import servicelistview

translate = QtGui.QApplication.translate

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
            return QtGui.QMessageBox.critical(parent, title, message)


class ServiceAssignDialog(QtGui.QDialog):
    """TODO Document ServiceAssignDialog"""

    def __init__(self, parent, simulation):
        super().__init__(parent)
        self.setWindowTitle(self.tr(
                                "Choose a service to assign to this train"))
        self.serviceListView = servicelistview.ServiceListView(self)
        self.serviceListView.setupServiceList(simulation)
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok|
                                           QtGui.QDialogButtonBox.Cancel)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.serviceListView)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.resize(600, 300)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

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
        if sad.exec_() == QtGui.QDialog.Accepted:
            newServiceCode = sad.getServiceCode()
            if newServiceCode != "":
                train = simulation.trains[trainId]
                train.serviceCode = newServiceCode

