import  os
import  pyqtgraph as pg
import  numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

class   Ui_ModPerf(object):
    def setupUi(self, ModFmcw):

        ModFmcw.setObjectName("ModFmcw")
        self.Log_Textbox = QtWidgets.QTextEdit()
        self.Log_Textbox.setReadOnly(True)
        self.progressbar = QtWidgets.QProgressBar()
        self.progressbar.setFixedHeight(10)
        self.progressbar.setTextVisible(False)
        self.progressbar.setRange(0,100)
        
        self.TabContWidget = QtWidgets.QTabWidget()

        #--------------------------------------------------------------------------------------
        # Fmcw Define Configuration Page
        #--------------------------------------------------------------------------------------
        # define system widget with grid layout
        inras_logo_path = os.path.join("src","ressource","img","adi.png")
        self.Image_Cfg_Logo = QtGui.QImage(inras_logo_path)
        self.Label_Cfg_Logo = QtWidgets.QLabel()
        self.Label_Cfg_Logo.setMinimumSize(200, 100)
        self.Label_Cfg_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_Cfg_Logo))


        self.Label_Cfg_fs = QtWidgets.QLabel("Sampling frequency (MSPS)")
        self.fsSel = ("1",)
        self.ComboBox_Cfg_fs = QtWidgets.QComboBox()
        self.ComboBox_Cfg_fs.addItems(self.fsSel)
        self.ComboBox_Cfg_fs.setCurrentIndex(0)

        self.Label_Cfg_RadStrtFreq = QtWidgets.QLabel("Start frequency (MHz):")
        self.Edit_Cfg_RadStrtFreq = QtWidgets.QLineEdit("24000")
        self.Label_Cfg_RadStopFreq = QtWidgets.QLabel("Stop frequency (MHz):")
        self.Edit_Cfg_RadStopFreq = QtWidgets.QLineEdit("24250")
        self.Label_Cfg_RadSamples = QtWidgets.QLabel("Samples ( ):")
        self.Edit_Cfg_RadSamples = QtWidgets.QLineEdit("256")

        self.Label_Cfg_RadPerd = QtWidgets.QLabel("Chirp Repetition (us):")
        self.Edit_Cfg_RadPerd = QtWidgets.QLineEdit("512")

        self.Label_Cfg_RadNp = QtWidgets.QLabel("Number of Chirps")
        self.Edit_Cfg_RadNp = QtWidgets.QLineEdit("128")

        self.Label_Cfg_RangeWinType = QtWidgets.QLabel("Range Window")
        self.Edit_Cfg_RangeWinType = QtWidgets.QLineEdit("Hanning")

        self.Label_Cfg_VelWinType = QtWidgets.QLabel("Velocity Window")
        self.Edit_Cfg_VelWinType = QtWidgets.QLineEdit("Hanning")

        self.Label_Cfg_AngWinType = QtWidgets.QLabel("Angular Window")
        self.Edit_Cfg_AngWinType = QtWidgets.QLineEdit("Boxcar")        

        self.Label_Cfg_FalseAlarmRate = QtWidgets.QLabel("False Alarm Rate")
        self.Edit_Cfg_FalseAlarmRate = QtWidgets.QLineEdit("10")

        self.Widget_Cfg = QtWidgets.QWidget()
        self.Layout_Cfg = QtWidgets.QGridLayout()
        self.Layout_Cfg.addWidget(self.Label_Cfg_Logo, 0, 0, 1, 1)
        
        self.Layout_Cfg.addWidget(self.Label_Cfg_fs, 5, 1)
        self.Layout_Cfg.addWidget(self.ComboBox_Cfg_fs, 5, 2)        
        
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadStrtFreq, 7, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadStrtFreq, 7, 2)
        
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadStopFreq, 7, 3)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadStopFreq, 7, 4)

        self.Layout_Cfg.addWidget(self.Label_Cfg_RadSamples, 9, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadSamples, 9, 2)

        self.Layout_Cfg.addWidget(self.Label_Cfg_RadPerd, 9, 3)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadPerd, 9, 4)
        
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadNp, 10, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadNp, 10, 2)

        self.Layout_Cfg.addWidget(self.Label_Cfg_FalseAlarmRate, 11, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_FalseAlarmRate, 11, 2)
        

        self.Layout_Cfg.addWidget(self.Label_Cfg_RangeWinType, 14, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RangeWinType, 14, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_VelWinType, 15, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_VelWinType, 15, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_AngWinType, 16, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_AngWinType, 16, 2)




        self.spacerItem = QtWidgets.QSpacerItem(20, 23, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.spacerWidget = QtWidgets.QWidget()
        self.spacerLayout = QtWidgets.QVBoxLayout()
        self.spacerLayout.addItem(self.spacerItem)
        self.spacerWidget.setLayout(self.spacerLayout)
        self.Layout_Cfg.addWidget(self.spacerWidget,17,1)

        self.Widget_Cfg.setLayout(self.Layout_Cfg)


        #--------------------------------------------------------------------------------------
        # Fmcw Measurement Page Time
        #--------------------------------------------------------------------------------------
        # define system widget with grid layout
        inras_logo_path = os.path.join("src","ressource","img","adi.png")
        self.Image_Meas_Logo = QtGui.QImage(inras_logo_path)
        self.Label_Meas_Logo = QtWidgets.QLabel()
        self.Label_Meas_Logo.setMinimumSize(200, 100)
        self.Label_Meas_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_Meas_Logo))

        self.Label_Meas_CfgInf = QtWidgets.QLabel("")
        self.Label_Meas_CfgInf = QtWidgets.QLabel("")
    
        self.Button_Meas_Est = QtWidgets.QPushButton("Estimate")

        self.ChkBox_Cfg_RangeDoppler = QtWidgets.QCheckBox("Range Dopper")
        self.ChkBox_Cfg_RangeDoppler.setChecked(False)


        self.ChkBox_Cfg_DBF = QtWidgets.QCheckBox("Beamforming")
        self.ChkBox_Cfg_DBF.setChecked(False)

        self.Label_Meas_RMin = QtWidgets.QLabel("R Min (m):")
        self.Edit_Meas_RMin = QtWidgets.QLineEdit("1")

        self.Label_Meas_RTar = QtWidgets.QLabel("R Tar. (m):")
        self.Edit_Meas_RTar = QtWidgets.QLineEdit("20")

        self.Label_Meas_RcsTar = QtWidgets.QLabel("RCS Tar. (dBsm):")
        self.Edit_Meas_RcsTar = QtWidgets.QLineEdit("0")

        self.Plot_Meas_Tim = pg.PlotWidget(background=(255, 255, 255))

        self.Plot_Meas_Tim.setLabel('left', "V", units='LSB')
        self.Plot_Meas_Tim.setLabel('bottom', "n", units='Samples')
        self.Plot_Meas_Tim.showGrid(x=True, y=True)

        self.Widget_Meas = QtWidgets.QWidget()
        self.Layout_Meas = QtWidgets.QGridLayout()
        self.Layout_Meas.addWidget(self.Label_Meas_Logo, 0, 0, 3, 1)
        self.Layout_Meas.addWidget(self.Label_Meas_CfgInf, 0, 1, 1, 3)
        self.Layout_Meas.addWidget(self.Button_Meas_Est, 1, 1)

        self.Layout_Meas.addWidget(self.ChkBox_Cfg_DBF, 1, 2)
        self.Layout_Meas.addWidget(self.ChkBox_Cfg_RangeDoppler, 1, 3)


        self.Layout_Meas.addWidget(self.Label_Meas_RMin, 1, 4)
        self.Layout_Meas.addWidget(self.Edit_Meas_RMin, 1, 5)

        self.Layout_Meas.addWidget(self.Label_Meas_RTar, 2, 2)
        self.Layout_Meas.addWidget(self.Edit_Meas_RTar, 2, 3)

        self.Layout_Meas.addWidget(self.Label_Meas_RcsTar, 2, 4)
        self.Layout_Meas.addWidget(self.Edit_Meas_RcsTar, 2, 5)


        self.Layout_Meas.addWidget(self.Plot_Meas_Tim, 3, 0, 1, 8)
        self.Widget_Meas.setLayout(self.Layout_Meas)

        self.TabContWidget.addTab(self.Widget_Cfg,"&Setup")
        self.TabContWidget.addTab(self.Widget_Meas,"&Estimation")
        
        #--------------------------------------------------------------------------------------
        # Position measurement page
        #--------------------------------------------------------------------------------------
        # define system widget with grid layout
        inras_logo_path = os.path.join("src","ressource","img","adi.png")
        self.Image_Posn_Logo = QtGui.QImage(inras_logo_path)
        self.Label_Posn_Logo = QtWidgets.QLabel()
        self.Label_Posn_Logo.setMinimumSize(200, 100)
        self.Label_Posn_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_Meas_Logo))

        self.Label_Posn_CfgInf = QtWidgets.QLabel("")
        self.Plot_Posn_Tim = pg.PlotWidget(background=(255, 255, 255))

        self.Plot_Posn_Tim.setLabel('left', "R", units='m')
        self.Plot_Posn_Tim.setLabel('bottom', "m", units='Meas')

        self.Widget_Posn = QtWidgets.QWidget()
        self.Layout_Posn = QtWidgets.QGridLayout()
        self.Layout_Posn.addWidget(self.Label_Posn_Logo, 0, 0, 3, 1)
        self.Layout_Posn.addWidget(self.Label_Posn_CfgInf, 0, 1, 1, 3)
        self.Layout_Posn.addWidget(self.Plot_Posn_Tim, 3, 0, 1, 8)
        self.Widget_Posn.setLayout(self.Layout_Posn)


        self.IniForm()
              

    def IniForm(self):
        pass

    def IniGui(self):
        labelstr = str(self.patre.GuiFontSiz) + "px"
        labelStyle = {'font-size': labelstr}

        self.Plot_Meas_Tim.setLabel('bottom', "R", units='m', **labelStyle)
        self.Plot_Meas_Tim.setLabel('left', "V", units='dBV', **labelStyle)

        datfont = QtGui.QFont()
        datfont.setPixelSize(self.patre.GuiFontSiz)
        self.Plot_Meas_Tim.getAxis('bottom').tickFont = datfont
        self.Plot_Meas_Tim.getAxis('left').tickFont = datfont
        self.Plot_Meas_Tim.getAxis('bottom').setHeight(int(int(self.patre.GuiFontSiz)*2.7+5))
        self.Plot_Meas_Tim.getAxis('left').setWidth(int(int(self.patre.GuiFontSiz)*2.6+8))
        self.Plot_Meas_Tim.getAxis('bottom').setFont(datfont)
        self.Plot_Meas_Tim.getAxis('left').setFont(datfont)

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

