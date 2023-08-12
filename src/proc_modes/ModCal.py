import  src.cmd_modules.TinyRad as TinyRad

import  src.S14.S14_ModBpa as S14_ModBpa

import  src.proc_modes.MyTableModel as MyTableModel
import  src.proc_modes.ThreadTableModel as ThreadTableModel
import  time as time
import  pyqtgraph as pg
import  src.cmd_modules.StrConv as StrConv

from PyQt5 import QtCore, QtGui, QtWidgets
import  threading as threading
import  numpy as np
import  src.ui.proc_modes.ui_ModCal as ui_ModCal
from    os.path import expanduser
import  re

import  datetime as datetime
import  tkinter as tk
from    tkinter import filedialog
import  src.cmd_modules.FileStore as FileStore

class ModCal(QtWidgets.QMainWindow, ui_ModCal.Ui_ModCal):
    IniViewThread = None
    # Configuration of Signal Processing
    dSigCfg = dict()
    ViewTableModel = None
    SigUpdateCalData = QtCore.pyqtSignal()
    CalData = None

    SigCalIniTim = QtCore.pyqtSignal()
    SigCalIniDone = QtCore.pyqtSignal()
    SigCalProgressDone = QtCore.pyqtSignal()
    SigCalMenuEna = QtCore.pyqtSignal()
    SigCalMenuDi = QtCore.pyqtSignal()
    SigCalMeasStop = QtCore.pyqtSignal()
    SigCalUpdIni = QtCore.pyqtSignal()  

    CalIniThread = None
    CalMeasIni = None  

    lUpdIni = list()
    LockUpdIni = threading.Lock()

    def __init__(self, patre):
        super(ModCal, self).__init__()
        self.patre = patre
        self.setupUi(self)
        self.Button_View_Get.clicked.connect(self.Button_View_Ini_StartThread)
        self.Button_View_Load.clicked.connect(self.Button_View_Load_Clicked)
        #Generate Signals
        self.SigUpdateCalData.connect(self.ActionUpdateCalData)

        # Signals and actions for Cal generation
        self.Button_Cal_Meas.clicked.connect(self.Button_Cal_StartThread)
        self.Button_Cal_Ini.clicked.connect(self.Button_Cal_Ini_StartThread)

        self.SigCalIniTim.connect(self.SigActionCalTimerStart)
        self.SigCalIniDone.connect(self.SigActionCalIniDone)
        self.SigCalProgressDone.connect(self.SigActionCalSetProgressDone)
        self.SigCalMenuEna.connect(self.SigActionCalShowMenubar)
        self.SigCalMenuDi.connect(self.SigActionCalHideMenubar)
        self.SigCalMeasStop.connect(self.SigActionCalMeasStop)
        self.SigCalUpdIni.connect(self.SigActionCalUpdIni)

        self.SigCfg_WinType = 'Hanning'
        self.SigCfg_NFFTCfg = 2048
        self.PltCfg_LineWidth = 1.0

        if self.patre.GuiSelIni:
            self.ParseCfgFile(self.patre.stFileCfg)

        self.ProcFrms = 0
        self.dSigCfg["CalLen"] = 64

    def Button_View_Ini_StartThread(self):

        if self.IniViewThread == None:
            self.IniViewStrt()
            self.IniViewThread = threading.Thread(target=self.Button_View_Get_Clicked, args=(self.ViewTableModel, self.CalData))
            self.IniViewThread.start()

        else:
            print(self.IniViewThread)

            if self.IniViewThread.is_alive():
                print("Thread is still running")
            else:
                print("Thread is not running")
                del self.IniViewThread             
                self.IniViewStrt()
                #self.IniViewThread = threading.Thread(target=self.Button_View_Get_Clicked(Tab=self.Table_View_Cfg))
                self.IniViewThread = threading.Thread(target=self.Button_View_Get_Clicked, args=(self.ViewTableModel, self.CalData))
                self.IniViewThread.start()   

    def Button_View_Load_Clicked(self):
        print('Load Clicked')
        root = tk.Tk()
        root.withdraw()        
        stFile = filedialog.askopenfilename(initialdir = 'C:/Tools/TinyRadTool/', filetypes = (("Result", "*.h5"), ("All", "*.*")))
        print('File: ', stFile)
        hFile = FileStore.FileStore(stFile)
        self.dCal = hFile.ReadDict('dCal')
        print("dRes: ", self.dCal)
        if 'Type' in self.dCal:
            print("Store Calibration")
            print("Shape: ", self.dCal['Dat'].shape) 
            self.dCal['Dat'] = self.dCal['Dat'].transpose()       
            self.patre.hTinyRad.BrdSetCalDat(self.dCal)


    def Button_View_Get_Clicked(self, ViewTableModel, CalData):

        Header = ['Parameter', 'Value']
        lData = list()
        UpdateTable = False
        # Get IP Address from configuration page
        dSwSts = self.patre.hTinyRad.BrdGetSwVers()

        # reset board to correctly read cal data
        self.patre.hTinyRad.BrdRst()

        dCal = dict()
        # Test cal 

        dVal = self.patre.hTinyRad.BrdGetCalDat()
        Val = dVal["Dat"]
        self.CalData = Val
        if len(Val) > 0:
           self.CalData = Val
           ChnIdx = 1
           lData.append(('Type ', str(dVal["Type"])))
           lData.append(('Range (m) ', str(dVal["R"])))
           lData.append(('RCS (sm) ', str(dVal["RCS"])))
           for Idx in range(0,len(Val)):
               lData.append(('Chn ' + str(ChnIdx), str(np.abs(Val[Idx]))))
               ChnIdx = ChnIdx + 1
           UpdateTable = True

        if UpdateTable:
           self.ViewTableModel = ThreadTableModel.ThreadTableModel(lData, Header)
           time.sleep(0.2)
           self.SigUpdateCalData.emit()

    def IniViewStrt(self):
        pass

    def ActionUpdateCalData(self):
        print("Update Table")
        if not (self.ViewTableModel == None):
            self.Table_View_Cfg.setModel(self.ViewTableModel)

        N = len(self.CalData)
        x = np.linspace(1,N,N)
        y = np.abs(self.CalData)
        self.Plot_View_Tim.clear()
        self.Plot_View_Tim.plot(x, np.abs(self.CalData), pen=pg.mkPen(color=(255, 0, 0)))
        self.Plot_View_Tim.plot(x, np.real(self.CalData), pen=pg.mkPen(color=(0, 128, 128)))
        self.Plot_View_Tim.plot(x, np.imag(self.CalData), pen=pg.mkPen(color=(128, 128, 128)))


    def Button_Cal_StartThread(self):

        if not (self.CalIniThread == None):
            if not self.CalIniThread.is_alive():
                print("Thread is not running")
                self.SigCalMenuDi.emit()
                self.CalMeasIni = True
                self.CalIniStrt()

                stTxt = self.Button_Cal_Meas.text()
                if stTxt == "Measure":
                    self.progressbar.setRange(0,0)
                    self.progressbar.setValue(0)
                    self.Edit_Cal_NrFrms.setText(str(self.dBrdCfg["NrFrms"]))
                    self.Button_Cal_Meas.setDisabled(True)
                    self.Button_Cal_Meas_Clicked()
                else:
                    self.progressbar.setRange(0,100)
                    self.progressbar.setValue(0)
                    self.Timer.start()
                    self.Button_Cal_Meas_Clicked()

    def Button_Cal_Ini_StartThread(self):

        self.SigCalMenuDi.emit()
        self.CalIniStrt()
        self.Button_Cal_Meas.setDisabled(True)

        if self.CalIniThread == None:
            self.CalIniThread = threading.Thread(target=self.Button_Cal_Meas_Ini_Clicked)
            self.CalIniThread.start()
        else:
            if self.CalIniThread.is_alive():
                print("Thread is still running")
            else:                            
                del self.CalIniThread
                self.CalIniThread = threading.Thread(target=self.Button_Cal_Meas_Ini_Clicked)
                self.CalIniThread.start()

    def SigActionCalSetProgressDone(self):
        self.progressbar.setRange(0,100)
        self.progressbar.setValue(100)

    def SigActionCalTimerStart(self):
        self.Timer = QtCore.QTimer()
        self.connect(self.Timer, QtCore.SIGNAL("timeout()"), self.CalMeasUpdate)
        self.Timer.setSingleShot(True)
        self.Timer.setInterval(2)
        self.Timer.start()

    def SigActionCalShowMenubar(self):
        try:
            self.patre.menuBar().setEnabled(True)
        except IOError:
            print("cought exception")

    def SigActionCalHideMenubar(self):
        try:
            self.patre.menuBar().setEnabled(False)
        except IOError:
            print("cought exception")
   
    def SigActionCalIniDone(self):
        if self.CalMeasIni != None:
            self.Button_Cal_Meas.setDisabled(False)
        else:
            if self.InitFailed:
                self.Button_Cal_Meas.setDisabled(True)
            else:
                self.Button_Cal_Meas.setDisabled(False)
            
            self.Button_Cal_Ini.setDisabled(False)
            self.Edit_Cal_NrFrms.setDisabled(False)
            self.Edit_Cal_RMin.setDisabled(False)
            self.Edit_Cal_RMax.setDisabled(False)
            self.Edit_Cal_Cfg.setDisabled(False)
            self.SigCalMenuEna.emit()
            self.SigCalProgressDone.emit()

    def SigActionCalMeasStop(self):
        self.Timer.stop()
        self.Button_Cal_Ini.setDisabled(False)
        self.Edit_Cal_NrFrms.setDisabled(False)
        self.Edit_Cal_RMin.setDisabled(False)
        self.Edit_Cal_RMax.setDisabled(False)
        
        self.Edit_Cal_Cfg.setEnabled(True)

        self.SigCalMenuEna.emit()
        self.SigCalProgressDone.emit()
        self.Button_Cal_Meas.setText("Measure")
        self.Edit_Cal_NrFrms.setText(str(self.CalNrFrmsIni))
        self.Label_Cal_CfgInf.setText("Measurement Stopped")
        self.CalMeasIni = None

        if self.ChkBox_Cal_Store.isChecked():
            Val = np.mean(self.CoeffHist, axis=0)
            NormVal = Val[self.dBrdCfg["RefIdx"]]
            CalTx = 1/(Val/NormVal)
            CalData = np.zeros(2*self.dBrdCfg["NRx"]*self.dBrdCfg["NTx"])
            CalData[0:2*self.dBrdCfg["NRx"]*self.dBrdCfg["NTx"]:2] = np.real(CalTx)
            CalData[1:2*self.dBrdCfg["NRx"]*self.dBrdCfg["NTx"]:2] = np.imag(CalTx)
            
            stIpAdr = self.patre.GuiIpAddr
            PortNr = self.patre.GuiCfgPortNr
            Brd = Radarbook.Radarbook("PNet", stIpAdr)
            CalData = Brd.Num2Cal(CalData)

            d = datetime.date.today()
            DateVal = d.toordinal()

            dCalCfg = dict()
            dCalCfg["Mask"] = 1
            dCalCfg["RevNr"] = 2
            dCalCfg["DateNr"] = DateVal + 365
            dCalCfg["Len"] = len(CalData)
            dCalCfg["Data"] = CalData
            dCalCfg["Table"] = 0
            Brd.BrdSetCal(dCalCfg)
            Brd.Fpga_StoreCalTable(dCalCfg)

            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
            self.Label_Cal_CfgInf.setPalette(palette) 
            self.Label_Cal_CfgInf.setText("Calibration stored to frontend") 


    def SigActionCalUpdIni(self):
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

    def CalIniStrt(self):
        self.progressbar.setRange(0,0)
        self.progressbar.setValue(0)

        self.Button_Cal_Ini.setDisabled(True)
        self.Edit_Cal_NrFrms.setDisabled(True)
        self.Edit_Cal_RMin.setDisabled(True)
        self.Edit_Cal_RMax.setDisabled(True)
        self.Edit_Cal_Cfg.setDisabled(True)

    def Button_Cal_Meas_Ini_Clicked(self):
        IniSts = 0
        self.ProcFrms = 0
        dIniCic = self.GetCicCfg()
        dIniAdc = self.GetAdcCfg()
        dIniCalCfg = self.GetCalCfg()
        self.dBrdCfg = self.GetBrdCfg(dIniAdc, dIniCic, dIniCalCfg)

        # Store Sampling Rate and Range
        if self.SigCfg_NFFTCfg  < self.dBrdCfg["N"]:
            N = self.dBrdCfg["N"]
            self.SigCfg_NFFT = int(2**np.ceil(np.log2(N)))     
        else:
            self.SigCfg_NFFT = int(self.SigCfg_NFFTCfg)
        
        fs = self.dBrdCfg["fs"]
        self.SigCfg_Freq = np.linspace(0,self.SigCfg_NFFT-1,self.SigCfg_NFFT)/self.SigCfg_NFFT*fs
        self.SigCfg_FreqDisp = self.SigCfg_Freq[0:self.SigCfg_NFFT/2]
        B = self.dBrdCfg["FreqStop"] - self.dBrdCfg["FreqStrt"]
        T = self.dBrdCfg["TimUp"]
        kf = B/T
        c0 = 2.99792458e8
        self.SigCfg_RangeDisp = self.SigCfg_FreqDisp*c0/(2*kf)

        #----------------------------------------------------------------
        # Check Prof of RMin and RMax
        self.SigCfg_RMin = StrConv.ToFloat(self.Edit_Cal_RMin.text())
        self.SigCfg_RMax = StrConv.ToFloat(self.Edit_Cal_RMax.text())
        # Check Limits and correct RMin and RMax
        if self.SigCfg_RMin  < 0:
            self.SigCfg_RMin = 0      
        if self.SigCfg_RMax > self.SigCfg_RangeDisp[self.SigCfg_NFFT/2-1]:
            self.SigCfg_RMax = self.SigCfg_RangeDisp[self.SigCfg_NFFT/2-1]
        if self.SigCfg_RMin >   self.SigCfg_RMax:
            self.SigCfg_RMin = self.SigCfg_RangeDisp[0]
            self.SigCfg_RMax = self.SigCfg_RangeDisp[self.SigCfg_NFFT/2-1]

        self.RMinIdx = np.argmin(np.abs(self.SigCfg_RangeDisp - self.SigCfg_RMin))
        self.RMaxIdx = np.argmin(np.abs(self.SigCfg_RangeDisp - self.SigCfg_RMax))

        self.UpdCalIniAppend('Func','self.Edit_Cal_RMin.setText',str(self.SigCfg_RMin)) 
        self.UpdCalIniAppend('Func','self.Edit_Cal_RMax.setText',str(self.SigCfg_RMax)) 

        
        # Get IP Address from configuration page
        stIpAdr = self.patre.GuiIpAddr
        PortNr = self.patre.GuiCfgPortNr
        Brd = Radarbook.Radarbook("PNet", stIpAdr)

        RetVal = Brd.Arm_GetAppSts()
        if RetVal[0] == False:
            Ret = -1
        else:
            if RetVal[1]   == 1:
                Ret = 0
                palette = QtGui.QPalette()
                palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
                self.UpdCalIniAppend('Func','self.Label_Cal_CfgInf.setPalette', palette) 
                self.UpdCalIniAppend('Func','self.Label_Cal_CfgInf.setText', "Application running") 
            else:
                Ret = -1
                palette = QtGui.QPalette()
                palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkRed)
                self.UpdCalIniAppend('Func','self.Label_Cal_CfgInf.setPalette', palette) 
                self.UpdCalIniAppend('Func','self.Label_Cal_CfgInf.setText', "Application not running, starting it...")              
                Brd.Arm_StrtApp()
                palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
                self.UpdCalIniAppend('Func','self.Label_Cal_CfgInf.setPalette', palette) 
                self.UpdCalIniAppend('Func','self.Label_Cal_CfgInf.setText', "Application started")              
                Ret = 0

        self.SigCalUpdIni.emit()

        if Ret == 0:
            dSwSts = Brd.BrdGetSwVers()
            if "SUid" in dSwSts:
                if dSwSts["SUid"] > 0:
                    palette = QtGui.QPalette()
                    palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
                    self.UpdCalIniAppend('Func','self.Label_Cal_CfgInf.setPalette', palette) 
                    self.UpdCalIniAppend('Func','self.Label_Cal_CfgInf.setText', "Connected: Initializing...") 
                    
                    self.SigCalUpdIni.emit()

                    del Brd
                    IniSts = 1
 
                    if dSwSts["SUid"] == 20:
                        self.dBrdCfg["Tx1"] = 1
                        self.dBrdCfg["Tx2"] = 4
                        self.dBrdCfg["NTx"] = 4
                        self.dBrdCfg["NRx"] = 8
                        self.dBrdCfg["RefIdx"] = 16
                        self.CoeffHist = np.zeros((self.dBrdCfg["NrFrms"],self.dBrdCfg["NRx"]*self.dBrdCfg["NTx"]), dtype=complex)
                        RadSys = Mimo77L.Mimo77L("PNet", stIpAdr)
                        self.RfBrd = S20_ModBpa.S20_ModBpa(RadSys, dIniAdc, dIniCic, self.dBrdCfg)
                        self.RfBrd.IniBrdModBpa()
                    elif dSwSts["SUid"] == 14:
                        self.dBrdCfg["Tx1"] = 1
                        self.dBrdCfg["Tx2"] = 1
                        self.dBrdCfg["NTx"] = 1
                        self.dBrdCfg["NRx"] = 8
                        self.dBrdCfg["RefIdx"] = 4
                        self.CoeffHist = np.zeros((self.dBrdCfg["NrFrms"],self.dBrdCfg["NRx"]*self.dBrdCfg["NTx"]), dtype=complex)
                        RadSys = Adf24Tx2Rx4.Adf24Tx2Rx4("PNet", stIpAdr)
                        self.RfBrd = S14_ModBpa.S14_ModBpa(RadSys, dIniAdc, dIniCic, self.dBrdCfg)
                        self.RfBrd.IniBrdModBpa()
                    else:
                        pass
        else:
            IniSts = -1

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.black)
        self.UpdCalIniAppend('Func','self.Label_Cal_CfgInf.setPalette', palette)        

        if IniSts == 1:
            fs = np.round(self.dBrdCfg["fs"]/1e6*1000)/1000
            self.stCfgInf = "Cfg: fs = " + str(fs) + " (MHz) | N = " + str(self.dBrdCfg["N"])
            self.UpdCalIniAppend('Func','self.SetInitFailed', False)  
        elif IniSts < 0:
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
            self.UpdCalIniAppend('Func','self.SetCfgInf','Board not responding') 
            self.UpdCalIniAppend('Func','self.Label_Cal_CfgInf.setPalette', palette)
            self.UpdCalIniAppend('Func','self.SetInitFailed', True)          
        else:
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
            self.Label_Meas_CfgInf.setPalette(palette)
            self.stCfgInf = "Initialization failed"
            self.UpdCalIniAppend('Func','self.SetInitFailed', True)  
        
        self.UpdCalIniAppend('FuncSt','self.Label_Cal_CfgInf.setText', 'self.stCfgInf') 
        
        self.SigCalUpdIni.emit()
        self.SigCalIniDone.emit()

    def GetCicCfg(self):
        Rad = Radarbook.Radarbook("PNet","192.168.1.1")
        #--------------------------------------------------------------------------------------
        # Bpa Measurement Page Time
        #--------------------------------------------------------------------------------------
        dIniCic1 = {   "FiltSel"       : 255,
                                "CombDel"       : 3,
                                "OutSel"        : 3,
                                "SampPhs"       : 0,
                                "SampRed"       : 1,
                                "Ctrl"          : Rad.cCIC1_REG_CONTROL_RSTCNTRSOP + Rad.cCIC1_REG_CONTROL_EN
                            }
        # currentText, currentIndex
        stEna = self.ComboBox_CalCfg_CicEna.currentText()
        stR = self.Edit_CalCfg_CicR.text()
        IdxOut = self.ComboBox_CalCfg_CicStage.currentIndex()
        IdxDelay = self.ComboBox_CalCfg_CicDelay.currentIndex()

        if stEna == "Bypass":
            dIniCic1["SampRed"] = 1;
            dIniCic1["Ctrl"] = Rad.cCIC1_REG_CONTROL_RSTCNTRSOP + Rad.cCIC1_REG_CONTROL_EN + Rad.cCIC1_REG_CONTROL_BYPASS
        else:
            dIniCic1["SampRed"] = StrConv.ToInt(stR)
            dIniCic1["Ctrl"] = Rad.cCIC1_REG_CONTROL_RSTCNTRSOP + Rad.cCIC1_REG_CONTROL_EN

        dIniCic1["OutSel"] = IdxOut
        dIniCic1["CombDel"] = IdxDelay

        return dIniCic1

    def GetAdcCfg(self):

        dIniAD8283 = {   "AdcSel"        : 3,
                                "FiltCtrl"      : self.Rad.cAD8283_REG_CHIN_FREQ_07_4,
                                "GainCtrl"      : self.Rad.cAD8283_REG_GAIN_16,
                                "ChnCtrl"       : self.Rad.cAD8283_REG_MUXCNTRL_ABCD,
                                "ImpCtrl"       : self.Rad.cAD8283_REG_CHIMP_200K,
                                "DivCtrl"       : 1,
                                "ClkCtrl"       : 1
                            }

        stFiltCtrl = self.ComboBox_CalCfg_AdcLowpass.currentText()
        stGainCtrl = self.ComboBox_CalCfg_AdcGain.currentText()
        stChnCtrl = self.ComboBox_CalCfg_AdcChn.currentText()
        stImpCtrl = self.ComboBox_CalCfg_AdcImp.currentText()
        stDivCtrl = self.ComboBox_CalCfg_ClkDiv.currentText()
        stClkSrcCtrl = self.ComboBox_CalCfg_AdcClkSrc.currentText()
        NrChn = len(self.ComboBox_CalCfg_AdcChn.currentText())

        dIniAD8283["FiltCtrl"] = self.dAdcLowpassSel[stFiltCtrl]
        dIniAD8283["GainCtrl"] = self.dAdcGainSel[stGainCtrl]
        dIniAD8283["ChnCtrl"] = self.dAdcChnSel[stChnCtrl]
        dIniAD8283["ImpCtrl"] = self.dAdcImpSel[stImpCtrl]
        dIniAD8283["DivCtrl"] = self.dClkDivSel[stDivCtrl]
        dIniAD8283["ClkCtrl"] = self.dAdcClkSrcSel[stClkSrcCtrl]
        dIniAD8283["NrChn"] = NrChn

        return  dIniAD8283

    def GetCalCfg(self):
        dIniCalCfg = dict()
        stStrtFreq = self.Edit_CalCfg_RadStrtFreq.text()
        dIniCalCfg["fStrt"] = StrConv.ToFloat(stStrtFreq)
        stStopFreq = self.Edit_CalCfg_RadStopFreq.text()
        dIniCalCfg["fStop"] = StrConv.ToFloat(stStopFreq)
        stDur = self.Edit_CalCfg_RadDur.text()
        dIniCalCfg["TimDur"] = StrConv.ToFloat(stDur)

        if dIniCalCfg["TimDur"] < 80:
            dIniCalCfg["TimDur"] = 80
            self.UpdCalIniAppend('Func','Edit_CalCfg_RadDur.setText', str(dIniCalCfg["TimDur"])) 
  
        stCfg = self.Edit_Cal_Cfg.text();

        # Read Reg Expression
        RegExp = re.compile(r"(TX(?P<TxAnt>[0-4]){1}(\({1,1}(?P<TxAmp>\d+)\){1,1}){1,1})")
        Match = RegExp.search(stCfg)
        if Match:
            TxSel = StrConv.ToInt(Match.group("TxAnt"))
            TxAmp = StrConv.ToInt(Match.group("TxAmp"))
            if TxAmp < 0:
                TxAmp = 0
            if TxAmp > 63:
                TxAmp = 63
        else:
            TxSel = 1
            TxAmp = 63


        dIniCalCfg["TxAmp"] = TxAmp
        # Segments are overwritten at Ini; always use max number of available antennas
        dIniCalCfg["Tx1"] = 1
        dIniCalCfg["Tx2"] = 1
    
        self.SigCalUpdIni.emit()

        return  dIniCalCfg

    def GetBrdCfg(self, dIniAdc, dIniCic, dIniCal):
        # calculate sampling rate

        dBrdCfg = dict()
        ClkDiv = float(dIniAdc["DivCtrl"])
        R = float(dIniCic["SampRed"])
        NrChn = float(dIniAdc["NrChn"])

        fs = 80e6/R/NrChn/ClkDiv
        TimUp = float(dIniCal["TimDur"])
        N = np.ceil(TimUp*1e-6*fs/8)*8

        RateFixed = ((TimUp*1e-6)+1e-3)*4

        dBrdCfg["RateEna"] = True
        dBrdCfg["RateFixed"] = RateFixed
        dBrdCfg["fs"] = fs
        dBrdCfg["N"] = N
        dBrdCfg["TimUp"] = TimUp*1e-6;
        dBrdCfg["FreqStrt"] = dIniCal["fStrt"]*1e6;
        dBrdCfg["FreqStop"] = dIniCal["fStop"]*1e6;
        dBrdCfg["NrCycles"] = 1
        dBrdCfg["Tx1"] = dIniCal["Tx1"]
        dBrdCfg["Tx2"] = dIniCal["Tx2"]
        dBrdCfg["TxAmp"] = dIniCal["TxAmp"]
        dBrdCfg["NTx"] = dIniCal["Tx2"] - dIniCal["Tx1"] + 1
        dBrdCfg["NRx"] = 8
        dBrdCfg["stCfg"] = self.Edit_Cal_Cfg.text();

        stNrFrms = self.Edit_Cal_NrFrms.text()
        dBrdCfg["NrFrms"] = int(stNrFrms)

        if (dBrdCfg["NrFrms"]) < 10:
            dBrdCfg["NrFrms"] = 10
            self.UpdCalIniAppend('Func','self.Edit_Cal_NrFrms.setText',str(dBrdCfg["NrFrms"]))
                

        if (dBrdCfg["NrFrms"]) > 200:
            dBrdCfg["NrFrms"] = 200
            self.UpdCalIniAppend('Func','self.Edit_Cal_NrFrms.setText',str(dBrdCfg["NrFrms"]))


        self.SigCalUpdIni.emit()

        return  dBrdCfg

    def UpdCalIniAppend(self,stType, stVal,Val):
        self.LockUpdIni.acquire()
        self.lUpdIni.append((stType, stVal, Val))
        self.LockUpdIni.release()

    def Button_Cal_Meas_Clicked(self):

        stTxt = self.Button_Cal_Meas.text()
        if stTxt == "Measure":
            self.CalUpdPlt = 0
            self.FrmIdx = 0
            self.ProcFrms = 0
            stNrFrms = self.Edit_Cal_NrFrms.text()
            self.CalNrFrmsIni = StrConv.ToInt(stNrFrms)
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
            self.Label_Cal_CfgInf.setPalette(palette)
            self.Label_Cal_CfgInf.setText("Starting Measurement...")

            self.RfBrd.OpenBrdMod0()
            self.SigCalIniTim.emit()
            self.SigCalProgressDone.emit()
            self.SigCalIniDone.emit()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.black)
            self.Label_Cal_CfgInf.setPalette(palette)
            self.Label_Cal_CfgInf.setText(self.stCfgInf)
            self.Button_Cal_Meas.setText("Stop")
        else:
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
            self.Label_Cal_CfgInf.setPalette(palette)

            self.Label_Cal_CfgInf.setText("Stopping Measurement...")
            self.Edit_Cal_NrFrms.setText(str(0))

    def CalMeasUpdate(self):
        stNrFrms = self.Edit_Cal_NrFrms.text()
        NrFrms = int(stNrFrms)
        NrFrms = NrFrms - 1
        self.Edit_Cal_NrFrms.setText(str(NrFrms))

        self.ProcFrms = self.ProcFrms + 1;
        self.progressbar.setRange(0,100)
        self.progressbar.setValue(100*(self.ProcFrms)/self.dBrdCfg["NrFrms"]) 

        if NrFrms < 0:
            self.SigCalMeasStop.emit()
            self.SigCalMenuEna.emit()
            self.RfBrd.CloseBrdMod0()

            # show calibration coefficients at the end
            self.Plot_Cal_Coeff.clear()
            xCoeff = np.linspace(1,self.FrmIdx,self.FrmIdx)
            yCoeff = np.abs(self.CoeffHist[0:self.FrmIdx,:])
            NAnt = int(self.dBrdCfg["NRx"]*self.dBrdCfg["NTx"])
            for Idx in range(0,NAnt):
                self.Plot_Cal_Coeff.plot(xCoeff, yCoeff[:, Idx])  ## setting pen=(i,3) automaticaly creates three different-colored pens                
        else:

            Data = self.RfBrd.GetDataEve()
            N = self.RfBrd.Rad.Get('N')
            NrChn = self.RfBrd.Rad.Get('NrChn')
            NChn = int(NrChn*self.dBrdCfg["NTx"])
            ProcData = False
            if hasattr(Data, "shape"):
                DatSiz = Data.shape
                if (len(DatSiz) == 2): 
                    if (DatSiz[0] == N) and (DatSiz[1] == NrChn*self.dBrdCfg["NTx"]):
                        ProcData = True   

            if ProcData:
                self.CalUpdPlt = self.CalUpdPlt + 1
                RP = self.CalcRangeProfile(Data)
                if self.CalUpdPlt < 2:
                    self.Plot_Cal_Tim.clear()
                    y = XData = 20*np.log10(np.abs(RP))
                    if  self.ChkBox_Cal_Zoom.checkState():
                        x = self.SigCfg_RangeDisp[self.RMinIdx:self.RMaxIdx]
                        for Idx in range(0,NChn):
                            self.Plot_Cal_Tim.plot(x, y[self.RMinIdx:self.RMaxIdx, Idx])  ## setting pen=(i,3) automaticaly creates three different-colored pens                        
                    else:
                        x = self.SigCfg_RangeDisp
                        for Idx in range(0,NChn):
                            self.Plot_Cal_Tim.plot(x, y[:, Idx])  ## setting pen=(i,3) automaticaly creates three different-colored pens
                MaxVals = self.RpMaxVal(RP)

                self.CoeffHist[self.FrmIdx,:] = MaxVals            
                self.FrmIdx = self.FrmIdx + 1
                self.Timer.start()
            else:
                self.SigCalMeasStop.emit()
                self.SigCalMenuEna.emit()
                self.RfBrd.CloseBrdMod0()  

    def CalcRangeProfile(self, Data):
        Siz = Data.shape
        N = self.dBrdCfg["N"]
        # Remove frame counter form data
        Data = Data[1:N,:]
        if self.SigCfg_WinType == 'Hanning':
            Win = np.hanning(N-1)
        else:
            if self.SigCfg_WinType == 'Hamming':
                Win = np.hamming(N-1)
            else:
                Win = np.ones(N-1)    
        Win2D = np.zeros((N-1,Siz[1]))
        for Idx in range(0,Siz[1]):
            Win2D[:,Idx] = Win

        ScaWin = np.sum(Win)
        FuSca = self.RfBrd.Rad.Get('FuSca') 
        XData = np.fft.fft(Data*Win2D, self.SigCfg_NFFT, 0)/ScaWin*FuSca
        XData = XData[0:self.SigCfg_NFFT/2,:]

        return XData

    def RpMaxVal(self, RP):
        RPExt = RP[self.RMinIdx:self.RMaxIdx,:] 
        MaxIdx = np.argmax(np.abs(RPExt), axis=0)
        MaxIdx = int(np.mean(MaxIdx))
        MaxVal = RPExt[MaxIdx,:]
        return MaxVal

    def SetCfgInf(self, stVal):
        self.stCfgInf = stVal

    def SetInitFailed(self, Val):
        self.InitFailed = Val

    def ParseCfgFile(self, stFile):
        if len(stFile) > 1:
            File = open(stFile, "r", encoding="utf-8", errors="ignore")
            
            lCmd = list()
            # Configure FMCW parameters
            lCmd.append((r"PageCalCfg_SetStrtFreq\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_CalCfg_RadStrtFreq.setText", "Func"))
            lCmd.append((r"PageCalCfg_SetStopFreq\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_CalCfg_RadStopFreq.setText", "Func"))
            lCmd.append((r"PageCalCfg_SetDuration\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_CalCfg_RadDur.setText", "Func"))
            # # Set Parameters for Number of Parameters for Cal measurement page
            lCmd.append((r"PageCalMeas_SetNrFrms\((?P<Arg>([0-9]+))\)", "self.Edit_Cal_NrFrms.setText", "Func"))
            lCmd.append((r"PageCalMeas_SetRMin\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cal_RMin.setText", "Func"))
            lCmd.append((r"PageCalMeas_SetRMax\((?P<Arg>([0-9]+[.]{0,1}[0-9]*))\)", "self.Edit_Cal_RMax.setText", "Func"))
            lCmd.append((r"PageCalMeas_SetTxCfg\('(?P<Arg>([0-9a-zA-Z\(\);]+))'\)", "self.Edit_Cal_Cfg.setText", "Func"))
            # configure signal processing
            lCmd.append((r"PageCalMeas_SetFFTSiz\((?P<Val>(128|256|512|1024|2048|4096|8192|16384|32768|65536))\)", "self.SigCfg_NFFTCfg", "VarSt"))
            lCmd.append((r"PageCalMeas_SetWinType\((?P<Val>('Hanning'|'Hamming'|'Boxcar'))\)", "self.SigCfg_WinType", "VarSt"))
            lCmd.append((r"PageCalMeas_SetPltLineWidth\((?P<Val>([0-9]+[.]{0,1}[0-9]*))\)", "self.PltCfg_LineWidth", "VarSt"))         
            
            for stLine in File:
                Ret = StrConv.ConvStrToCmd(stLine, lCmd)
                if Ret[0]:
                    exec(Ret[1])    