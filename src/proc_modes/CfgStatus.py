
import  src.proc_modes.MyTableModel as MyTableModel
import  src.proc_modes.ThreadTableModel as ThreadTableModel
#import  src.proc_modes.GetDevice as GetDevice

import  src.cmd_modules.TinyRad as TinyRad

from PyQt5 import QtCore, QtGui, QtWidgets
import  pyqtgraph as pg

import  threading as threading
import  numpy as np
import  src.ui.proc_modes.ui_CfgStatus as ui_CfgStatus
from    os.path import expanduser

import  time
import  datetime    as  datetime


class CfgStatus(QtWidgets.QMainWindow, ui_CfgStatus.Ui_CfgStatus):
    IniSoftwareThread = None
    ViewSoftwareTableModel = None
    SigUpdateSoftwareTable = QtCore.pyqtSignal()

    # Configuration of Signal Processing
    dSigCfg                 = dict()

    def __init__(self, patre):
        super(CfgStatus, self).__init__()
        self.setupUi(self)
        self.patre = patre
        self.Button_BoardSts_Get.clicked.connect(self.Action_BoardSts_Get)
        self.SigUpdateSoftwareTable.connect(self.ActionUpdateSoftwareTable)

    def Button_SoftwareSts_Get_StartThread(self):

        if self.IniSoftwareThread == None:
            self.IniSoftwareThread = threading.Thread(target=self.Action_SoftwareSts_Get, args=(self.ViewSoftwareTableModel, self))
            self.IniSoftwareThread.start()

        else:

            if self.IniSoftwareThread.is_alive():
                print("Thread is still running")
            else:
                print("Thread is not running")
                del self.IniSoftwareThread             
                self.IniSoftwareThread()
                #self.IniViewThread = threading.Thread(target=self.Button_View_Get_Clicked(Tab=self.Table_View_Cfg))
                self.IniSoftwareThread = threading.Thread(target=self.Action_SoftwareSts_Get, args=(self.ViewSoftwareTableModel, self))
                self.IniSoftwareThread.start()   



    def Action_BoardSts_Get(self):
        print("Action Get Board Status")

        Data = list()

        ConSts = False
        Header = ['Parameter', 'Value']

        Vers = self.patre.hTinyRad.Dsp_GetSwVers()
        if len(Vers) > 0 and Vers["SUid"] != -1:
            Data.append(('Board ID', str(Vers["SUid"])))
            Data.append(('Software Version', str(Vers["SwMaj"]) + '.' + str(Vers["SwMin"]) + '.' + str(Vers["SwPatch"])))
            Data.append(('Hardware ID', str(Vers["HUid"])))
        else:
            Data.append(("Board not responding", "-1"))
            print("Ret Val:", Vers)

        table_model = MyTableModel.MyTableModel(self, Data, Header)
        self.Table_BoardSts_Sts.setModel(table_model)

    def     GetDevice(self, SUID, ConType, IpAdr):
        Brd = TinyRad.TinyRad()
        return Brd

    def ActionUpdateSoftwareTable(self):

        if not (self.ViewSoftwareTableModel == None):
            self.Table_SoftwareSts_Sts.setModel(self.ViewSoftwareTableModel)
