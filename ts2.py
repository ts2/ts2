# File : ts2.py
import sys
from PyQt4 import QtGui, QtCore
from myCalendar import Ui_myCalendar

# We start a new class here
# derived from QMainWindow
# A calendar is displayed and clicking on a date makes this date be displayed on the label on the bottom

class ts2(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_myCalendar()
	myWidget = QtGui.QWidget()
        self.ui.setupUi(myWidget)
	self.setCentralWidget(myWidget)
	#set label text to current date
	self.ui.myLabel.setText(str(self.ui.calendarWidget.selectedDate().toPyDate()))
        # Connect the calendar to show the date on the QLabel
        self.connect(self.ui.calendarWidget, QtCore.SIGNAL('selectionChanged()'), self.showDate)

    def showDate(self):
	date = self.ui.calendarWidget.selectedDate()
	self.ui.myLabel.setText(str(date.toPyDate()))

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = ts2()
    window.show()
    sys.exit(app.exec_())
