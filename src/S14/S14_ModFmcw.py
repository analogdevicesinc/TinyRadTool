# (c) Haderer Andreas Basic RF Framework

import  re
import  time
from    numpy import *

class S14_ModFmcw():
    def __init__(self, Rad, dIniBrdCfg):
        self.dIniBrdCfg = dIniBrdCfg
        self.Rad = Rad

    def IniBrdModFmcw(self):
        self.Rad.BrdRst()

        #--------------------------------------------------------------------------
        # Configure Receiver
        #--------------------------------------------------------------------------
        self.Rad.RfRxEna();
        
        # Process stCfg string
        if "stCfg" in self.dIniBrdCfg:
        # Search for regular expression TX1(100);
            RegExp = re.compile(r"(TX(?P<TxAnt>[0-2]){1,1}(\({1,1}(?P<TxAmp>\d+)\){1,1}){1,1};{1,1})")
            Match = RegExp.search(self.dIniBrdCfg["stCfg"])
            if Match:
                TxSel = float(Match.group("TxAnt"))
                TxAmp = float(Match.group("TxAmp"))
                if TxAmp < 0:
                    TxAmp = 0
                if TxAmp > 100:
                    TxAmp = 100
            else:
                TxSel = 1
                TxAmp = 100
        else:
            print('Sel')
            TxSel = 1
            TxAmp = 100


        #--------------------------------------------------------------------------
        # Configure Transmitter (Antenna 0 - 4, Pwr 0 - 31)
        #--------------------------------------------------------------------------
        self.Rad.RfTxEna(TxSel, TxAmp)

        dCfg = {
                            "fStrt"     :   self.dIniBrdCfg["FreqStrt"],
                            "fStop"     :   self.dIniBrdCfg["FreqStop"],
                            "TRampUp"   :   self.dIniBrdCfg["TimUp"],
                            "N" : int(self.dIniBrdCfg["N"]), 
                            "Perd" : self.dIniBrdCfg["Tp"],
                            "CycSiz" : 4, 
                            "Seq" : [1],
                            "FrmSiz" : 2, 
                            "FrmMeasSiz" : 1                            
                        }            
                        
        self.Rad.RfMeas(dCfg);

    def GetDataEve(self):
        Data = self.Rad.BrdGetData()
        return Data
    def CloseBrdMod0(self):
        print("CloseBrdMod")
        self.Rad.BrdSampStp()
