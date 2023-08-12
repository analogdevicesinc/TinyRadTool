import  src.cmd_modules.TinyRad as TinyRad

import  src.S14.S14_ModRangeDoppler as S14_ModRangeDoppler
import  src.logger.Logger as Logger
import  src.cmd_modules.StrConv as StrConv


from PyQt5 import QtCore, QtGui, QtWidgets
import  threading as threading
import  numpy as np
import  src.ui.proc_modes.ui_ModRangeDoppler as ui_ModRangeDoppler
from    os.path import expanduser
import  re
import  time
#import  h5py


class ModRangeDoppler(QtWidgets.QMainWindow, ui_ModRangeDoppler.Ui_ModRangeDoppler):
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
        super(ModRangeDoppler, self).__init__()
        self.setupUi(self)
        self.patre = patre

        self.Button_Meas_Meas.clicked.connect(self.Button_Meas_StartThread)
        self.Button_Meas_Ini.clicked.connect(self.Button_Ini_StartThread)
        self.ChkBox_Histog.clicked.connect(self.ChkBox_Histog_stateChanged)
        
        QtWidgets.QShortcut(QtGui.QKeySequence("F10"), self.Widget_Meas, self.toggleHistog)
        QtWidgets.QShortcut(QtGui.QKeySequence("ALT+F2"), self.Widget_Meas, self.ToggleCmd)        
        QtWidgets.QShortcut(QtGui.QKeySequence("Up"), self.Widget_Meas, self.SetCmdTxtUp)
        QtWidgets.QShortcut(QtGui.QKeySequence("Down"), self.Widget_Meas, self.SetCmdTxtDown)
        
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

        # Configuration of Signal Processing
        self.SigCfg_RangeWinType = 'Hanning'
        self.SigCfg_RangeNFFTCfg = 1024
        self.SigCfg_VelWinType = 'Hanning'
        self.SigCfg_VelNFFTCfg = 512

        self.MeasData = 0
        self.RDMap = 0
        self.dBrdCfg = dict()
        self.ProcFrms = 0
        self.VelDoppler = 0
        self.Range = 0

        if self.patre.GuiSelIni:
            self.ParseCfgFile(self.patre.stFileCfg)

        self.toggleHistog()
        self.CmdHide = True

        self.StoreIf = False
        self.StoreIfGenArray = False
        self.StoreNrFrms = 0
        self.StoreIdx = 0

        self.ExecHist = list()
        self.ExecHistIdx = 0

        self.Brd = None

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
              
    def SetCmdTxtUp(self):
        if len(self.ExecHist) > 0:
            if not self.CmdHide:
                self.Edit_Meas_Cmd.setFocus()
                self.Edit_Meas_Cmd.setText(self.ExecHist[self.ExecHistIdx])      
                self.ExecHistIdx = self.ExecHistIdx - 1
                if self.ExecHistIdx < 0:
                    self.ExecHistIdx = 0
    
    def SetCmdTxtDown(self):
        if len(self.ExecHist) > 0:
            if not self.CmdHide:
                self.Edit_Meas_Cmd.setFocus()
                self.Edit_Meas_Cmd.setText(self.ExecHist[self.ExecHistIdx])      
                self.ExecHistIdx = self.ExecHistIdx + 1
                if self.ExecHistIdx >= len(self.ExecHist):
                    self.ExecHistIdx = len(self.ExecHist) - 1

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
                hFile.create_dataset('/RDMap', data = self.RDMap.transpose())
                hFile.create_dataset('/vVel', data = self.VelDoppler)
                hFile.create_dataset('/vRange', data = self.Range)
                for Key in self.dBrdCfg:
                    print('/BrdCfg/' + str(Key))
                    if isinstance(self.dBrdCfg[Key],str):
                        Dat = list()
                        Dat.append(self.dBrdCfg[Key])
                        dt = h5py.special_dtype(vlen=bytes)
                        DatSet = hFile.create_dataset('/BrdCfg/' + str(Key), (100,1), dtype=dt)
                        DatSet.attrs["name"] = (self.dBrdCfg[Key])      
                    else:
                        hFile.create_dataset('/BrdCfg/' + str(Key), data = self.dBrdCfg[Key])
            self.Label_Meas_CmdSts.setText("File " + Match.group("File") + " written")            

        RegCmd = re.compile(r"StoreIf\(\"(?P<File>[\w]+.h5)\",[ ]*(?P<Frms>([0-9]+))\)")
        Match = RegCmd.search(stCmd)
        if Match:
            self.StoreNrFrms = int(Match.group("Frms"))
            if self.StoreNrFrms > 1000:
                self.Label_Meas_CmdSts.setText("Number of frames to large! ")   
                CmdExec = True
            else:
                CmdExec = True
                self.StoreIf = True
                self.StoreIfGenArray=   True
                self.StoreIdx = 0
                self.StoreFileName = Match.group("File")
                stFile = self.patre.stFolderCfg + Match.group("File")

                self.Label_Meas_CmdSts.setText("Write to File " + Match.group("File"))

        RegCmd = re.compile(r"ExtendLim")
        Match = RegCmd.search(stCmd)
        if Match:
            CmdExec = True        
            self.patre.Lim_fMin = 23.9e9
            self.patre.Lim_fMax = 24.3e9
            self.Label_Meas_CmdSts.setText("Limits extended from 23.9 to 24.3 GHz ")

        if CmdExec:
            self.ExecHist.append(stCmd)
            self.ExecHistIdx = len(self.ExecHist) - 1
            self.Edit_Meas_Cmd.setText("")  
        else:
            self.Label_Meas_CmdSts.setText("Command " + stCmd + " not known")  
            self.Edit_Meas_Cmd.setText("")           
        

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

    def Button_Meas_Meas_Clicked(self):
        self.plot_state = False
        self.Log.Append("RangeDoppler: Button Meas clicked")
        stTxt = self.Button_Meas_Meas.text()

        if stTxt == "Measure":
            self.ProcFrms = 0
            self.NrFrmsInit = self.Edit_Meas_NrFrms.text()
            stNrFrms = self.Edit_Meas_NrFrms.text()
            self.MeasNrFrmsIni = int(stNrFrms)
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
            self.Log.Append("Board Rst...");
            self.Brd.BrdRst();

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
        self.Log.Append("Range-Doppler: Button Ini Clicked")

        IniSts = 0
        self.ProcFrms = 0

        dIniAdc = self.GetAdcCfg()
        dIniRangeDoppler = self.GetRangeDopplerCfg()
        self.dBrdCfg = self.GetBrdCfg(dIniAdc, dIniRangeDoppler)

        print("Check App Status")
        if self.Brd == None:
            self.Brd =   self.patre.hTinyRad

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
    

        B = self.dBrdCfg["FreqStop"] - self.dBrdCfg["FreqStrt"]
        T = self.dBrdCfg["TimUp"]
        kf = B/T
        c0 = 2.99792458e8

        if Ret == 0:
            dSwSts = self.Brd.BrdGetSwVers()
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
            self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setPalette', palette)
            self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setText', "Connected: Initializing...")
            self.Log.Append("Connected: Initializing...")

            self.SigUpdIni.emit()
            self.Log.SigUpd.emit()

            self.RfBrd = S14_ModRangeDoppler.S14_ModRangeDoppler(self.Brd, self.dBrdCfg)
            self.RfBrd.IniBrdModRangeDoppler()

            B = self.Brd.Adf_Pll.fStop - self.Brd.Adf_Pll.fStrt
            T = self.Brd.Adf_Pll.TRampUp
            kf = B/T

            IniSts = 1
        else:
            IniSts = -1
        


        self.IniRDMap()

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.black)
        self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setPalette', palette)        

        if IniSts == 1: 
            print("Ini:", IniSts)
            fs = round(self.dBrdCfg["fs"]/1e6*1000)/1000
            self.stCfgInf = "Range-Doppler Cfg: fs = " + str(fs) + " (MHz) | N = " + str(self.dBrdCfg["N"]) + " | Tp=" + str(np.round(10*self.dBrdCfg["Tp"]/1e-6)/10) + " us"
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
        
        self.SigUpdIni.emit()
        self.SigIniDone.emit()

        print("Initialization Done")

    def SigActionInitDone(self):
        print("SigActionInitDon executed: ", self.MeasIni)
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
        self.Edit_Meas_Cfg.setDisabled(False)
        
        self.SigMenuEna.emit()
        self.SigProgressDone.emit()
        self.Edit_Meas_NrFrms.setText(str(self.MeasNrFrmsIni))
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

        if NrFrms < 0:
            self.SigMeasStop.emit()
            self.SigMenuEna.emit()
            self.RfBrd.CloseBrdMod0()
        else:

            self.ProcFrms = self.ProcFrms + 1;
            self.progressbar.setRange(0,100)
            self.progressbar.setValue(100*(self.ProcFrms)/self.dBrdCfg["NrFrms"]) 


            BrdData = self.RfBrd.GetDataEve()
            Data = BrdData[:,0]
            Data = Data.reshape((self.dBrdCfg["Np"],self.dBrdCfg["N"]))
            Data = Data.transpose()

            N = self.RfBrd.Rad.Get('N')
            NrChn = self.RfBrd.Rad.Get('NrChn')
            ProcData = False
            if hasattr(Data, "shape"):
                DatSiz = Data.shape
                if (len(DatSiz) == 2): 
                    if (DatSiz[0] == N) and (DatSiz[1] == self.SigCfgNp):
                        ProcData = True   

            if self.StoreIf:
                if self.StoreIfGenArray:
                    self.StoreIfGenArray = False
                    self.StoreData = np.zeros((int(N*NrChn*self.dBrdCfg["Np"]), int(self.StoreNrFrms)), dtype='int16')
                    self.StoreTim = np.zeros(int(self.StoreNrFrms))

                Dummy = BrdData.transpose()
                self.StoreData[:,self.StoreIdx] = np.int16(Dummy.reshape(int(N*NrChn*self.dBrdCfg["Np"])))
                self.StoreTim[self.StoreIdx] = time.time()
                self.StoreIdx = self.StoreIdx + 1

                if self.StoreIdx >= self.StoreNrFrms:
                    self.StoreIf = False
                    print("Store Data")
                    stFile = self.patre.stFolderCfg + self.StoreFileName

                    with h5py.File(stFile,'w') as hFile:
                        hFile.create_dataset('/If', data = self.StoreData.transpose())   
                        hFile.create_dataset('/Tim', data = self.StoreTim)   
                          
                        for Key in self.dBrdCfg:
                            print('/BrdCfg/' + str(Key))
                            if isinstance(self.dBrdCfg[Key], str):
                                Dat = list()
                                Dat.append(self.dBrdCfg[Key]) 
                            else:
                                hFile.create_dataset('/BrdCfg/' + str(Key), data = self.dBrdCfg[Key]) 


            if ProcData:
                self.MeasData = np.copy(Data)
                Data = self.CalcRangeDopplerMap(Data) 
                self.RDMap = np.copy(Data)
                y = np.transpose(Data)     
                       
                if not self.plot_state:
                    self.plot_state = True
                    self.Image_Meas.setImage(y, pos=[self.SigCfgVelMin,self.SigCfgRMin], scale=[self.SigCfgVelScale, self.SigCfgRScale])
                    self.plotview.setAspectLocked(False)
                else:
                    state_store = self.plotview.getViewBox().getState()
                    self.Image_Meas.setImage(y, pos=[self.SigCfgVelMin,self.SigCfgRMin], scale=[self.SigCfgVelScale, self.SigCfgRScale])
                    #self.plotview.getViewBox().setState(state_store)
                    self.plotview.setAspectLocked(False)

                self.Timer.start()
            else:
                self.progressbar.setRange(0,100)
                self.progressbar.setValue(100)                          
                self.SigMeasStop.emit()
                self.SigMenuEna.emit()
                self.RfBrd.CloseBrdMod0()                

    def GetCicCfg(self):
        Rad = Radarbook.Radarbook("PNet","192.168.1.1")
        #--------------------------------------------------------------------------------------
        # RangeDoppler Measurement Page Time
        #--------------------------------------------------------------------------------------
        dIniCic1 = {   "FiltSel"       : 255,
                                "CombDel"       : 3,
                                "OutSel"        : 3,
                                "SampPhs"       : 0,
                                "SampRed"       : 1,
                                "Ctrl"          : Rad.cCIC1_REG_CONTROL_RSTCNTRSOP + Rad.cCIC1_REG_CONTROL_EN
                            }
        # currentText, currentIndex
        stEna = self.ComboBox_Cfg_CicEna.currentText()
        stR = self.Edit_Cfg_CicR.text()
        IdxOut = self.ComboBox_Cfg_CicStage.currentIndex()
        IdxDelay = self.ComboBox_Cfg_CicDelay.currentIndex()

        if stEna == "Bypass":
            dIniCic1["SampRed"] = 1;
            dIniCic1["RegCtrl"] = Rad.cCIC1_REG_CONTROL_RSTCNTRSOP + Rad.cCIC1_REG_CONTROL_EN + Rad.cCIC1_REG_CONTROL_BYPASS
        else:
            dIniCic1["SampRed"] = StrConv.ToInt(stR)
            dIniCic1["RegCtrl"] = Rad.cCIC1_REG_CONTROL_RSTCNTRSOP + Rad.cCIC1_REG_CONTROL_EN

        dIniCic1["OutSel"] = IdxOut
        dIniCic1["CombDel"] = IdxDelay

        return dIniCic1

    def GetAdcCfg(self):

        dIniAD8283 = {   "AdcSel"        : 3,
                            }

        return  dIniAD8283

    def GetRangeDopplerCfg(self):
        dIniRangeDoppler = dict()
        stStrtFreq = self.Edit_Cfg_RadStrtFreq.text()
        dIniRangeDoppler["fStrt"] = StrConv.ToFloat(stStrtFreq)*1e6
        if dIniRangeDoppler["fStrt"] < self.patre.Lim_fMin:
            dIniRangeDoppler["fStrt"] = self.patre.Lim_fMin
        stStopFreq = self.Edit_Cfg_RadStopFreq.text()
        dIniRangeDoppler["fStop"] = StrConv.ToFloat(stStopFreq)*1e6
        if dIniRangeDoppler["fStop"] > self.patre.Lim_fMax:
            dIniRangeDoppler["fStop"] = self.patre.Lim_fMax
        if dIniRangeDoppler["fStop"] <= dIniRangeDoppler["fStrt"]:
            dIniRangeDoppler["fStrt"] = self.patre.Lim_fMin 
            dIniRangeDoppler["fStop"] = self.patre.Lim_fMax   

        stDur = self.Edit_Cfg_RadDur.text()

        stPerd = self.Edit_Cfg_RadPerd.text()
        dIniRangeDoppler["TimPerd"] = round(StrConv.ToFloat(stPerd))*1e-6

        stSamples = self.Edit_Cfg_RadSamples.text()
        dIniRangeDoppler["N"] = StrConv.ToInt(stSamples)
        self.Edit_Cfg_RadDur.setText(stSamples)

        if dIniRangeDoppler["TimPerd"] < dIniRangeDoppler["N"]*1e-6 + 24e-6:
            dIniRangeDoppler["TimPerd"] = dIniRangeDoppler["N"]*1e-6 + 24e-6
            self.Edit_Cfg_RadPerd.setText(str(int(dIniRangeDoppler["TimPerd"]/1e-6)))    

        stNp = self.Edit_Cfg_RadNp.text()
        dIniRangeDoppler["Np"] = StrConv.ToInt(stNp)

        stTInt = self.Edit_Cfg_RadTInt.text() 
        dIniRangeDoppler["TInt"] =   StrConv.ToInt(stTInt)*1e-3

        if dIniRangeDoppler["N"] < 8:
            dIniRangeDoppler["N"] = 8
            self.Edit_Cfg_RadSamples.setText(str(int(dIniRangeDoppler["N"])))

        if dIniRangeDoppler["Np"] < 8:
            dIniRangeDoppler["Np"] = 8
            self.UpdIniAppend('Func','self.Edit_Cfg_RadNp.setText', str(dIniRangeDoppler["Np"])) 
        if dIniRangeDoppler["Np"] > 1024:
            dIniRangeDoppler["Np"] = int(1024)
            self.UpdIniAppend('Func','self.Edit_Cfg_RadNp.setText', str(dIniRangeDoppler["Np"])) 

        if 4*dIniRangeDoppler["Np"]*dIniRangeDoppler["N"] > int('0x60000',16)/2:
            dIniRangeDoppler["Np"] = int(np.floor(int('0x60000',16)/(2*4*dIniRangeDoppler["N"])))
            self.UpdIniAppend('Func','self.Edit_Cfg_RadNp.setText', str(dIniRangeDoppler["Np"]))       


        if dIniRangeDoppler["TInt"] < dIniRangeDoppler["TimPerd"]*dIniRangeDoppler["Np"]:
            dIniRangeDoppler["TInt"] = dIniRangeDoppler["TimPerd"]*(dIniRangeDoppler["Np"]+2)
            self.Edit_Cfg_RadTInt.setText(str((dIniRangeDoppler["TInt"]/1e-3)))   

        if dIniRangeDoppler["TInt"] < 20e-3:
            dIniRangeDoppler["TInt"] = 20e-3
            self.Edit_Cfg_RadTInt.setText(str((dIniRangeDoppler["TInt"]/1e-3))) 

        self.SigUpdIni.emit()

        return  dIniRangeDoppler


    def IniRDMap(self):

        stRMin = self.Edit_Meas_RMin.text()
        stRMax = self.Edit_Meas_RMax.text()
    
        self.SigCfgRMin = StrConv.ToFloat(stRMin)
        self.SigCfgRMax = StrConv.ToFloat(stRMax)

        fs = 1e6

        c0 = 2.99792458e8
        B = self.dBrdCfg["FreqStop"] - self.dBrdCfg["FreqStrt"]
        T = self.dBrdCfg["TimUp"]

        if "kf" in self.dBrdCfg:
            kf = self.dBrdCfg["kf"]  
        else:
            kf = B/T 

        self.SigCfgNp = self.dBrdCfg["Np"]  

        # Configure FFT Siz

        self.SigCfg_RangeWinType = self.Edit_Cfg_RangeWinType.text()
        self.SigCfg_VelWinType = self.Edit_Cfg_VelWinType.text()

        TmpVal = StrConv.ToFloat(self.Edit_Cfg_RangeFftSiz.text())
        TmpVal = pow(2, np.ceil(np.log2(TmpVal)))
        self.SigCfg_RangeNFFTCfg = int(TmpVal)

        TmpVal = StrConv.ToFloat(self.Edit_Cfg_VelFftSiz.text())
        TmpVal = pow(2, np.ceil(np.log2(TmpVal)))
        self.SigCfg_VelNFFTCfg = int(TmpVal)        

        if self.SigCfg_RangeNFFTCfg < self.dBrdCfg["N"]:
            self.SigCfgRFFT = int(2**np.ceil(np.log2(self.dBrdCfg["N"])))
        else:
            self.SigCfgRFFT = int(self.SigCfg_RangeNFFTCfg)

        self.Edit_Cfg_RangeFftSiz.setText(str(self.SigCfgRFFT)) 

        if self.SigCfg_VelNFFTCfg < self.dBrdCfg["Np"]:
            self.SigCfgVFFT = int(2**np.ceil(np.log2(self.dBrdCfg["Np"])))
        else:
            self.SigCfgVFFT = int(self.SigCfg_VelNFFTCfg)

        self.Edit_Cfg_VelFftSiz.setText(str(self.SigCfgVFFT)) 

        print("RangeFft: ", self.SigCfgRFFT)
        print("VelFft: ", self.SigCfgVFFT)



        # Get Normalize Configuration
        if self.ChkBox_SigCfg_NormMax.isChecked():
            self.SigCfgScaMax = True
        else:
            self.SigCfgScaMax = False

        if self.ChkBox_SigCfg_MeanRemove.isChecked():
            self.SigCfgMeanRemove = True
        else:
            self.SigCfgMeanRemove = False

        if self.ChkBox_SigCfg_NormFixed.isChecked():
            self.SigCfgScaLim = True
        else:
            self.SigCfgScaLim = False

        stLimMin = self.Edit_Cfg_LimMaxMin.text()
        self.SigCfgLimMaxMin = float(stLimMin) 

        stLimLev = self.Edit_Cfg_LimMaxSideLev.text()
        self.SigCfgLimMaxSideLev=   float(stLimLev) 

            
        stLimMin = self.Edit_Cfg_LimFixedMin.text()
        self.SigCfgLimFixedMin = float(stLimMin) 

        stLimMax = self.Edit_Cfg_LimFixedMax.text()
        self.SigCfgLimFixedMax = float(stLimMax) 

        if self.SigCfgLimMaxSideLev < 5:
            self.SigCfgLimMaxSideLev = 5
            self.Edit_Cfg_LimMaxSideLev.setText(str(self.SigCfgLimMaxSideLev))
            
        stLimMin = self.Edit_Cfg_LimFixedMin.text()
        self.SigCfgLimFixedMin = float(stLimMin) 

        stLimMax = self.Edit_Cfg_LimFixedMax.text()
        self.SigCfgLimFixedMax = float(stLimMax) 

        if self.SigCfgLimFixedMax < self.SigCfgLimFixedMin:
            self.SigCfgLimFixedMax = self.SigCfgLimFixedMin + 10
            self.Edit_Cfg_LimFixedMin.setText(str(self.SigCfgLimFixedMin))
            self.Edit_Cfg_LimFixedMax.setText(str(self.SigCfgLimFixedMax))

        # Calculate Scaling for x and y axis
        FreqDisp = np.linspace(0, int(self.SigCfgRFFT/2-1), int(self.SigCfgRFFT/2))
        FreqDisp = FreqDisp/self.SigCfgRFFT*fs
        Range = FreqDisp*c0/(2*kf)
        self.Range = np.copy(Range)

        if Range[int(self.SigCfgRFFT/2-1)] < self.SigCfgRMax:
            self.SigCfgRMax = Range[int(self.SigCfgRFFT/2-1)]  
            self.SigCfgRMax = np.floor(self.SigCfgRMax * 10)/10

        if self.SigCfgRMin < 0:
            self.SigCfgRMin = 0
        if self.SigCfgRMax < self.SigCfgRMin:
            self.SigCfgRMin = 0
            self.SigCfgRMax = Range[int(self.SigCfgRFFT/2-1)] 

        #Update RMin RMax
        self.UpdIniAppend('Func','self.Edit_Meas_RMin.setText', str(self.SigCfgRMin)) 
        self.UpdIniAppend('Func','self.Edit_Meas_RMax.setText', str(self.SigCfgRMax)) 

        RangeMin = Range - self.SigCfgRMin
        RangeMin = np.abs(RangeMin)
        self.SigCfgRIdxMin = np.argmin(RangeMin)

        RangeMax = Range - self.SigCfgRMax
        RangeMax = np.abs(RangeMax)
        self.SigCfgRIdxMax = np.argmin(RangeMax)
        self.SigCfgRScale = (self.SigCfgRMax - self.SigCfgRMin)/(self.SigCfgRIdxMax - self.SigCfgRIdxMin)

        freqDoppler = np.linspace(-self.SigCfgVFFT/2,self.SigCfgVFFT/2-1,self.SigCfgVFFT)/self.SigCfgVFFT/self.dBrdCfg["TimPerd"]        
        freqCenter = (self.dBrdCfg["FreqStrt"] + self.dBrdCfg["FreqStop"])/2

        self.VelDoppler = freqDoppler/freqCenter*3e8/2
        self.SigCfgVelMin = self.VelDoppler[0]
        self.SigCfgVelScale = (self.VelDoppler[self.SigCfgVFFT-1] - self.VelDoppler[0])/self.SigCfgVFFT

        self.SigUpdIni.emit()

    def GetBrdCfg(self, dIniAdc, dIniRangeDoppler):
        # calculate sampling rate

        dBrdCfg = dict()

        fs = 1e6
 
        dBrdCfg["stCfg"] = self.Edit_Meas_Cfg.text()
        dBrdCfg["fs"] = 1e6
        dBrdCfg["N"] = int(dIniRangeDoppler["N"])
        dBrdCfg["TimUp"] = dIniRangeDoppler["N"]*1e-6
        dBrdCfg["FreqStrt"] = dIniRangeDoppler["fStrt"]
        dBrdCfg["FreqStop"] = dIniRangeDoppler["fStop"]
        dBrdCfg["TimPerd"] = dIniRangeDoppler["TimPerd"]
        dBrdCfg["Tp"] = dIniRangeDoppler["TimPerd"]
        dBrdCfg["Np"] = dIniRangeDoppler["Np"]
        dBrdCfg["TInt"] = dIniRangeDoppler["TInt"]

        stNrFrms = self.Edit_Meas_NrFrms.text()
        dBrdCfg["NrFrms"] = StrConv.ToInt(stNrFrms)

        if (dBrdCfg["NrFrms"]*8) > (2**30 - 1):
            print("To many frams")
            dBrdCfg["NrFrms"] = (2**30)//8
            self.UpdIniAppend('Func','self.Edit_Meas_NrFrms.setText', str(dBrdCfg["NrFrms"])) 
        if dBrdCfg["NrFrms"] < 10:
            dBrdCfg["NrFrms"] = 10
            self.UpdIniAppend('Func','self.Edit_Meas_NrFrms.setText', str(dBrdCfg["NrFrms"])) 

        self.UpdIniAppend('Func','self.Edit_Cfg_RadDur.setText', str(np.floor(dBrdCfg["TimUp"]/1e-6*10)/10))
        self.UpdIniAppend('Func','self.Edit_Cfg_RadPerd.setText', str(np.floor(dBrdCfg["Tp"]/1e-6*10)/10))


        self.SigUpdIni.emit()

        return  dBrdCfg

    def CalcRangeDopplerMap(self, Data):

        Siz = Data.shape
        N = self.dBrdCfg["N"]

        # Remove frame counter form data
        Data = Data[2:N,:]
        Win = np.hanning(N-2)
        if self.SigCfg_RangeWinType == 'Hanning':
            Win = np.hanning(N-2)
        else:
            if self.SigCfg_RangeWinType == 'Hamming':
                Win = np.hamming(N-2)
            else:
                Win = np.ones(N-2)

        Win2D = np.zeros((N-2,self.SigCfgNp))

        DataMean = np.mean(Data,1)
        #DataMean = np.zeros(N-2)
        for Idx in range(0,self.SigCfgNp):
            Win2D[:,Idx] = Win
            if self.ChkBox_SigCfg_MeanRemove.isChecked():
                Data[:,Idx] = Data[:,Idx] - DataMean

        ScaWin = np.sum(Win)
        FuSca = self.RfBrd.Rad.Get('FuSca')
        XData = np.fft.fft(Data*Win2D, self.SigCfgRFFT, 0)/ScaWin*FuSca

        XData = XData[self.SigCfgRIdxMin:self.SigCfgRIdxMax,:]
        Siz = XData.shape


        Win = np.hanning(self.SigCfgNp)
        if self.SigCfg_VelWinType == 'Hanning':
            Win = np.hanning(self.SigCfgNp)
        else:
            if self.SigCfg_VelWinType == 'Hamming':
                Win = np.hamming(self.SigCfgNp)
            else:
                Win = np.ones(self.SigCfgNp)
        ScaWin = np.sum(Win)
        Win2D = np.zeros((Siz[0],self.SigCfgNp))
        for Idx in range(0,Siz[0]):
            Win2D[Idx,:] = Win

        XData = np.fft.fft(XData*Win2D, self.SigCfgVFFT, 1)/ScaWin
        XData = np.abs(np.fft.fftshift(XData,1))
        XData = 20*np.log10(XData)
        Siz = XData.shape
        DataMax = XData.reshape(Siz[0]*Siz[1])
        
        if self.SigCfgScaMax:
            DataMax = np.max(DataMax)
            if DataMax > self.SigCfgLimMaxMin + self.SigCfgLimMaxSideLev:
                XData = XData - DataMax
                XData[XData < -self.SigCfgLimMaxSideLev] = -self.SigCfgLimMaxSideLev
            else:
                XData[XData < self.SigCfgLimMaxMin] = self.SigCfgLimMaxMin;
                XData = XData - self.SigCfgLimMaxMin - self.SigCfgLimMaxSideLev;
                XData[0,0] = 0; 

        elif self.SigCfgScaLim:
            XData[0,0] = self.SigCfgLimFixedMax;
            XData[XData > self.SigCfgLimFixedMax] = self.SigCfgLimFixedMax;
            XData[XData < self.SigCfgLimFixedMin] = self.SigCfgLimFixedMin;  

        return XData
        
    def SetCfgInf(self, stVal):
        self.stCfgInf = stVal

    def SetInitFailed(self, Val):
        self.InitFailed = Val

    def ParseCfgFile(self, stFile):
        if len(stFile) > 1:
            File = open(stFile, "r", encoding="utf-8", errors="ignore")
            
            lCmd = list()
            # Configure RangeDoppler parameters
            lCmd.append((r"PageRangeDopplerCfg_SetStrtFreq\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_RadStrtFreq.setText", "Func"))
            lCmd.append((r"PageRangeDopplerCfg_SetStopFreq\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_RadStopFreq.setText", "Func"))
            lCmd.append((r"PageRangeDopplerCfg_SetSamples\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_RadSamples.setText", "Func"))
            lCmd.append((r"PageRangeDopplerCfg_SetChirpRep\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_RadPerd.setText", "Func"))
            lCmd.append((r"PageRangeDopplerCfg_SetNrChirp\((?P<Arg>([0-9]+))\)", "self.Edit_Cfg_RadNp.setText", "Func"))   
            lCmd.append((r"PageRangeDopplerCfg_SetTInt\((?P<Arg>([0-9]+))\)", "self.Edit_Cfg_RadTInt.setText", "Func"))   
            # Configure parameters for signal processing
            lCmd.append((r"PageRangeDopplerCfg_EnaNormMax\((?P<Arg>(True|False))\)", "self.ChkBox_SigCfg_NormMax.setChecked", "FuncSt"))
            lCmd.append((r"PageRangeDopplerCfg_SetNormLimMin\((?P<Arg>(-[0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_LimMaxMin.setText", "Func"))
            lCmd.append((r"PageRangeDopplerCfg_SetNormSidelobe\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_LimMaxSideLev.setText", "Func"))
            lCmd.append((r"PageRangeDopplerCfg_EnaLimMinMax\((?P<Arg>(True|False))\)", "self.ChkBox_SigCfg_NormFixed.setChecked", "FuncSt"))
            lCmd.append((r"PageRangeDopplerCfg_SetLimMin\((?P<Arg>(-[0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_LimFixedMin.setText", "Func"))
            lCmd.append((r"PageRangeDopplerCfg_SetLimMax\((?P<Arg>(-[0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_LimFixedMax.setText", "Func"))

            # Set Parameters for Number of Parameters for RangeDoppler measurement page
            lCmd.append((r"PageRangeDopplerMeas_SetNrFrms\((?P<Arg>([0-9]+))\)", "self.Edit_Meas_NrFrms.setText", "Func"))
            lCmd.append((r"PageRangeDopplerMeas_SetRMin\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Meas_RMin.setText", "Func"))
            lCmd.append((r"PageRangeDopplerMeas_SetRMax\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Meas_RMax.setText", "Func"))
            lCmd.append((r"PageRangeDopplerMeas_EnaFFT\((?P<Arg>(True|False))\)", "self.ChkBox_Meas_FFT.setChecked", "FuncSt"))
            lCmd.append((r"PageRangeDopplerMeas_EnaAverage\((?P<Arg>(True|False))\)", "self.ChkBox_Meas_PSD.setChecked", "FuncSt"))
            lCmd.append((r"PageRangeDopplerMeas_SetTxCfg\('(?P<Arg>([0-9a-zA-Z \(\);]+))'\)", "self.Edit_Meas_Cfg.setText", "Func"))
            # Set parameters for Range-Time measuremet view
            lCmd.append((r"PageRangeDopplerMeas_SetRangeFFTSiz\((?P<Val>(64|128|256|512|1024|2048|4096|8192|16384|32768|65536))\)", "self.Edit_Cfg_RangeFftSiz.setText", "Func"))
            lCmd.append((r"PageRangeDopplerMeas_SetRangeWinType\((?P<Val>(Hanning|Hamming|Boxcar))\)", "self.Edit_Cfg_RangeWinType.setText", "Func"))
            lCmd.append((r"PageRangeDopplerMeas_SetVelFFTSiz\((?P<Val>(64|128|256|512|1024|2048|4096|8192|16384|32768|65536))\)", "self.Edit_Cfg_VelFftSiz.setText", "Func"))
            lCmd.append((r"PageRangeDopplerMeas_SetVelWinType\((?P<Val>(Hanning|Hamming|Boxcar))\)", "self.Edit_Cfg_VelWinType.setText", "Func"))
                        
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

            