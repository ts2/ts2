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

tr = QtCore.QObject().tr

class ExceptionDialog:
    """A Dialog box for displaying exception information
    """

    @staticmethod
    def popupException(parent, exception=None):
        """Displays a dialog with all the information about the exception and
        the traceback."""
        title = tr("Error")
        if exception is not None:
            message = str(exception) + "\n\n"
            message += message.join(traceback.format_tb(sys.exc_info()[2]))
        else:
            message += message.join(traceback.format_exc())
            return QtGui.QMessageBox.critical(parent, title, message)
