import  PyQt5.QtGui as QtGui
import  PyQt5.QtCore as QtCore

class MyTableModel(QtCore.QAbstractTableModel):

    def __init__(self, parent, mylist, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header
    
    def rowCount(self, parent):
        return len(self.mylist)
    
    def columnCount(self, parent):
        return len(self.mylist[0])
    
    def data(self, index, role):
        if not index.isValid():
            #return QVariant()
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]
    
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None