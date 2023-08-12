import  os
from PyQt5 import QtCore, QtGui, QtWidgets

import  src.proc_modes.MyTableModel as MyTableModel

import  re


class   Ui_CfgStatus(object):
    def setupUi(self, CfgStatus):

        self.lSysCmd = list()
        self.LineNr = 1

        CfgStatus.setObjectName("CfgStatus")
        self.progressbar = QtWidgets.QProgressBar()
        self.progressbar.setFixedHeight(10)
        self.progressbar.setTextVisible(False)
        self.progressbar.setRange(0,100)
        self.TabContWidget = QtWidgets.QTabWidget()

        inras_logo_path = os.path.join("src","ressource","img","adi.png")

        #--------------------------------------------------------------------------------------
        # Fmcw Define Configuration Page
        #--------------------------------------------------------------------------------------
        # define system widget with grid layout


        #--------------------------------------------------------------------------------------
        # Board Status:  Board status
        #--------------------------------------------------------------------------------------
        self.Widget_BoardSts = QtWidgets.QWidget()
        self.Layout_BoardSts = QtWidgets.QGridLayout()
        self.Label_BoardSts = QtWidgets.QLabel("TinyRad Status")
        self.Image_BoardSts_Logo = QtGui.QImage(inras_logo_path)
        self.Button_BoardSts_Get = QtWidgets.QPushButton("Get Status")
        self.Label_BoardSts_Logo = QtWidgets.QLabel()
        self.Label_BoardSts_Logo.setMinimumSize(200, 100)
        self.Label_BoardSts_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_BoardSts_Logo))

        header = ['Parameter', 'Value']
        # a list of (name, age, weight) tuples
        data_list = [
        ('Board ID', '-'),
        ('Software Version', '-'),
        ('Hardware ID', '-')
        ]
        table_model = MyTableModel.MyTableModel(self, data_list, header)
        self.Table_BoardSts_Sts = QtWidgets.QTableView()
        self.Table_BoardSts_Sts.setModel(table_model)
        
        
        self.Table_BoardSts_Sts.setAlternatingRowColors(True)
        #self.Table_BoardSts_Sts.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)        
        
        self.Layout_BoardSts.addWidget(self.Label_BoardSts_Logo, 0, 0, 3, 1)
        self.Layout_BoardSts.addWidget(self.Label_BoardSts, 0, 1, 1, 1)
        self.Layout_BoardSts.addWidget(self.Button_BoardSts_Get, 1, 1, 1, 1)
        self.Layout_BoardSts.addWidget(self.Table_BoardSts_Sts, 3, 0, 1, 7)

        self.Widget_BoardSts.setLayout(self.Layout_BoardSts)
        self.TabContWidget.addTab(self.Widget_BoardSts,"&Board Status")
        table_model = MyTableModel.MyTableModel(self, data_list, header)
        self.IniForm()
        self.AddCmd()

    def Action_SoftwareCfg_Enter(self):
        stCmd = self.Edit_SoftwareCfg.text()  
        self.Txt_SoftwareCfg.append('-> ' + stCmd)
        # Parse Help Commands
        self.ParseCmdHelp()
        # Parse Command
        self.ParseCmdSys()
        # Pase Board Commands
        self.ParseCmdBrd()

        self.Edit_SoftwareCfg.setText('')
        

    def ParseCmdSys(self):
        stCmd = self.Edit_SoftwareCfg.text()
        
        # Command:  Clr:All
        #           Clr:Tab
        #           Clr:   
        RegClr = re.compile(r"(Clr(:(?P<SubCmd>([A-Z][a-z]*)))+)")
        Match = RegClr.search(stCmd)

        if Match:
            SubCmd = Match.group("SubCmd")
            if (SubCmd == 'All') or (SubCmd == 'Tab'):
                header = ['Parameter', 'Value']
                # a list of (name, age, weight) tuples
                data_list = [
                ('-', '1'),
                ]            
                TableModel = MyTableModel.MyTableModel(self, data_list, header)
                self.Table_SoftwareCfg_Cfg.setModel(TableModel)
            if (SubCmd == 'All') or (SubCmd == 'Txt'):
                self.Txt_SoftwareCfg.selectAll()
                self.Txt_SoftwareCfg.clear()

    def ParseCmdHelp(self):
        stCmd = self.Edit_SoftwareCfg.text()
        RegHelp = re.compile(r"(\?((?P<SubCmd>([A-Z][a-z]*)))+)")
        Match = RegHelp.search(stCmd)

        if Match:
            SubCmd = Match.group("SubCmd")
            print(SubCmd) 
            self.Txt_SoftwareCfg.append(' Help ' + SubCmd)
            if SubCmd == 'Sys':
                for Idx in self.lSysCmd:
                    self.Txt_SoftwareCfg.append('  ' + str(Idx))    

    def ParseCmdBrd(self):
        stCmd = self.Edit_SoftwareCfg.text()
        RegBrd = re.compile(r"(Brd:((?P<Cmd>([A-Z][A-Za-z( )\"]*)))+)")      
        Match = RegBrd.search(stCmd)

        if Match:
            stIpAdr = configreader.getStoredIPAdr()
            PortNr = configreader.getStoredPort()
            self.Rad.stIpAdr = stIpAdr
            self.Rad.PortNr = PortNr
            stBrd = 'self.Rad.' + Match.group('Cmd')
            print(stBrd)
            try:    
                print("Eval command")            
                Ret = eval(stBrd)
                if Ret[0]:
                    self.Txt_SoftwareCfg.append('::  ' + str(Ret[1]))          
            except:
                print(Match.group('Cmd') + ' does not exist')    
    
    def AddCmd(self):
        self.lSysCmd.append(('Clr:All','Clear output (table and text field)'))
        self.lSysCmd.append(('Clr:Tab','Clear table output'))
        self.lSysCmd.append(('Clr:Txt','Clear text output'))        


    def GetPageCfg(self):
        pass

    def SetPageCfg(self, dGuiCfg):
        pass
              
    def IniForm(self):
        pass


    def IniGui(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for i in self.__dict__:
            item = self.__dict__[i]
            clean(item)

def clean(item):
    if isinstance(item, list) or isinstance(item, dict):
        for _ in range(len(item)):
            clean(item.pop())
    else:
        try:
            item.close()
        except (RuntimeError, AttributeError):
            pass

