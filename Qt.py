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
# 
# @pedro notes
# This script is inspired by PyQtGraph
# https://github.com/pyqtgraph/pyqtgraph/blob/develop/pyqtgraph/Qt.py
# and a future idea of loading either pyside or even android qt.py
# lets dream on..
#
# This pull the libs into a common name space
# 
# Constants and Enums etc..
# In c++ `Qt::AlignLeft` is just there 
# but in PyQt land its at `PyQt5.QtCore.Qt.AlignLeft` .. phew
# So this imports for shortcut.. ta snake

from PyQt5.QtCore import Qt

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
