import  src.cmd_modules.TinyRad as TinyRad
import  src.S14.S14_ModBpa as S14_ModBpa

import  src.logger.Logger as Logger
import  src.cmd_modules.StrConv as StrConv

from PyQt5 import QtCore, QtGui, QtWidgets
import  pyqtgraph as pg
import  threading as threading
import  time as time
import  numpy as np
import  src.ui.proc_modes.ui_ModBpa as ui_ModBpa
from    os.path import expanduser
import  re
#import  h5py


class ModBpa(QtWidgets.QMainWindow, ui_ModBpa.Ui_ModBpa):
    fullscreen_state = False
    plot_state = False
    histog_state = False
    SigIniTim = QtCore.pyqtSignal()
    SigIniDone = QtCore.pyqtSignal()
    SigProgressDone = QtCore.pyqtSignal()
    SigMenuEna = QtCore.pyqtSignal()
    SigMenuDi = QtCore.pyqtSignal()
    SigMeasStop = QtCore.pyqtSignal()

    SigUpdIni = QtCore.pyqtSignal()  
    IniThread = None
    MeasIni = None  

    lUpdIni = list()
    LockUpdIni = threading.Lock()

    stCfgInf = ""
    InitFailed = True


    # Configuration of Signal Processing
    dSigCfg = dict()
    def __init__(self, patre):
        super(ModBpa, self).__init__()
        self.patre = patre
        self.setupUi(self)
        self.Button_Meas_Meas.clicked.connect(self.Button_Meas_StartThread)
        self.Button_Meas_Ini.clicked.connect(self.Button_Ini_StartThread)
        self.ChkBox_Histog.clicked.connect(self.ChkBox_Histog_stateChanged)
        QtWidgets.QShortcut(QtGui.QKeySequence("F11"), self.Widget_Meas, self.toggleFullScreen)
        QtWidgets.QShortcut(QtGui.QKeySequence("F10"), self.Widget_Meas, self.toggleHistog)
        self.Button_LogtoFile.clicked.connect(self.Button_LogToFile_Clicked)
        self.Button_ClearLog.clicked.connect(self.Button_ClearLog_Clicked)
        self.Edit_Meas_Cmd.returnPressed.connect(self.CmdExec)
        self.SigIniTim.connect(self.SigActionTimerStart)
        self.SigIniDone.connect(self.SigActionInitDone)
        self.SigProgressDone.connect(self.SigActionSetProgressDone)
        self.SigMenuEna.connect(self.SigActionShowMenubar)
        self.SigMenuDi.connect(self.SigActionHideMenubar)
        self.SigMeasStop.connect(self.SigActionMeasureStop)
        self.SigUpdIni.connect(self.SigActionUpdIni)

        self.Log = Logger.Logger(self.Log_Textbox)

        self.SigCfg_RangeNFFTCfg = 1024
        self.SigCfg_RangeWinType = 'Hanning'
        self.SigCfg_Ny = 128
        self.SigCfg_Nx = 256
        self.PltCfg_LineWidth = 2.0
        self.ProcFrms = 0
        self.SigCfg_ViewAngDeg = 45
        self.PltCfg_SegLineWidth = 10
        self.lPlotData = list()

        self.RefMap = 0
        self.CalData = 0
        self.MeasData = 0

        self.SigCfg_Imx = 0
        self.SigCfg_Imy = 0
        self.dBrdCfg = dict()

        self.RMin = 1.0
        self.RMax = 10.0

        self.SigCfg_NIni = 10

        self.VirtAntScale = -1
        self.UserWin = False

        self.ShowRp = False
        self.SigCfg_BpaSeg = False

        if self.patre.GuiSelIni:
            self.ParseCfgFile(self.patre.stFileCfg)

        self.toggleHistog()
        self.CmdHide = True
        self.Brd = None

        self.MimoEna = 0

        self.LimFreq()
    
    def LimFreq(self):
        stStrtFreq = self.Edit_Cfg_RadStrtFreq.text()
        fMin = StrConv.ToFloat(stStrtFreq)*1e6            
        stStopFreq = self.Edit_Cfg_RadStopFreq.text()
        fMax = StrConv.ToFloat(stStopFreq)*1e6

        if fMin < self.patre.Lim_fMin:
            fMin = self.patre.Lim_fMin
            self.UpdIniAppend('Func','self.Edit_Cfg_RadStrtFreq.setText',str(fMin/1e6)) 
        if fMax > self.patre.Lim_fMax:
            fMax = self.patre.Lim_fMax
            self.UpdIniAppend('Func','self.Edit_Cfg_RadStopFreq.setText',str(fMax/1e6)) 

        if fMax <= fMin:
            fMin = self.patre.Lim_fMin
            self.UpdIniAppend('Func','self.Edit_Cfg_RadStrtFreq.setText',str(fMin/1e6))             
            fMax = self.patre.Lim_fMax
            self.UpdIniAppend('Func','self.Edit_Cfg_RadStopFreq.setText',str(fMax/1e6))             

        
        self.SigUpdIni.emit()            

    def ToggleCmd(self):
        if self.CmdHide:
            self.CmdHide = False
            self.Label_Meas_Cmd.show()
            self.Edit_Meas_Cmd.show()
            self.Label_Meas_CmdSts.show()  
        else:
            self.CmdHide = True
            self.Label_Meas_Cmd.hide()
            self.Edit_Meas_Cmd.hide()
            self.Label_Meas_CmdSts.hide()  

    def CmdExec(self):
        CmdExec = False
        stCmd = self.Edit_Meas_Cmd.text()        
        RegCmd = re.compile(r"Store\(\"(?P<File>[\w]+.h5)\"\)")
        Match = RegCmd.search(stCmd)
        if Match:
            CmdExec = True
            stFile = self.patre.stFolderCfg + Match.group("File")
            with h5py.File(stFile,'w') as hFile:
                hFile.create_dataset('/Data', data = self.MeasData.transpose())
                hFile.create_dataset('/RefMap', data = self.RefMap.transpose())
                hFile.create_dataset('/vImx', data = self.SigCfg_Imx)
                hFile.create_dataset('/vImy', data = self.SigCfg_Imy)               
                for Key in self.dBrdCfg:
                    print('/BrdCfg/' + str(Key))
                    if isinstance(self.dBrdCfg[Key],str):
                        print(np.fromstring(self.dBrdCfg[Key]))
                        Dat = list()
                        Dat.append(self.dBrdCfg[Key])
                        dt = h5py.special_dtype(vlen=bytes)
                        DatSet = hFile.create_dataset('/BrdCfg/' + str(Key), (100,1), dtype=dt)
                        DatSet.attrs["name"] = (self.dBrdCfg[Key])      
                    else:
                        hFile.create_dataset('/BrdCfg/' + str(Key), data = self.dBrdCfg[Key])            
            #sio.savemat(stFile, dSave)
            self.Label_Meas_CmdSts.setText("File " + Match.group("File") + " written")            

        if not CmdExec:
            self.Label_Meas_CmdSts.setText("Command " + stCmd + " not known")  
            self.Edit_Meas_Cmd.setText("")   

    def toggleFullScreen(self):
        if self.fullscreen_state:
            self.fullscreen_state = False
            self.fullscreen_layout.removeWidget(self.Image_Meas)
            self.Layout_Meas.addWidget(self.Image_Meas, 4, 0, 1, 8)
            self.fullscreen_widget.close()
        else:
            self.fullscreen_widget = QtGui.QWidget()
            self.fullscreen_child_window = QtGui.QWidget(self.fullscreen_widget)
            self.fullscreen_layout = QtGui.QVBoxLayout(self.fullscreen_widget)
            self.fullscreen_layout.addWidget(self.Image_Meas)
            self.fullscreen_widget.showFullScreen()
            QtGui.QShortcut(QtGui.QKeySequence("F11"), self.fullscreen_child_window, self.toggleFullScreen)
            QtGui.QShortcut(QtGui.QKeySequence("F10"), self.fullscreen_child_window, self.toggleHistogFullScreen)
            self.fullscreen_state = True


    def ChkBox_Histog_stateChanged(self):
        if self.ChkBox_Histog.isChecked():
            self.Image_Meas.ui.histogram.hide()
            self.histog_state = False
        else:
            self.Image_Meas.ui.histogram.show()
            self.histog_state = True

    def toggleHistog(self):
        if self.ChkBox_Histog.isChecked():
            self.ChkBox_Histog.setChecked(False)
            self.Image_Meas.ui.histogram.show()
            self.histog_state = True
        else:
            self.ChkBox_Histog.setChecked(True)
            self.Image_Meas.ui.histogram.hide()
            self.histog_state = False

    def toggleHistogFullScreen(self):
        if self.histog_state:
            self.Image_Meas.ui.histogram.hide()
            self.histog_state = False
        else:
            self.Image_Meas.ui.histogram.show()
            self.histog_state = True

    def Button_Meas_Meas_Clicked(self):

        stTxt = self.Button_Meas_Meas.text()
        if stTxt == "Measure":
            self.ProcFrms = 0
            self.NrFrmsInit = self.Edit_Meas_NrFrms.text()
            stNrFrms = self.Edit_Meas_NrFrms.text()
            self.MeasNrFrmsIni = StrConv.ToInt(stNrFrms)
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
            self.Label_Meas_CfgInf.setPalette(palette)
            self.Label_Meas_CfgInf.setText("Starting Measurement...")
            self.Log.Append("Starting Measurement...")

            self.SigIniTim.emit()
            self.SigProgressDone.emit()
            self.SigIniDone.emit()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.black)
            self.Label_Meas_CfgInf.setPalette(palette)
            self.Label_Meas_CfgInf.setText(self.stCfgInf)
            self.Button_Meas_Meas.setText("Stop")
        else:
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
            self.Label_Meas_CfgInf.setPalette(palette)

            self.Label_Meas_CfgInf.setText("Stopping Measurement...")
            self.Log.Append("Stopping Measurement...")
            self.Edit_Meas_NrFrms.setText(str(0))
            self.Log.Append("Brd Reset...")
            self.Brd.BrdRst()

        self.Log.SigUpd.emit()
           
    def SigActionSetProgressDone(self):
        self.progressbar.setRange(0,100)
        self.progressbar.setValue(100)

    def SigActionTimerStart(self):
        self.Timer = QtCore.QTimer()
        self.Timer.timeout.connect(self.MeasUpdate)
        self.Timer.setSingleShot(True)
        self.Timer.setInterval(20)
        self.Timer.start()

    def UpdIniAppend(self,stType, stVal,Val):
        self.LockUpdIni.acquire()
        self.lUpdIni.append((stType, stVal, Val))
        self.LockUpdIni.release()

    def SigActionUpdIni(self):
        self.LockUpdIni.acquire()
        for Elem in self.lUpdIni:
            if Elem[0] == 'Func':
                stCmd = Elem[1] + '(Elem[2])'
                eval(stCmd)
            if Elem[0] == 'FuncV':
                stCmd = Elem[1] + '(' + str(Elem[2]) + ')'
                eval(stCmd)            
            if Elem[0] == 'FuncSt':
                stCmd = Elem[1] + '(' + Elem[2] + ')'
                eval(stCmd)      
        self.lUpdIni = list()
        self.LockUpdIni.release()
    
    def Button_LogToFile_Clicked(self):
        StoreData = self.Log.GetTxt()
        Home = expanduser("~")
        FileName = QtGui.QFileDialog.getSaveFileName(self, str("Set Output Path"), Home)
        if FileName != "":
            fs = open(FileName, 'w', encoding="utf-8", errors="ignore")
            fs.write(StoreData)
            fs.close()

    def Button_ClearLog_Clicked(self):
        self.Log.ClrTxt()

    def SigActionShowMenubar(self):
        try:
            self.patre.menuBar().setEnabled(True)
        except IOError:
            print("cought exception")

    def SigActionHideMenubar(self):
        try:
            self.patre.menuBar().setEnabled(False)
        except IOError:
            print("cought exception")

    def Button_Ini_StartThread(self):

        self.SigMenuDi.emit()
        self.IniStrt()
        self.Button_Meas_Ini_Clicked()
        self.Button_Meas_Meas.setDisabled(False)

    def Button_Meas_StartThread(self):


        print("Measurement Button Pressed")
        self.SigMenuDi.emit()
        self.MeasIni = True
        self.IniStrt()

        stTxt= self.Button_Meas_Meas.text()
        if stTxt == "Measure":
            self.progressbar.setRange(0,0)
            self.progressbar.setValue(0)
            self.Edit_Meas_NrFrms.setText(str(self.dBrdCfg["NrFrms"]))
            self.Button_Meas_Ini.setDisabled(True)
            self.Button_Meas_Meas_Clicked()
        else:
            self.progressbar.setRange(0,100)
            self.progressbar.setValue(0)
            self.Timer.start()
            self.Button_Meas_Meas.setDisabled(True)
            self.Button_Meas_Meas_Clicked()
            self.Button_Meas_Ini.setDisabled(False)            

    def Button_Meas_Ini_Clicked(self):

        self.LimFreq()
        self.Log.Append("Bpa: Button Ini Clicked")

        IniSts = 0
        self.ProcFrms = 0
        dIniAdc = self.GetAdcCfg()

        print("Check App Status")
        if self.Brd == None:
            self.Brd = self.patre.hTinyRad

        RetVal = self.Brd.BrdGetUID() 
        if RetVal[0] == False:
            Ret = -1
            self.Log.Append("Application not responding: " + str(RetVal[0]))
            self.Log.Append("Reset Board and Restart Application")
        else:
            Ret = 0
            self.Log.Append("Application running" + str(RetVal[0]) + ' | ' + str(RetVal[1]))
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
            self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setPalette', palette) 
            self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setText', "Application running") 


        self.SigUpdIni.emit()
        self.Log.SigUpd.emit()

        if Ret == 0:
            dSwSts = self.Brd.BrdGetSwVers()
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
            self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setPalette', palette)
            self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setText', "Connected: Initializing...")
            self.Log.Append("Connected: Initializing...")

            self.SigUpdIni.emit()
            self.Log.SigUpd.emit()
                    
            IniSts = 1
            CalError = False

            dIniBpa = self.GetBpaCfg()
            self.dBrdCfg = self.GetBrdCfg(dIniAdc, dIniBpa)
            self.IniBpaMap()

            # reset board to correctly read cal data
            self.Brd.BrdRst()
            dCalData = self.Brd.BrdGetCalDat()

            self.RfBrd = S14_ModBpa.S14_ModBpa(self.Brd, self.dBrdCfg)
            self.RfBrd.IniBrdModBpa()

            self.dBrdCfg["FreqStrt"] = self.Brd.Adf_Pll.fStrt
            self.dBrdCfg["FreqStop"] = self.Brd.Adf_Pll.fStop
            self.dBrdCfg["TimUp"] = self.Brd.Adf_Pll.TRampUp

            print("fStop: ", self.Brd.Adf_Pll.fStop)
            print("T: ", self.Brd.Adf_Pll.TRampUp)

            self.MimoEna = self.RfBrd.MimoEna  

            self.dBrdCfg["NRx"] = len(self.RfBrd.Rad.RfGet('RxPosn'))
            
            
            if self.MimoEna > 0:
                IdxStrt = 0   
                IdxStop = 8    
                self.dBrdCfg['NTx'] = 2  
                self.dBrdCfg["Tx2"] = 2       
            else:
                IdxStrt = 0   
                IdxStop = 4
                self.dBrdCfg['NTx'] = 1
                self.dBrdCfg["Tx2"] = 1

            CalDataCplx = dCalData["Dat"]
            CalDataCplx = CalDataCplx[int(IdxStrt):int(IdxStop)]

            print("Cal:", CalDataCplx)
            self.mCal = np.tile(np.transpose(CalDataCplx),(self.SigCfg_NFFT,1))
                  
        else:
            IniSts = -1

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.black)
        self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setPalette', palette)        

        if IniSts == 1:
            self.IniBpaMat()
            fs = np.round(self.dBrdCfg["fs"]/1e6*1000)/1000
            self.stCfgInf = "Cfg: fs = " + str(fs) + " (MHz) | N = " + str(self.dBrdCfg["N"]) + " | Tup = " + str(round(self.dBrdCfg["TimUp"]/1e-6/10)*10) + " us"
            if CalError == True:
                self.stCfgInf  += "| Calibration data invalid"
            self.UpdIniAppend('Func','self.SetInitFailed', False)  
        elif IniSts < 0:
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
            self.UpdIniAppend('Func','self.SetCfgInf','Board not responding') 
            self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setPalette', palette)
            self.UpdIniAppend('Func','self.SetInitFailed', True)          
        else:
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
            self.Label_Meas_CfgInf.setPalette(palette)
            self.stCfgInf = "Initialization failed"
            self.UpdIniAppend('Func','self.SetInitFailed', True)  
        
        self.UpdIniAppend('FuncSt','self.Label_Meas_CfgInf.setText', 'self.stCfgInf') 
        self.Log.Append(self.stCfgInf)
        
        if IniSts > 0:
            # configure plot options
            self.PenChn = pg.mkPen(color=(255, 255, 255), width=self.PltCfg_SegLineWidth)
            Phi = np.linspace(90 - self.SigCfg_ViewAngDeg, 90 + self.SigCfg_ViewAngDeg, num = 180)/180*np.pi

            self.xLimMin = self.RMin*np.cos(Phi)
            self.yLimMin = self.RMin*np.sin(Phi)
            self.xLimMax = self.RMax*np.cos(Phi)
            self.yLimMax = self.RMax*np.sin(Phi)        
            self.xLimAngPos = (self.RMin*np.cos((90 - self.SigCfg_ViewAngDeg)/180*np.pi), self.RMax*np.cos((90 - self.SigCfg_ViewAngDeg)/180*np.pi))
            self.yLimAngPos = (self.RMin*np.sin((90 - self.SigCfg_ViewAngDeg)/180*np.pi), self.RMax*np.sin((90 - self.SigCfg_ViewAngDeg)/180*np.pi))
            self.xLimAngNeg = (self.RMin*np.cos((90 + self.SigCfg_ViewAngDeg)/180*np.pi), self.RMax*np.cos((90 + self.SigCfg_ViewAngDeg)/180*np.pi))
            self.yLimAngNeg = (self.RMin*np.sin((90 + self.SigCfg_ViewAngDeg)/180*np.pi), self.RMax*np.sin((90 + self.SigCfg_ViewAngDeg)/180*np.pi))

        self.SigUpdIni.emit()
        self.Log.SigUpd.emit()
        self.SigIniDone.emit()

    def SigActionInitDone(self):
        if self.MeasIni != None:
            self.Button_Meas_Meas.setDisabled(False)
        else:
            if self.InitFailed:
                self.Button_Meas_Meas.setDisabled(True)
            else:
                self.Button_Meas_Meas.setDisabled(False)
            
            self.Button_Meas_Ini.setDisabled(False)
            self.Edit_Meas_NrFrms.setDisabled(False)
            self.Edit_Meas_RMin.setDisabled(False)
            self.Edit_Meas_RMax.setDisabled(False)
            self.Edit_Meas_Cfg.setDisabled(False)
            self.SigMenuEna.emit()
            self.SigProgressDone.emit()

    def SigActionMeasureStop(self):
        self.Timer.stop()
        self.Button_Meas_Ini.setDisabled(False)
        self.Edit_Meas_NrFrms.setDisabled(False)
        self.Edit_Meas_RMin.setDisabled(False)
        self.Edit_Meas_RMax.setDisabled(False)
        
        self.Edit_Meas_Cfg.setEnabled(True)

        self.SigMenuEna.emit()
        self.SigProgressDone.emit()
        self.Button_Meas_Meas.setText("Measure")
        self.Edit_Meas_NrFrms.setText(str(self.NrFrmsInit))
        self.Label_Meas_CfgInf.setText("Measurement Stopped")
        self.MeasIni = None

    def IniStrt(self):
        self.progressbar.setRange(0,0)
        self.progressbar.setValue(0)

        self.Button_Meas_Ini.setDisabled(True)
        self.Edit_Meas_NrFrms.setDisabled(True)
        self.Edit_Meas_RMin.setDisabled(True)
        self.Edit_Meas_RMax.setDisabled(True)
        self.Edit_Meas_Cfg.setDisabled(True)

    def MeasUpdate(self):
        stNrFrms = self.Edit_Meas_NrFrms.text()
        NrFrms = int(stNrFrms)
        NrFrms = NrFrms - 1
        self.Edit_Meas_NrFrms.setText(str(NrFrms))


        if NrFrms <= 0:
            self.SigMeasStop.emit()
            self.SigMenuEna.emit()
            self.RfBrd.CloseBrdMod0()

        else:
            
            Data = self.RfBrd.GetDataEve()
            self.MeasData = np.copy(Data)
            N = self.RfBrd.Rad.Get('N')
            NrChn = self.RfBrd.Rad.Get('NrChn')
            ProcData = False
            if hasattr(Data, "shape"):
                DatSiz = Data.shape
                if (len(DatSiz) == 2): 
                    if (DatSiz[0] == N*self.dBrdCfg["NTx"]) and (DatSiz[1] == NrChn):
                        ProcData = True   

            if ProcData:
                if self.ProcFrms < 1 and self.SigCfg_BpaSeg:

                    if len(self.lPlotData) > 0:
                        # remove items from list
                        for Elem in self.lPlotData:
                            self.plotview.removeItem(Elem)
                        self.lPlotData = list()       

                    self.lPlotData.append(self.plotview.plot(self.xLimMin , self.yLimMin , pen=self.PenChn))
                    self.lPlotData.append(self.plotview.plot(self.xLimMax , self.yLimMax , pen=self.PenChn))
                    self.lPlotData.append(self.plotview.plot(self.xLimAngPos , self.yLimAngPos , pen=self.PenChn))
                    self.lPlotData.append(self.plotview.plot(self.xLimAngNeg , self.yLimAngNeg , pen=self.PenChn))


                self.ProcFrms = self.ProcFrms + 1;
                self.progressbar.setRange(0,100)
                self.progressbar.setValue(100*(self.ProcFrms)/self.dBrdCfg["NrFrms"])     

                Bpa = self.CalcBpaMap(Data)
                self.RefMap = np.copy(Bpa)
                y = np.transpose(Bpa)
                xscale = (self.SigCfg_xMax - self.SigCfg_xMin)/self.SigCfg_Nx
                yscale = (self.SigCfg_yMax - self.SigCfg_yMin)/self.SigCfg_Ny
                
                #self.Plotview_MeasProf.plot(x=dates_x, y=dates_y, pen=None, linestyle='none', symbol='o')    
                self.Image_Meas.setImage(y, pos=[self.SigCfg_xMin,self.SigCfg_yMin], scale=[xscale, yscale])
                
                if self.ShowRp:
                    NAnt = self.dBrdCfg["NRx"]*self.dBrdCfg["NTx"]
                    self.Plot_Meas.clear()
                    for Idx in range(0,4):
                        self.Plot_Meas.plot(self.SigCfg_Range[0:self.SigCfg_NFFT/2] , 20*np.log10(np.abs(self.Rp[:,Idx])))  ## setting pen=(i,3) automaticaly creates three different-colored pens

                self.Timer.start()
            else:
                self.SigMeasStop.emit()
                self.SigMenuEna.emit()
                self.RfBrd.CloseBrdMod0()                

    def GetAdcCfg(self):

        dIniAD8283 = {   "AdcSel"        : 3
                            }
        self.Log.SigUpd.emit()

        return  dIniAD8283

    def GetBpaCfg(self):
        dIniBpa = dict()
        stStrtFreq = self.Edit_Cfg_RadStrtFreq.text()
        dIniBpa["fStrt"] = StrConv.ToFloat(stStrtFreq)*1e6
        if dIniBpa["fStrt"] < self.patre.Lim_fMin:
            dIniBpa["fStrt"] = self.patre.Lim_fMin
        stStopFreq = self.Edit_Cfg_RadStopFreq.text()
        dIniBpa["fStop"] = StrConv.ToFloat(stStopFreq)*1e6
        if dIniBpa["fStop"] > self.patre.Lim_fMax:
            dIniBpa["fStop"] = self.patre.Lim_fMax
        if dIniBpa["fStop"] <= dIniBpa["fStrt"]:
            dIniBpa["fStrt"] = self.patre.Lim_fMin 
            dIniBpa["fStop"] = self.patre.Lim_fMax  


        stCfg = self.Edit_Meas_Cfg.text();

        dIniBpa["Tx1"] = 1
        dIniBpa["Tx2"] = 1
        dIniBpa["TxAmp"] = 100

        stSamples = self.Edit_Cfg_RadSamples.text()
        dIniBpa["N"] = StrConv.ToInt(stSamples)

        self.Edit_Cfg_RadDur.setText(stSamples)

        stPerd = self.Edit_Cfg_RadPerd.text()
        dIniBpa["Perd"] = StrConv.ToFloat(stPerd)*1e-3


        if dIniBpa["N"] < 8:
            dIniBpa["N"] = int(8)
            self.Edit_Cfg_RadSamples.setText(str(dIniBpa["N"]))    

        if dIniBpa["Perd"]/4 < dIniBpa["N"]*1e-6:
            dIniBpa["Perd"] = 4*dIniBpa["N"]*1e-6
            self.Edit_Cfg_RadPerd.setText(str(int(dIniBpa["Perd"]/1e-3)))    

        if dIniBpa["Perd"] < 1e-3:
            dIniBpa["Perd"] = 1e-3
            self.Edit_Cfg_RadPerd.setText(str(int(dIniBpa["Perd"]/1e-3)))  

        self.Log.AppendDict('Bpa Cfg: ', dIniBpa)
        self.Log.SigUpd.emit()        

        self.SigUpdIni.emit()

        return  dIniBpa

    def GetBrdCfg(self, dIniAdc, dIniBpa):
        # calculate sampling rate

        dBrdCfg = dict()


        N = dIniBpa["N"]

        # Check if fixed measurement rate is sufficient
        fs = 1e6
        dBrdCfg["fs"] = fs
        dBrdCfg["N"] = N
        dBrdCfg["TimUp"] = N*1e-6
        dBrdCfg["Tp"] = dIniBpa["Perd"]/2
        dBrdCfg["FreqStrt"] = dIniBpa["fStrt"];
        dBrdCfg["FreqStop"] = dIniBpa["fStop"];
        dBrdCfg["Tx1"] = dIniBpa["Tx1"]
        dBrdCfg["Tx2"] = dIniBpa["Tx2"]
        dBrdCfg["TxAmp"] = dIniBpa["TxAmp"]
        dBrdCfg["NTx"] = dIniBpa["Tx2"] - dIniBpa["Tx1"] + 1

        dBrdCfg["stCfg"] = self.Edit_Meas_Cfg.text();

        stNrFrms = self.Edit_Meas_NrFrms.text()
        dBrdCfg["NrFrms"] = int(stNrFrms)

        self.Log.Append("\n\nFrms:" + str(dBrdCfg["NrFrms"]))
        if (dBrdCfg["NrFrms"]) < 10:
            dBrdCfg["NrFrms"] = 10
            self.UpdIniAppend('Func','self.Edit_Meas_NrFrms.setText',str(dBrdCfg["NrFrms"]))

        self.UpdIniAppend('Func','self.Edit_Cfg_RadDur.setText', str(np.floor(dBrdCfg["TimUp"]/1e-6*10)/10))
                
        # Get Normalize Configuration
        if self.ChkBox_SigCfg_NormMax.isChecked():
            self.SigCfgScaMax = True
        else:
            self.SigCfgScaMax = False

        if self.ChkBox_SigCfg_NormFixed.isChecked():
            self.SigCfgScaLim = True
        else:
            self.SigCfgScaLim = False

        stLimMin = self.Edit_Cfg_LimMaxMin.text()
        self.SigCfgLimMaxMin = StrConv.ToFloat(stLimMin) 

        stLimLev = self.Edit_Cfg_LimMaxSideLev.text()
        self.SigCfgLimMaxSideLev=   StrConv.ToFloat(stLimLev) 

        if self.SigCfgLimMaxSideLev < 5:
            self.SigCfgLimMaxSideLev = 5
            self.UpdIniAppend('Func','self.Edit_Cfg_LimMaxSideLev.setText',str(self.SigCfgLimMaxSideLev))
            
        stLimMin = self.Edit_Cfg_LimFixedMin.text()
        self.SigCfgLimFixedMin = StrConv.ToFloat(stLimMin) 

        stLimMax = self.Edit_Cfg_LimFixedMax.text()
        self.SigCfgLimFixedMax = StrConv.ToFloat(stLimMax) 

        if self.SigCfgLimFixedMax < self.SigCfgLimFixedMin:
            self.SigCfgLimFixedMax = self.SigCfgLimFixedMin + 10
            self.UpdIniAppend('Func','self.Edit_Cfg_LimFixedMin.setText',str(self.SigCfgLimFixedMin))
            self.UpdIniAppend('Func','self.Edit_Cfg_LimFixedMax.setText',str(self.SigCfgLimFixedMax))

        self.SigUpdIni.emit()

        return  dBrdCfg

    def IniBpaMap(self):

        #--------------------------------------------------------------------------
        # Configure Backprojection Algorithm
        #--------------------------------------------------------------------------
        if  self.SigCfg_RangeNFFTCfg < self.dBrdCfg["N"]:
            self.SigCfg_NFFT = int(2**np.ceil(np.log2(self.dBrdCfg["N"])))
        else:
            self.SigCfg_NFFT = int(self.SigCfg_RangeNFFTCfg)


        fs = self.dBrdCfg["fs"]
        T = self.dBrdCfg["TimUp"]
        FreqStrt = self.dBrdCfg["FreqStrt"]
        FreqStop = self.dBrdCfg["FreqStop"]

        B = FreqStop - FreqStrt

        if "kf" in self.dBrdCfg:
            kf = self.dBrdCfg["kf"]
        else:
            kf = B/T

        c0 = 2.99792458e8
        fc = 0.5*(FreqStrt + FreqStop)

        self.SigCfg_Freq = np.linspace(0,self.SigCfg_NFFT-1,self.SigCfg_NFFT)/self.SigCfg_NFFT*fs
        self.SigCfg_Range = self.SigCfg_Freq*c0/(2*kf)


        stRMin = self.Edit_Meas_RMin.text()
        self.RMin = StrConv.ToFloat(stRMin)
        stRMax = self.Edit_Meas_RMax.text()
        self.RMax = StrConv.ToFloat(stRMax)

        if self.RMin < 0:
            self.RMin = 0

        if self.RMax < self.RMin:
            self.RMin = 0
            self.RMax = self.SigCfg_Range[int(self.SigCfg_NFFT/2-1)]
            self.RMax = np.floor(self.RMax*10)/10
            self.UpdIniAppend('Func','slef.Edit_Meas_RMin.setText',str(self.RMin))
            self.UpdIniAppend('Func','self.Edit_Meas_RMax.setText',str(self.RMax))

        if self.RMax > self.SigCfg_Range[int(self.SigCfg_NFFT/2-1)]:
            self.RMax = self.SigCfg_Range[self.SigCfg_NFFT/2-1]
            self.RMax = np.floor(self.RMax*10)/10
            self.UpdIniAppend('Func','self.Edit_Meas_RMax.setText',str(self.RMax))

        #####################
        # Update

        self.SigCfg_xMin = -self.RMax*np.sin(self.SigCfg_ViewAngDeg/180*np.pi)
        self.SigCfg_xMax = self.RMax*np.sin(self.SigCfg_ViewAngDeg/180*np.pi)

        self.SigCfg_yMin = 0.0
        self.SigCfg_yMax = self.RMax


        self.SigUpdIni.emit()

    def IniBpaMat(self):

        fs = self.dBrdCfg["fs"]
        T = self.dBrdCfg["TimUp"]
        FreqStrt = self.dBrdCfg["FreqStrt"]
        FreqStop = self.dBrdCfg["FreqStop"]

        B = FreqStop - FreqStrt
        
        if "kf" in self.dBrdCfg:
            kf = self.dBrdCfg["kf"]
        else:
            kf = B/T

        c0 = 2.99792458e8
        fc = 0.5*(FreqStrt + FreqStop)

        self.SigCfg_Freq = np.linspace(0,self.SigCfg_NFFT-1,self.SigCfg_NFFT)/self.SigCfg_NFFT*fs
        self.SigCfg_Range = self.SigCfg_Freq*c0/(2*kf)
        self.SigCfg_R0 = 0
        self.SigCfg_dR = self.SigCfg_Range[2] - self.SigCfg_Range[1]

        self.SigCfg_Imx = np.linspace(self.SigCfg_xMin,self.SigCfg_xMax,self.SigCfg_Nx)
        self.SigCfg_Imx = self.SigCfg_Imx.reshape(self.SigCfg_Nx,1)

        self.SigCfg_Imy = np.linspace(self.SigCfg_yMin,self.SigCfg_yMax,self.SigCfg_Ny)
        self.SigCfg_Imy = self.SigCfg_Imy.reshape(self.SigCfg_Ny,1)

        SigCfg_mImx = np.tile(np.transpose(self.SigCfg_Imx),(self.SigCfg_Ny,1))
        SigCfg_mImy = np.tile(self.SigCfg_Imy,(1,self.SigCfg_Nx))

        SigCfg_mImx = np.transpose(SigCfg_mImx)
        vImxLin = SigCfg_mImx.reshape(self.SigCfg_Nx*self.SigCfg_Ny,1)
        SigCfg_mImy = np.transpose(SigCfg_mImy)
        vImyLin = SigCfg_mImy.reshape(self.SigCfg_Nx*self.SigCfg_Ny,1)

        # Read Tx and Rx Position
        TxPosn = self.RfBrd.Rad.RfGet('TxPosn')
        RxPosn = self.RfBrd.Rad.RfGet('RxPosn')

        NTx = self.dBrdCfg["NTx"]
        NRx = self.dBrdCfg["NRx"]
        xTx = TxPosn[self.dBrdCfg["Tx1"]-1:self.dBrdCfg["Tx2"]]
        yTx = np.zeros((1,self.dBrdCfg["NTx"]))
        xRx = RxPosn
        yRx = np.zeros((1,len(RxPosn)))


        print("xTx:", xTx)
        print("xRx:", xRx)
        # Repeat xRx for number of Tx antennas
        xRx = np.tile(xRx,(1,NTx))
        yRx = np.tile(yRx,(1,NTx))
        # Repmat xTx for number of RX antennas
        xTx = np.tile(xTx, (NRx, 1))
        yTx = np.tile(yTx, (NRx, 1))

        xTx = np.reshape(np.transpose(xTx), (1,NRx*NTx))
        yTx = np.reshape(np.transpose(yTx), (1,NRx*NTx))
        

        mImxLin = np.tile(vImxLin,(1,NRx*NTx))
        mImyLin = np.tile(vImyLin,(1,NRx*NTx))
        
        mxRx = np.tile(xRx,(self.SigCfg_Nx*self.SigCfg_Ny,1))
        myRx = np.tile(yRx,(self.SigCfg_Nx*self.SigCfg_Ny,1))
        mxTx = np.tile(xTx,(self.SigCfg_Nx*self.SigCfg_Ny,1))
        myTx = np.tile(yTx,(self.SigCfg_Nx*self.SigCfg_Ny,1))

        if self.UserWin:
            AntWin = self.AntWin             
        else:
            if self.MimoEna > 0:
                AntWin = np.ones(NRx*NTx)
                AntWin[0] = 0.0495
                AntWin[1] = 0.3887
                AntWin[2] = 0.8117
                AntWin[3] = 1.0000/2
                AntWin[4] = 1.0000/2
                AntWin[5] = 0.8117
                AntWin[6] = 0.3887
                AntWin[7] = 0.0495   
            else:
                AntWin = np.ones(NRx*NTx)
                AntWin[0] = 0.1464
                AntWin[1] = 0.8536
                AntWin[2] = 0.8536
                AntWin[3] = 0.1464 
        
        AntWin = AntWin.reshape(NRx*NTx,1)
        mAntWin = np.tile(np.transpose(AntWin),(self.SigCfg_Nx*self.SigCfg_Ny,1))

        SigCfg_kc = 2*np.pi*fc/c0

        # % Calculate Linear Index
        vIdcsOffs = np.linspace(0,NRx*NTx-1,NRx*NTx)*self.SigCfg_NFFT
        vIdcsOffs = vIdcsOffs.reshape(NRx*NTx,1)
        mIdcsOffs = np.tile(np.transpose(vIdcsOffs),(self.SigCfg_Nx*self.SigCfg_Ny,1))

        mR1 = 0.5*(np.sqrt((mImxLin-mxRx)*(mImxLin-mxRx) + (mImyLin-myRx)*(mImyLin-yRx)) + np.sqrt((mImxLin - mxTx)*(mImxLin - mxTx) + (mImyLin - myTx)*(mImyLin - myTx)))
        self.SigCfg_TxCfg1_Idcs = np.floor((mR1-self.SigCfg_R0)/self.SigCfg_dR) + mIdcsOffs
        self.SigCfg_TxCfg1_dR = (mR1-self.SigCfg_R0)/self.SigCfg_dR  - np.floor((mR1-self.SigCfg_R0)/self.SigCfg_dR)
        self.SigCfg_TxCfg1_Exp = mAntWin*np.exp(-1j*2*SigCfg_kc*mR1)
        self.SigCfg_ScaAntWin = np.sum(AntWin)

        self.vR1 = mR1[:,1]
        self.vRCor = mR1[:,1]*mR1[:,1]
        self.SigCfg_TxCfg1_Idcs = np.int32(self.SigCfg_TxCfg1_Idcs)

        mAng = np.arctan2(mImyLin, mImxLin)
        vAng = mAng[:,1]/np.pi*180


        self.ImOutsideSeg = np.zeros(self.vR1.shape);
        self.ImInsideSeg = np.ones(self.vR1.shape);
        self.ImOutsideSeg[self.vR1 > self.RMax] = 1
        self.ImOutsideSeg[self.vR1 < self.RMin] = 1
        self.ImOutsideSeg[vAng < (90 - self.SigCfg_ViewAngDeg)] = 1
        self.ImOutsideSeg[vAng > (90 + self.SigCfg_ViewAngDeg)] = 1
        self.ImInsideSeg[self.vR1 > self.RMax] = 0
        self.ImInsideSeg[self.vR1 < self.RMin] = 0
        self.ImInsideSeg[vAng < (90 - self.SigCfg_ViewAngDeg)] = 0
        self.ImInsideSeg[vAng > (90 + self.SigCfg_ViewAngDeg)] = 0        
        
    def CalcBpaMap(self, Data):

        N = self.dBrdCfg["N"]
        NAnt = self.dBrdCfg["NRx"]*self.dBrdCfg["NTx"]



        if self.MimoEna > 0:
            TmpDat = np.copy(Data)
            TData = np.zeros((N,NAnt))
            TData[:,0:4] = TmpDat[0:N,0:4]
            TData[:,4:8] = TmpDat[N:2*N,0:4] 
        else:
            TData = Data      

        Siz = TData.shape


        # Remove frame counter form data
        TData = TData[self.SigCfg_NIni:N,:]
        if self.SigCfg_RangeWinType == 'Hanning':
            Win = np.hanning(N-self.SigCfg_NIni)
        else:
            if self.SigCfg_RangeWinType == 'Hamming':
                Win = np.hamming(N-self.SigCfg_NIni)
            else:
                Win = np.ones(N-self.SigCfg_NIni)    

        Win2D = np.zeros((N-self.SigCfg_NIni,NAnt))
        DataMean = np.mean(TData,0)

        for Idx in range(0,NAnt):
            Win2D[:,Idx] = Win
            TData[:,Idx] = TData[:,Idx] - DataMean[Idx]

        ScaWin = np.sum(Win)

        StrtIdx = (self.SigCfg_NFFT - (N-self.SigCfg_NIni))/2
        StrtIdx = np.int32(StrtIdx)
        StopIdx = np.int32(StrtIdx + N - self.SigCfg_NIni)

        FuSca = self.RfBrd.Rad.Get('FuSca')
        DataPad = np.zeros((self.SigCfg_NFFT,NAnt))
        DataPad[StrtIdx:StopIdx,:] = TData*Win2D
        DataPad = np.fft.fftshift(DataPad,0)
        XData = np.fft.fft(DataPad, self.SigCfg_NFFT, 0)/ScaWin*FuSca
        XData = XData*self.mCal
        self.Rp = XData[0:int(self.SigCfg_NFFT/2),:]

        XData = np.transpose(XData)
        XData = XData.reshape(self.SigCfg_NFFT*NAnt)
        
        X0 = XData[self.SigCfg_TxCfg1_Idcs]
        #X1 = XData[self.SigCfg_TxCfg1_Idcs+1]

        Bpa = X0; # + (X1 - X0)*self.SigCfg_TxCfg1_dR

        Bpa = Bpa*self.SigCfg_TxCfg1_Exp

        Bpa = np.sum(Bpa,1)/self.SigCfg_ScaAntWin 
        Bpa = np.abs(Bpa)
        # Correction to eliminate
        #Bpa = Bpa*self.vRCor
        Bpa = 20*np.log10(Bpa)

        BpaMin = np.min(Bpa)  
        if self.SigCfg_BpaSeg:
            Bpa = Bpa*self.ImInsideSeg + (BpaMin-5)*self.ImOutsideSeg
        if  self.SigCfgScaMax:

            Bpa[self.vR1 < self.RMin] = BpaMin
            BpaMax = np.max(Bpa)
            
            if BpaMax > self.SigCfgLimMaxMin + self.SigCfgLimMaxSideLev:
                Bpa = Bpa - BpaMax
                Bpa[Bpa < -self.SigCfgLimMaxSideLev] = -self.SigCfgLimMaxSideLev
            else:
                Bpa[Bpa < self.SigCfgLimMaxMin] = self.SigCfgLimMaxMin;
                Bpa = Bpa - self.SigCfgLimMaxMin - self.SigCfgLimMaxSideLev;
                Bpa[0] = 0; 
        elif self.SigCfgScaLim:
            Bpa[0] = self.SigCfgLimFixedMax;
            Bpa[Bpa > self.SigCfgLimFixedMax] = self.SigCfgLimFixedMax;
            Bpa[Bpa < self.SigCfgLimFixedMin] = self.SigCfgLimFixedMin;  
            Bpa[self.vR1 < self.RMin] = self.SigCfgLimFixedMin;
        else:
            BpaMin = np.min(Bpa)
            Bpa[self.vR1 < self.RMin] = BpaMin


        Bpa = Bpa.reshape(self.SigCfg_Nx,self.SigCfg_Ny)
        Bpa = np.transpose(Bpa)

        return Bpa

    def SetCfgInf(self, stVal):
        self.stCfgInf = stVal

    def SetInitFailed(self, Val):
        self.InitFailed = Val


    def ParseCfgFile(self, stFile):
        if len(stFile) > 1:
            File = open(stFile, "r", encoding="utf-8", errors="ignore")
            
            lCmd = list()
            # Configure DBF parameters
            lCmd.append((r"PageDBFCfg_SetStrtFreq\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_RadStrtFreq.setText", "Func"))
            lCmd.append((r"PageDBFCfg_SetStopFreq\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_RadStopFreq.setText", "Func"))
            lCmd.append((r"PageDBFCfg_SetTInt\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_RadPerd.setText", "Func"))
            lCmd.append((r"PageDBFCfg_SetSamples\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_RadSamples.setText", "Func"))
            
            # Configure parameters for Cic filter
            lCmd.append((r"PageDBFCfg_SetNormLimMin\((?P<Arg>(-[0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_LimMaxMin.setText", "Func"))
            lCmd.append((r"PageDBFCfg_SetNormSidelobe\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_LimMaxSideLev.setText", "Func"))
            lCmd.append((r"PageDBFCfg_EnaLimMinMax\((?P<Arg>(True|False))\)", "self.ChkBox_SigCfg_NormFixed.setChecked", "FuncSt"))
            lCmd.append((r"PageDBFCfg_SetLimMin\((?P<Arg>(-[0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_LimFixedMin.setText", "Func"))
            lCmd.append((r"PageDBFCfg_SetLimMax\((?P<Arg>(-[0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_LimFixedMax.setText", "Func"))
            
            # Set Parameters for Number of Parameters for DBF measurement page
            lCmd.append((r"PageDBFMeas_SetNrFrms\((?P<Arg>([0-9]+))\)", "self.Edit_Meas_NrFrms.setText", "Func"))
            lCmd.append((r"PageDBFMeas_SetRMin\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Meas_RMin.setText", "Func"))
            lCmd.append((r"PageDBFMeas_SetRMax\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Meas_RMax.setText", "Func"))
            lCmd.append((r"PageDBFMeas_EnaFFT\((?P<Arg>(True|False))\)", "self.ChkBox_Meas_FFT.setChecked", "FuncSt"))
            lCmd.append((r"PageDBFMeas_EnaAverage\((?P<Arg>(True|False))\)", "self.ChkBox_Meas_PSD.setChecked", "FuncSt"))
            lCmd.append((r"PageDBFMeas_SetTxCfg\('(?P<Arg>([0-9a-zA-Z\(\)-; ]+))'\)", "self.Edit_Meas_Cfg.setText", "Func"))
            
            # Set parameters for Range-Time measuremet view
            lCmd.append((r"PageDBFMeas_SetRangeFFTSiz\((?P<Val>(64|128|256|512|1024|2048|4096|8192|16384|32768|65536))\)", "self.Edit_Cfg_RangeFftSiz.setText", "Func"))
            lCmd.append((r"PageDBFMeas_SetRangeWinType\((?P<Val>(Hanning|Hamming|Boxcar))\)", "self.Edit_Cfg_RangeWinType.setText", "Func"))
            lCmd.append((r"PageDBFMeas_SetAngWinType\((?P<Val>(Hanning|Hamming|Boxcar))\)", "self.Edit_Cfg_AngWinType.setText", "Func"))

            lCmd.append((r"PageDBFMeas_SetBpaImSizX\((?P<Arg>([0-9]{2,4}))\)", "self.SigCfg_Nx", "Var"))
            lCmd.append((r"PageDBFMeas_SetBpaImSizY\((?P<Arg>([0-9]{2,4}))\)", "self.SigCfg_Ny", "Var"))
            lCmd.append((r"PageDBFMeas_SetBpaViewAng\((?P<Arg>([0-9]{2,4}))\)", "self.SigCfg_ViewAngDeg", "Var"))  
            lCmd.append((r"PageDBFMeas_EnaBpaSeg\((?P<Arg>(True|False))\)", "self.SigCfg_BpaSeg", "Var")) 
            lCmd.append((r"PageDBFMeas_SetSegLineWidth\((?P<Arg>([0-9]+))\)", "self.PltCfg_SegLineWidth", "Var")) 
            
            for stLine in File:
                Ret = StrConv.ConvStrToCmd(stLine, lCmd)
                if Ret[0]:
                    try: 
                        exec(Ret[1])        
                    except:
                        print("Err: ", Ret[1])

            # Initialize duration field with number of samples
            stSamples = self.Edit_Cfg_RadSamples.text()
            self.Edit_Cfg_RadDur.setText(stSamples)

