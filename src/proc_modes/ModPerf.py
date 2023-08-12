# (c) Haderer Andreas Inras GmbH

# Import modules for radarsignal processing and control of radar system

import  src.cmd_modules.TinyRad as TinyRad

import  src.logger.Logger as Logger
import  src.cmd_modules.StrConv as StrConv


from PyQt5 import QtCore, QtGui, QtWidgets
import  pyqtgraph as pg
import  threading as threading
import  time as time
import  numpy as np
import  src.ui.proc_modes.ui_ModPerf as ui_ModPerf
from    os.path import expanduser
from    array import array
import  re
import  time

#import  h5py


class ModPerf(QtWidgets.QMainWindow, ui_ModPerf.Ui_ModPerf):


    def __init__(self, patre):
        super(ModPerf, self).__init__()
        self.patre = patre
        self.setupUi(self)

        self.Button_Meas_Est.clicked.connect(self.Button_Meas_Est_Clicked)

        #--------------------------------------------------------------------------
        # Input Section 
        #--------------------------------------------------------------------------
        self.PtVCO_dBm = 8
        self.Gat_dB = 0
        self.Lt_dB = 1
        self.Gt_dB = 12
        self.Gr_dB = 12
        self.Lr_dB = 1
        self.Gar_dB = 0
        self.Fr_dB = 0
        self.Gm_dB = 18
        self.Fm_dB = 13.5
        self.Zm = 50
        self.fs = 1e6
        self.k = 1.38e-23
        self.T0 = 300.15

        
    def Button_Meas_Est_Clicked(self):

        print('Estimate')

        c0 = 2.99792458e8
        # Read Configuration parameters

        fStrt = StrConv.ToFloat(self.Edit_Cfg_RadStrtFreq.text())*1e6
        fStop = StrConv.ToFloat(self.Edit_Cfg_RadStopFreq.text())*1e6

        fc = (fStrt + fStop)/2
        B = (fStop - fStrt)

        print("fc: ", fc)
        print("Bandwidth: ", B)

        Samples = round(StrConv.ToFloat(self.Edit_Cfg_RadSamples.text()))
        Tp = StrConv.ToFloat(self.Edit_Cfg_RadPerd.text())*1e-6


        N = Samples
        T = Samples/self.fs
        Np = round(StrConv.ToFloat(self.Edit_Cfg_RadNp.text()))

        kf = B/T
        NFFT = 2**16

        R = StrConv.ToFloat(self.Edit_Meas_RTar.text())
        Rcs_dB = StrConv.ToFloat(self.Edit_Meas_RcsTar.text())
        RMin = StrConv.ToFloat(self.Edit_Meas_RMin.text())


        Pfa = StrConv.ToFloat(self.Edit_Cfg_FalseAlarmRate.text())*1e-6


        #--------------------------------------------------------------------------
        # Convert and calculate performance parameters
        #--------------------------------------------------------------------------
        PtVCO = 10**(self.PtVCO_dBm/10)*1e-3
        Gat = 10**(self.Gat_dB/10)
        Lt = 10**(self.Lt_dB/10)
        Gt = 10**(self.Gt_dB/10)
        Gr = 10**(self.Gr_dB/10)
        Lr = 10**(self.Lr_dB/10)
        Gar = 10**(self.Gar_dB/10)
        Fr = 10**(self.Fr_dB/10)
        Gm = 10**(self.Gm_dB/10)
        Fm = 10**(self.Fm_dB/10)
        Rcs = 10**(Rcs_dB/10) 
        Lambdac = c0/fc
        Ts = 1/self.fs

        dThres = np.sqrt(-np.log(Pfa))

        Pt = PtVCO*Gat/Lt
        Gi = Gar*Gm/Lr
        Fi = Lr + (Fr - 1)*Lr + (Fm - 1)*Lr/Gar
        uNIF = np.sqrt(self.Zm*self.k*self.T0*Gi*Fi)
        SigmaIn = uNIF*np.sqrt(self.fs)

        if self.Edit_Cfg_RangeWinType.text() == 'Hanning':
            Win = np.hanning(N)
            self.Edit_Cfg_RangeWinType.setText('Hanning')
        else:
            if self.Edit_Cfg_RangeWinType.text() == 'Hamming':
                Win = np.hamming(N)
                self.Edit_Cfg_RangeWinType.setText('Hamming')
            else:
                Win = np.ones(N) 
                self.Edit_Cfg_RangeWinType.setText('Boxcar')
        ScaWin = np.sum(Win)
        ScaWinNoise = np.sum(Win**2)

        if self.Edit_Cfg_VelWinType.text() == 'Hanning':
            WinVel = np.hanning(Np)
            self.Edit_Cfg_VelWinType.setText('Hanning')
        else:
            if self.Edit_Cfg_VelWinType.text() == 'Hamming':
                WinVel = np.hamming(Np)
                self.Edit_Cfg_VelWinType.setText('Hamming')
            else:
                WinVel = np.ones(Np) 
                self.Edit_Cfg_VelWinType.setText('Boxcar')
        ScaWinVel = np.sum(WinVel)
        ScaWinVelNoise = np.sum(WinVel**2)

        if self.Edit_Cfg_AngWinType.text() == 'Hanning':
            WinAng = np.hanning(4)
            self.Edit_Cfg_AngWinType.setText('Hanning')
        else:
            if self.Edit_Cfg_AngWinType.text() == 'Hamming':
                WinAng = np.hamming(4)
                self.Edit_Cfg_AngWinType.setText('Hamming')
            else:
                WinAng = np.ones(4) 
                self.Edit_Cfg_AngWinType.setText('Boxcar')
        ScaWinAng = np.sum(WinAng)
        ScaWinAngNoise = np.sum(WinAng**2)

        Freq = np.linspace(0,int(NFFT-1),int(NFFT))/NFFT*self.fs
        Freq = Freq[0:int(NFFT/2)]
        n = np.linspace(0,int(N-1),int(N))
        #Freq = [0:NFFT./2-1].'./NFFT.*fs;
        vRange = Freq*c0/(2*kf)  
        RMinIdx = np.argmin(abs(vRange - RMin))
        vR = vRange[RMinIdx:]

        tau = 2*R/c0
        Sigma = SigmaIn
        if self.ChkBox_Cfg_DBF.checkState():
            Sigma = Sigma*np.sqrt(ScaWinAngNoise/ScaWinAng**2)
                
        if self.ChkBox_Cfg_RangeDoppler.checkState():
            Sigma = Sigma*np.sqrt(ScaWinVelNoise/ScaWinVel**2)

        Noise = Sigma*np.random.randn(N)
        Amp = np.sqrt(Pt*2*Gi*self.Zm*Gt*Gr*Lambdac**2*Rcs/((4*np.pi)**3*vR**4))
        Amp_dB = 20*np.log10(Amp)
        sIF = np.sqrt(Pt*2*Gi*self.Zm*Gt*Gr*Lambdac**2*Rcs/((4*np.pi)**3*R**4))*np.cos(2*np.pi*fc*tau+2*np.pi*kf*tau*Ts*n - np.pi*kf*tau**2)

        #XNoise = abs(fft(Noise.*Win,NFFT)).^2./ScaWinNoise;
        RP = 2*np.abs(np.fft.fft((sIF + Noise)*Win,int(NFFT),0))/np.sum(Win)
        RP = RP[0:int(NFFT/2)]
        #Psd = Psd + RP(1:NFFT./2,:).^2;  
        #PsdNoise = PsdNoise + XNoise(1:NFFT./2);

        Var_k = 4*SigmaIn**2*ScaWinNoise/ScaWin**2

        if self.ChkBox_Cfg_DBF.checkState():
            Var_k = Var_k*ScaWinAngNoise/ScaWinAng**2
                
        if self.ChkBox_Cfg_RangeDoppler.checkState():
            Var_k = Var_k*ScaWinVelNoise/ScaWinVel**2

        Sigma_k = np.sqrt(Var_k)
        NoiseFloor = Sigma_k*np.sqrt(np.pi)/2

        NoiseFloor_dB = 20*np.log10(NoiseFloor)
        ThresHold_dB = NoiseFloor_dB + 20*np.log10(dThres); 

        self.Plot_Meas_Tim.clear()
        PenRp = pg.mkPen(color='k', width=1.0)
        PenNoise = pg.mkPen(color='r', width = 2.0)
        PenAmp = pg.mkPen(color='b', width = 2.0)
        PenThres = pg.mkPen(color='r', width = 2.0, style=QtCore.Qt.DashLine)

        self.Plot_Meas_Tim.plot(vRange, 20*np.log10(RP), pen = PenRp)          
        self.Plot_Meas_Tim.plot(vR, NoiseFloor_dB*np.ones(vR.shape), pen = PenNoise) 
        self.Plot_Meas_Tim.plot(vR, ThresHold_dB*np.ones(vR.shape), pen = PenThres) 
        self.Plot_Meas_Tim.plot(vR, Amp_dB, pen = PenAmp)          
