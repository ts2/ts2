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

from Qt import QtCore, QtWidgets, Qt

from ts2 import simulation


class ClockWidget(QtWidgets.QLCDNumber):
    """Clock LCD Widget"""
    def __init__(self, parent):
        """Constructor for the ClockWidget class."""
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setSegmentStyle(QtWidgets.QLCDNumber.Flat)

        self.setNumDigits(8)
        self.display("--:--:--")
        self.resize(100, 20)

    @QtCore.pyqtSlot(QtCore.QTime)
    def setTime(self, t):
        self.display(t.toString("hh:mm:ss"))


class ZoomWidget(QtWidgets.QWidget):
    """Zoom slider bar with associated spinBox."""

    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        """Constructor for the ZoomWidget class."""
        super().__init__(parent)
        #self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
        #                   QtWidgets.QSizePolicy.Minimum)
        self.button = QtWidgets.QPushButton(self.tr("100%"), self)

        self.slider = QtWidgets.QSlider(Qt.Horizontal, self)
        self.slider.setRange(10, 200)
        self.slider.setValue(100)
        self.slider.setSingleStep(10)

        self.spinBox = QtWidgets.QSpinBox(self)
        self.spinBox.setRange(10, 200)
        self.spinBox.setSingleStep(1)
        self.spinBox.setValue(100)
        self.spinBox.setSuffix("%")
        self.spinBox.setCorrectionMode(
            QtWidgets.QAbstractSpinBox.CorrectToNearestValue
        )

        self.button.clicked.connect(self.setDefaultZoom)
        self.slider.valueChanged.connect(self.spinBox.setValue)
        self.spinBox.valueChanged.connect(self.slider.setValue)
        self.spinBox.valueChanged.connect(self.valueChanged)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(0,0,0,0)
        hlayout.addWidget(self.button)
        hlayout.addWidget(self.slider)
        hlayout.addWidget(self.spinBox)
        self.setLayout(hlayout)

    @QtCore.pyqtSlot()
    def setDefaultZoom(self):
        """Sets the zoom to 100%."""
        self.spinBox.setValue(100)
    """
    def sizeHint(self):
        return QtCore.QSize(300, 50)

    def minimumSizeHint(self):
        return QtCore.QSize(300, 50)
    """



class XGraphicsView(QtWidgets.QGraphicsView):
    """An extended QGraphicsView to handle wheel events"""

    wheelChanged = QtCore.pyqtSignal(int)
    """Signal emited when wheel has changed, direction = +1 or -1 """

    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, ev):
        """Override the wheelEvent, and send signal with direction"""
        if ev.angleDelta().y() > 1:
            self.wheelChanged.emit(+1)
        else:
            self.wheelChanged.emit(-1)


class StatusBar(QtWidgets.QStatusBar):
    """A horizontal bar with enbedded progress bar

    .. todo: The progressBar is not showing progress !!
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.progressTimer = QtCore.QTimer()
        self.progressTimer.setInterval(100)
        self.progressTimer.timeout.connect(self.onProgressTimeout)

        self.progressContainerWidget = HBoxWidget()
        self.progressContainerWidget.setFixedWidth(100)
        self.progressContainerWidget.setFixedHeight(15)
        self.addPermanentWidget(self.progressContainerWidget)

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setTextVisible(False)
        self.progressContainerWidget.addWidget(self.progressBar, 1)
        self.progressBar.setVisible(False)


    def showMessage(self, txt, timeout=0, info=False, warn=False):
        """Shows a message

        :param str txt: Text to display
        :param int timeout: Timeout in seconds
        :param bool info: shows blue
        :param bool warn: shows red
        """
        color = "black"
        if warn:
            color = "#AC3636"
        elif info:
            color = "#204292"
        self.setStyleSheet("color: %s" % color )

        if timeout > 0:
            super().showMessage(txt, timeout * 1000)
        else:
            super().showMessage(txt)

    @QtCore.pyqtSlot()
    def onProgressTimeout(self):
        print("onTimer")
        QtCore.QApplication.processEvents()

    def showBusy(self, is_busy):
        """Shows the progress bar and makes busy bee"""
        if is_busy:
            self.progressBar.setRange(0,0)
            self.progressTimer.start()
        else:
            self.progressBar.setRange(0,0)
            self.progressTimer.stop()
        self.progressBar.setVisible(is_busy)


class ToolBarGroup(QtWidgets.QWidget):

    def __init__(self, parent=None, title=None):
        """Constructor for the ToolBarGroup class."""
        super().__init__(parent)

        # Main Layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins( 0, 0, 0, 0 )
        mainLayout.setSpacing( 0 )
        self.setLayout( mainLayout )

        # Label
        self.label = QtWidgets.QLabel()
        lbl_sty = "background: #cccccc; " # qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #fefefe, stop: 1 #CECECE);"
        lbl_sty += " color: #333333; font-size: 7pt; padding: 1px;" # border: 1px outset #cccccc;"
        self.label.setStyleSheet( lbl_sty )
        self.label.setAlignment( QtCore.Qt.AlignCenter )
        mainLayout.addWidget( self.label )

        # Toolbar - were using a toolbar as we can addAction, Q*box dont allow
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setToolButtonStyle( QtCore.Qt.ToolButtonTextBesideIcon )
        self.toolbar.setFixedHeight( 30 )
        mainLayout.addWidget( self.toolbar )

        if title:
            self.setTitle(title)

    def setTitle(self, title):
        self.label.setText( "%s" % title )

    def addWidget(self, widget):
        self.toolbar.addWidget(widget)

    def addAction(self, action):
        self.toolbar.addAction(action)

class VBoxWidget(QtWidgets.QWidget):
    """Widget with a Vertical Box"""
    def __init__(self, parent=None, margin=0):
        super().__init__(parent)

        lay = QtWidgets.QVBoxLayout()
        lay.setContentsMargins(margin,margin,margin,margin)
        self.setLayout(lay)

    def addWidget(self, widget, stretch=0):
        self.layout().addWidget(widget, stretch)

    def addLayout(self, layout, stretch=0):
        self.layout().addLayout(layout, stretch)

class HBoxWidget(QtWidgets.QWidget):
    """Widget with a Horizontal Box"""
    def __init__(self, parent=None, margin=0):
        super().__init__(parent)

        lay = QtWidgets.QVBoxLayout()
        lay.setContentsMargins(margin,margin,margin,margin)
        self.setLayout(lay)

    def addWidget(self, widget, stretch=0):
        self.layout().addWidget(widget, stretch)

    def addLayout(self, layout, stretch=0):
        self.layout().addLayout(layout, stretch)
