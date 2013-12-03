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
import sys
from ts2 import mainwindow
from ts2 import ressources_rc
from ts2 import gui

def Main():
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(":/ts2.png")))
    qtTranslator = QtCore.QTranslator()
    qtTranslator.load("qt_" + QtCore.QLocale.system().name(),
                      QtCore.QLibraryInfo.location(
                                      QtCore.QLibraryInfo.TranslationsPath))
    app.installTranslator(qtTranslator)
    ts2Translator = QtCore.QTranslator()
    ts2Translator.load(QtCore.QLocale.system(), "ts2", "_", "i18n", ".qm")
    app.installTranslator(ts2Translator)
    QtCore.qDebug(QtCore.QLocale.system().name())
    try:
        mw = mainwindow.MainWindow()
        mw.show()
        return app.exec_();
    except:
        gui.dialogs.ExceptionDialog.popupException(None)
        #QMessageBox.critical(None,
                             #QObject.trUtf8(QObject(), "Error"),
                             #str(e),
                             #QMessageBox.StandardButtons(QMessageBox.Ok))
        return 1
    else:
        return 0

if __name__ == "__main__":
    Main()
