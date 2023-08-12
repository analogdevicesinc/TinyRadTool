# ADF24Tx2RX8 -- Class for 24-GHz Radar
#
# Copyright (C) 2015-11 Inras GmbH Haderer Andreas
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import  src.cmd_modules.DevAdf5904  as DevAdf5904
import  src.cmd_modules.DevAdf5901  as DevAdf5901
import  src.cmd_modules.DevAdf4159  as DevAdf4159
import  src.cmd_modules.UsbADI as UsbADI
from    numpy import *

class TinyRad(UsbADI.UsbADI):

    def __init__(self):
        # Call Constructor of DemoRad Class
        super().__init__()
        self.DebugInf                   =   0
        #>  Object of first receiver (DevAdf5904 class object)
        self.Adf_Rx                =   []
        #>  Object of transmitter (DevAdf5901 class object)
        self.Adf_Tx                 =   []
        #>  Object of transmitter Pll (DevAdf4159 class object)
        self.Adf_Pll                    =   []

        self.Rf_USpiCfg_Pll_Chn         =   2
        self.Rf_USpiCfg_Tx_Chn          =   1
        self.Rf_USpiCfg_Rx_Chn          =   0

        self.Rf_fStrt                   =   24e9
        self.Rf_fStop                   =   24.256e9
        self.Rf_TRampUp                 =   256e-6
        self.Rf_TRampDo                 =   256e-6
        self.Rf_fs                      =   1.0e6

        self.Rf_VcoDiv                  =   2

        self.stRfVers                   =   '1.1.0'
        self.Rad_N = 256
        self.Rad_NrChn = 4

        self.Seq = []
        self.FrmMeasSiz = 1

        # Initialize Receiver

        dUSpiCfg                        =   dict()
        dUSpiCfg                        =   {   "Mask"          : 7,
                                                "Chn"           : self.Rf_USpiCfg_Rx_Chn
                                            }
        self.Adf_Rx = DevAdf5904.DevAdf5904(self, dUSpiCfg)
        dUSpiCfg                        =   dict()
        dUSpiCfg                        =   {   "Mask"          : 7,
                                                "Chn"           : self.Rf_USpiCfg_Tx_Chn
                                            }

        self.Adf_Tx                     =   DevAdf5901.DevAdf5901(self, dUSpiCfg)

        dUSpiCfg                        =   dict()
        dUSpiCfg                        =   {   "Mask"          : 7,
                                                "Chn"           : self.Rf_USpiCfg_Pll_Chn
                                            }
        self.Adf_Pll                    =   DevAdf4159.DevAdf4159(self, dUSpiCfg)




    # DOXYGEN ------------------------------------------------------
    #> @brief Get Version information of Adf24Tx2Rx8 class
    #>
    #> Get version of class
    #>      - Version string is returned as string
    #>
    #> @return  Returns the version string of the class (e.g. 0.5.0)
    def     RfGetVers(self):
        return self.stVers

    # DOXYGEN ------------------------------------------------------
    #> @brief Get attribute of class object
    #>
    #> Reads back different attributs of the object
    #>
    #> @param[in]   stSel: String to select attribute
    #>
    #> @return      Val: value of the attribute (optional); can be a string or a number
    #>
    #> Supported parameters
    #>      -   <span style="color: #ff9900;"> 'TxPosn': </span> Array containing positions of Tx antennas
    #>      -   <span style="color: #ff9900;"> 'RxPosn': </span> Array containing positions of Rx antennas
    #>      -   <span style="color: #ff9900;"> 'ChnDelay': </span> Channel delay of receive channels
    def RfGet(self, *varargin):
        if len(varargin) > 0:
            stVal       = varargin[0]
            if stVal == 'TxPosn':
                Ret     =   zeros(2)
                Ret[0]  =   -18.654e-3
                Ret[1]  =   0.0e-3
                return Ret
            elif stVal == 'RxPosn':
                Ret     =   arange(4)
                Ret     =   Ret*6.2170e-3 + 32.014e-3
                return Ret
            elif stVal == 'B':
                Ret     =   (self.Rf_fStop - self.Rf_fStrt)
                return  Ret
            elif stVal == 'kf':
                Ret     =   (self.Rf_fStop - self.Rf_fStrt)/self.Rf_TRampUp
                return  Ret
            elif stVal == 'kfUp':
                Ret     =   (self.Rf_fStop - self.Rf_fStrt)/self.Rf_TRampUp
                return  Ret
            elif stVal == 'kfDo':
                Ret     =   (self.Rf_fStop - self.Rf_fStrt)/self.Rf_TRampDo
                return  Ret
            elif stVal == 'fc':
                Ret     =   (self.Rf_fStop + self.Rf_fStrt)/2
                return  Ret
            elif stVal == 'fs':
                Ret     =   self.Rf_fs
                return  Ret
        return -1

    # DOXYGEN ------------------------------------------------------
    #> @brief Enable all receive channels
    #>
    #> Enables all receive channels of frontend
    #>
    #>
    #> @note: This command calls the Adf4904 objects Adf_Rx
    #>        In the default configuration all Rx channels are enabled. The configuration of the objects can be changed before
    #>        calling the RxEna command.
    #>
    #> @code
    #> CfgRx1.Rx1      =   0;
    #> Brd.Adf_Rx1.SetCfg(CfgRx1);
    #> CfgRx2.All      =   0;
    #> Brd.Adf_Rx2.SetCfg(CfgRx2);
    #> @endcode
    #>  In the above example Chn1 of receiver 1 is disabled and all channels of receiver Rx2 are disabled
    def     RfRxEna(self):
        print("RfRxEna")
        self.RfAdf5904Ini(1);

    # DOXYGEN ------------------------------------------------------
    #> @brief Configure receivers
    #>
    #> Configures selected receivers
    #>
    #> @param[in]   Mask: select receiver: 1 receiver 1; 2 receiver 2
    #>
    def     RfAdf5904Ini(self, Mask):
        if Mask == 1:
            self.Adf_Rx.Ini();
            if self.DebugInf > 10:
                print('Rf Initialize Rx1 (ADF5904)')
        else:
            pass

    # DOXYGEN -------------------------------------------------
    #> @brief Displays status of frontend in Matlab command window
    #>
    #> Display status of frontend in Matlab command window
    def     BrdDispSts(self):
        self.BrdDispInf()

    def     BrdGetData(self):
        return self.Dsp_GetChirp(self.StrtIdx,self.StopIdx)

    def     RfGetChipSts(self):
        lChip   =   list()
        Val     =   self.Fpga_GetRfChipSts(1)
        print(Val)
        if Val[0] == True:
            Val     =   Val[1]
            if len(Val) > 2:
                if Val[0] == 202:
                    lChip.append(('Adf4159 PLL', 'No chip information available'))
                    lChip.append(('Adf5901 TX', 'No chip information available'))
                    lChip.append(('Adf5904 RX', 'No chip information available'))
        return lChip

    # DOXYGEN ------------------------------------------------------
    #> @brief Set attribute of class object
    #>
    #> Sets different attributes of the class object
    #>
    #> @param[in]     stSel: String to select attribute
    #>
    #> @param[in]     Val: value of the attribute (optional); can be a string or a number
    #>
    #> Supported parameters
    #>              - Currently no set parameter supported
    def RfSet(self, *varargin):
        if len(varargin) > 0:
            stVal   =   varargin[0]


    # DOXYGEN ------------------------------------------------------
    #> @brief Enable transmitter
    #>
    #> Configures TX device
    #>
    #> @param[in]   TxChn
    #>                  - 0: off
    #>                  - 1: Transmitter 1 on
    #>                  - 2: Transmitter 2 on
    #> @param[in]   TxPwr: Power register setting 0 - 256; only 0 to 100 has effect
    #>
    #>
    def     RfTxEna(self, TxChn, TxPwr):
        TxChn       =   (TxChn % 3)
        TxPwr       =   (TxPwr % 2**8)
        if self.DebugInf > 10:
            stOut   =   "Rf Initialize Tx (ADF5901): Chn: " + str(TxChn) + " | Pwr: " + str(TxPwr)
            print(stOut)
        dCfg            =   dict()
        dCfg["TxChn"]   =   TxChn
        dCfg["TxPwr"]   =   TxPwr


        self.Adf_Tx.SetCfg(dCfg)
        self.Adf_Tx.Ini()


    def RfMeas(self, dCfg):  
        dAdarCfg = dict()        
        dAdarCfg['X'] = 3
        dAdarCfg['R'] = 5
        dAdarCfg['N'] = 76
        dAdarCfg['M'] = 100
        RetVal  =   self.Dsp_CfgAdarPll(dAdarCfg)
        if RetVal[0]   == 1:
            print('ADAR PLL Locked')
        else:
            print('ADAR PLL not locked')
        

        #Check configuration
        if dCfg['Perd'] <= dCfg['N']*1e-6 + 22e-6:
            print('Period is to short: increase period > TRampUp + 20us')
            dCfg['Perd'] = dCfg['N']*1e-6 + 22e-6
        
        if (4*dCfg['N']*dCfg['FrmMeasSiz']*dCfg['CycSiz']*len(dCfg['Seq'])) > int('0x60000',16):
            print('Required memory greater than DSP buffer size: decrease CycSiz, N, FrmMeasSiz')
        
        
        if dCfg['FrmMeasSiz'] > dCfg['FrmSiz']:
            print('Number of frames to record > number of frames')

        self.RfAdf4159Ini(dCfg)
        self.Dsp_CfgMeas(dCfg)
        self.Dsp_StrtMeas(dCfg)            
        
        
    def BrdRst(self):
        DspCmd = zeros(2, dtype='uint32')
        Cod = int('0x9031',16)
        DspCmd[0] = 1
        DspCmd[1] = 0
        Ret     = self.CmdSend(0, Cod, DspCmd)
        Ret     = self.CmdRecv() 
        return Ret
        
    def Dsp_CfgMeas(self, dCfg):
            
        self.Seq         =   dCfg['Seq']
        self.FrmMeasSiz  =   dCfg['FrmMeasSiz']
        self.Dsp_CfgMeasSiz(dCfg)
        Ret     =   self.Dsp_CfgMeasSeq(dCfg)
        return Ret
        
        
    def Dsp_CfgAdarPll(self, dCfg):
        DspCmd = zeros(6, dtype='uint32')
        Cod = int('0x9031',16)
        DspCmd[0] = 1
        DspCmd[1] = 12
        DspCmd[2] = dCfg['X']
        DspCmd[3] = dCfg['R']
        DspCmd[4] = dCfg['N']
        DspCmd[5] = dCfg['M']
        Ret     = self.CmdSend(0, Cod, DspCmd)
        Ret     = self.CmdRecv()
        return Ret
            
    def Dsp_SetAdarReg(self, Regs):
        DspCmd =   zeros(2 + len(Regs), dtype='uint32')
        Regs = Regs.flatten() 
        Cod = int('0x9031',16)
        DspCmd[0]  = 1
        DspCmd[1]  = 10
        DspCmd[2:] = Regs
        Ret     = self.CmdSend(0, Cod, DspCmd)
        Ret     = self.CmdRecv()         
        return Ret
        
    def Dsp_CfgMeasSeq(self, dCfg):

        Seq = dCfg['Seq']
        # Rotate by one because state refers to next measurement state
        #Seq = [Seq[0], [Seq[1:]]]
        print("Seq", Seq)
        #Seq = concatenate(Seq)
        print("Seq array: ", Seq)
        DspCmd = zeros(2 + len(Seq), dtype='uint32')
        Cod = int('0x9031',16)
        DspCmd[0] = 1
        DspCmd[1] = 3
        DspCmd[2:] = Seq
        Ret     = self.CmdSend(0, Cod, DspCmd)
        Ret     = self.CmdRecv()
        return Ret
        
    def Dsp_CfgMeasSiz(self, dCfg):
                        
        DspCmd = zeros(6, dtype='uint32')
        Cod = int('0x9031',16)
        DspCmd[0] = 1
        DspCmd[1] = 2
        DspCmd[2] = len(dCfg['Seq'])
        DspCmd[3] = dCfg['FrmSiz']
        DspCmd[4] = dCfg['FrmMeasSiz']
        DspCmd[5] = dCfg['CycSiz']
        Ret     = self.CmdSend(0, Cod, DspCmd)
        Ret     = self.CmdRecv()
        return Ret
            
            
    def Dsp_StrtMeas(self, dCfg):
            
        self.Rad_N = dCfg['N']
        DspCmd = zeros(4, dtype='uint32')
        Cod = int('0x9031',16)
        DspCmd[0] = 1
        DspCmd[1] = 1
        DspCmd[2] = round(dCfg['Perd']/10e-9)
        DspCmd[3] = dCfg['N']
        Ret     = self.CmdSend(0, Cod, DspCmd)
        Ret     = self.CmdRecv()
        return Ret
  
    def Dsp_GetDmaErr(self):
        DspCmd = zeros(4, dtype='uint32')
        Cod = int('0x9033',16)
        DspCmd[0] = 1
        DspCmd[1] = 1
        Ret     = self.CmdSend(0, Cod, DspCmd)
        Ret     = self.CmdRecv()
        return Ret
           
    def Dsp_GetDat(self, Len):
        DspCmd = zeros(4, dtype='uint32')
        Cod = int('0x9032',16)
        DspCmd[0] = 1
        DspCmd[1] = 1
        DspCmd[2] = Len                                        #Cfg.N*4*numel(Cfg.Seq)*Cfg.FrmMeasSiz;
        self.usbLen   = Len;
        self.usbState = 1; # start cmd send
        self.CmdSend(0, Cod, DspCmd);
        self.usbState = 2; # start get data
        UsbData = self.ConGetUsbData(Len * 2);
        Data    = reshape(UsbData, (int(Len/4), 4));

        self.usbState = 3;  # cmd Recv
        self.CmdRecv();

        self.usbState = 0; # do nothing
        return Data
       
    def BrdGetData(self):
        Len = 4*self.Rad_N*len(self.Seq)*self.FrmMeasSiz
        Dat = self.Dsp_GetDat(Len)
        return Dat
    
    # DOXYGEN ------------------------------------------------------
    #> @brief Initialize PLL with selected configuration
    #>
    #> Configures PLL
    #>
    #> @param[in]   Cfg: structure with PLL configuration
    #>      -   <span style="color: #ff9900;"> 'fStrt': </span> Start frequency in Hz
    #>      -   <span style="color: #ff9900;"> 'fStrt': </span> Stop frequency in Hz
    #>      -   <span style="color: #ff9900;"> 'TRampUp': </span> Upchirp duration in s
    #>
    #> %> @note Function is obsolete in class version >= 1.0.0: use function Adf_Pll.SetCfg() and Adf_Pll.Ini()
    def     RfAdf4159Ini(self, Cfg):
        self.Adf_Pll.SetCfg(Cfg);
        self.Adf_Pll.Ini();

    # DOXYGEN ------------------------------------------------------
    #> @brief <span style="color: #ff0000;"> LowLevel: </span> Generate hanning window
    #>
    #> This function returns a hanning window.
    #>
    #>  @param[in]   M: window size
    #>
    #>  @param[In]   N (optional): Number of copies in second dimension
    def     hanning(self, M, *varargin):
        #m   =   [-(M-1)/2: (M-1)/2].';
        m       =   linspace(-(M-1)/2,(M-1)/2,M)  
        Win     =   0.5 + 0.5*cos(2*pi*m/M)
        if len(varargin) > 0:
            N       =   varargin[0]
            Win     =   broadcast_to(Win,(N,M)).T
        return Win



    def     RefCornerCube(self, fc, aCorner, R, Freq):        
        
        c0 = 2.99792458e8

        PtdBm =  7
        GtdB = 12-1
        GrdB = 12-1
        GcdB = 17  
            
        C1 = 10e-9
        R1 = 2.86e3
        
        FreqC = 1/(2*pi*C1*R1)            
        HHighPass = (1j*Freq/FreqC)/(1 + 1j*Freq/FreqC)
        
        #--------------------------------------------------------------------------
        # Calculate Values
        #--------------------------------------------------------------------------
        Pt = 10**(PtdBm/10)*1e-3
        Gt = 10**(GtdB/10)
        Gr = 10**(GrdB/10)
        Lambdac = c0/fc
        RCS = 4*pi*aCorner**4/(3*Lambdac**2)
        Pr = Pt/(4*pi*R**4)*Gt/(4*pi)*Gr/(4*pi)*RCS*Lambdac**2
        PrdBm = 10*log10(Pr/1e-3)
        PIfdBm = PrdBm + GcdB
        UIf = sqrt(50*10**(PIfdBm/10)*1e-3)*sqrt(2)
        UIfdB = 20*log10(UIf) + 20*log10(abs(HHighPass))  
        return UIfdB     

    def     RefRcs(self, fc, RcsdB, R, Freq):        
        
        c0 = 2.99792458e8

        PtdBm =  7
        GtdB = 12
        GrdB = 12
        GcdB = 17 
            
        C1 = 10e-9
        R1 = 2.86e3
        
        FreqC = 1/(2*pi*C1*R1)            
        HHighPass = (1j*Freq/FreqC)/(1 + 1j*Freq/FreqC)
        
        RZero = argwhere(R < 0.01);
        R[RZero] = 1e-3;
        Freq[RZero] = 1e-3;
        
        #--------------------------------------------------------------------------
        # Calculate Values
        #--------------------------------------------------------------------------
        Pt = 10**(PtdBm/10)*1e-3
        Gt = 10**(GtdB/10)
        Gr = 10**(GrdB/10)
        Lambdac = c0/fc

        RCS = 10**(RcsdB/10)

        Pr = Pt/(4*pi*R**4)*Gt/(4*pi)*Gr/(4*pi)*RCS*Lambdac**2
        PrdBm = 10*log10(Pr/1e-3)
        PIfdBm = PrdBm + GcdB
        UIf = sqrt(50*10**(PIfdBm/10)*1e-3)*sqrt(2)
        UIfdB = 20*log10(UIf) + 20*log10(abs(HHighPass)) 
        return UIfdB              

    def     UIfToRcs(self, UIf, fc, R, Freq):        
        

        c0 = 2.99792458e8

        PtdBm =  7
        GtdB = 12-1
        GrdB = 12-1
        GcdB = 17
        
        Pt = 10**(PtdBm/10)*1e-3
        Gt = 10**(GtdB/10)
        Gr = 10**(GrdB/10)
        Gc = 10**(GcdB/10)

        Lambdac = c0/fc

        C1 = 10e-9
        R1 = 2.86e3
                
        Siz = UIf.shape

        FreqC = 1/(2*pi*C1*R1)          
        HHighPass = (1j*Freq/FreqC)/(1 + 1j*Freq/FreqC)
        
        High = broadcast_to(abs(HHighPass),(Siz[1], Siz[0])).T
        Range = broadcast_to(R,(Siz[1], Siz[0])).T

        UIn = UIf/High
        PIn = (UIn**2)/(2*50)
        Pr = PIn/Gc

        #--------------------------------------------------------------------------
        # Calculate Values
        #--------------------------------------------------------------------------
        RCS = ((4*pi*Range**4)/Pt)*((4*pi)/Gt)*((4*pi)/Gr)*(Pr/(Lambdac**2))
        return RCS

      
        