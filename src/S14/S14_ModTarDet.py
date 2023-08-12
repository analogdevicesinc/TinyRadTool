# (c) Haderer Andreas Basic RF Framework

import  re
import  time
from    numpy import *

class S14_ModTarDet():

    def __init__(self, Rad, dIniBrdCfg):
        self.dIniBrdCfg     =   dIniBrdCfg
        self.Rad            =   Rad
        
    def IniBrdModTarDet(self):

        self.Rad.Brd.BrdRst()
        self.Rad.Brd.BrdGetUID()
        self.Rad.Brd.BrdPwrEna()
        #--------------------------------------------------------------------------
        # Configure Receiver
        #--------------------------------------------------------------------------
        self.Rad.RfRxEna();
        
        # Process stCfg string
        if "stCfg" in self.dIniBrdCfg:
        # Search for regular expression TX1(100);
            RegExp          =               re.compile(r"(TX(?P<TxAnt>[0-2]){1,1}(\({1,1}(?P<TxAmp>\d+)\){1,1}){1,1};{1,1})")
            Match           =               RegExp.search(self.dIniBrdCfg["stCfg"])
            if Match:
                TxSel       =               float(Match.group("TxAnt"))
                TxAmp       =               float(Match.group("TxAmp"))
                if TxAmp < 0:
                    TxAmp   = 0
                if TxAmp > 100:
                    TxAmp   = 100
            else:
                TxSel           =               1
                TxAmp           =               100
        else:
            print('Sel')
            TxSel   =       1
            TxAmp   =       100

        print("BrdCfg: ", self.dIniBrdCfg["Np"])
        #--------------------------------------------------------------------------
        # Configure Transmitter (Antenna 0 - 4, Pwr 0 - 31)
        #--------------------------------------------------------------------------
        self.Rad.RfTxEna(TxSel, TxAmp)

        dCfg        =   {
                            "fStrt"     :   self.dIniBrdCfg["FreqStrt"],
                            "fStop"     :   self.dIniBrdCfg["FreqStop"],
                            "TRampUp"   :   self.dIniBrdCfg["TimUp"],
                            "StrtIdx"   :   0,
                            "StopIdx"   :   1
                        }            

        self.Rad.Brd.Dsp_SetTestDat(0)

        self.Rad.RfMeas('Adi', dCfg);

        for Idx in range(0,4):
            try:
                Data            =   self.RfBrd.GetDataEve()
            except OSError:
                pass
            except AttributeError:
                pass
            except ValueError:
                pass
            except:
                pass

        dCfg        =   {
                            "fStrt"     :   self.dIniBrdCfg["FreqStrt"],
                            "fStop"     :   self.dIniBrdCfg["FreqStop"],
                            "TRampUp"   :   self.dIniBrdCfg["TimUp"],
                            "StrtIdx"   :   0,
                            "StopIdx"   :   self.dIniBrdCfg["Np"]
                        }            

        self.Rad.Brd.Dsp_SetTestDat(0)
        self.Rad.RfMeas('Adi', dCfg);

        #--------------------------------------------------------------------------
        # Configure Transmitter (Antenna 0 - 4, Pwr 0 - 31)
        #--------------------------------------------------------------------------
        self.Rad.RfTxEna(TxSel, TxAmp)

        print("dCfg:", dCfg)

    def OpenBrdMod0(self):
        self.Rad.BrdSampStrt()

    def CloseBrdMod0(self):
        print("CloseBrdMod")
        self.Rad.BrdSampStp()

    def GetDataEve(self):
        Data            =   self.Rad.BrdGetData()
        return Data
