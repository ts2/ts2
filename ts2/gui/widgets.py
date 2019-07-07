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
        if t.isNull():
            self.display("--:--:--")
            return
        self.display(t.toString("hh:mm:ss"))


class ZoomWidget(QtWidgets.QWidget):
    """Zoom slider bar with associated spinBox."""

    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        """Constructor for the ZoomWidget class."""
        super().__init__(parent)
        self.button = QtWidgets.QToolButton(self)
        self.button.setText(self.tr("100%"))
        self.button.setAutoRaise(True)

        self.slider = QtWidgets.QSlider(Qt.Horizontal, self)
        self.slider.setRange(10, 200)
        self.slider.setValue(100)
        self.slider.setSingleStep(10)
        self.slider.setMinimumWidth(140)

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
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.addWidget(self.button)
        hlayout.addWidget(self.slider)
        hlayout.addWidget(self.spinBox)
        self.setLayout(hlayout)

    @QtCore.pyqtSlot()
    def setDefaultZoom(self):
        """Sets the zoom to 100%."""
        self.spinBox.setValue(100)


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
    """A horizontal bar with embedded progress bar

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
        self.setStyleSheet("color: %s" % color)

        if timeout > 0:
            super().showMessage(txt, timeout * 1000)
        else:
            super().showMessage(txt)

    @QtCore.pyqtSlot()
    def onProgressTimeout(self):
        QtWidgets.qApp.processEvents()

    def showBusy(self, is_busy):
        """Shows the progress bar and makes busy bee"""
        if is_busy:
            self.progressBar.setRange(0, 0)
            self.progressTimer.start()
        else:
            self.progressBar.setRange(0, 0)
            self.progressTimer.stop()
        self.progressBar.setVisible(is_busy)


class ToolBarGroup(QtWidgets.QWidget):
    """Created a widget with a small label, containing a toolbar with widgets


    """
    def __init__(self, parent=None, title=None, fg=None, bg=None):
        """
        :param title: The title to show in header

        """
        super().__init__(parent)

        self.fg = "#333333" if fg is None else fg
        self.bg = "#cccccc" if bg is None else bg

        # Main Layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        # Label
        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        mainLayout.addWidget(self.label)
        self.updateStyle()

        # Toolbar - were using a toolbar as we can addAction, Q*box dont allow
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolbar.setFixedHeight(30)
        self.toolbar.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        mainLayout.addWidget(self.toolbar)

        if title:
            self.setTitle(title)

    def updateStyle(self):
        lbl_sty = "background: %s; " % self.bg
        lbl_sty += " color: %s; font-size: 7pt; padding: 1px;" % self.fg
        self.label.setStyleSheet(lbl_sty)

    def setTitle(self, title):
        self.label.setText("%s" % title)

    def addWidget(self, widget):
        self.toolbar.addWidget(widget)

    def addAction(self, action):
        self.toolbar.addAction(action)


class VBoxWidget(QtWidgets.QWidget):
    """A QWidget with a Vertical Box"""

    def __init__(self, parent=None, margin=0):
        super().__init__(parent)

        lay = QtWidgets.QVBoxLayout()
        lay.setContentsMargins(margin, margin, margin, margin)
        self.setLayout(lay)

    def addWidget(self, widget, stretch=0):
        self.layout().addWidget(widget, stretch)

    def addLayout(self, layout, stretch=0):
        self.layout().addLayout(layout, stretch)


class HBoxWidget(QtWidgets.QWidget):
    """A `QWidget` with a Horizontal Box"""

    def __init__(self, parent=None, margin=0):
        super().__init__(parent)

        lay = QtWidgets.QVBoxLayout()
        lay.setContentsMargins(margin, margin, margin, margin)
        self.setLayout(lay)

    def addWidget(self, widget, stretch=0):
        self.layout().addWidget(widget, stretch)

    def addLayout(self, layout, stretch=0):
        self.layout().addLayout(layout, stretch)


class HeaderLabel(QtWidgets.QLabel):
    def __init__(self, parent=None, text="", start=None, end=None, align=None):
        super().__init__(parent)

        self.setText(text)

        align = align if align else Qt.AlignCenter
        self.setAlignment(align | Qt.AlignVCenter)

        start = start if start else "#ffffff"
        end = end if end else "#aaaaaa"

        sty = "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0," \
              " stop: 0 %s, stop: 1 %s);" % (start, end)
        sty += " color: #333333; font-size: 14pt; padding: 5px;"
        self.setStyleSheet(sty)
