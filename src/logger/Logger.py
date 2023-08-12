from    PyQt5 import QtCore, QtGui
import  threading as threading

class Logger(QtCore.QObject):
    lString         =   list()
    LockUpd         =   threading.Lock()
    SigUpd          =   QtCore.pyqtSignal()

    def __init__(self, TxtBox, parent=None):
        super(Logger, self).__init__(parent)
        self.TxtBox     =   TxtBox
        self.SigUpd.connect(self.SigActionUpd)

    def Append(self, text):
        self.LockUpd.acquire()
        self.lString.append(text)
        self.LockUpd.release()


    def AppendDict(self, text, dCfg):
        dCp     =   dCfg.copy()
        self.LockUpd.acquire()
        self.lString.append(text)
        for Idx in range(len(dCp)):
            Item    =   dCp.popitem()
            self.lString.append('  ' + str(Item[0]) + ' = ' +  str(Item[1]))
        self.LockUpd.release()        

    def SigActionUpd(self):
        self.LockUpd.acquire()
        for Idx in self.lString:
            self.TxtBox.append(Idx)
        self.lString    =   list()  
        self.LockUpd.release()

    def ClrTxt(self):
        self.LockUpd.acquire()
        self.TxtBox.selectAll()
        self.TxtBox.clear()
        self.LockUpd.release()    

    def GetTxt(self):
        self.LockUpd.acquire()
        Txt     =   self.TxtBox.toPlainText()
        self.LockUpd.release()               
        return Txt  


