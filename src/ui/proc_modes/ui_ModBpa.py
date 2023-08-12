import  os
import  pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
import  numpy as np
import  src.logger.Logger as Logger


class   Ui_ModBpa(object):

    def setupUi(self, ModBpa):
        ModBpa.setObjectName("ModBpa")
        self.Log_Textbox = QtWidgets.QTextEdit()
        self.Log_Textbox.setReadOnly(True)
        self.Log_BG_Textbox = QtWidgets.QTextEdit()
        self.progressbar = QtWidgets.QProgressBar()
        self.progressbar.setFixedHeight(10)
        self.progressbar.setTextVisible(False)
        self.progressbar.setRange(0,100)
        self.log = Logger.Logger(self.Log_BG_Textbox, self.Log_Textbox)
        self.TabContWidget = QtWidgets.QTabWidget()

        #--------------------------------------------------------------------------------------
        # Bpa Define Configuration Page
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
        self.Edit_Cfg_RadStrtFreq = QtWidgets.QLineEdit("24010")
        self.Label_Cfg_RadStopFreq = QtWidgets.QLabel("Stop frequency (MHz):")
        self.Edit_Cfg_RadStopFreq = QtWidgets.QLineEdit("24240")
        self.Label_Cfg_RadSamples = QtWidgets.QLabel("Samples ( ):")
        self.Edit_Cfg_RadSamples = QtWidgets.QLineEdit("256")
        self.Label_Cfg_RadDur = QtWidgets.QLabel("Chirp Dur. (us):")
        self.Edit_Cfg_RadDur = QtWidgets.QLineEdit("256")
        self.Edit_Cfg_RadDur.setDisabled(True)
        self.Label_Cfg_RadPerd = QtWidgets.QLabel("TInt (ms):")
        self.Edit_Cfg_RadPerd = QtWidgets.QLineEdit("20")
        
        self.ChkBox_SigCfg_NormMax = QtWidgets.QCheckBox("Norm (Max)")
        self.ChkBox_SigCfg_NormMax.setChecked(True)
        self.Label_Cfg_LimMaxMin = QtWidgets.QLabel("Min. Limit (dBV):")
        self.Edit_Cfg_LimMaxMin = QtWidgets.QLineEdit("-100")
        self.Label_Cfg_LimMaxSideLev = QtWidgets.QLabel("Sidelobe Level:")
        self.Edit_Cfg_LimMaxSideLev = QtWidgets.QLineEdit("15")
        self.ChkBox_SigCfg_NormFixed = QtWidgets.QCheckBox("Lim (Min/Max)")
        self.ChkBox_SigCfg_NormFixed.setChecked(False)
        self.Label_Cfg_LimFixedMin = QtWidgets.QLabel("Min. Limit (dBV):")
        self.Edit_Cfg_LimFixedMin = QtWidgets.QLineEdit("-80")
        self.Label_Cfg_LimFixedMax = QtWidgets.QLabel("Max. Limit (dBV):")
        self.Edit_Cfg_LimFixedMax = QtWidgets.QLineEdit("-20")

        self.Label_Cfg_RangeFftSiz = QtWidgets.QLabel("FFT Size Range")
        self.Edit_Cfg_RangeFftSiz = QtWidgets.QLineEdit("2048")
        self.Label_Cfg_RangeWinType = QtWidgets.QLabel("Window Range")
        self.Edit_Cfg_RangeWinType = QtWidgets.QLineEdit("Hanning")
        self.Label_Cfg_AngWinType = QtWidgets.QLabel("Window Angle")
        self.Edit_Cfg_AngWinType = QtWidgets.QLineEdit("Hanning")


        self.Widget_Cfg = QtWidgets.QWidget()
        self.Layout_Cfg = QtWidgets.QGridLayout()
        self.Layout_Cfg.addWidget(self.Label_Cfg_Logo, 0, 0, 1, 1)
        self.Layout_Cfg.addWidget(self.Label_Cfg_fs, 5, 1)
        self.Layout_Cfg.addWidget(self.ComboBox_Cfg_fs, 5, 2)          
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadStrtFreq, 7, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadStrtFreq, 7, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadStopFreq, 8, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadStopFreq, 8, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadSamples, 9, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadSamples, 9, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadDur, 9, 3)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadDur, 9, 4)
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadPerd, 10, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadPerd, 10, 2)

        self.Layout_Cfg.addWidget(self.ChkBox_SigCfg_NormMax, 11, 1)
        self.Layout_Cfg.addWidget(self.Label_Cfg_LimMaxMin, 12, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_LimMaxMin, 12, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_LimMaxSideLev, 12, 3)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_LimMaxSideLev, 12, 4)
        self.Layout_Cfg.addWidget(self.ChkBox_SigCfg_NormFixed, 13, 1)
        self.Layout_Cfg.addWidget(self.Label_Cfg_LimFixedMin, 14, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_LimFixedMin, 14, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_LimFixedMax, 14, 3)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_LimFixedMax, 14, 4)

        self.Layout_Cfg.addWidget(self.Label_Cfg_RangeFftSiz, 15, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RangeFftSiz, 15, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_RangeWinType, 16, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RangeWinType, 16, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_AngWinType, 17, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_AngWinType, 17, 2)  


        self.spacerItem     = QtWidgets.QSpacerItem(20, 23, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.spacerWidget   = QtWidgets.QWidget()
        self.spacerLayout   = QtWidgets.QVBoxLayout()
        self.spacerLayout.addItem(self.spacerItem)
        self.spacerWidget.setLayout(self.spacerLayout)
        self.Layout_Cfg.addWidget(self.spacerWidget,18,1)

        self.Widget_Cfg.setLayout(self.Layout_Cfg)


        #--------------------------------------------------------------------------------------
        # Bpa Measurement Page Time
        #--------------------------------------------------------------------------------------
        # define system widget with grid layout
        inras_logo_path = os.path.join("src","ressource","img","adi.png")
        self.Image_Meas_Logo = QtGui.QImage(inras_logo_path)
        self.Label_Meas_Logo = QtWidgets.QLabel()
        self.Label_Meas_Logo.setMinimumSize(200, 100)
        self.Label_Meas_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_Meas_Logo))

        self.Label_Meas_CfgInf = QtWidgets.QLabel("")
        self.Label_Meas_Cfg = QtWidgets.QLabel("Tx Cfg:")
        self.Edit_Meas_Cfg = QtWidgets.QLineEdit("TX1(100); MimoEna")
        self.Button_Meas_Ini = QtWidgets.QPushButton("Initialize")
        self.Button_Meas_Meas = QtWidgets.QPushButton("Measure")
        self.Button_Meas_Meas.setDisabled(True)
        self.ChkBox_Histog = QtWidgets.QCheckBox("Hide Colormap")
        self.Label_Meas_NrFrms = QtWidgets.QLabel("NrFrms:")
        self.Edit_Meas_NrFrms = QtWidgets.QLineEdit("10000")
        self.Label_Meas_RMin = QtWidgets.QLabel("RMin (m):")
        self.Edit_Meas_RMin = QtWidgets.QLineEdit("1")
        self.Label_Meas_RMax = QtWidgets.QLabel("RMax (m):")
        self.Edit_Meas_RMax = QtWidgets.QLineEdit("6")

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')        
        self.plotview = pg.PlotItem()

        #self.plotview.setLabel('left', "y", units='m')
        #self.plotview.setLabel('bottom', "x", units='m')
        labelStyle = {'font-size': '20px'}
        self.plotview.setLabel('bottom', "x", units='m', **labelStyle)
        self.plotview.setLabel('left', "y", units='m', **labelStyle)
        #style = {'tickTextHeight':100, 'tickTextWidth':100}
        datfont = QtGui.QFont()
        datfont.setPixelSize(self.patre.GuiFontSiz)
        #style = { 'tickFont': datfont}
        self.plotview.getAxis('bottom').tickFont = datfont
        self.plotview.getAxis('left').tickFont = datfont
        #self.plotview.getAxis('left').setHeight(0)
        self.plotview.getAxis('bottom').setHeight(int(24*1.7+5))
        self.plotview.getAxis('left').setWidth(int(24*2.6+8))
        self.plotview.getAxis('bottom').setFont(datfont)
        self.plotview.getAxis('left').setFont(datfont)

        self.Image_Meas     = pg.ImageView(view=self.plotview, name="DBF Map")

        self.Plot_Meas = pg.PlotWidget(background=(255, 255, 255))
        PenChn = pg.mkPen(color=(255, 15, 0))
        x = np.arange(1000)
        y = np.zeros(1000)
        self.Plot_Meas.plot(x, y, pen=PenChn)
        self.Plot_Meas.setLabel('left', "V", units='LSB')
        self.Plot_Meas.setLabel('bottom', "n", units='Samples')        
        self.Plot_Meas.hide()
        
        y = np.random.randn(256,256)
        xscale = 1/128
        yscale = 1/256
        self.Image_Meas.setImage(y, pos=[-1,0], scale=[xscale, yscale])
        self.Image_Meas.ui.roiBtn.hide()
        self.Image_Meas.ui.menuBtn.hide()
        # https://github.com/campagnola/pyqtgraph/blob/master/pyqtgraph/graphicsItems/GradientEditorItem.py
        self.Image_Meas.getHistogramWidget().gradient.loadPreset('bipolar')

        self.Label_Meas_Cmd = QtWidgets.QLabel("           Command: ")
        self.Edit_Meas_Cmd = QtWidgets.QLineEdit("")
        self.Label_Meas_CmdSts = QtWidgets.QLabel(" ")
        self.Label_Meas_Cmd.hide()
        self.Edit_Meas_Cmd.hide()
        self.Label_Meas_CmdSts.hide()

        self.Widget_Meas = QtWidgets.QWidget()
        self.Layout_Meas = QtWidgets.QGridLayout()
        self.Layout_Meas.addWidget(self.Label_Meas_Logo, 0, 0, 3, 1)
        self.Layout_Meas.addWidget(self.Label_Meas_CfgInf, 0, 1, 1, 4)
        self.Layout_Meas.addWidget(self.Label_Meas_Cfg, 0, 6)
        self.Layout_Meas.addWidget(self.Edit_Meas_Cfg, 0, 7)
        self.Layout_Meas.addWidget(self.Button_Meas_Ini, 1, 1)
        self.Layout_Meas.addWidget(self.Button_Meas_Meas, 2, 1)
        self.Layout_Meas.addWidget(self.Label_Meas_NrFrms, 1, 2)
        self.Layout_Meas.addWidget(self.Edit_Meas_NrFrms, 1, 3)
        self.Layout_Meas.addWidget(self.Label_Meas_RMin, 1, 4)
        self.Layout_Meas.addWidget(self.Edit_Meas_RMin, 1, 5)
        self.Layout_Meas.addWidget(self.Label_Meas_RMax, 1, 6)
        self.Layout_Meas.addWidget(self.Edit_Meas_RMax, 1, 7)
        self.Layout_Meas.addWidget(self.ChkBox_Histog, 2, 7)
        self.Layout_Meas.addWidget(self.Image_Meas, 4, 0, 1, 8)
        self.Layout_Meas.addWidget(self.Plot_Meas, 5, 0, 1, 8)
        self.Layout_Meas.addWidget(self.Label_Meas_Cmd, 6, 0, 1, 1)
        self.Layout_Meas.addWidget(self.Edit_Meas_Cmd, 6, 1, 1, 3)
        self.Layout_Meas.addWidget(self.Label_Meas_CmdSts, 6, 5, 1, 3)
        self.Layout_Meas.addWidget(self.progressbar, 7, 0, 1, 8)

        self.Widget_Meas.setLayout(self.Layout_Meas)

        self.TabContWidget.addTab(self.Widget_Meas,"&DBF")
        self.TabContWidget.addTab(self.Widget_Cfg,"&Configuration")

        self.Widget_Log = QtWidgets.QWidget()
        self.Layout_Log = QtWidgets.QGridLayout()
        self.Label_Log = QtWidgets.QLabel("Debug Log")
        self.Image_Log_Logo = QtGui.QImage(inras_logo_path)
        self.Label_Log_Logo =   QtWidgets.QLabel()
        self.Label_Log_Logo.setMinimumSize(200, 100)
        self.Label_Log_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_Meas_Logo))

        self.Button_LogtoFile = QtWidgets.QPushButton("Save Output to file")
        self.Button_ClearLog = QtWidgets.QPushButton("Clear Log")
        self.Layout_Log.addWidget(self.Label_Log_Logo, 0, 0, 3, 1)
        self.Layout_Log.addWidget(self.Label_Log, 0, 1, 1, 1)
        self.Layout_Log.addWidget(self.Button_LogtoFile, 1, 1, 1, 1)
        self.Layout_Log.addWidget(self.Button_ClearLog, 1, 2)
        self.Layout_Log.addWidget(self.Log_Textbox, 3, 0, 1, 7)

        self.Widget_Log.setLayout(self.Layout_Log)

        if True:
            self.TabContWidget.addTab(self.Widget_Log,"&Log")

        self.IniForm()

    def IniForm(self):
            self.Button_Meas_Meas.setText("Measure")
            self.Button_Meas_Meas.setEnabled(False)
            self.Button_Meas_Ini.setEnabled(True)
            self.Edit_Meas_NrFrms.setEnabled(True)

    def IniGui(self):
            labelstr = str(self.patre.GuiFontSiz) + "px"
            labelStyle = {'font-size': labelstr}
            self.plotview.setLabel('bottom', "x", units='m', **labelStyle)
            self.plotview.setLabel('left', "y", units='m', **labelStyle)

            datfont = QtGui.QFont()
            datfont.setPixelSize(int(self.patre.GuiFontSiz))
            self.plotview.getAxis('bottom').tickFont = datfont
            self.plotview.getAxis('left').tickFont = datfont
            self.plotview.getAxis('bottom').setHeight(int(int(self.patre.GuiFontSiz)*2.7+5))
            self.plotview.getAxis('left').setWidth(int(int(self.patre.GuiFontSiz)*2.6+8))
            self.plotview.getAxis('bottom').setFont(datfont)
            self.plotview.getAxis('left').setFont(datfont)

