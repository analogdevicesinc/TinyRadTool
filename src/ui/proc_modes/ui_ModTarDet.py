import  os
import  pyqtgraph as pg
import  numpy as np
import  PyQt5.QtGui as QtGui

class ui_ModTarDet(object):
    def setupUi(self, ModTarDet):
        ModTarDet.setObjectName("ModTarDet")
        self.Log_Textbox = QtGui.QTextEdit()
        self.Log_Textbox.setReadOnly(True)
        self.progressbar = QtGui.QProgressBar()
        self.progressbar.setFixedHeight(10)
        self.progressbar.setTextVisible(False)
        self.progressbar.setRange(0,100)

        self.TabContWidget                  =   QtGui.QTabWidget()

        #--------------------------------------------------------------------------------------
        # TarDet Define Configuration Page
        #--------------------------------------------------------------------------------------
        # define system widget with grid layout
        inras_logo_path = os.path.join("src", "ressource", "img", "adi.png")
        self.Image_Cfg_Logo             =   QtGui.QImage(inras_logo_path)
        self.Label_Cfg_Logo             =   QtGui.QLabel()
        self.Label_Cfg_Logo.setMinimumSize(200, 100)
        #SysLabel_Logo.setAlignment(Qt.AlignCenter)
        self.Label_Cfg_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_Cfg_Logo))

        self.Label_Cfg_RadStrtFreq      =   QtGui.QLabel("Start frequency (MHz):")
        self.Edit_Cfg_RadStrtFreq       =   QtGui.QLineEdit("24010")
         
        self.Label_Cfg_RadStopFreq      =   QtGui.QLabel("Stop frequency (MHz):")
        self.Edit_Cfg_RadStopFreq       =   QtGui.QLineEdit("24240")

        self.Label_Cfg_RadDur           =   QtGui.QLabel("Duration (us):")
        self.Edit_Cfg_RadDur            =   QtGui.QLineEdit("")
        self.Edit_Cfg_RadDur.setDisabled(True)

        self.Label_Cfg_RadPerd          =   QtGui.QLabel("Period (us):")
        self.Edit_Cfg_RadPerd           =   QtGui.QLineEdit("284")
        self.Edit_Cfg_RadPerd.setDisabled(True)

        self.Label_Cfg_RadNp            =   QtGui.QLabel("Np:")
        self.Edit_Cfg_RadNp             =   QtGui.QLineEdit("128")

        self.ChkBox_SigCfg_NormMax      =   QtGui.QCheckBox("Norm (Max)")
        self.ChkBox_SigCfg_NormMax.setChecked(True)
        self.Label_Cfg_LimMaxMin        =   QtGui.QLabel("Min. Limit (dBV):")
        self.Edit_Cfg_LimMaxMin         =   QtGui.QLineEdit("-120")
        self.Label_Cfg_LimMaxSideLev    =   QtGui.QLabel("Sidelobe Level:")
        self.Edit_Cfg_LimMaxSideLev     =   QtGui.QLineEdit("40")
        self.ChkBox_SigCfg_NormFixed    =   QtGui.QCheckBox("Lim (Min/Max)")
        self.ChkBox_SigCfg_NormFixed.setChecked(False)
        self.Label_Cfg_LimFixedMin      =   QtGui.QLabel("Min. Limit (dBV):")
        self.Edit_Cfg_LimFixedMin       =   QtGui.QLineEdit("-130")
        self.Label_Cfg_LimFixedMax      =   QtGui.QLabel("Max. Limit (dBV):")
        self.Edit_Cfg_LimFixedMax       =   QtGui.QLineEdit("-80")
        self.ChkBox_SigCfg_MeanRemove   =   QtGui.QCheckBox("Subtract Mean")
        self.ChkBox_SigCfg_MeanRemove.setChecked(False)

        self.Widget_Cfg                 =   QtGui.QWidget()
        self.Layout_Cfg                 =   QtGui.QGridLayout()
        self.Layout_Cfg.addWidget(self.Label_Cfg_Logo, 0, 0, 1, 1)
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadStrtFreq, 7, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadStrtFreq, 7, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadStopFreq, 8, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadStopFreq, 8, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadDur, 9, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadDur, 9, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadPerd, 10, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadPerd, 10, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_RadNp, 11, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_RadNp, 11, 2)
        self.Layout_Cfg.addWidget(self.ChkBox_SigCfg_NormMax, 12, 1)
        self.Layout_Cfg.addWidget(self.Label_Cfg_LimMaxMin, 13, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_LimMaxMin, 13, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_LimMaxSideLev, 13, 3)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_LimMaxSideLev, 13, 4)
        self.Layout_Cfg.addWidget(self.ChkBox_SigCfg_NormFixed, 14, 1)
        self.Layout_Cfg.addWidget(self.Label_Cfg_LimFixedMin, 15, 1)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_LimFixedMin, 15, 2)
        self.Layout_Cfg.addWidget(self.Label_Cfg_LimFixedMax, 15, 3)
        self.Layout_Cfg.addWidget(self.Edit_Cfg_LimFixedMax, 15, 4)
        self.Layout_Cfg.addWidget(self.ChkBox_SigCfg_MeanRemove,16,1)

        self.spacerItem     = QtGui.QSpacerItem(20, 23, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.spacerWidget   = QtGui.QWidget()
        self.spacerLayout   = QtGui.QVBoxLayout()
        self.spacerLayout.addItem(self.spacerItem)
        self.spacerWidget.setLayout(self.spacerLayout)
        self.Layout_Cfg.addWidget(self.spacerWidget,17,1)

        self.Widget_Cfg.setLayout(self.Layout_Cfg)
        

        #--------------------------------------------------------------------------------------
        # TarDet Measurement Page Time
        #--------------------------------------------------------------------------------------
        # define system widget with grid layout
        inras_logo_path = os.path.join("src","ressource","img","adi.png")
        self.Image_Meas_Logo            =   QtGui.QImage(inras_logo_path)
        self.Label_Meas_Logo            =   QtGui.QLabel()
        self.Label_Meas_Logo.setMinimumSize(200, 100)
        self.Label_Meas_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_Meas_Logo))

        self.Label_Meas_CfgInf                  =   QtGui.QLabel("")
        self.Label_Meas_CfgInf                  =   QtGui.QLabel("")
        self.Label_Meas_Cfg                     =   QtGui.QLabel("Tx Cfg:")
        self.Edit_Meas_Cfg                      =   QtGui.QLineEdit("TX1(100);")
        self.Edit_Meas_Cfg.setDisabled(True)      
        self.Button_Meas_Ini                    =   QtGui.QPushButton("Initialize")
        self.Button_Meas_Meas                   =   QtGui.QPushButton("Measure")
        self.Button_Meas_Meas.setDisabled(True)
        self.ChkBox_Histog                      =   QtGui.QCheckBox("Hide Colormap")
        self.Label_Meas_NrFrms                  =   QtGui.QLabel("NrFrms:")
        self.Edit_Meas_NrFrms                   =   QtGui.QLineEdit("10000")
        self.Label_Meas_RMin                    =   QtGui.QLabel("RMin (m):")
        self.Edit_Meas_RMin                     =   QtGui.QLineEdit("1")
        self.Label_Meas_RMax                    =   QtGui.QLabel("RMax (m):")
        self.Edit_Meas_RMax                     =   QtGui.QLineEdit("15")

        #self.Edit_Meas_NrFrms.setFixedWidth(200)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.plotview = pg.PlotItem()
        self.plotview.setLabel('left', "R", units='m')
        self.plotview.setLabel('bottom', "vn", units=' ')
        #plotview.getAxis('bottom').setPen(color=(0,0,0), width=1)
        self.plotview.getAxis('bottom').setTickSpacing(1, 0.5) # beschriftung, intervall
        self.plotview.getAxis('left').setTickSpacing(5, 1) # beschriftung, intervall
        #plotview.getViewBox().enableAutoRange(axis=plotview.getViewBox().XAxis, enable=True)
        #plotview.getViewBox().enableAutoRange(axis=plotview.getViewBox().YAxis, enable=True)
        #plotview.getAxis('bottom').setHeight(h=None)
        self.Image_Meas = pg.ImageView(view = self.plotview, name="Rane-Doppler Map")

        y = np.random.randn(256,256)
        xscale = 1/128
        yscale = 1/256
        self.Image_Meas.setImage(y, pos=[-1,0], scale=[xscale, yscale])
        self.Image_Meas.ui.roiBtn.hide()
        self.Image_Meas.ui.menuBtn.hide()
        self.Image_Meas.getHistogramWidget().gradient.loadPreset('bipolar')

        self.Label_Meas_Cmd                     =   QtGui.QLabel("           Command: ")
        self.Edit_Meas_Cmd                      =   QtGui.QLineEdit("")
        self.Label_Meas_CmdSts                  =   QtGui.QLabel(" ")
        self.Label_Meas_Cmd.hide()
        self.Edit_Meas_Cmd.hide()
        self.Label_Meas_CmdSts.hide()


        self.Widget_Meas                        =   QtGui.QWidget()
        self.Layout_Meas                        =   QtGui.QGridLayout()
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
        self.Layout_Meas.addWidget(self.ChkBox_Histog, 2, 7)
        self.Layout_Meas.addWidget(self.Image_Meas, 4, 0, 1, 8)
        self.Layout_Meas.addWidget(self.Label_Meas_Cmd, 5, 0, 1, 1)
        self.Layout_Meas.addWidget(self.Edit_Meas_Cmd, 5, 1, 1, 3)
        self.Layout_Meas.addWidget(self.Label_Meas_CmdSts, 5, 4, 1, 4)
        self.Layout_Meas.addWidget(self.progressbar, 6, 0, 1, 8)
        #self.Layout_Meas.addWidget(self.Bar_Meas_MeasProg, 5, 0, 1, 4)

        self.Widget_Meas.setLayout(self.Layout_Meas)

        self.TabContWidget.addTab(self.Widget_Meas,"&Range-Doppler")
        self.TabContWidget.addTab(self.Widget_Cfg,"&Configuration")

        self.Widget_Log = QtGui.QWidget()
        self.Layout_Log = QtGui.QGridLayout()
        self.Label_Log = QtGui.QLabel("Debug Log")
        self.Image_Log_Logo                =   QtGui.QImage(inras_logo_path)
        self.Label_Log_Logo =   QtGui.QLabel()
        self.Label_Log_Logo.setMinimumSize(200, 100)
        self.Label_Log_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_Meas_Logo))

        self.Button_LogtoFile = QtGui.QPushButton("Save Output to file")
        self.Button_ClearLog = QtGui.QPushButton("Clear Log")
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
            self.plotview.setLabel('bottom', "v", units='m/s', **labelStyle)
            self.plotview.setLabel('left', "R", units='m', **labelStyle)

            datfont = QtGui.QFont()
            datfont.setPixelSize(int(self.patre.GuiFontSiz))
            self.plotview.getAxis('bottom').tickFont = datfont
            self.plotview.getAxis('left').tickFont = datfont
            self.plotview.getAxis('bottom').setHeight(int(int(self.patre.GuiFontSiz)*2.7+5))
            self.plotview.getAxis('left').setWidth(int(int(self.patre.GuiFontSiz)*2.6+8))
            self.plotview.getAxis('bottom').setFont(datfont)
            self.plotview.getAxis('left').setFont(datfont)
