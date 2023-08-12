
import  sys
import  numpy
from    numpy import *

from    pyqtgraph.Qt import QtGui, QtCore
import  pyqtgraph as pg

class Computation():

    ## Constructor, stConnection must be a weakreference to the Connection class
    def __init__(self, stConnection=0):
        self.isSupported   = False;
        self.nrChn         = 1;
        self.dataType      = 0;
        self.dtypeLen      = 4;
        
        self.rpMult        = 0;
        self.rpMin         = 0;
        self.rpMax         = 0;
        self.rpLen         = 0;
        self.rpSort        = 0;
        
        self.rdLen         = 0; 
        self.rdVelMin      = 0;
        self.rdVelMax      = 0;
                               
        self.Raw           = 'Raw';
        self.Range         = 'Range';
        self.RP            = 'RangeProfile';
        self.Vel           = 'Vel';
        self.RD            = 'RangeDoppler';
        self.Ang           = 'Ang';
        self.Thres         = 'Thres';
        self.DL            = 'DetectionList';
        self.Track         = 'Track';
        self.TT            = 'TargetTracker';
        
        self.isSet_FuSca   = False;
        self.isSet_fStrt   = False;
        self.isSet_fStop   = False;
        self.isSet_TRampUp = False;
        self.isSet_fs      = False;
        self.isSet_CalRe   = False;
        self.isSet_CalIm   = False;
        self.isSet_Tp      = False;
        self.isSet_Np      = False;
        
        self.viewX         = [];
        self.viewY         = [];
    
        if (stConnection == 0):
            sys.exit("No Connection class given");
            
        self.connection    = stConnection;
        
    def Plot(self, Data):
        if (self.dataType <= 1):
            for idxChn in range(0, self.nrChn):
                self.viewCurves[idxChn].setData(self.viewX[0:], Data[1:, idxChn]);
        
        elif (self.dataType == 2):
            if numpy.count_nonzero(Data) == size(Data):
                for idxChn in range(0, self.nrChn):
                    self.viewCurves[idxChn].setData(self.viewX[0:], 20*log10(abs(Data[0,:,idxChn,0])));

        elif (self.dataType == 3):
            self.viewImg.setImage(20*numpy.log10(numpy.abs(Data[:,:,0,0]))+0.5e-6, pos=[self.viewY[0], self.viewX[0]], scale=[(self.viewY[-1]-self.viewY[0])/len(self.viewY), (self.viewX[-1]-self.viewX[0])/len(self.viewX)]);
            self.viewPlot.setAspectLocked(False);
            
        elif (self.dataType == 4):
            self.viewImg.clear();
            tar = [];
            for Idx in range(size(Data)):
                #print("Idx ", Data[Idx]);
                x = Data[Idx]['Range'] * math.sin(Data[Idx]['Ang']);
                y = Data[Idx]['Range'] * math.cos(Data[Idx]['Ang']);
                if (Data[Idx]['Vel'] < 0):
                    if (Data[Idx]['Vel'] < -1.):
                        tar.append({'pos': (x,y), 'data': 1, 'brush': pg.mkBrush(255,0,0,255), 'size': 10});
                    else:
                        tar.append({'pos': (x,y), 'data': 1, 'brush': pg.mkBrush(100,0,0,255), 'size': 7});
                else:
                    if (Data[Idx]['Vel'] > 1.):
                        tar.append({'pos': (x,y), 'data': 1, 'brush': pg.mkBrush(0,0,255,255), 'size': 10});
                    else:
                        tar.append({'pos': (x,y), 'data': 1, 'brush': pg.mkBrush(0,0,100,255), 'size': 7});
            
            self.viewImg.addPoints(tar); 
        
        elif (self.dataType == 5):
            print("Data");
        
        pg.QtGui.QApplication.processEvents()
       
    def CreateView(self):
        self.viewApp = QtGui.QApplication([]);
    
        if (self.dataType <= 1):
            self.viewWin = pg.GraphicsWindow("Plot");          
            self.viewWin.setBackground((255, 255, 255))
            self.viewWin.resize(1000,600)
            self.viewPlot   = self.viewWin.addPlot(title="Raw Data", col=0, row=0)
            self.viewPlot.showGrid(x=True, y=True)
            
            Pen = [];
            Pen.append(pg.mkPen(color=(  0,  95, 162), width=1));
            Pen.append(pg.mkPen(color=(253, 188,   0), width=1));
            Pen.append(pg.mkPen(color=(253,  68,   0), width=1));
            Pen.append(pg.mkPen(color=(  0,  59, 100), width=1));
            Pen.append(pg.mkPen(color=(156, 116,   0), width=1));
            Pen.append(pg.mkPen(color=(156,  42,   0), width=1));
            Pen.append(pg.mkPen(color=( 11, 152, 251), width=1));
            Pen.append(pg.mkPen(color=(  0,   5, 176), width=1));
            
            Pen.append(pg.mkPen(color=(  0,  36,  60), width=1));
            Pen.append(pg.mkPen(color=(151, 112,   0), width=1));
            Pen.append(pg.mkPen(color=(151,  41,   0), width=1));
            Pen.append(pg.mkPen(color=(  0,   0,   0), width=1));
            Pen.append(pg.mkPen(color=(140, 108,  16), width=1));
            Pen.append(pg.mkPen(color=(140,  49,  16), width=1));
            Pen.append(pg.mkPen(color=(  3,  94, 157), width=1));
            Pen.append(pg.mkPen(color=( 18,  22, 158), width=1));
            
            self.viewCurves = []
            for idxChn in range(0, self.nrChn):
                self.viewCurves.append(self.viewPlot.plot(pen=Pen[idxChn]))
                
            conn = self.connection();
            if (conn is None):
                sys.exit("Computations are not supported with this version.");    
                
            self.viewX = numpy.arange(1, conn.Get('N'));
                
        elif (self.dataType == 2): 
            self.viewWin = pg.GraphicsWindow("Plot");          
            self.viewWin.setBackground((255, 255, 255))
            self.viewWin.resize(1000,600)
            self.viewPlot = self.viewWin.addPlot(title="Range Profile", col=0, row=0)
            self.viewPlot.showGrid(x=True, y=True)
            
            Pen = [];
            Pen.append(pg.mkPen(color=(  0,  95, 162), width=1));
            Pen.append(pg.mkPen(color=(253, 188,   0), width=1));
            Pen.append(pg.mkPen(color=(253,  68,   0), width=1));
            Pen.append(pg.mkPen(color=(  0,  59, 100), width=1));
            Pen.append(pg.mkPen(color=(156, 116,   0), width=1));
            Pen.append(pg.mkPen(color=(156,  42,   0), width=1));
            Pen.append(pg.mkPen(color=( 11, 152, 251), width=1));
            Pen.append(pg.mkPen(color=(  0,   5, 176), width=1));
            
            Pen.append(pg.mkPen(color=(  0,  36,  60), width=1));
            Pen.append(pg.mkPen(color=(151, 112,   0), width=1));
            Pen.append(pg.mkPen(color=(151,  41,   0), width=1));
            Pen.append(pg.mkPen(color=(  0,   0,   0), width=1));
            Pen.append(pg.mkPen(color=(140, 108,  16), width=1));
            Pen.append(pg.mkPen(color=(140,  49,  16), width=1));
            Pen.append(pg.mkPen(color=(  3,  94, 157), width=1));
            Pen.append(pg.mkPen(color=( 18,  22, 158), width=1));
            
            self.viewCurves = []
            for idxChn in range(0, self.nrChn):
                self.viewCurves.append(self.viewPlot.plot(pen=Pen[idxChn]))
                
            conn = self.connection();
            if (conn is None):
                sys.exit("Computations are not supported with this version.");    
                
            c0         = 3e8;
            kf         = ( conn.GetFileParam('fStop') - conn.GetFileParam('fStrt') ) / conn.GetFileParam('TRampUp');
            fs         = conn.GetFileParam('fs');
            NFFT       = conn.GetFileParam('Range_NFFT');
            
            self.viewX = numpy.arange(NFFT//2+1)/NFFT*fs*c0/(2*kf);
    
        elif (self.dataType == 3):
            self.viewPlot = pg.PlotItem();
            self.viewPlot.setLabel('left', 'R', units='m')
            self.viewPlot.setLabel('bottom', 'u')
            
            self.viewImg     =   pg.ImageView(view = self.viewPlot, name='Adf24Tx2Rx8_AN24_39')
            self.viewImg.show()
            self.viewImg.ui.roiBtn.hide()
            self.viewImg.ui.menuBtn.hide()
            self.viewImg.ui.histogram.hide()
            self.viewImg.getHistogramWidget().gradient.loadPreset('bipolar')
        
            conn = self.connection();
            if (conn is None):
                sys.exit("Computations are not supported with this version.");  
                
            ## Configure Range Doppler Visualization
            fs         = conn.GetFileParam('fs');
            NFFT       = conn.GetFileParam('Range_NFFT');
            c0         = 3e8;
            kf         = ( conn.GetFileParam('fStop') - conn.GetFileParam('fStrt') ) / conn.GetFileParam('TRampUp');
            self.viewX = numpy.arange(NFFT//2+1)/NFFT*fs*c0/(2*kf); # vRange
            NFFTVel    = conn.GetFileParam('Vel_NFFT');
            fc         = (conn.GetFileParam('fStop') + conn.GetFileParam('fStrt'))/2
            vFreqVel   = numpy.linspace(-NFFTVel/2,NFFTVel/2-1,NFFTVel)/NFFTVel/conn.GetFileParam('Tp');
            self.viewY = vFreqVel/fc*c0/2 # vVel
    
        elif (self.dataType == 4):
            self.viewWin = QtGui.QMainWindow();
            view = pg.GraphicsLayoutWidget()
            self.viewWin.setCentralWidget(view);
            self.viewWin.show();
            self.viewWin.setWindowTitle('Adf24Tx2Rx8_AN24_34-Replay');
            self.viewPlot = view.addPlot();
            self.viewPlot.setXRange(-150, 150, padding=0);
            self.viewPlot.setYRange(0, 200, padding=0);
            
            self.viewImg = pg.ScatterPlotItem(size=10, pen=None, pxMode=True)
            self.viewPlot.addItem(self.viewImg);
        
        #elif (self.dataType == 5):
        
    def Enable(self):
        self.isSupported = True;
        
    def Disable(self):
        self.isSupported = False;
        
    def GetDataType(self):
        return self.dataType;
        
    def SetNrChn(self, nrChn):
        self.nrChn = int(nrChn);
        
    def SetDataType(self, Type, Param):
        if not self.isSupported:
            sys.exit("Computations are not supported with this version.");
        
        if (Type == 2 and len(Param) == 5):
            self.dataType = Type;
            self.rpLen    = int(Param[0]);
            self.rpMin    = Param[1];
            self.rpMax    = Param[2];
            self.rpMult   = int(Param[3]);
            self.rpSort   = int(Param[4]);
            
        elif (Type == 3 and len(Param) == 6):
            self.dataType = Type;
            self.rpLen    = int(Param[0]);
            self.rpMin    = Param[1];
            self.rpMax    = Param[2];
            self.rdLen    = int(Param[3]);
            self.rdVelMin = Param[4];
            self.rdVelMax = Param[5];
            
        elif (Type == 4 and len(Param) == 1):
            self.dataType = Type;
            self.dlLen    = int(Param[0]);
            
        elif (Type == 5 and len(Param) == 4):
            self.dataType    = Type;
            self.ttNumTar    = int(Param[0]);
            self.ttTarSize   = int(Param[1]);
            self.ttNumTracks = int(Param[2]);
            self.ttNumHist   = int(Param[3]);
            
        else:
            print("Not enough parameters received.");
                
    def SetType(self, stType):
        conn = self.connection();
        if (conn is None):
            sys.exit("Computations are not supported with this version.");           
        
        if (stType == self.Raw):
            id = 0;
            
            Data = zeros(int(4 + 0), dtype='uint32')
            Data[0] = uint32(-1);
            Data[1] = uint32(0);
            Data[2] = uint32(id);
            Data[3] = uint32(0);
            
            Ret = conn.CmdSend(0, int('0x6160', 0), Data, 0);
            Ret = conn.CmdRecv();
            
            self.datatype = id;
            return;
            
        if not self.isSupported:
            sys.exit("Computations are not supported with this version.");           
        
        if (stType == self.RP):
            if (self.isSet_FuSca and self.isSet_fStrt and self.isSet_fStop and self.isSet_TRampUp and self.isSet_fs and self.isSet_CalRe and self.isSet_CalIm):
                id = 2;
                
                Data = zeros(int(4 + 0), dtype='uint32')
                Data[0] = uint32(-1); #uint32(-id);
                Data[1] = uint32(0);
                Data[2] = uint32(id);
                Data[3] = uint32(0);
                
                Ret = conn.CmdSend(0, int('0x6160', 0), Data, 0);
                Ret = conn.CmdRecv();
                
                self.SetDataType(id, fromstring(Ret.tostring(), dtype='float32'));
            
        elif (stType == self.RD):
            if (self.isSet_Np and self.isSet_Tp):
                id = 3;
                self.SetParam('SortOutput', 0, 'RangeProfile');
                
                Data = zeros(int(4 + 0), dtype='uint32') 
                Data[0] = uint32(-1); #uint32(-id);
                Data[1] = uint32(0);
                Data[2] = uint32(id);
                Data[3] = uint32(0);
                
                Ret = conn.CmdSend(0, int('0x6160', 0), Data, 0);
                Ret = conn.CmdRecv();
                                
                self.SetDataType(id, fromstring(Ret.tostring(), dtype='float32'));
                
        elif (stType == self.DL):
            id = 4;
            self.SetParam('SortOutput', 0, 'RangeProfile');
            
            Data = zeros(int(4 + 0), dtype='uint32') 
            Data[0] = uint32(-1); #uint32(-id);
            Data[1] = uint32(0);
            Data[2] = uint32(id);
            Data[3] = uint32(0);
            
            Ret = conn.CmdSend(0, int('0x6160', 0), Data, 0);
            Ret = conn.CmdRecv();
                            
            self.SetDataType(id, fromstring(Ret.tostring(), dtype='float32'));
            
        elif (stType == self.TT):
            id = 5;  
            self.SetParam('SortOutput', 0, 'RangeProfile');
            
            Data = zeros(int(4 + 0), dtype='uint32') 
            Data[0] = uint32(-1); #uint32(-id);
            Data[1] = uint32(0);
            Data[2] = uint32(id);
            Data[3] = uint32(0);
            
            Ret = conn.CmdSend(0, int('0x6160', 0), Data, 0);
            Ret = conn.CmdRecv();
            
            self.SetDataType(id, fromstring(Ret.tostring(), dtype='float32'));
            
        else:
            print('DataType unknown');
            
    def SetParam(self, stParam, val, stType='Internal'):
        conn = self.connection();
        if conn is None:
            return;
        
        if stParam == 'FuSca':
            conn.ConSetFileParam('FuSca', val, 'DOUBLE');
            self.isSet_FuSca   = True;
        elif stParam == 'fStrt':
            conn.ConSetFileParam('fStrt', val, 'DOUBLE');
            self.isSet_fStrt   = True;
        elif stParam == 'fStop':
            conn.ConSetFileParam('fStop', val, 'DOUBLE');
            self.isSet_fStop   = True;
        elif stParam == 'TRampUp':
            conn.ConSetFileParam('TRampUp', val, 'DOUBLE');
            self.isSet_TRampUp = True;
        elif stParam == 'fs':
            conn.ConSetFileParam('fs', val, 'DOUBLE');
            self.isSet_fs      = True;
        elif stParam == 'CalRe':
            conn.ConSetFileParam('CalRe', val, 'ARRAY64');
            self.isSet_CalRe   = True;
        elif stParam == 'CalIm':
            conn.ConSetFileParam('CalIm', val, 'ARRAY64');
            self.isSet_CalIm   = True;
        elif stParam == 'Tp':
            conn.ConSetFileParam('Tp', val, 'DOUBLE');
            self.isSet_Tp      = True;
        elif stParam == 'Np':
            conn.ConSetFileParam('Np', val, 'INT');
            self.isSet_Np      = True;
        elif stParam == 'Range_NFFT':
            conn.ConSetFileParam('Range_NFFT', val, 'INT');
        elif stParam == 'Range_IniN':
            conn.ConSetFileParam('Range_IniN', val, 'INT');
        elif stParam == 'Range_WinType':
            conn.ConSetFileParam('Range_WinType', val, 'INT');
        elif stParam == 'Range_SubtractMean':
            conn.ConSetFileParam('Range_SubtractMean', val, 'INT');
        elif stParam == 'Range_RMin':
            conn.ConSetFileParam('Range_RMin', float(val), 'DOUBLE');
        elif stParam == 'Range_RMax':
            conn.ConSetFileParam('Range_RMax', float(val), 'DOUBLE');
        elif stParam == 'RP_Mult':
            conn.ConSetFileParam('RP_Mult', val, 'INT');
        elif stParam == 'RP_SortOutput':
            conn.ConSetFileParam('RP_SortOutput', val, 'INT');
        elif stParam == 'Vel_NFFT':
            conn.ConSetFileParam('Vel_NFFT', val, 'INT');
        elif stParam == 'Vel_WinType':
            conn.ConSetFileParam('Vel_WinType', val, 'INT');
        elif stParam == 'RD_BufSiz':
            conn.ConSetFileParam('RD_BufSiz', val, 'INT');
        elif stParam == 'Ang_NFFT':
            conn.ConSetFileParam('Ang_NFFT', val, 'INT');
        elif stParam == 'Ang_Interpolate':
            conn.ConSetFileParam('Ang_Interpolate', val, 'INT');
        elif stParam == 'Ang_Flip':
            conn.ConSetFileParam('Ang_Flip', val, 'INT');
        elif stParam == 'Thres_Mult':
            conn.ConSetFileParam('Thres_Mult', float(val), 'DOUBLE');
        elif stParam == 'Thres_Mult2':
            conn.ConSetFileParam('Thres_Mult2', float(val), 'DOUBLE');
        elif stParam == 'Thres_Old':
            conn.ConSetFileParam('Thres_Old',  float(val), 'DOUBLE');
        elif stParam == 'Thres_VelMin':
            conn.ConSetFileParam('Thres_VelMin', float(val), 'DOUBLE');
        elif stParam == 'Thres_VelMax':
            conn.ConSetFileParam('Thres_VelMax', float(val), 'DOUBLE');
        elif stParam == 'Thres_UseVel':
            conn.ConSetFileParam('Thres_UseVel', val, 'INT');            
        elif stParam == 'Thres_Range1':
            conn.ConSetFileParam('Thres_Range1', float(val), 'DOUBLE');
        elif stParam == 'Thres_Range2':
            conn.ConSetFileParam('Thres_Range2', float(val), 'DOUBLE');
        elif stParam == 'DL_NumDetections':
            conn.ConSetFileParam('DL_NumDetections', val, 'INT');
        elif stParam == 'DL_SortAsc':
            conn.ConSetFileParam('DL_SortAsc', val, 'INT');
        elif stParam == 'DL_BufSiz':
            conn.ConSetFileParam('DL_BufSiz', val, 'INT');
        elif stParam == 'DL_Mode':
            conn.ConSetFileParam('DL_Mode', val, 'INT');
        elif stParam == 'Track_SigmaX':
            conn.ConSetFileParam('Track_SigmaX', float(val), 'DOUBLE');
        elif stParam == 'Track_SigmaY':
            conn.ConSetFileParam('Track_SigmaY', float(val), 'DOUBLE');
        elif stParam == 'Track_VarX':
            conn.ConSetFileParam('Track_VarX', float(val), 'DOUBLE');
        elif stParam == 'Track_VarY':
            conn.ConSetFileParam('Track_VarY', float(val), 'DOUBLE');
        elif stParam == 'Track_VarVel':
            conn.ConSetFileParam('Track_VarVel', float(val), 'DOUBLE');
        elif stParam == 'Track_MinVarX':
            conn.ConSetFileParam('Track_MinVarX', float(val), 'DOUBLE');
            conn.ConSetFileParam('Track_HasMinVar', 1, 'INT');
        elif stParam == 'Track_MinVarY':
            conn.ConSetFileParam('Track_MinVarY', float(val), 'DOUBLE');
            conn.ConSetFileParam('Track_HasMinVar', 1, 'INT');
        elif stParam == 'TT_NumDetections':
            conn.ConSetFileParam('TT_NumDetections', val, 'INT');
        elif stParam == 'TT_NumTracks':
            conn.ConSetFileParam('TT_NumTracks', val, 'INT');
        elif stParam == 'TT_HistLen':
            conn.ConSetFileParam('TT_HistLen', val, 'INT');
        elif stParam == 'TT_MaxHist':
            conn.ConSetFileParam('TT_MaxHist', val, 'INT');
        elif stParam == 'TT_UseAreas':
            conn.ConSetFileParam('TT_UseAreas', val, 'INT');
        elif stParam == 'TT_Areas':
            conn.ConSetFileParam('TT_Areas', numpy.array(val, dtype=float), 'ARRAY64');
        elif stParam == 'TT_ExcludeVel':
            conn.ConSetFileParam('TT_ExcludeVel', val, 'INT');
        elif stParam == 'TT_Vel_UseRange':
            conn.ConSetFileParam('TT_Vel_UseRange', val, 'INT');
        elif stParam == 'TT_Vel_Min':
            conn.ConSetFileParam('TT_Vel_Min', float(val), 'DOUBLE');
        elif stParam == 'TT_Vel_Max':
            conn.ConSetFileParam('TT_Vel_Max', float(val), 'DOUBLE');
        elif stParam == 'TT_BufSiz':
            conn.ConSetFileParam('TT_BufSiz', val, 'INT');
        elif stParam == 'TT_RemCnt':
            conn.ConSetFileParam('TT_RemCnt', val, 'INT');
        elif stParam == 'TT_OutputCluster':
            conn.ConSetFileParam('TT_OutputCluster', val, 'INT');
                
    def GetData(self, NrPack):
        conn = self.connection();
        if conn is None:
            return [];
            
        if self.dataType == 2:
            ## range profile
            rpData = conn.ConGetData(NrPack * self.rpLen * self.nrChn * self.dtypeLen * 2);
            if (rpData == []):
                return rpData;
            rpData.dtype = 'float32';
            cData  = rpData[0::2] + 1j*rpData[1::2];
            if (NrPack == 1):
                Data = cData.reshape(int(self.nrChn), self.rpLen).transpose(1, 0);
            else:
                if (self.rpSort > 0):
                    Data   = cData.reshape(NrPack, int(self.nrChn), self.rpLen).transpose(1, 2, 0);
                else:
                    Data   = cData.reshape(NrPack, int(self.nrChn), self.rpLen).transpose(2, 1, 0);
            
            ## Todo DataIdx
            return Data;
            
        elif self.dataType == 3:
            ## range doppler
            rdData = conn.ConGetData(NrPack * self.rpLen * self.rdLen * self.nrChn * self.dtypeLen * 2);
            rdData.dtype = 'float32';
            cData  = rdData[0::2] + 1j*rdData[1::2];
            if (NrPack == 1):
                Data = cData.reshape(int(self.nrChn), self.rpLen, self.rdLen).transpose(2, 1, 0);
            else:
                Data   = cData.reshape(int(self.nrChn), self.rpLen, self.rdLen, NrPack).transpose(2, 1, 0, 3);
                
            ## Todo DataIdx
            return Data;
            
        elif self.dataType == 4:
            ## detection list
            Offset = int(5 + self.nrChn * 2);
            dlData = conn.ConGetData(NrPack * self.dlLen * (5 * self.dtypeLen + 2 * self.dtypeLen * self.nrChn));
            dlData.dtype = 'float32';
            detList = [];
            for tIdx in range(1, NrPack * self.dlLen):
                Target = dict(
                            Range=dlData[int(Offset * (tIdx - 1))],
                            Vel=dlData[int(1 + Offset * (tIdx - 1))],
                            Mag=dlData[int(2 + Offset * (tIdx - 1))],
                            Ang=dlData[int(3 + Offset * (tIdx - 1))],
                            Noise=dlData[int(4 + Offset * (tIdx - 1))],
                            Amp=[]);
                Target['Amp'] = dlData[int(5 + Offset * (tIdx - 1)):int(5 + 2 * self.nrChn + Offset * (tIdx - 1)):2] + 1j * dlData[int(6 + Offset * (tIdx - 1)):int(6 + 2 * self.nrChn + Offset * (tIdx - 1)):2];
                if not (Target['Range'] == 0 and Target['Vel'] == 0 and Target['Mag'] == 0 and Target['Ang'] == 0):
                    detList.append(Target);
                else:
                    break;
                    
            ## Todo DataIdx
            return detList;
            
        elif self.dataType == 5:
            ## track list
            len    = self.dtypeLen * ( 3 + ( 9 + 2 * self.ttNumHist ) * self.ttNumTracks + self.ttTarSize * self.ttNumTar );
            
            ttData = conn.ConGetData(NrPack * len);
            ttData.dtype = 'float32';
            ttData = ttData[3:]; # ignore first three entries, as they contain the LenHist, Target count and TarSize values
            
            
            Tracks = [];
            for trackIdx in range(0, self.ttNumTracks):
                Track = dict(
                            Id=fromstring(ttData[int((9 + 2 * self.ttNumHist) * trackIdx + 0)].tostring(), dtype='int32')[0],
                            X=ttData[int((9 + 2 * self.ttNumHist) * trackIdx + 1)],
                            Y=ttData[int((9 + 2 * self.ttNumHist) * trackIdx + 2)],
                            Vel=ttData[int((9 + 2 * self.ttNumHist) * trackIdx + 3)],
                            VelX=ttData[int((9 + 2 * self.ttNumHist) * trackIdx + 4)],
                            VelY=ttData[int((9 + 2 * self.ttNumHist) * trackIdx + 5)],
                            Mag=ttData[int((9 + 2 * self.ttNumHist) * trackIdx + 6)],
                            VarX=ttData[int((9 + 2 * self.ttNumHist) * trackIdx + 7)],
                            VarY=ttData[int((9 + 2 * self.ttNumHist) * trackIdx + 8)],
                            HistX=[], HistY=[]);
                
                hist = ttData[int((9 + 2 * self.ttNumHist) * trackIdx + 9):];
                if not (Track['Id'] == 0 and Track['X'] == 0 and Track['Y'] == 0 and Track['VelX'] == 0 and Track['VelY'] == 0):
                    for histIdx in range(0, self.ttNumHist):
                        HistX = hist[2 * histIdx + 0];
                        HistY = hist[2 * histIdx + 1];
                        if not (HistX == 0 and HistY == 0):
                            Track['HistX'].append(HistX);
                            Track['HistY'].append(HistY);
                        else:
                            break;
                    Tracks.append(Track);
                else:
                    break;
            
            Detections = [];
            DetOffset = ( 9 + 2 * self.ttNumHist ) * self.ttNumTracks;
            ttData = ttData[DetOffset:];
            
            for tarIdx in range(0, self.ttNumTar):
                if (self.ttTarSize == 2):
                    Det = dict(
                            X=ttData[int(self.ttTarSize * tarIdx + 0)],
                            Y=ttData[int(self.ttTarSize * tarIdx + 1)]);
                
                    if not (Det['X'] == 0 and Det['Y'] == 0):
                        Detections.append(Det);
                    else:
                        break;                                
                else:
                    Det = dict(
                                X=ttData[int(self.ttTarSize * tarIdx)]*sin(ttData[int(3 + self.ttTarSize * tarIdx)]),
                                Y=ttData[int(self.ttTarSize * tarIdx)]*cos(ttData[int(3 + self.ttTarSize * tarIdx)]),
                                Range=ttData[int(self.ttTarSize * tarIdx)],
                                Vel=ttData[int(1 + self.ttTarSize * tarIdx)],
                                Mag=ttData[int(2 + self.ttTarSize * tarIdx)],
                                Ang=ttData[int(3 + self.ttTarSize * tarIdx)],
                                Noise=ttData[int(4 + self.ttTarSize * tarIdx)],
                                Track=fromstring(ttData[int(5 + self.ttTarSize * tarIdx)].tostring(), dtype='int32')[0],
                                Amp=[]);
                    Det['Amp'] = ttData[int(6 + self.ttTarSize * tarIdx):int(6 + 2 * self.nrChn + self.ttTarSize * tarIdx):2] + 1j * ttData[int(7 + self.ttTarSize * tarIdx):int(7 + 2 * self.nrChn + self.ttTarSize * tarIdx):2];
                    if not (Det['Range'] == 0 and Det['Vel'] == 0 and Det['Mag'] == 0 and Det['Ang'] == 0):
                        Detections.append(Det);
                    else:
                        break;
            
            Data = dict(Detections=Detections, Tracks=Tracks);
                    
            ## Todo DataIdx
            return Data;
            
    def GetRangeBins(self):
        conn = self.connection();
        if conn is None:
            return [];
    
        NFFT    =   conn.GetFileParam('Range_NFFT');
        c0      =   1 / sqrt( 4 * pi * 1e-7 * 8.85e-12);
        kf      =   (conn.GetFileParam('fStop') - conn.GetFileParam('fStrt'))/conn.GetFileParam('TRampUp');
        fs      =   conn.GetFileParam('fs');
                
        vRange  =   range(0, int(NFFT/2));
        vRange  =   vRange / NFFT * fs * c0 / (2 * kf);
        dR      =   1 / NFFT * fs * c0 / (2 * kf);    
        
        RMinIdx =   int(self.rpMin / dR + 0.5) - 1;
        RMaxIdx =   int(self.rpMax / dR + 0.5) + 1;
        
        if (RMaxIdx >= len(vRange)):
            RMaxIdx = len(vRange) - 1;
        
        if RMaxIdx > NFFT/2 + 1:
            RMaxIdx = NFFT/2 + 1;
        if RMinIdx < 1:
            RMinIdx = 1;
        
        return vRange[RMinIdx:RMaxIdx + 1];
     
    def GetVelBins(self):
        conn = self.connection();
        if conn is None:
            return [];
            
        fStop   = conn.GetFileParam('fStop');
        fStrt   = conn.GetFileParam('fStrt');
        NFFTVel = conn.GetFileParam('Vel_NFFT');
        Tp      = conn.GetFileParam('Tp');
        c0      = 1 / sqrt ( 4 * pi * 1e-7 * 8.85e-12);
        
        fc      = (fStop + fStrt) / 2;
        vVel    = range(0, int(NFFTVel));
        vVel    = vVel - NFFTVel/2;
        vVel    = vVel / NFFTVel * (1 / Tp) * c0 / (2 * fc);
        
        return vVel;