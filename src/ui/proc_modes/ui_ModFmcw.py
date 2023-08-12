import  os
import  pyqtgraph as pg
import  numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets


class   Ui_ModFmcw(object):
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
        #SysLabel_Logo.setAlignment(Qt.AlignCenter)
        self.Label_Cfg_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_Cfg_Logo))


        self.Label_Cfg_fs = QtWidgets.QLabel("Sampling frequency (MSPS)")
        self.fsSel = ("1",)
        self.ComboBox_Cfg_fs = QtWidgets.QComboBox()
        self.ComboBox_Cfg_fs.addItems(self.fsSel)
        self.ComboBox_Cfg_fs.setCurrentIndex(0)

        self.Label_Cfg_RadStrtFreq = QtWidgets.QLabel("Start frequency (MHz):")
        #self.Edit_Cfg_RadStrtFreq = QtGui.QLineEdit("23900")
        self.Edit_Cfg_RadStrtFreq = QtWidgets.QLineEdit("24010")
        self.Label_Cfg_RadStopFreq = QtWidgets.QLabel("Stop frequency (MHz):")
        #self.Edit_Cfg_RadStopFreq = QtGui.QLineEdit("24250")
        self.Edit_Cfg_RadStopFreq = QtWidgets.QLineEdit("24240")
        self.Label_Cfg_RadSamples = QtWidgets.QLabel("Samples ( ):")
        self.Edit_Cfg_RadSamples = QtWidgets.QLineEdit("256")
        self.Label_Cfg_RadDur = QtWidgets.QLabel("Chirp Dur. (us):")
        self.Edit_Cfg_RadDur = QtWidgets.QLineEdit("256")
        self.Edit_Cfg_RadDur.setDisabled(True)
        self.Label_Cfg_RadPerd = QtWidgets.QLabel("TInt (ms):")
        self.Edit_Cfg_RadPerd = QtWidgets.QLineEdit("20")


        self.ChkBox_Cfg_Chn1 = QtWidgets.QCheckBox("Chn 1")
        self.ChkBox_Cfg_Chn1.setChecked(True)
        self.CButton_Cfg_Chn1 = pg.ColorButton()
        self.CButton_Cfg_Chn1.setColor((0,0,127))
        self.ChkBox_Cfg_Chn2 = QtWidgets.QCheckBox("Chn 2")
        self.ChkBox_Cfg_Chn2.setChecked(True)
        self.CButton_Cfg_Chn2 = pg.ColorButton()
        self.CButton_Cfg_Chn2.setColor((0,85,0))
        self.ChkBox_Cfg_Chn3 = QtWidgets.QCheckBox("Chn 3")
        self.ChkBox_Cfg_Chn3.setChecked(True)
        self.CButton_Cfg_Chn3 = pg.ColorButton()
        self.CButton_Cfg_Chn3.setColor((255,0,0))
        self.ChkBox_Cfg_Chn4 = QtWidgets.QCheckBox("Chn 4")
        self.ChkBox_Cfg_Chn4.setChecked(True)
        self.CButton_Cfg_Chn4 = pg.ColorButton()
        self.CButton_Cfg_Chn4.setColor((0,0,0))

        self.Label_Cfg_FftSiz = QtWidgets.QLabel("FFT Size")
        self.Edit_Cfg_FftSiz = QtWidgets.QLineEdit("2048")
        self.Label_Cfg_WinType = QtWidgets.QLabel("Window")
        self.Edit_Cfg_WinType = QtWidgets.QLineEdit("Hanning")
        self.Label_Cfg_LineWidth = QtWidgets.QLabel("Line Width")
        self.Edit_Cfg_LineWidth = QtWidgets.QLineEdit("1")
        
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
        
        self.Layout_Cfg.addWidget(self.ChkBox_Cfg_Chn1 , 11, 1)
        self.Layout_Cfg.addWidget(self.CButton_Cfg_Chn1, 11, 2)
        self.Layout_Cfg.addWidget(self.ChkBox_Cfg_Chn2 , 12, 1)
        self.Layout_Cfg.addWidget(self.CButton_Cfg_Chn2, 12, 2)
        self.Layout_Cfg.addWidget(self.ChkBox_Cfg_Chn3, 11, 3)
        self.Layout_Cfg.addWidget(self.CButton_Cfg_Chn3, 11, 4)
        self.Layout_Cfg.addWidget(self.ChkBox_Cfg_Chn4, 12, 3)
        self.Layout_Cfg.addWidget(self.CButton_Cfg_Chn4, 12, 4)

        self.Layout_Cfg.addWidget(self.Label_Cfg_FftSiz, 13, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_FftSiz, 13, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_WinType, 14, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_WinType, 14, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_LineWidth, 15, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_LineWidth, 15, 2)


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
        self.Label_Meas_Cfg = QtWidgets.QLabel("Tx Cfg:")
        self.Edit_Meas_Cfg = QtWidgets.QLineEdit("TX1(20);")        
        self.Button_Meas_Ini = QtWidgets.QPushButton("Initialize")
        self.Button_Meas_Meas = QtWidgets.QPushButton("Measure")
        self.ChkBox_Meas_FFT = QtWidgets.QCheckBox("FFT")
        self.ChkBox_Meas_PSD = QtWidgets.QCheckBox("Average")
        self.Label_Meas_NrFrms = QtWidgets.QLabel("NrFrms:")
        self.Edit_Meas_NrFrms = QtWidgets.QLineEdit("100000")
        self.Label_Meas_RMin = QtWidgets.QLabel("RMin (m):")
        self.Edit_Meas_RMin = QtWidgets.QLineEdit("0")
        self.Label_Meas_RMax = QtWidgets.QLabel("RMax (m):")
        self.Edit_Meas_RMax = QtWidgets.QLineEdit("40")
        self.Plot_Meas_Tim = pg.PlotWidget(background=(255, 255, 255))

        ColorChn = self.CButton_Cfg_Chn1.color()
        PenChn = pg.mkPen(color=ColorChn)
        self.Plot_Meas_Tim.setLabel('left', "V", units='LSB')
        self.Plot_Meas_Tim.setLabel('bottom', "n", units='Samples')
        self.Plot_Meas_Tim.showGrid(x=True, y=True)

        self.Plot_Meas_Rp = pg.PlotWidget(background=(255, 255, 255))
        self.Plot_Meas_Rp.setLabel('left', "RP", units='dBV')
        self.Plot_Meas_Rp.setLabel('bottom', "R", units='m')  
        self.Plot_Meas_Rp.showGrid(x=True, y=True)

        self.Label_Meas_Cmd = QtWidgets.QLabel("           Command: ")
        self.Edit_Meas_Cmd = QtWidgets.QLineEdit("")
        self.Label_Meas_CmdSts = QtWidgets.QLabel(" ")

        self.Label_Meas_Cmd.hide()
        self.Edit_Meas_Cmd.hide()
        self.Label_Meas_CmdSts.hide()
        self.Plot_Meas_Rp.hide()     

        self.Widget_Meas = QtWidgets.QWidget()
        self.Layout_Meas = QtWidgets.QGridLayout()
        self.Layout_Meas.addWidget(self.Label_Meas_Logo, 0, 0, 3, 1)
        self.Layout_Meas.addWidget(self.Label_Meas_CfgInf, 0, 1, 1, 3)
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
        self.Layout_Meas.addWidget(self.ChkBox_Meas_FFT, 2, 6)
        self.Layout_Meas.addWidget(self.ChkBox_Meas_PSD, 2, 7)
        self.Layout_Meas.addWidget(self.Plot_Meas_Tim, 3, 0, 1, 8)
        self.Layout_Meas.addWidget(self.Plot_Meas_Rp, 4, 0, 1, 8)
        self.Layout_Meas.addWidget(self.Label_Meas_Cmd, 5, 0, 1, 1)
        self.Layout_Meas.addWidget(self.Edit_Meas_Cmd, 5, 1, 1, 3)
        self.Layout_Meas.addWidget(self.Label_Meas_CmdSts, 5, 5, 1, 3)
        self.Layout_Meas.addWidget(self.progressbar, 6, 0, 1, 8)

        self.Widget_Meas.setLayout(self.Layout_Meas)

        #--------------------------------------------------------------------------------------
        # Fmcw Measurement Range Time Profile
        #--------------------------------------------------------------------------------------
        # define system widget with grid layout
        inras_logo_path = os.path.join("src","ressource","img","adi.png")
        self.Image_MeasProf_Logo = QtGui.QImage(inras_logo_path)
        self.Label_MeasProf_Logo = QtWidgets.QLabel()
        self.Label_MeasProf_Logo.setMinimumSize(200, 100)
        self.Label_MeasProf_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_Meas_Logo))

        self.Label_MeasProf_CfgInf = QtWidgets.QLabel("")
        self.Label_MeasProf_RMin = QtWidgets.QLabel("RMin (m):")
        self.Edit_MeasProf_RMin = QtWidgets.QLineEdit("1")
        self.Label_MeasProf_RMax = QtWidgets.QLabel("RMax (m):")
        self.Edit_MeasProf_RMax = QtWidgets.QLineEdit("8")
        self.Label_MeasProf_NrHist = QtWidgets.QLabel("NHist:")
        self.Edit_MeasProf_NrHist = QtWidgets.QLineEdit("200")
        self.ChkBox_MeasProf_Histog = QtWidgets.QCheckBox("Hide Colormap")

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.Plotview_MeasProf = pg.PlotItem()
        self.Plotview_MeasProf.setLabel('left', "R", units='m')
        self.Plotview_MeasProf.setLabel('bottom', "n", units=' ')


        self.Image_MeasProf = pg.ImageView(view = self.Plotview_MeasProf, name="Range-Doppler Map")
        self.Plot_MeasProf_Prof = pg.PlotWidget(background=(255, 255, 255))
        y = np.random.randn(int(256),int(256))
        xscale = int(1)
        yscale = int(1)
        self.Image_MeasProf.setImage(y, pos=[0,1], scale=[xscale, yscale])
        self.Image_MeasProf.ui.roiBtn.hide()
        self.Image_MeasProf.ui.menuBtn.hide()
        self.Image_MeasProf.getHistogramWidget().gradient.loadPreset('bipolar')
        self.Widget_MeasProf = QtWidgets.QWidget()
        self.Layout_MeasProf = QtWidgets.QGridLayout()
        self.Layout_MeasProf.addWidget(self.Label_MeasProf_Logo, 0, 0, 3, 1)
        self.Layout_MeasProf.addWidget(self.Label_MeasProf_CfgInf, 0, 1, 1, 3)
        self.Layout_MeasProf.addWidget(self.Label_MeasProf_RMin, 1, 1)
        self.Layout_MeasProf.addWidget(self.Label_MeasProf_RMax, 2, 1)
        self.Layout_MeasProf.addWidget(self.Edit_MeasProf_RMin, 1, 2)
        self.Layout_MeasProf.addWidget(self.Edit_MeasProf_RMax, 2, 2)
        self.Layout_MeasProf.addWidget(self.Label_MeasProf_NrHist, 1, 3)
        self.Layout_MeasProf.addWidget(self.Edit_MeasProf_NrHist, 1, 4)
        self.Layout_MeasProf.addWidget(self.ChkBox_MeasProf_Histog, 2, 4)
        self.Layout_MeasProf.addWidget(self.Image_MeasProf, 3, 0, 1, 5)
        self.Layout_MeasProf.addWidget(self.Image_MeasProf, 3, 0, 1, 5)
        self.Widget_MeasProf.setLayout(self.Layout_MeasProf)

        self.TabContWidget.addTab(self.Widget_Meas,"&FMCW")
        self.TabContWidget.addTab(self.Widget_MeasProf,"&Range-Time")

        self.TabContWidget.addTab(self.Widget_Cfg,"&Configuration")

        self.Widget_Log = QtWidgets.QWidget()
        self.Layout_Log = QtWidgets.QGridLayout()
        self.Label_Log = QtWidgets.QLabel("Debug Log")
        self.Image_Log_Logo = QtGui.QImage(inras_logo_path)
        self.Label_Log_Logo = QtWidgets.QLabel()
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
        self.TabContWidget.addTab(self.Widget_Log,"&Log")


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
        self.Button_Meas_Meas.setText("Measure")
        self.Button_Meas_Meas.setEnabled(False)
        self.Button_Meas_Ini.setEnabled(True)
        self.Edit_Meas_NrFrms.setEnabled(True)


    def IniGui(self):
        labelstr = str(self.patre.GuiFontSiz) + "px"
        labelStyle = {'font-size': labelstr}

        if  self.ChkBox_Meas_FFT.checkState():
            self.Plot_Meas_Tim.setLabel('bottom', "R", units='m', **labelStyle)
            self.Plot_Meas_Tim.setLabel('left', "V", units='dBV', **labelStyle)
        else:
            self.Plot_Meas_Tim.setLabel('bottom', "n", units='Samples', **labelStyle)
            self.Plot_Meas_Tim.setLabel('left', "V", units='LSB', **labelStyle)

        datfont = QtGui.QFont()
        datfont.setPixelSize(self.patre.GuiFontSiz)
        self.Plot_Meas_Tim.getAxis('bottom').tickFont = datfont
        self.Plot_Meas_Tim.getAxis('left').tickFont = datfont
        self.Plot_Meas_Tim.getAxis('bottom').setHeight(int(int(self.patre.GuiFontSiz)*2.7+5))
        self.Plot_Meas_Tim.getAxis('left').setWidth(int(int(self.patre.GuiFontSiz)*2.6+8))
        self.Plot_Meas_Tim.getAxis('bottom').setFont(datfont)
        self.Plot_Meas_Tim.getAxis('left').setFont(datfont)


        self.Plotview_MeasProf.setLabel('bottom', "n", units=' ', **labelStyle)
        self.Plotview_MeasProf.setLabel('left', "R", units='m', **labelStyle)

        #style = { 'tickFont': datfont}
        self.Plotview_MeasProf.getAxis('bottom').tickFont = datfont
        self.Plotview_MeasProf.getAxis('left').tickFont = datfont
        #self.plotview.getAxis('left').setHeight(0)
        self.Plotview_MeasProf.getAxis('bottom').setHeight(int(24*2.7+5))
        self.Plotview_MeasProf.getAxis('left').setWidth(int(24*2.6+8))
        self.Plotview_MeasProf.getAxis('bottom').setFont(datfont)
        self.Plotview_MeasProf.getAxis('left').setFont(datfont)

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

