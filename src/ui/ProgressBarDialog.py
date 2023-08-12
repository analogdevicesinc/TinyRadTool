from PyQt4 import QtGui
import src.ui.ui_ProgressBarDialog as ui_progressbardialog


class ProgressBarDialog(QtGui.QDialog, ui_progressbardialog.Ui_ProgressBarDialog):

    def __init__(self):
        super(ProgressBarDialog, self).__init__()
        self.setupUi(self)
        self.center()


    def center(self):
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        self.move(centerPoint.x() - self.width() * 0.5, centerPoint.y() - self.height() * 0.5)
