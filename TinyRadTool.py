#!/usr/bin/python3.4
import  src.ui.StackGui as StackGui


from PyQt5 import QtGui, QtCore, QtWidgets

def main():
    app     =   QtWidgets.QApplication([])
    Win     =   StackGui.StackGui()
    Win.show()
    app.aboutToQuit.connect(Win.cleanUp)
    ret = app.exec_()
    return 0


if __name__ == "__main__":
    main()

