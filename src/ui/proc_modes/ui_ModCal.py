import  os
import  pyqtgraph as pg
import  numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import  src.proc_modes.MyTableModel as MyTableModel


class   Ui_ModCal(object):
    def setupUi(self, ModCal):

        ModCal.setObjectName("ModCal")

        self.progressbar = QtWidgets.QProgressBar()
        self.progressbar.setFixedHeight(10)
        self.progressbar.setTextVisible(False)
        self.progressbar.setRange(0,100)
        self.TabContWidget = QtWidgets.QTabWidget()



 
        #--------------------------------------------------------------------------------------
        # View Calibration Data
        #--------------------------------------------------------------------------------------
        # define system widget with grid layout
        inras_logo_path = os.path.join("src","ressource","img","adi.png")
        self.Image_View_Logo = QtGui.QImage(inras_logo_path)
        self.Label_View_Logo = QtWidgets.QLabel()
        self.Label_View_Logo.setMinimumSize(200, 100)
        self.Label_View_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_View_Logo))

        self.Label_View_CfgInf = QtWidgets.QLabel("")
        self.Label_View_CfgInf = QtWidgets.QLabel("")     
        self.Button_View_Get = QtWidgets.QPushButton("Get")
        self.Button_View_Load = QtWidgets.QPushButton("Load from File")

        Header = ['Parameter', 'Value']
        # a list of (name, age, weight) tuples
        lData = [('-', '-'),]
        TableModel = MyTableModel.MyTableModel(self, lData, Header)
        self.Table_View_Cfg = QtWidgets.QTableView()
        self.Table_View_Cfg.setModel(TableModel)
        self.Table_View_Cfg.setAlternatingRowColors(True)
        #self.Table_View_Cfg.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)  

        self.Plot_View_Tim = pg.PlotWidget(background=(255, 255, 255))
        x = np.arange(10)
        y = np.zeros(10)
        self.Plot_View_Tim.plot(x, y)
        self.Plot_View_Tim.setLabel('left', "Val", units=' ')
        self.Plot_View_Tim.setLabel('bottom', "Coef", units=' ')


        self.Widget_View = QtWidgets.QWidget()
        self.Layout_View = QtWidgets.QGridLayout()
        self.Layout_View.addWidget(self.Label_View_Logo, 0, 0, 3, 1)
        self.Layout_View.addWidget(self.Label_View_CfgInf, 0, 1, 1, 3)   
        self.Layout_View.addWidget(self.Button_View_Get, 1, 1)
        self.Layout_View.addWidget(self.Button_View_Load, 1, 6, 1, 2)
        self.Layout_View.addWidget(self.Table_View_Cfg, 3, 1, 1, 7)
        self.Layout_View.addWidget(self.Plot_View_Tim, 4, 0, 1, 8)
        self.Layout_View.addWidget(self.progressbar, 5, 0, 1, 8)
        self.Widget_View.setLayout(self.Layout_View)

        self.TabContWidget.addTab(self.Widget_View,"&View Calibration")

        #--------------------------------------------------------------------------------------
        # Calibrate Frontend
        #--------------------------------------------------------------------------------------
        # define system widget with grid layout
        inras_logo_path = os.path.join("src","ressource","img","adi.png")
        self.Image_Cal_Logo = QtGui.QImage(inras_logo_path)
        self.Label_Cal_Logo = QtWidgets.QLabel()
        self.Label_Cal_Logo.setMinimumSize(200, 100)
        self.Label_Cal_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_Cal_Logo))

        self.Label_Cal_CfgInf = QtWidgets.QLabel("")
        self.Label_Cal_CfgInf = QtWidgets.QLabel("")
        self.Label_Cal_Cfg = QtWidgets.QLabel("Tx Cfg:")
        self.Edit_Cal_Cfg = QtWidgets.QLineEdit("TX1(20);")        
        self.Button_Cal_Ini = QtWidgets.QPushButton("Initialize")
        self.Button_Cal_Meas = QtWidgets.QPushButton("Measure")
        self.Button_Cal_Meas.setDisabled(True)
        self.ChkBox_Cal_Zoom = QtWidgets.QCheckBox("Zoom")
        self.ChkBox_Cal_Store = QtWidgets.QCheckBox("Store")
        self.Label_Cal_NrFrms = QtWidgets.QLabel("NrFrms:")
        self.Edit_Cal_NrFrms = QtWidgets.QLineEdit("100")
        self.Label_Cal_RMin = QtWidgets.QLabel("RMin (m):")
        self.Edit_Cal_RMin = QtWidgets.QLineEdit("2")
        self.Label_Cal_RMax = QtWidgets.QLabel("RMax (m):")
        self.Edit_Cal_RMax = QtWidgets.QLineEdit("4")
        self.Plot_Cal_Tim = pg.PlotWidget(background=(255, 255, 255))
        self.Plot_Cal_Coeff = pg.PlotWidget(background=(255, 255, 255))      

        x = np.arange(1000)
        y = np.zeros(1000)
        self.Plot_Cal_Tim.plot(x, y)
        self.Plot_Cal_Tim.setLabel('left', "Val", units=' ')
        self.Plot_Cal_Tim.setLabel('bottom', "Coef", units=' ')

        self.Widget_Cal = QtWidgets.QWidget()
        self.Layout_Cal = QtWidgets.QGridLayout()
        self.Layout_Cal.addWidget(self.Label_Cal_Logo, 0, 0, 3, 1)
        self.Layout_Cal.addWidget(self.Label_Cal_CfgInf, 0, 1, 1, 3)
        self.Layout_Cal.addWidget(self.Label_Cal_Cfg, 0, 6)
        self.Layout_Cal.addWidget(self.Edit_Cal_Cfg, 0, 7)        
        self.Layout_Cal.addWidget(self.Button_Cal_Ini, 1, 1)
        self.Layout_Cal.addWidget(self.Button_Cal_Meas, 2, 1)
        self.Layout_Cal.addWidget(self.Label_Cal_NrFrms, 1, 2)
        self.Layout_Cal.addWidget(self.Edit_Cal_NrFrms, 1, 3)
        self.Layout_Cal.addWidget(self.Label_Cal_RMin, 1, 4)
        self.Layout_Cal.addWidget(self.Edit_Cal_RMin, 1, 5)
        self.Layout_Cal.addWidget(self.Label_Cal_RMax, 1, 6)
        self.Layout_Cal.addWidget(self.Edit_Cal_RMax, 1, 7)
        self.Layout_Cal.addWidget(self.ChkBox_Cal_Store, 2,4)
        self.Layout_Cal.addWidget(self.ChkBox_Cal_Zoom, 2,7) 
        self.Layout_Cal.addWidget(self.Plot_Cal_Tim, 3, 0, 1, 8)
        self.Layout_Cal.addWidget(self.Plot_Cal_Coeff, 4, 0, 1, 8)
        self.Layout_Cal.addWidget(self.progressbar, 5, 0, 1, 8)

        self.Widget_Cal.setLayout(self.Layout_Cal)


        #--------------------------------------------------------------------------------------
        # Bpa Define Configuration Page
        #--------------------------------------------------------------------------------------
        # define system widget with grid layout
        inras_logo_path = os.path.join("src","ressource","img","adi.png")
        self.Image_CalCfg_Logo = QtGui.QImage(inras_logo_path)
        self.Label_CalCfg_Logo = QtWidgets.QLabel()
        self.Label_CalCfg_Logo.setMinimumSize(200, 100)
        #SysLabel_Logo.setAlignment(Qt.AlignCenter)
        self.Label_CalCfg_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_CalCfg_Logo))

        self.Label_CalCfg_ClkDiv = QtWidgets.QLabel("Clock divider:")
        self.ClkDivSel = ("2", "4", "8","16","32","1 (Not supported anymore AD8283 Rev C)")
        self.dClkDivSel = {   "1 (Not supported anymore AD8283 Rev C)" : 1,
                                                "2" : 2,
                                                "4" : 4,
                                                "8" : 8,
                                                "16": 16,
                                                "32": 32}
        self.ComboBox_CalCfg_ClkDiv = QtWidgets.QComboBox()
        self.ComboBox_CalCfg_ClkDiv.addItems(self.ClkDivSel)
        self.ComboBox_CalCfg_ClkDiv.setCurrentIndex(0)

        self.Label_CalCfg_AdcGain = QtWidgets.QLabel("ADC gain:")
        self.Label_CalCfg_RadStrtFreq = QtWidgets.QLabel("Start frequency (MHz):")
        self.Edit_CalCfg_RadStrtFreq = QtWidgets.QLineEdit("76000")
        self.Label_CalCfg_RadStopFreq = QtWidgets.QLabel("Stop frequency (MHz):")
        self.Edit_CalCfg_RadStopFreq = QtWidgets.QLineEdit("77000")
        self.Label_CalCfg_RadDur = QtWidgets.QLabel("Duration (us):")
        self.Edit_CalCfg_RadDur = QtWidgets.QLineEdit("256")

        self.Widget_CalCfg = QtWidgets.QWidget()
        self.Layout_CalCfg = QtWidgets.QGridLayout()
        self.Layout_CalCfg.addWidget(self.Label_CalCfg_Logo, 0, 0, 1, 1)
        self.Layout_CalCfg.addWidget(self.Label_CalCfg_ClkDiv, 1, 1)
        self.Layout_CalCfg.addWidget(self.ComboBox_CalCfg_ClkDiv, 1, 2)
        self.Layout_CalCfg.addWidget(self.Label_CalCfg_AdcGain, 2, 1)

        self.Layout_CalCfg.addWidget(self.Label_CalCfg_RadStrtFreq, 7, 1)
        self.Layout_CalCfg.addWidget(self.Edit_CalCfg_RadStrtFreq, 7, 2)
        self.Layout_CalCfg.addWidget(self.Label_CalCfg_RadStopFreq, 8, 1)
        self.Layout_CalCfg.addWidget(self.Edit_CalCfg_RadStopFreq, 8, 2)
        self.Layout_CalCfg.addWidget(self.Label_CalCfg_RadDur, 9, 1)
        self.Layout_CalCfg.addWidget(self.Edit_CalCfg_RadDur, 9, 2)

        self.spacerItem = QtWidgets.QSpacerItem(20, 23, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.spacerWidget = QtWidgets.QWidget()
        self.spacerLayout = QtWidgets.QVBoxLayout()
        self.spacerLayout.addItem(self.spacerItem)
        self.spacerWidget.setLayout(self.spacerLayout)
        self.Layout_CalCfg.addWidget(self.spacerWidget,14,1)

        self.Widget_CalCfg.setLayout(self.Layout_CalCfg)

        self.IniForm()


    def GetPageCfg(self):
        print("Get Configuration of GUI")
        dGuiCfg = dict()
        return dGuiCfg

    def SetPageCfg(self, dGuiCfg):
        print("Set Configuration of GUI")
              

    def IniForm(self):
        self.Button_Cal_Meas.setText("Measure")
        self.Button_Cal_Meas.setEnabled(False)
        self.Button_Cal_Ini.setEnabled(True)
        self.Edit_Cal_NrFrms.setEnabled(True)


    def IniGui(self):
        labelstr = str(self.patre.GuiFontSiz) + "px"
        labelStyle = {'font-size': labelstr}

        self.Plot_Cal_Tim.setLabel('bottom', "R", units='m', **labelStyle)
        self.Plot_Cal_Tim.setLabel('left', "X", units='dBV', **labelStyle)


        datfont = QtGui.QFont()
        datfont.setPixelSize(int(self.patre.GuiFontSiz))
        self.Plot_Cal_Tim.getAxis('bottom').tickFont = datfont
        self.Plot_Cal_Tim.getAxis('left').tickFont = datfont
        self.Plot_Cal_Tim.getAxis('bottom').setHeight(int(int(self.patre.GuiFontSiz)*2.7+5))
        self.Plot_Cal_Tim.getAxis('left').setWidth(int(int(self.patre.GuiFontSiz)*2.6+8))
        self.Plot_Cal_Tim.getAxis('bottom').setFont(datfont)
        self.Plot_Cal_Tim.getAxis('left').setFont(datfont)

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

