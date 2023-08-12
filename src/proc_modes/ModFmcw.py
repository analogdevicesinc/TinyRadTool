# (c) Haderer Andreas Inras GmbH

# Import modules for radarsignal processing and control of radar system
import  src.S14.S14_ModFmcw as S14_ModFmcw
import  src.cmd_modules.TinyRad as TinyRad

import  src.logger.Logger as Logger
import  src.cmd_modules.StrConv as StrConv

from PyQt5 import QtCore, QtGui, QtWidgets
import  pyqtgraph as pg
import  threading as threading
import  time as time
import  numpy as np
import  src.ui.proc_modes.ui_ModFmcw as ui_ModFmcw
from    os.path import expanduser
from    array import array
import  re
import  time

#import  h5py


class ModFmcw(QtWidgets.QMainWindow, ui_ModFmcw.Ui_ModFmcw):

    plot_state = False
    histog_state = False
    SigIniTim = QtCore.pyqtSignal()
    SigIniDone = QtCore.pyqtSignal()
    SignalProgressDone = QtCore.pyqtSignal()
    SigMenuEna = QtCore.pyqtSignal()
    SigMenuDi = QtCore.pyqtSignal()
    SigMeasStop = QtCore.pyqtSignal()
    SigPlotMeasData = QtCore.pyqtSignal()


    SigUpdIni = QtCore.pyqtSignal()  
    IniThread = None
    MeasIni = None  

    lUpdIni = list()
    LockUpdIni = threading.Lock()
    LockMeasData = threading.Lock()

    stCfgInf = ""
    InitFailed = True

    def __init__(self, patre):
        super(ModFmcw, self).__init__()
        self.patre = patre
        self.setupUi(self)
        self.Button_Meas_Meas.clicked.connect(self.Button_Meas_StartThread)
        self.Button_Meas_Ini.clicked.connect(self.Button_Ini_StartThread)
        self.ChkBox_MeasProf_Histog.clicked.connect(self.ChkBox_MeasProf_Histog_stateChanged)

        QtWidgets.QShortcut(QtGui.QKeySequence("ALT+F2"), self.Widget_Meas, self.ToggleCmd)
        QtWidgets.QShortcut(QtGui.QKeySequence("Up"), self.Widget_Meas, self.SetCmdTxtUp)
        QtWidgets.QShortcut(QtGui.QKeySequence("Down"), self.Widget_Meas, self.SetCmdTxtDown)
        
        self.Button_LogtoFile.clicked.connect(self.Button_LogToFile_Clicked)
        self.Button_ClearLog.clicked.connect(self.Button_ClearLog_Clicked)
        self.Edit_Meas_Cmd.returnPressed.connect(self.CmdExec)
        self.SigIniTim.connect(self.SigActionTimerStart)
        self.SigIniDone.connect(self.SigActionInitDone)
        self.SignalProgressDone.connect(self.SigActionSetProgressDone)
        self.SigMenuEna.connect(self.SigActionShowMenubar)
        self.SigMenuDi.connect(self.SigActionHideMenubar)
        self.SigMeasStop.connect(self.SigActionMeasureStop)
        self.SigUpdIni.connect(self.SigActionUpdIni)
        self.SigPlotMeasData.connect(self.SigActionPlotMeasData)

        self.Log= Logger.Logger(self.Log_Textbox)

        # Configuration of Signal Processing
        self.SigCfg_WinType= 'Hanning'
        self.SigCfg_NFFTCfg= 2048
        self.PltCfg_LineWidth= 1.0

        self.ProcFrms = 0
        self.MeasData = 0
        self.dBrdCfg = dict()
        self.RangeTimProf = 0

        self.CmdHide= True
        self.NrChn= int(4)
 
        self.ShowSecndPlt= False 
        self.Plt_UpdLabel= True
        self.Plt_LabelState= 0

        self.EstPosn_Ena= False

        self.TrigOut_Ena= False

        self.StoreIf = False
        self.StoreIfGenArray = False
        self.StoreNrFrms = 0
        self.StoreIdx = 0

        self.ExecHist = list()
        self.ExecHistIdx = 0
        self.Brd = None


        self.ScaRcs = False
        self.lRcs = list()

        self.CalcPsd = False
        self.NrFrmsPsd = 0   

        if self.patre.GuiSelIni:
            self.ParseCfgFile(self.patre.stFileCfg)

        self.LimFreq()

    def LimFreq(self):
        stStrtFreq= self.Edit_Cfg_RadStrtFreq.text()
        fMin= StrConv.ToFloat(stStrtFreq)*1e6            
        stStopFreq= self.Edit_Cfg_RadStopFreq.text()
        fMax= StrConv.ToFloat(stStopFreq)*1e6

        if fMin < self.patre.Lim_fMin:
            fMin= self.patre.Lim_fMin
            self.UpdIniAppend('Func','self.Edit_Cfg_RadStrtFreq.setText',str(fMin/1e6)) 
        if fMax > self.patre.Lim_fMax:
            fMax= self.patre.Lim_fMax
            self.UpdIniAppend('Func','self.Edit_Cfg_RadStopFreq.setText',str(fMax/1e6)) 

        if fMax <= fMin:
            fMin= self.patre.Lim_fMin
            self.UpdIniAppend('Func','self.Edit_Cfg_RadStrtFreq.setText',str(fMin/1e6))             
            fMax= self.patre.Lim_fMax
            self.UpdIniAppend('Func','self.Edit_Cfg_RadStopFreq.setText',str(fMax/1e6))             
        
        self.SigUpdIni.emit()          
        
    def ToggleCmd(self):
        if self.CmdHide:
            self.CmdHide= False
            self.Label_Meas_Cmd.show()
            self.Edit_Meas_Cmd.show()
            self.Label_Meas_CmdSts.show()  
        else:
            self.CmdHide= True
            self.Label_Meas_Cmd.hide()
            self.Edit_Meas_Cmd.hide()
            self.Label_Meas_CmdSts.hide() 
    
    def SetCmdTxtUp(self):
        if len(self.ExecHist) > 0:
            if not self.CmdHide:
                self.Edit_Meas_Cmd.setFocus()
                self.Edit_Meas_Cmd.setText(self.ExecHist[self.ExecHistIdx])      
                self.ExecHistIdx= self.ExecHistIdx - 1
                if self.ExecHistIdx < 0:
                    self.ExecHistIdx= 0
    
    def SetCmdTxtDown(self):
        if len(self.ExecHist) > 0:
            if not self.CmdHide:
                self.Edit_Meas_Cmd.setFocus()
                self.Edit_Meas_Cmd.setText(self.ExecHist[self.ExecHistIdx])      
                self.ExecHistIdx= self.ExecHistIdx + 1
                if self.ExecHistIdx >= len(self.ExecHist):
                    self.ExecHistIdx= len(self.ExecHist) - 1

    def CmdExec(self):
        CmdExec= False
        stCmd= self.Edit_Meas_Cmd.text()        
        RegCmd= re.compile(r"Store\(\"(?P<File>[\w]+.h5)\"\)")
        Match= RegCmd.search(stCmd)
        if Match:
            CmdExec= True
            stFile= self.patre.stFolderCfg + Match.group("File")
            with h5py.File(stFile,'w') as hFile:
                hFile.create_dataset('/Data', data = self.MeasData.transpose())
                hFile.create_dataset('/RPTime', data = self.RangeTimProf.transpose())
                for Key in self.dBrdCfg:
                    print('/BrdCfg/' + str(Key))
                    if isinstance(self.dBrdCfg[Key],str):
                        Dat= list()
                        Dat.append(self.dBrdCfg[Key])
                        dt = h5py.special_dtype(vlen=bytes)
                        DatSet= hFile.create_dataset('/BrdCfg/' + str(Key), (100,1), dtype=dt)
                        DatSet.attrs["name"]= (self.dBrdCfg[Key])      
                    else:
                        hFile.create_dataset('/BrdCfg/' + str(Key), data = self.dBrdCfg[Key])

            self.Label_Meas_CmdSts.setText("File " + Match.group("File") + " written")
        
      
        RegCmd= re.compile(r"StoreIf\(\"(?P<File>[\w]+.h5)\",[ ]*(?P<Frms>([0-9]+))\)")
        Match= RegCmd.search(stCmd)
        if Match:
            CmdExec = True
            self.StoreIf = True
            self.StoreIfGenArray = True
            self.StoreNrFrms = int(Match.group("Frms"))
            self.StoreIdx = 0
            self.StoreFileName = Match.group("File")
            stFile = self.patre.stFolderCfg + Match.group("File")

            self.Label_Meas_CmdSts.setText("Write to File " + Match.group("File"))


        RegCmd= re.compile(r"AddPlt\((?P<Arg>(0|1))\)")
        Match= RegCmd.search(stCmd)
        if Match:
            CmdExec = True
            Arg = int(Match.group("Arg"))
            if Arg == 0:
                self.ShowSecndPlt= False
                self.Plt_UpdLabel= True
                self.UpdIniAppend('FuncSt','self.Plot_Meas_Rp.hide', " ") 
            else:
                self.Plt_UpdLabel= True
                self.ShowSecndPlt= True
                self.UpdIniAppend('FuncSt','self.Plot_Meas_Rp.show', " ") 
                
        RegCmd = re.compile(r"AddPosn\((?P<Arg>(0|1))\)")
        Match = RegCmd.search(stCmd)
        if Match:
            CmdExec = True
            Arg = int(Match.group("Arg"))
            if Arg == 0:
                self.TabContWidget.removeTab(self.Widget_Posn_Idx)
            else:
                self.Widget_Posn_Idx= self.TabContWidget.addTab(self.Widget_Posn,"&Posn")

        RegCmd = re.compile(r"EstPosn\((?P<Min>([0-9]+)),[ ]*(?P<Max>([0-9]+)),[ ]*(?P<N>([0-9]+))\)")
        Match = RegCmd.search(stCmd)
        if Match:
            CmdExec = True
            Min = int(Match.group("Min"))
            Max = int(Match.group("Max"))
            N = int(Match.group("N"))
            print("M:", Min, Max, N)
            if Min < Max:
                self.EstPosn_Min = Min
                self.EstPosn_Max = Max
                self.EstPosn_N = N
                self.EstPosn_Idx = 0
                self.EstPosn_Val = np.zeros((int(N),8))
                self.EstPosn_Ena = True

        RegCmd = re.compile(r"ExtendLim")
        Match = RegCmd.search(stCmd)
        if Match:
            CmdExec = True        
            self.patre.Lim_fMin = 23.9e9
            self.patre.Lim_fMax = 24.3e9
            self.Label_Meas_CmdSts.setText("Limits extended from 23.9 to 24.3 GHz ")

        RegCmd= re.compile(r"ScaleRcs\((?P<Arg>(0|1))\)")
        Match= RegCmd.search(stCmd)
        if Match:
            CmdExec= True
            Arg= int(Match.group("Arg"))
            if Arg == 0:
                self.ScaRcs = False
                self.Plt_UpdLabel = True
            else:
                self.ScaRcs = True
                self.Plt_UpdLabel = True

        RegCmd = re.compile(r"AddRcs\((?P<Arg>([\-0-9]+))\)")
        Match = RegCmd.search(stCmd)
        if Match:
            CmdExec = True
            Arg = int(Match.group("Arg"))
            self.lRcs.append(Arg)              

        RegCmd = re.compile(r"ClrRcs")
        Match = RegCmd.search(stCmd)
        if Match:
            CmdExec = True
            self.lRcs.clear()

        RegCmd = re.compile(r"CalcPsd\((?P<Arg>(0|1))\)")
        Match = RegCmd.search(stCmd)
        if Match:
            CmdExec= True
            Arg= int(Match.group("Arg"))
            if Arg > 0.1:
                self.CalcPsd = True
                self.NrFrmsPsd = 0
            else:
                self.CalcPsd = False
                self.NrFrmsPsd = 0                        

        if CmdExec:
            self.ExecHist.append(stCmd)
            self.ExecHistIdx= len(self.ExecHist) - 1
            self.Edit_Meas_Cmd.setText("")  
        else:
            self.Label_Meas_CmdSts.setText("Command " + stCmd + " not known")  
            self.Edit_Meas_Cmd.setText("")

        self.SigUpdIni.emit()

    def toggleHistog(self):
        if self.ChkBox_MeasProf_Histog.isChecked():
            self.ChkBox_MeasProf_Histog.setChecked(False)
            self.Image_MeasProf.ui.histogram.show()
            self.histog_state = True
        else:
            self.ChkBox_MeasProf_Histog.setChecked(True)
            self.Image_MeasProf.ui.histogram.hide()
            self.histog_state = False


    def ChkBox_MeasProf_Histog_stateChanged(self):
        if self.ChkBox_MeasProf_Histog.isChecked():
            self.Image_MeasProf.ui.histogram.hide()
            self.histog_state = False
        else:
            self.Image_MeasProf.ui.histogram.show()
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
            self.Label_MeasProf_CfgInf.setPalette(palette)
            self.Label_Meas_CfgInf.setPalette(palette)
            self.Label_Meas_CfgInf.setText("Starting Measurement...")
            self.Label_MeasProf_CfgInf.setText("Starting Measurement...")
            self.Log.Append("Starting Measurement...")

            self.SigIniTim.emit()
            self.SignalProgressDone.emit()
            self.SigIniDone.emit()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.black)
            self.Label_MeasProf_CfgInf.setPalette(palette)
            self.Label_Meas_CfgInf.setPalette(palette)

            self.Label_Meas_CfgInf.setText(self.stCfgInf)
            self.Label_MeasProf_CfgInf.setText(self.stCfgInf)
            self.Button_Meas_Meas.setText("Stop")
        else:
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
            self.Label_MeasProf_CfgInf.setPalette(palette)
            self.Label_Meas_CfgInf.setPalette(palette)

            self.Label_Meas_CfgInf.setText("Stopping Measurement...")
            self.Label_MeasProf_CfgInf.setText("Stopping Measurement...")
            self.Log.Append("Stopping Measurement...")
            self.Edit_Meas_NrFrms.setText(str(0))
            self.Log.Append("Brd Reset...");
            # self.Brd.BrdRst();

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
        self.CntBgFx = 0
        self.Log.Append("Start Timer")

    def UpdIniAppend(self,stType, stVal,Val):
        self.LockUpdIni.acquire()
        self.lUpdIni.append((stType, stVal, Val))
        self.LockUpdIni.release()

    def SigActionUpdIni(self):
        self.LockUpdIni.acquire()
        for Elem in self.lUpdIni:
            if Elem[0] == 'Func':
                stCmd= Elem[1] + '(Elem[2])'
                eval(stCmd)
            if Elem[0] == 'FuncV':
                stCmd= Elem[1] + '(' + str(Elem[2]) + ')'
                eval(stCmd)            
            if Elem[0] == 'FuncSt':
                stCmd= Elem[1] + '(' + Elem[2] + ')'
                eval(stCmd)      
        self.lUpdIni= list()
        self.LockUpdIni.release()
    
    def Button_LogToFile_Clicked(self):
        StoreData   = self.Log.GetTxt()
        Home        = expanduser("~")
        FileName    = QtGui.QFileDialog.getSaveFileName(self, str("Set Output Path"), Home)
        if FileName != "":
            fs= open(FileName, 'w', encoding="utf-8", errors="ignore")
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
        self.Log.Append("Fmcw: Button Ini Clicked")

        IniSts = 0
        self.ProcFrms = 0

        dIniAdc = self.GetAdcCfg()
        dIniFmcw = self.GetFmcwCfg()
        self.dBrdCfg = self.GetBrdCfg(dIniAdc,dIniFmcw)

        print("Fmcw: Button Ini Clicked")
        print("Check App Status 1: ")
        if self.Brd == None:
            self.Brd = self.patre.hTinyRad

        RetVal = self.Brd.BrdGetUID()
        if RetVal[0] == False:
            Ret= -1
            self.Log.Append("Application not responding: " + str(RetVal[0]))
            self.Log.Append("Reset Board and Restart Application")
        else:
            Ret= 0
            self.Log.Append("Application running" + str(RetVal[0]) + ' | ' + str(RetVal[1]))
            palette     = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
            self.UpdIniAppend('Func','self.Label_MeasProf_CfgInf.setPalette', palette) 
            self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setPalette', palette) 
            self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setText', "Application running") 
            self.UpdIniAppend('Func','self.Label_MeasProf_CfgInf.setText', "Application running") 

        self.SigUpdIni.emit()
        self.Log.SigUpd.emit()
        
        B= self.dBrdCfg["FreqStop"] - self.dBrdCfg["FreqStrt"]
        T= self.dBrdCfg["TimUp"]
        kf= B/T
        c0= 2.99792458e8
        self.FreqCenter = (self.dBrdCfg["FreqStop"] + self.dBrdCfg["FreqStrt"])/2

        if Ret == 0:
            dSwSts= self.Brd.BrdGetSwVers()
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
            self.UpdIniAppend('Func','self.Label_MeasProf_CfgInf.setPalette', palette)
            self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setPalette', palette)
            self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setText', "Connected: Initializing...")
            self.UpdIniAppend('Func','self.Label_MeasProf_CfgInf.setText', "Connected: Initializing...")

            self.Log.Append("Connected: Initializing...")

            self.SigUpdIni.emit()
            self.Log.SigUpd.emit()

            self.RfBrd = S14_ModFmcw.S14_ModFmcw(self.Brd, self.dBrdCfg)
            self.RfBrd.IniBrdModFmcw()

            B= self.Brd.Adf_Pll.fStop - self.Brd.Adf_Pll.fStrt
            T= self.Brd.Adf_Pll.TRampUp
            kf= B/T

            IniSts = 1
        else:
            IniSts= -1

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.black)
        self.UpdIniAppend('Func','self.Label_MeasProf_CfgInf.setPalette', palette)
        self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setPalette', palette)        

        self.SigCfg_WinType= self.Edit_Cfg_WinType.text()
        TmpVal = StrConv.ToFloat(self.Edit_Cfg_FftSiz.text())
        TmpVal = pow(2, np.ceil(np.log2(TmpVal)))
        self.SigCfg_NFFTCfg = int(TmpVal)

        self.SigCfg_NFFT = int(self.SigCfg_NFFTCfg)
        if self.SigCfg_NFFT < int(self.dBrdCfg["N"]):
            self.SigCfg_NFFT = int(pow(2, np.ceil(np.log2(self.dBrdCfg["N"]))))

        self.Edit_Cfg_FftSiz.setText(str(self.SigCfg_NFFT)) 

        self.PltCfg_LineWidth= StrConv.ToFloat(self.Edit_Cfg_LineWidth.text())

        if self.PltCfg_LineWidth < 0.1:
            self.PltCfg_LineWidth = 0.1
        if self.PltCfg_LineWidth > 10:
            self.PltCfg_LineWidth = 10

        self.Edit_Cfg_LineWidth.setText(str(self.PltCfg_LineWidth))
        
        self.SigCfg_NIni = 1
        fs= self.dBrdCfg["fs"]
        self.SigCfg_Freq = np.linspace(0,int(self.SigCfg_NFFT-1),int(self.SigCfg_NFFT))/self.SigCfg_NFFT*fs
        self.SigCfg_FreqDisp = self.SigCfg_Freq[0:int(self.SigCfg_NFFT/2)]
        self.SigCfg_RangeDisp = self.SigCfg_FreqDisp*c0/(2*kf)

        self.RangeTimProfLen = StrConv.ToInt(self.Edit_MeasProf_NrHist.text())
        if self.RangeTimProfLen < 10:
            self.RangeTimProfLen = 10
        self.UpdIniAppend('Func','self.Edit_MeasProf_NrHist.setText',str(self.RangeTimProfLen))

        self.RangeTimProf= -100*np.ones((int(self.SigCfg_NFFT/2), int(self.RangeTimProfLen)))

        #----------------------------------------------------------------
        # Check Limits for RMin and RMax; Chech if RMin and RMax are used
        RMin= StrConv.ToFloat(self.Edit_Meas_RMin.text())
        RMax= StrConv.ToFloat(self.Edit_Meas_RMax.text())
        if RMin  < 0:
            RMin= 0
        # Check Limits and correct fMin and fMax
        if RMax > self.SigCfg_RangeDisp[int(self.SigCfg_NFFT/2-1)]:
            RMax= self.SigCfg_RangeDisp[int(self.SigCfg_NFFT/2-1)]
            RMax= np.floor(RMax*10)/10
        if RMin > RMax:
            RMin= self.SigCfg_RangeDisp[0]
            RMax= self.SigCfg_RangeDisp[int(self.SigCfg_NFFT/2-1)]  
            RMax= np.floor(RMax*10)/10      
        self.UpdIniAppend('Func','self.Edit_Meas_RMin.setText',str(RMin))
        self.UpdIniAppend('Func','self.Edit_Meas_RMax.setText',str(RMax))

        #----------------------------------------------------------------
        # Check Prof of RMin and RMax
        self.SigCfg_RMin= StrConv.ToFloat(self.Edit_MeasProf_RMin.text())
        self.SigCfg_RMax= StrConv.ToFloat(self.Edit_MeasProf_RMax.text())

        # Check Limits and correct RMin and RMax
        if self.SigCfg_RMin  < 0:
            self.SigCfg_RMin= 0      
        if self.SigCfg_RMax > self.SigCfg_RangeDisp[int(self.SigCfg_NFFT/2-1)]:
            self.SigCfg_RMax= self.SigCfg_RangeDisp[int(self.SigCfg_NFFT/2-1)]
        if self.SigCfg_RMin >   self.SigCfg_RMax:
            self.SigCfg_RMin= self.SigCfg_RangeDisp[0]
            self.SigCfg_RMax= self.SigCfg_RangeDisp[int(self.SigCfg_NFFT/2-1)]

        self.UpdIniAppend('Func','self.Edit_MeasProf_RMin.setText',str(self.SigCfg_RMin)) 
        self.UpdIniAppend('Func','self.Edit_MeasProf_RMax.setText',str(self.SigCfg_RMax)) 
        
        self.SigUpdIni.emit()
        self.Log.SigUpd.emit()

        if IniSts == 1:
            fs= round(self.dBrdCfg["fs"]/1e6*1000)/1000
            self.stCfgInf= "Fmcw Cfg: fs = " + str(fs) + " (MHz) | Tup = " + str(np.floor(self.dBrdCfg["N"] / self.dBrdCfg["fs"] / 1e-6*10)/10) + " us"
            self.UpdIniAppend('Func','self.SetInitFailed', False)  
        elif IniSts < 0:
            palette     = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
            self.UpdIniAppend('Func','self.SetCfgInf','Board not responding. Reset Board and restart Application')
            self.UpdIniAppend('Func','self.Label_MeasProf_CfgInf.setPalette', palette)
            self.UpdIniAppend('Func','self.Label_Meas_CfgInf.setPalette', palette)
            self.UpdIniAppend('Func','self.SetInitFailed', True)          
        else:
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
            self.Label_MeasProf_CfgInf.setPalette(palette)
            self.Label_Meas_CfgInf.setPalette(palette)
            self.stCfgInf= "Initialization failed"
            self.UpdIniAppend('Func','self.SetInitFailed', True)  
        
        self.UpdIniAppend('FuncSt','self.Label_Meas_CfgInf.setText', 'self.stCfgInf') 
        self.Log.Append(self.stCfgInf)
        
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
            
            self.Edit_MeasProf_RMin.setDisabled(False)
            self.Edit_MeasProf_RMax.setDisabled(False)
            self.Edit_MeasProf_NrHist.setDisabled(False)
            self.Edit_Meas_Cfg.setDisabled(False)

            self.ChkBox_Meas_FFT.setDisabled(False)
            self.ChkBox_Meas_PSD.setDisabled(False)
            self.SigMenuEna.emit()
            self.SignalProgressDone.emit()

    def SigActionMeasureStop(self):
        self.Timer.stop()
        self.Button_Meas_Ini.setDisabled(False)
        self.Edit_Meas_NrFrms.setDisabled(False)
        self.Edit_Meas_RMin.setDisabled(False)
        self.Edit_Meas_RMax.setDisabled(False)
        
        self.Edit_MeasProf_RMin.setEnabled(True)
        self.Edit_MeasProf_RMax.setEnabled(True)
        self.Edit_MeasProf_NrHist.setEnabled(True)
        self.Edit_Meas_Cfg.setEnabled(True)

        self.ChkBox_Meas_FFT.setDisabled(False)
        self.ChkBox_Meas_PSD.setDisabled(False)
        self.SigMenuEna.emit()
        self.SignalProgressDone.emit()
        self.Button_Meas_Meas.setText("Measure")
        self.Edit_Meas_NrFrms.setText(str(self.NrFrmsInit))
        self.Label_Meas_CfgInf.setText("Measurement Stopped")
        self.Label_MeasProf_CfgInf.setText("Measurement Stopped")
        self.MeasIni = None

    def IniStrt(self):
        self.progressbar.setRange(0,0)
        self.progressbar.setValue(0)

        self.Button_Meas_Ini.setDisabled(True)
        self.Edit_Meas_NrFrms.setDisabled(True)
        self.Edit_Meas_RMin.setDisabled(True)
        self.Edit_Meas_RMax.setDisabled(True)
        
        self.Edit_MeasProf_RMin.setDisabled(True)
        self.Edit_MeasProf_RMax.setDisabled(True)
        self.Edit_MeasProf_NrHist.setDisabled(True)
        self.Edit_Meas_Cfg.setDisabled(True)

        if self.MeasIni == None:
            self.ChkBox_Meas_FFT.setDisabled(True)
            self.ChkBox_Meas_PSD.setDisabled(True)
        else:
            self.ChkBox_Meas_FFT.setDisabled(False)
            self.ChkBox_Meas_PSD.setDisabled(False)

    def MeasUpdate(self):
        stNrFrms= self.Edit_Meas_NrFrms.text()
        NrFrms= int(stNrFrms)
        NrFrms= NrFrms - 1
        self.Edit_Meas_NrFrms.setText(str(NrFrms))

        if NrFrms < 0:
            self.Log.Append("NrFrms < 0")
            self.SigMeasStop.emit()
            self.SigMenuEna.emit()

        else:
            try:
                Data= self.RfBrd.GetDataEve()
            except OSError:
                self.Log.Append("OSError")
                pass
            except AttributeError:
                self.Log.Append("AttributeError")
                pass
            except ValueError:
                self.Log.Append("ValueError")
                pass
            except:
                self.Log.Append("Other Exception caught")
                pass

            N= self.Brd.Get('N')
            NrChn= self.Brd.Get('NrChn')
            self.NrChn= int(NrChn)
            ProcData= False
            try:
                if hasattr(Data, "shape"):
                    ProcData = True
            except NameError:
                Data = None
                pass

            if self.StoreIf:
                if self.StoreIfGenArray:
                    self.StoreIfGenArray= False
                    self.StoreDatav= np.zeros((int(N*NrChn), int(self.StoreNrFrms)), dtype = 'int16')
                    self.StoreTimv= np.zeros(int(self.StoreNrFrms))

                Dummy= np.int16(Data.transpose())
                self.StoreData[:,self.StoreIdx]= Dummy.reshape(N*NrChn)
                self.StoreTim= time.time()
                self.StoreIdx= self.StoreIdx + 1

                if self.StoreIdx >= self.StoreNrFrms:
                    self.StoreIf= False
                    print("Store Data")
                    stFile= self.patre.stFolderCfg + self.StoreFileName

                    with h5py.File(stFile,'w') as hFile:
                        hFile.create_dataset('/If', data = self.StoreData.transpose())
                        hFile.create_dataset('/Tim', data = self.StoreTim)
                        if self.EstPosn_Ena:
                            hFile.create_dataset('/Posn', data = self.EstPosn_Val.transpose())      
                        for Key in self.dBrdCfg:
                            print('/BrdCfg/' + str(Key))
                            if isinstance(self.dBrdCfg[Key], str):
                                Dat= list()
                                Dat.append(self.dBrdCfg[Key]) 
                            else:
                                hFile.create_dataset('/BrdCfg/' + str(Key), data = self.dBrdCfg[Key])                  

            if ProcData:
                self.LockMeasData.acquire()
                self.MeasData = Data
                self.LockMeasData.release()
                self.SigPlotMeasData.emit()                  
                self.Timer.start()                    
            else:
                if self.CntBgFx > 2:
                    self.progressbar.setRange(0,100)
                    self.progressbar.setValue(100)
                    self.SigMeasStop.emit()
                    self.SigMenuEna.emit()
                else:
                    #self.Log.Append("CntBgFx")
                    self.CntBgFx = self.CntBgFx + 1
                    self.LockMeasData.acquire()
                    self.LockMeasData.release()
                    self.SigPlotMeasData.emit()
                    self.Timer.start()


    def GetAdcCfg(self):
        dIniADAR7251 = dict()

        dIniADAR7251["NrChn"]= 4
        self.Log.AppendDict('ADC Cfg: ', dIniADAR7251)
        self.Log.SigUpd.emit()

        return  dIniADAR7251

    def GetFmcwCfg(self):
        dIniFmcw= dict()
        stStrtFreq= self.Edit_Cfg_RadStrtFreq.text()
        dIniFmcw["fStrt"]= StrConv.ToFloat(stStrtFreq)*1e6
        if dIniFmcw["fStrt"] < self.patre.Lim_fMin:
            dIniFmcw["fStrt"]= self.patre.Lim_fMin
        stStopFreq= self.Edit_Cfg_RadStopFreq.text()
        dIniFmcw["fStop"]= StrConv.ToFloat(stStopFreq)*1e6
        if dIniFmcw["fStop"] > self.patre.Lim_fMax:
            dIniFmcw["fStop"]= self.patre.Lim_fMax

        if dIniFmcw["fStop"] <= dIniFmcw["fStrt"]:
            dIniFmcw["fStrt"]= self.patre.Lim_fMin 
            dIniFmcw["fStop"]= self.patre.Lim_fMax   

        stSamples= self.Edit_Cfg_RadSamples.text()
        dIniFmcw["N"]= StrConv.ToInt(stSamples)

        self.Edit_Cfg_RadDur.setText(stSamples)

        stPerd= self.Edit_Cfg_RadPerd.text()
        dIniFmcw["Perd"]= round((StrConv.ToFloat(stPerd)*1e-3)*1e6)*1e-6

        if dIniFmcw["N"] < 8:
            dIniFmcw["N"] = int(8)
            self.Edit_Cfg_RadSamples.setText(str(dIniFmcw["N"]))    

        if dIniFmcw["Perd"]/4 < dIniFmcw["N"]*1e-6:
            dIniFmcw["Perd"] = 4*dIniFmcw["N"]*1e-6
            self.Edit_Cfg_RadPerd.setText(str(int(dIniFmcw["Perd"]/1e-3)))    

        if dIniFmcw["Perd"] < 1e-3:
            dIniFmcw["Perd"] = 1e-3
            self.Edit_Cfg_RadPerd.setText(str(int(dIniFmcw["Perd"]/1e-3)))               

        self.SigUpdIni.emit()

        return  dIniFmcw

    def GetBrdCfg(self, dIniAdc, dIniFmcw):
        # calculate sampling rate
        dBrdCfg= dict()

        NrChn= float(dIniAdc["NrChn"])
        N= dIniFmcw["N"]
        dBrdCfg["stCfg"]= self.Edit_Meas_Cfg.text()
        dBrdCfg["fs"]= 1e6
        dBrdCfg["N"]= N
        dBrdCfg["TimUp"]= N*1e-6
        dBrdCfg["FreqStrt"]= dIniFmcw["fStrt"]
        dBrdCfg["FreqStop"]= dIniFmcw["fStop"]
        dBrdCfg["Tp"]= dIniFmcw["Perd"]/2

        stNrFrms= self.Edit_Meas_NrFrms.text()
        dBrdCfg["NrFrms"]= StrConv.ToInt(stNrFrms)
        if dBrdCfg["NrFrms"] < 10:
            dBrdCfg["NrFrms"]= 10
            self.UpdIniAppend('Func','self.Edit_Meas_NrFrms.setText',str(dBrdCfg["NrFrms"]))
        if (dBrdCfg["NrFrms"]*8) > (2**30 - 1):
            dBrdCfg["NrFrms"]= (2**30)//8
            self.UpdIniAppend('Func','self.Edit_Meas_NrFrms.setText',str(dBrdCfg["NrFrms"]))

        self.UpdIniAppend('Func','self.Edit_Cfg_RadDur.setText', str(np.floor(dBrdCfg["TimUp"]/1e-6*10)/10))
        
        self.Log.AppendDict('Cfg: ', dBrdCfg)
        self.Log.SigUpd.emit()

        return  dBrdCfg

    def CalcRangeProfile(self, Data):
        Siz= Data.shape
        N= self.dBrdCfg["N"]
        # Remove frame counter form data
        Data= Data[1:int(N),:]
        if self.SigCfg_WinType == 'Hanning':
            Win= np.hanning(N-1)
        else:
            if self.SigCfg_WinType == 'Hamming':
                Win= np.hamming(int(N-1))
            else:
                Win= np.ones(int(N-1))   

        Win2D= np.zeros((int(N-1),int(self.NrChn)))
        DataFft = np.zeros(Data.shape)
        for Idx in range(0, int(self.NrChn)):
            Win2D[:,Idx]= Win
            DataMean= np.mean(Data[:,Idx])
            DataFft[:,Idx]= Data[:,Idx] - DataMean

        ScaWin= np.sum(Win)
        FuSca= self.RfBrd.Rad.Get('FuSca')
        XData= 2*np.fft.fft(DataFft*Win2D, self.SigCfg_NFFT, 0)/ScaWin*FuSca
        XData= np.abs(XData[0:int(self.SigCfg_NFFT/2),:])

        if self.CalcPsd:
            if self.NrFrmsPsd == 0:
                self.MagSqXData = XData*XData
            else:
                self.MagSqXData = self.MagSqXData + XData*XData

            self.NrFrmsPsd = self.NrFrmsPsd + 1

            XData = np.sqrt(1/self.NrFrmsPsd*self.MagSqXData)

        if self.ScaRcs:
            #Scale to RCS instead of Uif 
            XData = 20*np.log10(self.Brd.UIfToRcs(XData, self.FreqCenter, self.SigCfg_RangeDisp, self.SigCfg_FreqDisp)) 
        else:    
            XData = 20*np.log10(XData)

        return XData

    def CalcPsdChn(self, Data):

        Siz= Data.shape
        N= self.dBrdCfg["N"]

        # Remove frame counter form data
        Data= Data[1:int(N)]
        if self.SigCfg_WinType == 'Hanning':
            Win= np.hanning(int(N-1))
        else:
            if self.SigCfg_WinType == 'Hamming':
                Win= np.hamming(int(N-1))
            else:
                Win= np.ones(int(N-1))    
        Win2D= np.zeros((int(N-1), int(self.NrChn)))
        for Idx in range(0, int(self.NrChn)):
            Win2D[:,Idx]= Win
            DataMean= np.mean(Data[Idx])
            Data[Idx]= Data[Idx] - DataMean

        ScaWin= np.sum(Win)
        FuSca= self.RfBrd.Rad.Get('FuSca')

        XData= 2*np.fft.fft(Data*Win2D, self.SigCfg_NFFT, 0)/ScaWin*FuSca
        XData= np.abs(XData[0:int(self.SigCfg_NFFT/2),:])
        XData= XData*XData
        XData= np.mean(XData,1)
        XData= np.sqrt(XData)
        XData= 20*np.log10(XData)

        return XData

    def EstPosn(self, Data):

        Siz= Data.shape
        N= self.dBrdCfg["N"]
        # Remove frame counter form data
        Data= Data[1:int(N),:]
        if self.SigCfg_WinType == 'Hanning':
            Win= np.hanning(int(N-1))
        else:
            if self.SigCfg_WinType == 'Hamming':
                Win= np.hamming(int(N-1))
            else:
                Win= np.ones(int(N-1))    
        Win2D= np.zeros((int(N-1), int(self.NrChn)))
        for Idx in range(0, int(self.NrChn)):
            Win2D[:,Idx]= Win
            DataMean= np.mean(Data[:,Idx])
            Data[:,Idx]= Data[:,Idx] - DataMean

        ScaWin= np.sum(Win)
        FuSca= self.RfBrd.Rad.Get('FuSca') 
        XData= np.fft.fft(Data*Win2D, self.SigCfg_NFFT, 0)/ScaWin*FuSca
        
        IdxMin= np.argmin(np.abs(self.SigCfg_RangeDisp - self.EstPosn_Min))
        IdxMax= np.argmin(np.abs(self.SigCfg_RangeDisp - self.EstPosn_Max))
        dR= self.SigCfg_RangeDisp[1] - self.SigCfg_RangeDisp[0]
        R0= self.SigCfg_RangeDisp[int(IdxMin)] 
        XData= np.abs(XData[int(IdxMin):int(IdxMax),:])
        DatSiz= XData.shape
        for Idx in range(0, Siz[1]):
            IdxMax= np.argmax(XData[:,Idx])
            if IdxMax == 0:
                self.EstPosn_Val[int(self.EstPosn_Idx), int(Idx)]= R0     
            elif IdxMax == DatSiz[0] - 1:
                self.EstPosn_Val[int(self.EstPosn_Idx), int(Idx)]= R0 + dR*IdxMax
            else:
                Vals= XData[int(IdxMax-1):int(IdxMax+2),int(Idx)]
                a1= 0.5*(Vals[2] - Vals[0])
                a2= 0.5*(Vals[2] + Vals[0] - 2*Vals[1])
                x= -a1/(2*a2)
                self.EstPosn_Val[int(self.EstPosn_Idx), int(Idx)]= R0 + dR*(IdxMax + x)


        self.EstPosn_Idx= self.EstPosn_Idx + 1
        if self.EstPosn_Idx >= self.EstPosn_N:
            self.EstPosn_Ena= False
        
    def SetCfgInf(self, stVal):
        self.stCfgInf= stVal

    def SetInitFailed(self, Val):
        self.InitFailed= Val

    def SigActionPlotMeasData(self):
        self.LockMeasData.acquire()
        Data = self.MeasData
        self.LockMeasData.release()

        if self.ShowSecndPlt:
            self.Plot_Meas_Rp.clear()
                
        self.Plot_Meas_Tim.clear()

        self.ProcFrms= self.ProcFrms + 1;
        self.progressbar.setRange(0,100)
        self.progressbar.setValue(100*(self.ProcFrms)/self.dBrdCfg["NrFrms"]) 

        ColorChn1= self.CButton_Cfg_Chn1.color()
        ColorChn2= self.CButton_Cfg_Chn2.color()
        ColorChn3= self.CButton_Cfg_Chn3.color()
        ColorChn4= self.CButton_Cfg_Chn4.color()

        dPenChn= (   pg.mkPen(color=ColorChn1, width=self.PltCfg_LineWidth), 
                                pg.mkPen(color=ColorChn2, width=self.PltCfg_LineWidth), 
                                pg.mkPen(color=ColorChn3, width=self.PltCfg_LineWidth), 
                                pg.mkPen(color=ColorChn4, width=self.PltCfg_LineWidth))

        PenRcs= pg.mkPen(color='k', width=2)
                             



        dChkChn= (   self.ChkBox_Cfg_Chn1.checkState(),  self.ChkBox_Cfg_Chn2.checkState(),
                                self.ChkBox_Cfg_Chn3.checkState(),  self.ChkBox_Cfg_Chn4.checkState()
                            )

        if self.EstPosn_Ena:
            self.Plot_Posn_Tim.clear()
            self.EstPosn(Data)
            x= np.arange(int(self.EstPosn_Idx))
            for Idx in range(0, int(self.NrChn)):
                if dChkChn[Idx]:
                    self.Plot_Posn_Tim.plot(x, self.EstPosn_Val[0:int(self.EstPosn_Idx),Idx], pen=dPenChn[Idx])  ## setting pen=(i,3) automaticaly creates three different-colored pens

        DataRp= self.CalcPsdChn(Data)

        self.RangeTimProf[:,0:int(self.RangeTimProfLen-1)]= self.RangeTimProf[:,1:int(self.RangeTimProfLen)]
        self.RangeTimProf[:,int(self.RangeTimProfLen-1)]= DataRp

        RMin= StrConv.ToFloat(self.Edit_Meas_RMin.text())
        RMax= StrConv.ToFloat(self.Edit_Meas_RMax.text())

        if RMin  < 0:
            RMin= 0
            self.Edit_Meas_RMin.setText(str(RMin))

        # Check Limits and correct fMin and fMax
        if RMax > self.SigCfg_RangeDisp[int(self.SigCfg_NFFT/2-1)]:
            RMax= self.SigCfg_RangeDisp[int(self.SigCfg_NFFT/2-1)]
            self.Edit_Meas_RMax.setText(str(RMax))

        if RMin > RMax:
            RMin= self.SigCfg_RangeDisp[0]
            RMax= self.SigCfg_RangeDisp[int(self.SigCfg_NFFT/2-1)]
            self.Edit_Meas_RMin.setText(str(RMin))
            self.Edit_Meas_RMax.setText(str(RMax))

        RMinIdx= np.argmin(np.abs(self.SigCfg_RangeDisp - RMin))
        RMaxIdx= np.argmin(np.abs(self.SigCfg_RangeDisp - RMax))

        if  not self.ChkBox_Meas_PSD.checkState():
            DataRp= self.CalcRangeProfile(Data)

        xRp= self.SigCfg_RangeDisp

        xTim= np.arange(StrConv.ToInt(self.dBrdCfg["N"]-2*self.SigCfg_NIni))
        DataTim= Data[int(self.SigCfg_NIni):int(StrConv.ToInt(self.dBrdCfg["N"])-self.SigCfg_NIni),:]

        if self.ShowSecndPlt:

            for Idx in range(0, int(self.NrChn)):
                if dChkChn[Idx]:
                    self.Plot_Meas_Tim.plot(xTim, DataTim[:,Idx], pen=dPenChn[Idx])  ## setting pen=(i,3) automaticaly creates three different-colored pens

            if  self.ChkBox_Meas_PSD.checkState():
                self.Plot_Meas_Rp.plot(xRp[RMinIdx:RMaxIdx], DataRp[RMinIdx:RMaxIdx], pen=dPenChn[0])  ## setting pen=(i,3) automaticaly creates three different-colored pens
            else:
                for Idx in range(0, int(self.NrChn)):
                    if dChkChn[Idx]:
                        self.Plot_Meas_Rp.plot(xRp[RMinIdx:RMaxIdx], DataRp[RMinIdx:RMaxIdx, Idx], pen=dPenChn[Idx])  ## setting pen=(i,3) automaticaly creates three different-colored pens

            if self.Plt_UpdLabel:
                self.Plt_UpdLabel= False

                self.Plot_Meas_Tim.enableAutoRange(enable = True)
                self.Plot_Meas_Tim.setLabel('left', "V", units='LSB')
                self.Plot_Meas_Tim.setLabel('bottom', "n", units='Samples')

                self.Plot_Meas_Rp.enableAutoRange(enable = True)
                if self.ScaRcs:
                    self.Plot_Meas_Rp.setLabel('left', "RCS", units='dBsm')    
                else:
                    self.Plot_Meas_Rp.setLabel('left', "RP", units='dBV')
                self.Plot_Meas_Rp.setLabel('bottom', "R", units='m')

        else:
            # Plot Time Signals if view is set
            if self.TabContWidget.currentIndex() == 0:
                if  self.ChkBox_Meas_FFT.checkState():
                    if self.Plt_LabelState != 1:
                        self.Plt_UpdLabel= True                    
                    self.Plt_LabelState= 1


                    if  self.ChkBox_Meas_PSD.checkState():
                        self.Plot_Meas_Tim.plot(xRp[RMinIdx:RMaxIdx], DataRp[RMinIdx:RMaxIdx], pen=dPenChn[0])  ## setting pen=(i,3) automaticaly creates three different-colored pens
                    else:
                        for Idx in range(0, int(self.NrChn)):
                            if dChkChn[Idx]:
                                self.Plot_Meas_Tim.plot(xRp[RMinIdx:RMaxIdx], DataRp[RMinIdx:RMaxIdx, Idx], pen=dPenChn[Idx])  ## setting pen=(i,3) automaticaly creates three different-colored pens

                        if len(self.lRcs) > 0 and not self.ScaRcs:
                            for Elem in self.lRcs:
                                #RefRcs(self, fc, RCS, R, Freq):   
                                Ref = self.Brd.RefRcs(self.FreqCenter, float(Elem), self.SigCfg_RangeDisp, self.SigCfg_FreqDisp)
                                self.Plot_Meas_Tim.plot(xRp[RMinIdx:RMaxIdx], Ref[RMinIdx:RMaxIdx], pen=PenRcs)                             

                    if self.Plt_UpdLabel:
                        self.Plt_UpdLabel= False
                        self.Plot_Meas_Tim.enableAutoRange(enable = True)
                        if self.ScaRcs:
                            self.Plot_Meas_Tim.setLabel('left', "RCS", units='dBsm')
                        else:
                            #Calculate Magnitude spectrum FFT
                            self.Plot_Meas_Tim.setLabel('left', "RP", units='dBV')
                        self.Plot_Meas_Tim.setLabel('bottom', "R", units='m')


                else:
                    if self.Plt_LabelState != 0:
                        self.Plt_UpdLabel= True                    
                    self.Plt_LabelState= 0

                    for Idx in range(0, int(self.NrChn)):
                        if dChkChn[Idx]:
                            self.Plot_Meas_Tim.plot(xTim, DataTim[:,Idx], pen=dPenChn[Idx])  ## setting pen=(i,3) automaticaly creates three different-colored pens

                    if self.Plt_UpdLabel:
                        self.Plt_UpdLabel= False
                        self.Plot_Meas_Tim.enableAutoRange(enable = True)
                        self.Plot_Meas_Tim.setLabel('left', "V", units='LSB')
                        self.Plot_Meas_Tim.setLabel('bottom', "n", units='Samples')

        # Plot Range Time Profile if view is set
        if self.TabContWidget.currentIndex() == 1:

            self.SigCfg_RMin= StrConv.ToFloat(self.Edit_MeasProf_RMin.text())
            self.SigCfg_RMax= StrConv.ToFloat(self.Edit_MeasProf_RMax.text())

            RMinIdx= np.argmin(np.abs(self.SigCfg_RangeDisp - self.SigCfg_RMin))
            RMaxIdx= np.argmin(np.abs(self.SigCfg_RangeDisp - self.SigCfg_RMax))

            yscale= (self.SigCfg_RMax - self.SigCfg_RMin)/(RMaxIdx - RMinIdx)
            xscale= (self.RangeTimProfLen - 0)/self.RangeTimProfLen
            y= self.RangeTimProf[RMinIdx:RMaxIdx,:]
            if not self.plot_state:
                self.plot_state = True
                self.Image_MeasProf.setImage(y.transpose(),pos=[0, self.SigCfg_RMin], scale=[xscale, yscale])
                self.Plotview_MeasProf.setAspectLocked(False)

            else:
                state_store = self.Plotview_MeasProf.getViewBox().getState()
                self.Image_MeasProf.setImage(y.transpose(),pos=[0, self.SigCfg_RMin], scale=[xscale, yscale])

    def ParseCfgFile(self, stFile):
        if len(stFile) > 1:
            File= open(stFile, "r", encoding="utf-8", errors="ignore")
            
            lCmd= list()
            # Configure FMCW parameters
            lCmd.append((r"PageFmcwCfg_SetStrtFreq\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_RadStrtFreq.setText", "Func"))
            lCmd.append((r"PageFmcwCfg_SetStopFreq\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_RadStopFreq.setText", "Func"))
            lCmd.append((r"PageFmcwCfg_SetTInt\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_RadPerd.setText", "Func"))
            lCmd.append((r"PageFmcwCfg_SetSamples\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_RadSamples.setText", "Func"))
            
            # Enable or disable channels
            lCmd.append((r"PageFmcwCfg_EnaChn1\((?P<Arg>(True|False))\)", "self.ChkBox_Cfg_Chn1.setChecked", "FuncSt"))
            lCmd.append((r"PageFmcwCfg_EnaChn2\((?P<Arg>(True|False))\)", "self.ChkBox_Cfg_Chn2.setChecked", "FuncSt"))
            lCmd.append((r"PageFmcwCfg_EnaChn3\((?P<Arg>(True|False))\)", "self.ChkBox_Cfg_Chn3.setChecked", "FuncSt"))
            lCmd.append((r"PageFmcwCfg_EnaChn4\((?P<Arg>(True|False))\)", "self.ChkBox_Cfg_Chn4.setChecked", "FuncSt"))
            # Set Parameters for Number of Parameters for FMCW measurement page
            lCmd.append((r"PageFmcwMeas_SetNrFrms\((?P<Arg>([0-9]+))\)", "self.Edit_Meas_NrFrms.setText", "Func"))
            lCmd.append((r"PageFmcwMeas_SetRMin\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Meas_RMin.setText", "Func"))
            lCmd.append((r"PageFmcwMeas_SetRMax\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Meas_RMax.setText", "Func"))
            lCmd.append((r"PageFmcwMeas_EnaFFT\((?P<Arg>(True|False))\)", "self.ChkBox_Meas_FFT.setChecked", "FuncSt"))
            lCmd.append((r"PageFmcwMeas_EnaAverage\((?P<Arg>(True|False))\)", "self.ChkBox_Meas_PSD.setChecked", "FuncSt"))
            lCmd.append((r"PageFmcwMeas_SetTxCfg\('(?P<Arg>([0-9a-zA-Z \(\);]+))'\)", "self.Edit_Meas_Cfg.setText", "Func"))
            lCmd.append((r"PageFmcwMeas_EnaTrigOut\((?P<Arg>(True|False))\)", "self.TrigOut_Ena", "VarSt"))
            # Set parameters for Range-Time measuremet view
            lCmd.append((r"PageFmcwTimProf_SetNrFrms\((?P<Arg>([0-9]+))\)", "self.Edit_MeasProf_NrHist.setText", "Func"))
            lCmd.append((r"PageFmcwTimProf_SetRMin\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_MeasProf_RMin.setText", "Func"))
            lCmd.append((r"PageFmcwTimProf_SetRMax\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_MeasProf_RMax.setText", "Func"))
            lCmd.append((r"PageFmcwMeas_SetFFTSiz\((?P<Val>(128|256|512|1024|2048|4096|8192|16384|32768|65536))\)", "self.Edit_Cfg_FftSiz.setText", "Func"))
            lCmd.append((r"PageFmcwMeas_SetWinType\('(?P<Val>(Hanning|Hamming|Boxcar))'\)", "self.Edit_Cfg_WinType.setText", "Func"))
            lCmd.append((r"PageFmcwMeas_SetPltLineWidth\((?P<Val>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cfg_LineWidth.setText", "Func"))
            for stLine in File:
                Ret= StrConv.ConvStrToCmd(stLine, lCmd)
                if Ret[0]:
                    try: 
                        exec(Ret[1])        
                    except:
                        print("Err: ", Ret[1])  

            # Initialize duration field with number of samples
            stSamples = self.Edit_Cfg_RadSamples.text()
            self.Edit_Cfg_RadDur.setText(stSamples)


            