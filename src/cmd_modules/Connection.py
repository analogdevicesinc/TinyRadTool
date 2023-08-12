"""This module contains the classes and methods for communication to the RadarLog
   """
# Version 1.0.0 
#     Supports RadServe for Radarbook and RadarLog
#     Supports PNet for Radarbook with ARM module

# Version 1.0.1
#     Correct  return value

# Version 1.0.2
# 	  RDL: Added functions from RadarLog
#	  RDL: Get file params by type (with arrays)
#     RDL: Bufsize unified
#     RBK: OpenTcpIpDatCom used in all functions requiring a connection to the dataport
#     RBK: Added function ConSetDatSockTimeout to allow setting of socket timeout for slow measurements

# Version 1.0.3
#     RDL: Use OpenTcpIpDatCom in all functions requiring a connection to DataPort
#     RDL: Added ConSetDatSockTimeout to allow setting the socket timeout for slow measurements
#     RBK: SetFileParam with Strings is working

# Version 1.0.4
#     RDL: Handle double-responses from RadServe
#     RBK: Allow setting device index in constructor

# Version 1.0.5
#     Set max number of simultaneously queued USB transfers
#     Merged class (Radarbook/Radarlog)

# Version 1.0.6
#     Add Parameters to OpenExtensionPort
#     Created PollClosed functions for DataPort, Replay, File

# Version 1.0.7
#     Add function to set usb config timeout

# Version 1.0.8
#     Add functions to set/get RadServe timestamp

# Version 1.1.0
#     Added members: cDevIndex, cDPVideo, cVideoFrmsColl
#     Support of multiple camera streams
#     Camera data can also be provided via data port
#     Simplified RadServe commands
#     ----
#     Added functions:
#        CfgRadServe [AddVideoToFile, AddVideoToDataPort, AddTimStmpToFilename, LogDataPortToFile, HdfPath]
#        CfgRadServe_Extension (Path, Selection, Param)
#        CfgRadServe_ExtensionFile (AddChn, SplitChn)
#        CfgRadServe_CameraList, CfgRadServe_CameraDeselectAll, CfgRadServe_CameraSelect, CfgRadServe_CameraDeselect
#     Updated functions:
#        CmdSend, OpenTcpIpVideoCom, CloseTcpIpVideoCom, CloseFile, PollFileClosed
#        ReplayFile, StopReplayFile, PollReplayClosed, GetDataPort, CloseDataPort
#        PollDataPortClosed, RestartDataPort, SetIndex, ConAppendTimestamp, ConSetFileParam
#        ConSetConfig, ConGetConfig, ConSetTimeout, ConSetCfgTimeout, ConGetData
#        DispSrvVers, ListDev, ConSet, DispVideo, GetVideo
#     Obsolete functions:
#        AddVideo, StopFile
#     Removed functions:
#        CloseFileExtension, StopReplayFileExtension, CloseExtensionPort
#        CreateStream, StopStream, CloseStream, CreateFileExtension, ReplayFileExtension

# Version 1.2.0
#     Updated RadServe Cfg Functions (CfgRadServe_Camera(), CfgRadServe_Extension())

# Version 1.2.1
#     Updated CfgRadServe_Camera('Select') to allow setting width and height of video streaming
#     Updated CfgRadServe_Camera('AddOptris'/'UpdateOptris') to allow storing raw optris data
#     Fixed GetVideo/DispVideo/GetAllVideos/DispAllVideos Functions

# Version 1.3.0
#     Allow device selection via UID, add port to parameters

# Version 1.3.2
#     Exit on Open-Error

# Version 1.4.0
#     Functions to support RadServe v3.2.0

# Version 1.4.1
#     Update for cleaned-up parameters for computation
#     Renamed ConGetConfig to ConGetFileParam, and ConSetConfig to ConSetFileParam (= Matlab names)

# Version 1.5.0
#     Combine Connection class for RadarLog and Radarbook2

# Version 1.5.1
#     Added function ConForceSet for setting Mult

# Version 1.6.0
#     Added Support for TinyRad and RadServe v3.4.0

# Version 1.6.1
#     Fix open Rbk2

# Version 1.6.2
#     Fix CfgRadServe functions

import  os
import  sys
import  ctypes
import  socket
import  select as sockSelect
import  signal

import  usb.core
import  usb.util

#import  cv2
import  numpy
from    numpy import *
from struct import pack, unpack
import weakref
#import matplotlib.pyplot as plt
import  src.cmd_modules.Computation as Computation

class Connection():

    ## Constructor
    def __init__(self, devType, stConType='Usb', *args):
        self.cType              =   stConType;
        self.cIpAddr            =   '127.0.0.1';
        self.cCfgPort           =   8000;
        self.cDataPort          =   6000
        self.cDebugInf          =   1
        
        ## RBK Specifics ----------------------
        self.cRbkIp             =   '192.168.1.1';
        self.cRbkCfg            =   8001;
        self.cRbkDat            =   6000;
        ##-------------------------------------
                
        self.cUid               =   0;
        self.cDevIndex          =   0;
        self.cDataOpened        =   -1
        self.cReplay            =   -1
        self.cReplayExt         =   -1
        self.cExtSize           =   0
        self.cExtMult           =   0
        self.cDataIdx           =   0
        
        self.cOpened            =   -1
        self.cResponseOk        =   1
        self.cResponseMsg       =   2
        self.cResponseInt       =   3
        self.cResponseData      =   4
        self.cResponseDouble    =   5
        self.cArmCmdBegin       =   int('0x6000', 0)
        self.cArmCmdEnd         =   int('0x7FFF', 0)
        self.cFpgaCmdBegin      =   int('0x9000', 0)
        self.cFpgaCmdEnd        =   int('0xAFFF', 0)
        
        self.cBufSiz            =   256
        
        self.hCon               =   -1
        self.hConDat            =   -1
        self.hConDatTimeout     =    8
        self.cPortOpen          =   -1
        self.cPortNum           =    0
        self.cRadVideoSocket    = []
        
        self.cDPVideo           = False
        self.hConVideo          = []
        self.cVideoPort         = []
        self.cVideoPortOpen     = []
        self.cVideoCols         = []
        self.cVideoRows         = []
        self.cVideoChn          = []
        self.cVideoRate         = []
        self.cVideoSize         = []
        self.cVideoFrames       = []
        self.cVideoFrmsColl     = []
        self.cDataIdx           = 0
        
        self.cMult              = 32
        self.cDataPortKeepAlive = False
        self.cNumPackets        =  0

        self.cUsbNrTx           = 96
        
        self.cCfgTimeout        = 100
        self.cTimeout           =  -1
        self.ConNew             =   0
        
        self.cTimStampRS        =   0;
        
        self.usbDev             =   0
        self.usbLen             =   0
        self.usbState           =   0
        #if self.cType == 'Usb':
        #    self.usb            = ctypes.cdll.LoadLibrary("Dll/usb.dll")
        #    self.hCon           = self.usb.ConnectToDevice(True);
        
        self.cDevType = devType;
        
        nargin = len(args);
        if self.cDevType == 'RadarLog':    
            if nargin >= 1:
                self.cIpAddr         =   args[0];
                if nargin >= 2:
                    self.cCfgPort    =   args[1];
                    if nargin >= 3:
                        devIdx       =   args[2];
                        if (isinstance(devIdx, str)):
                            if (len(devIdx) == 16):
                                self.cUid = int(devIdx, 16);
                            else:
                                sys.exit("UID too short");
                        elif (devIdx > 0):
                            self.SetIndex(devIdx);
                        
        elif self.cDevType == 'Radarbook2':
            if nargin >= 0:
                # Set default values
                self.cType           =   stConType;
                self.cRbkIp          =   '192.168.1.1';
                self.cRbkCfg         =   8001;
                self.cRbkDat         =   6000 + floor(1000*random.rand());
                
                if nargin >= 1 and stConType == 'RadServe':
                    self.cIpAddr    =   args[0];
                    if nargin >= 2:
                        self.cCfgPort =   args[1];
                        if (nargin >= 3):
                            self.cRbkIp = args[2];
                            if (nargin >= 4):
                                self.cRbkCfg = args[3];
                                if (nargin >= 5):
                                    self.cRbkDat = args[4];
                    self.cType = 'RadServe';
                elif nargin >= 1:
                    self.cRbkIp = args[0];
                    if nargin >= 2:
                        self.cRbkCfg = args[1];
        elif self.cDevType == 'TinyRad':
            if nargin >= 1:
                self.cIpAddr         =   args[0];
                if nargin >= 2:
                    self.cCfgPort    =   args[1];
                    if nargin >= 3:
                        devIdx       =   args[2];
                        if (isinstance(devIdx, str)):
                            if (len(devIdx) == 16):
                                self.cUid = int(devIdx, 16);
                            else:
                                sys.exit("UID too short");
                        elif (devIdx > 0):
                            self.SetIndex(devIdx);
            if stConType == 'Usb':
                # setup signal handler for sigint to avoid terminating the script inbetween the read function
                signal.signal(signal.SIGINT, self.HandleSigInt)
                
                self.usbDev = usb.core.find(idVendor=0x064B, idProduct=0x7823);
                if self.usbDev is None:
                    self.hCon = -1;
                    raise IOError('Device not found.');
                else:
                    self.usbDev.reset();
                    self.hCon = 1;
                    self.usbDev.set_configuration();
                    self.usbCfg  = self.usbDev.get_active_configuration();
                    self.usbIntf = self.usbCfg[(0,0)]
                    self.usbWrEp = usb.util.find_descriptor(
                        self.usbIntf,
                        # match the first OUT endpoint
                        custom_match = \
                        lambda e: \
                            usb.util.endpoint_direction(e.bEndpointAddress) == \
                            usb.util.ENDPOINT_OUT)
                    assert self.usbWrEp is not None
                    self.usbRdEp = usb.util.find_descriptor(
                        self.usbIntf,
                        # match the first OUT endpoint
                        custom_match = \
                        lambda e: \
                            usb.util.endpoint_direction(e.bEndpointAddress) == \
                            usb.util.ENDPOINT_IN)
                    assert self.usbRdEp is not None
                #if platform.system() == 'Linux':
                #else:
                #    self.usb  = ctypes.cdll.LoadLibrary("Dll/usb.dll")
                #    self.hCon = self.usb.ConnectToDevice(True);
            
        self.Computation        =   Computation.Computation(weakref.ref(self));
        if self.cType == 'RadServe':
            self.Computation.SetType('Raw');

    ## Destructor
    def __del__(self):
        if self.cType == 'Usb':
            usb.util.dispose_resources(self.usbDev);
        # Delete handles if exist
        if self.cType == 'RadServe' or self.cType == 'PNet':
            if self.hConDat > 0:
                self.cRadDatSocket.shutdown(socket.SHUT_RDWR);
                self.cRadDatSocket.close();
                self.hConDat = -1;
            for Idx in range(0, len(self.hConVideo)):
                if self.hConVideo[Idx] > 0:
                    self.cRadVideoSocket[Idx].shutdown(socket.SHUT_RDWR);
                    self.cRadVideoSocket[Idx].close();
                    self.hConVideo[Idx] = -1;
                    
            if self.hCon > 0:
                self.cRadSocket.shutdown(socket.SHUT_RDWR);
                self.cRadSocket.close() 
                self.hCon   =   -1
                
    def HandleSigInt(self, signum, frame):
        if self.usbState == 1:
            self.ConGetUsbData(self.usbLen * 2);
            self.CmdRecv();
        elif self.usbState == 2:
            self.CmdRecv();
        exit();

    #-------------- cmd functions --------------
    # DOXYGEN ------------------------------------------------------
    #> @brief Build command send to the Radar system 
    #>
    #>
    #> @param[in]     Ack: acknowledge flag
    #> 
    #> @param[in]     CmdCod: Command code
    #> 
    #> @param[in]     Data: Data values
    #>                  
    def CmdBuild(self, Ack, CmdCod, Data):
        LenData     =   len(Data) + 1
        TxData      =   zeros(LenData,dtype= 'uint32')
        TxData[0]   =   (2**24)*Ack + (2**16)*LenData + CmdCod
        TxData[1:]  =   uint32(Data)
        return TxData
        
    ##  @brief       Convert the uint32 command values to uint8 (byte)
    #   @param[in] cmd      Command array as int type
    #   @return             Array of bytes
    def ToUint8(self, Cmd):
        BufLen          = len(Cmd)*4
        CmdBytes        = (ctypes.c_ubyte*BufLen)()
        Idx = 0
        for Cmd32 in Cmd:
            CmdBytes[0+Idx]     = (Cmd32>>0) & 0xff
            CmdBytes[1+Idx]     = (Cmd32>>8) & 0xff
            CmdBytes[2+Idx]     = (Cmd32>>16) & 0xff
            CmdBytes[3+Idx]     = (Cmd32>>24) & 0xff
            Idx += 4

        return CmdBytes

    # DOXYGEN ------------------------------------------------------
    #> @brief Send command to device
    #>
    #>
    #> @param[in]     Ack: acknowledge flag
    #> 
    #> @param[in]     CmdCod: Command code
    #> 
    #> @param[in]     Data: Data values
    #>      
    def CmdSend(self, Ack, Cod, Data, Open=1):
        #   @function    CmdSend                                                               
        #   @author      Haderer Andreas (HaAn)                                                  
        #   @date        2013-12-01          
        #   @brief       Transmit command to ARM processor

        Cmd             =   self.CmdBuild(Ack,Cod,Data)
        #print("Cmd: ", Cmd)
        Ret             =   []
        if self.cType == 'Usb':
            CmdBytes        =   self.ToUint8(Cmd)                
            TxData          =   0
            if self.hCon > -1:
                TxData      =   1
                self.ConNew =   0
            else:
                self.usbDev      =   self.UsbOpen()
                if self.usbDev != 0:
                    self.hCon       =   0
                    TxData          =   1
                    self.ConNew     =   1
                
            if TxData > 0:
                if self.cDevType == 'RadarLog':
                    pass
                    #self.usb.UsbPySend(self.usbDev, 1, CmdBytes, len(CmdBytes))
                else:
                    Len = uint16(len(CmdBytes));
                    Data2048 = (ctypes.c_ubyte*2048)();
                    Data2048[0] = (Len >> 0) & 0xff;
                    Data2048[1] = (Len >> 8) & 0xff;
                    Data2048[2:int(2 + len(CmdBytes))] = CmdBytes;
                    
                    if self.usbDev is not None:
                        self.usbWrEp.write(Data2048);
           
        elif self.cType == 'PNet': 
            TxData                  =   0
            if self.hCon > -1:
                TxData              =   1
                self.ConNew         =   0
            else:
                Ip = self.cIpAddr;
                Port = self.cCfgPort;
                if self.cDevType == 'Radarbook2':
                    Ip = self.cRbkIp;
                    Port = self.cRbkCfg;
                
                self.hCon       = self.OpenTcpipCom(Ip, Port)
                if self.hCon > -1:
                    TxData          =   1
                    self.ConNew     =   1    
            if TxData > 0:        
                try:
                    self.cRadSocket.sendall(Cmd)
                except socket.timeout:
                    TxData      =   -1
                    print("Socket timed out")
                except socket.error:
                    TxData      =   -1
                    print("error")
                finally:
                    pass

        elif self.cType == 'RadServe':
            if self.hCon == -1:
                self.hCon       =   self.OpenTcpipCom(self.cIpAddr, self.cCfgPort)
                self.hCon
                if self.hCon == -1:
                    print('Couldn''t connect to RadServe');
                
            if self.cOpened == -1 and Open == 1:
                if self.cDevType == 'RadarLog' or self.cDevType == 'TinyRad':
                    DevType = uint32(0); # RadarLog
                    if self.cDevType == 'TinyRad':
                        DevType = uint32(2); # TinyRad^
                        
                    # send command to open device on RadServe
                    if (self.cUid > 0):
                        Data    = zeros(int(4), dtype='uint32');
                        Data[0] = DevType # type usb
                        Data[1] = uint32(self.cDevIndex)
                        uid = fromstring(numpy.array(self.cUid, dtype=numpy.uint64).tostring(), dtype='uint32');
                        Data[2] = uid[1];
                        Data[3] = uid[0];
                    else:
                        Data        =   zeros(int(2), dtype='uint32')
                        Data[0]     =   DevType
                        Data[1]     =   uint32(self.cDevIndex)
                else:
                    stIp    = self.cRbkIp;
                    Len     =   len(stIp)
                    for Idx in range (0, 16-Len):
                        stIp  =   stIp + ' '
                    Data = zeros(int(3 + len(stIp)/4), dtype='uint32');
                    Data[0] = uint32(1);
                    Data[1:int(1 + len(stIp)/4)] = fromstring(stIp, dtype='uint32');
                    Data[int(1 + len(stIp)/4)] = self.cRbkCfg;
                    Data[int(2 + len(stIp)/4)] = self.cRbkDat;
                        
                CmdOpen         =   self.CmdBuild(0, int('0x6103', 0), Data)
                try:
                    self.cRadSocket.sendall(CmdOpen)
                except socket.timeout:
                    TxData      =   -1
                    print("Socket timed out")
                except socket.error:
                    TxData      =   -1
                    print("error")
                finally:
                    pass
                Ret             =   self.CmdRecv(stopOnError=True)
                self.cOpened    = 1

            try:
                self.cRadSocket.sendall(Cmd)
                
            except socket.timeout:
                TxData      =   -1
                print("Socket timed out")
            except socket.error:
                TxData      =   -1
                print("error")
            finally:
                pass

        return Ret

    #   @function       CmdRecv                                                               
    #   @author         Haderer Andreas (HaAn)                                                  
    #   @date           2013-12-01          
    #   @brief          Receive response from baseboard
    def CmdRecv(self, dispError = True, stopOnError = False):
        Ret         =   []
        if self.cType == 'Usb':
            TxData          =   0
            if self.hCon > -1:
                TxData      =   1
            else:
                print('REC: USB Connection closed previously')
            if TxData > 0:
                HeaderLen   =   128;
                HeaderData  =   self.usbRdEp.read(HeaderLen);
                RxDataLen   =   (HeaderData[2] - 1) * 4;
                RecvLen     =   RxDataLen - (len(HeaderData)  - 4);
                RxData      =   HeaderData[4:].tobytes()
                NrBytes     =   RxDataLen - RecvLen;
                if RecvLen > 0:
                    # todo append data
                    print("TODO read moe .. ");
                    pass
                if NrBytes != 0:
                    Ret = fromstring(RxData, dtype=uint32);
        elif self.cType == 'PNet':
            TxData          =   0
            if self.hCon > -1:
                TxData      =   1
            else:
                print('REC: TCPIP Connection closed previously')
            if TxData > 0:
                #----------------------------------------------------------
                # Read response
                #----------------------------------------------------------
                try:
                    # Receive data from the server and shut down
                    RxBytes         =   self.cRadSocket.recv(4)          
                    RxData          =   fromstring(RxBytes, dtype='uint32')
                    LenRxData       =   RxData[0]//(2**16)
                    RxBytes         =   self.cRadSocket.recv((LenRxData-1)*4)
                    if len(RxBytes) == ((LenRxData-1)*4):                       
                        Data        =   zeros(LenRxData-1,dtype ='uint32')    
                        Data        =   fromstring(RxBytes, dtype=uint32)
                        Ret         =   Data
                    else:
                        Ret         =   []
                        print("len(RxBytes) wrong: %d != %d" % (len(RxBytes), (LenRxData-1)*4))
                except socket.timeout:
                    Ret             =   []
                    print("socket timed out")
                except socket.error:
                    Ret             =   []
                finally:    
                    if self.ConNew > 0:
                        self.CloseTcpipCom()

        elif self.cType == 'RadServe':
            #print("Cmd Recv RadServe: ", self.hCon)
            if self.hCon > -1:
                Len         =   self.cRadSocket.recv(4) 
                Len         =   fromstring(Len, dtype='uint32')
                Type        =   Len % 2**16
                Len         =   floor(Len/2**16)
                Err         =   0
                if (Len > 1024):
                    Err     =   1
                    Len     =   Len - 1024
                Len         =   Len - 1
                
                #print("Len: ", Len, "Err: ", Err, "Type:", Type)
                if (Err > 0) and (Len > 0): 
                    #print("If first")
                    Ret     =   self.cRadSocket.recv(int(4*Len[0])) 
                    if (stopOnError):
                        sys.exit(Ret.decode('ASCII'));
                    elif (dispError):
                        print(Ret.decode('ASCII'));
                    Ret     =   Ret.decode('ASCII')
                    #Ret     =   -1
                elif ((((self.cArmCmdBegin <= Type) and (Type <= self.cArmCmdEnd)) or ((self.cFpgaCmdBegin <= Type) and (Type <= self.cFpgaCmdEnd)) ) and (Len > 0)):
                    #print("Elff 1")
                    Ret     =   self.cRadSocket.recv(int(4*Len[0])) 
                    Ret     =   fromstring(Ret, dtype='uint32')
                elif (Err == 0) and (Type == self.cResponseMsg) and (Len > 0):
                    # handle non error case - TODO !
                    Ret     =   self.cRadSocket.recv(int(4*Len[0]))
                    if (stopOnError):
                        sys.exit(Ret.decode('ASCII'));
                    elif (dispError):
                        print(Ret.decode('ASCII'));
                    Ret     =   Ret.decode('ASCII');
                elif (Err == 0) and (Type == self.cResponseOk):
                    Ret     =   0
                elif (Err == 0) and (Type == self.cResponseDouble):
                    Ret     = self.cRadSocket.recv(int(4*Len[0]));
                    Ret     = fromstring(Ret, dtype='double');
                elif (Err == 0) and (Type == self.cResponseInt):
                    Ret     =   self.cRadSocket.recv(int(4*Len[0])) 
                    Ret     =   fromstring(Ret, dtype='uint32')                        
                elif (Err == 0) and (Type == self.cResponseData):
                    if (Len > 0):
                        Ret     =   self.cRadSocket.recv(4*int(Len)) 
                        Ret     =   fromstring(Ret, dtype='uint32')                            
                    else:
                        Ret =   []
                else:
                    Ret     =   0
        return Ret

    #------------- Open/Close functions ---------
    # DOXYGEN ------------------------------------------------------
    #> @brief Open connection for the different types of communication
    #>
    #> Opens communication and set hCon parameter if opened
    #>       
    def     ConOpen(self):
        if self.cType == 'Usb':
            if self.hCon > -1:
                self.UsbClose()
                self.UsbOpen()
            else:
                self.UsbOpen()
        elif self.cType == 'PNet':
            if self.hCon > -1:
                self.CloseTcpipCom();
                self.OpenTcpipCom(self.cIpAddr, self.cCfgPort)
            else:
                self.OpenTcpipCom(self.cIpAddr, self.cCfgPort)
        elif self.cType == 'RadServe':
            if self.hCon == -1:
                self.OpenTcpipCom(self.cIpAddr, self.cCfgPort);

    def     ConClose(self):      
        if self.cType == 'Usb':
            self.UsbClose()
        elif self.cType == 'PNet':
            if self.hCon > -1:
                self.CloseTcpipCom()
                self.hCon       =   -1
        elif self.cType == 'RadServe':
            if self.hCon > -1:
                self.CloseTcpipCom()
                self.hCon = -1

    def     ConCloseData(self):       
        if self.cType == 'Usb':
            self.UsbClose();
        elif self.cType == 'RadServe':
            self.ConCloseDataPort()
        else:
            if self.hConDat > -1:
                self.CloseTcpipDataCom();
                self.hConDat     =   -1;

    def     UsbOpen(self):
        if self.cDevType == 'TinyRad':
            self.usbDev = usb.core.find(idVendor=0x064B, idProduct=0x7823);
            if self.usbDev is None:
                self.hCon = -1;
                raise IOError('Device not found.');
            else:
                self.hCon = 1;
                self.usbDev.set_configuration();
                self.usbCfg  = self.usbDev.get_active_configuration();
                self.usbIntf = self.usbCfg[(0,0)]
                self.usbWrEp = usb.util.find_descriptor(
                    self.usbIntf,
                    # match the first OUT endpoint
                    custom_match = \
                    lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT)
                assert self.usbWrEp is not None
                self.usbRdEp = usb.util.find_descriptor(
                    self.usbIntf,
                    # match the first OUT endpoint
                    custom_match = \
                    lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_IN)
                assert self.usbRdEp is not None
            
    def     UsbClose(self):
        pass
        #if self.hCon > -1:
        #    self.usb.UsbPyClose(sel.usbDev);
        #    self.hConDat        =   -1
        #    self.hCon           =   -1
            
    # DOXYGEN ------------------------------------------------------
    #> @brief Open TCPIP connection
    #>
    #> Open TCPIP connection
    #>
    #> @param[in]     IpAdr: IP address
    #> 
    #> @param[in]     Port: Port number of connection 
    #>         
    def     OpenTcpipCom(self, IpAdr, Port):  
        hCon    =   -1        
        if (self.cType == 'PNet') or (self.cType == 'RadServe'):
            try:
                self.cRadSocket         =   socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.cRadSocket.settimeout(4)
                self.cRadSocket.connect((IpAdr, Port))
                hCon            =   1
            except socket.timeout:
                hCon            =   -1
                print("Socket timed out")
            except socket.error:
                hCon            =   -1
                print("error")
            finally:
                pass
        return hCon

    def     CloseTcpipCom(self):        
        if self.cType == 'PNet':
            # Use Pnet functions
            if self.hCon > -1:
                self.cRadSocket.close() 
                self.hCon   =   -1
                
    def OpenTcpIpDatCom(self, IpAdr, Port):
        #   @function       OpenTcpipCom.m                                                                
        #   @author         Haderer Andreas (HaAn)                                                  
        #   @date           2013-12-01          
        #   @brief          Open TCPIP connection at given address and port number
        #   @param[in]      IpAdr:  String containing valid IP address; string is not checked
        #   @param[in]      Port:   Port number of connection
        #   @return         tcpCon: Handle to TCP connection            
        try:
            self.cRadDatSocket          =   socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cRadDatSocket.settimeout(self.hConDatTimeout)
            self.cRadDatSocket.connect((IpAdr, Port))
            self.hConDat            =   1
        except socket.timeout:
            self.hConDat            =   -1
            print("Socket timed out")
        except socket.error:
            self.hConDat            =   -1
            print("error")
        finally:
            pass
        
    def     CloseTcpipDataCom(self):         
        if ((self.cType == 'PNet') or (self.cType == 'RadServe')):
            if self.hConDat > 0:
                self.cRadDatSocket.close() 
                self.hConDat     =   -1
            
    def     OpenTcpIpVideoCom(self, Idx):
        if ((self.cType == 'RadServe') and (self.hConVideo[Idx] == -1)):
            # Use Pnet functions
            #disp('TCP/IP with PNet functions');
            #disp(['Con:', num2str(Port)]);
            try:
                #self.cRadVideoSocket[Idx] =   socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.cRadVideoSocket[Idx].settimeout(None) # receive complete video frame at once
                self.cRadVideoSocket[Idx].connect((self.cIpAddr, self.cVideoPort[Idx]))
                self.hConVideo[Idx]        =   1
            except socket.timeout:
                self.hConVideo[Idx]        =   -1
                print("Socket timed out")
            except socket.error:
                self.hConVideo[Idx]        =   -1
                print("error")
            finally:
                pass
            
    def     CloseTcpipVideoCom(self, Idx):
        if self.hConVideo[Idx] > -1:
            self.cRadVideoSocket[Idx].close()
            self.hConVideo[Idx] = -1;
    
    # ----- file functions --------------
    def     CreateFile(self, stName, Max=-1, Extension=False):
        Len         =   (len(stName) % 4)
        for Idx in range (0, 4-Len):
            stName  =   stName + ' '
        Data        =   zeros(int(2 + len(stName)/4 + 1), dtype='uint32')
        Data[0]     =   uint32(Extension)
        Data[1]     =   uint32(len(stName))
        Data[2:int(2 + len(stName)/4)]    =   fromstring(stName,dtype='uint32')
        if (Max != -1):
          Data[int(2 + len(stName)/4)]  =   uint32(Max);
        else:
          Data[int(2 + len(stName)/4)]  =   uint32(self.cNumPackets)
        # create file
        Ret         =   self.CmdSend(0, int('0x6145',0), Data);
        Ret         =   self.CmdRecv();
            
    def     StopFile(self):
        print('StopFile() is obsolete');
        
    def     CloseFile(self):
        Ret         =   self.CmdSend(0, int('0x6147',0), [])
        Ret         =   self.CmdRecv()
        
        self.PollFileClosed();
    
    def     PollFileClosed(self):
        if self.cOpened == 1:
            Ret = 1;
            # poll file closed?
            while (Ret == 1):
                Ret = self.CmdSend(0, int('0x6148',0), []);
                Ret = self.CmdRecv();
                
    def     ReplayFileAs(self, stTarget, stName, FrameIdx=0, WithVideo=0, Extension=False, ):
        if (stTarget == 'Raw'):
            return self.ReplayFile(stName, FrameIdx=FrameIdx, WithVideo=WithVideo, targetLvl=1, Extension=Extension);
        elif (stTarget == 'RangeProfile'):
            return self.ReplayFile(stName, FrameIdx=FrameIdx, WithVideo=WithVideo, targetLvl=2, Extension=Extension);
        elif (stTarget == 'RangeDoppler'):
            return self.ReplayFile(stName, FrameIdx=FrameIdx, WithVideo=WithVideo, targetLvl=3, Extension=Extension);
        elif (stTarget == 'DetectionList'):
            return self.ReplayFile(stName, FrameIdx=FrameIdx, WithVideo=WithVideo, targetLvl=4, Extension=Extension);
        elif (stTarget == 'TargetTracker'):
            return self.ReplayFile(stName, FrameIdx=FrameIdx, WithVideo=WithVideo, targetLvl=5, Extension=Extension);
        else: # Extension
            return self.ReplayFile(stName, FrameIdx=FrameIdx, WithVideo=WithVideo, targetLvl=1, Extension=Extension);
    
    def     ReplayFile(self, stName, FrameIdx=1, WithVideo=0, Extension=False, targetLvl=0, stDataType='Raw'):
        wasSupported = self.Computation.isSupported;
        
        if (not wasSupported):
            self.Computation.Enable();
        
        compData = False;
        if stDataType == 'RangeProfile' or stDataType == 'RangeDoppler' or stDataType == 'DetectionList' or stDataType == 'TargetTracker':
            compData = True;
            
        if Extension or compData:
            intExt = 1;
        else:
            intExt = 0;
    
        Len         =   (len(stName) % 4)
        for Idx in range (0, 4-Len):
            stName  =   stName + ' '
        
        Data    =   zeros(int(3 + len(stName)/4 + 1), dtype='uint32')
        Data[0]     =   uint32(intExt)
        Data[1]     =   uint32(FrameIdx)
        Data[2]     =   uint32(len(stName))
        Data[3:int(3 + len(stName)/4)]    =   fromstring(stName,dtype='uint32')
        Data[int(3 + len(stName)/4)] = uint32(targetLvl);
        
        Ret         =   self.CmdSend(0, int('0x6149',0), Data, 0);
        Ret         =   self.CmdRecv();
        
        if (isinstance(Ret, str)):
            if (not wasSupported):
                self.Computation.Disable();
            return;
        
        if len(Ret) == 1 and Ret != -1:
            self.cPortOpen  =   1
            self.cPortNum   =   Ret
        elif len(Ret) == 2:
            self.cPortOpen = 1;
            self.cPortNum = Ret[0];
        elif len(Ret) > 4:
            self.cPortOpen = 1;
            self.cPortNum  = Ret[0];
            self.cExtSize  = Ret[1];
            self.cExtMult  = Ret[2];
            dataType       = Ret[3];
            if intExt != 0 and targetLvl != 0:
                self.cReplayExt = 1;
            NumVideo       = Ret[4];
            
            Remainder = [];
            if (len(Ret) > 5):
                Remainder = fromstring(Ret[5:].tostring(), dtype=float32);
            
            if (dataType != 0 and len(Remainder) > 0):
                self.Computation.SetDataType(dataType, Remainder);            
                               
            # video info must be called before connecting -> if called after, no video will be provided
            if (NumVideo > 0):
                self.cVideoPort     = zeros(NumVideo, dtype='uint32');
                self.cVideoCols     = zeros(NumVideo, dtype='uint32');
                self.cVideoRows     = zeros(NumVideo, dtype='uint32');
                self.cVideoChn      = zeros(NumVideo, dtype='uint32');
                self.cVideoRate     = zeros(NumVideo, dtype='uint32');
                self.cVideoSize     = zeros(NumVideo, dtype='uint32');
                self.cVideoFrames   = zeros(NumVideo, dtype='uint32');
                self.cVideoFrmsColl = zeros(NumVideo, dtype='uint32');
                self.cVideoPort     = zeros(NumVideo, dtype='uint32');
                self.cVideoPortOpen = zeros(NumVideo, dtype='uint32');
                self.cVideoName     = ["" for x in range(NumVideo)];
                self.hConVideo      = zeros(NumVideo, dtype='int32');
                self.cRadVideoSocket = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(NumVideo)]
            
                for VidIdx in range(0, NumVideo):
                    Ret = self.CmdSend(0, int('0x614B',0), [uint32(VidIdx)], 0);
                    Ret = self.CmdRecv();
            
                    if (len(Ret) >= 7):
                        if (Ret[0] > 0):
                            self.cVideoPort[VidIdx]     = Ret[0];
                            self.cVideoCols[VidIdx]     = Ret[1];
                            self.cVideoRows[VidIdx]     = Ret[2];
                            self.cVideoChn[VidIdx]      = Ret[3];
                            self.cVideoRate[VidIdx]     = Ret[5];
                            self.cVideoSize[VidIdx]     = Ret[1]*Ret[2]*Ret[3];
                            self.cVideoFrames[VidIdx]   = Ret[6];
                            self.cVideoPortOpen[VidIdx] =    1;
                            self.hConVideo[VidIdx]      =   -1;
                            
                            if (len(Ret) >= 8):
                                self.cVideoName[VidIdx] = numpy.array(Ret[7:], dtype=numpy.uint32).tostring().decode("utf-8").replace('\x00', '');
            
            self.OpenTcpIpDatCom(self.cIpAddr, self.cPortNum);

            if WithVideo and (sum(self.cVideoPortOpen) >= 1):
                for VidIdx in range(0, NumVideo):
                    self.OpenTcpIpVideoCom(VidIdx);
            
            self.cReplay = 1;
            
        if (not wasSupported):
            self.Computation.Disable();
        
    def     StopReplayFile(self):      
        if self.cReplay > -1:
            Ret  =   self.CmdSend(0, int('0x614C',0), [], 0)
            Ret  =   self.CmdRecv()
            
            self.PollReplayClosed();
        self.cReplay = -1;
        
        for Idx in range(0, len(self.hConVideo)):
            self.CloseTcpipVideoCom(Idx);
        
        self.CloseTcpipDataCom();
    
    def     PollReplayClosed(self):
        Ret = 1;
        while (Ret == 1):
            Ret = self.CmdSend(0, int('0x614D',0), [], 0)
            Ret = self.CmdRecv();
    # ----- end of file functions --------------
    
    # ----- data port functions --------------
    def     GetDataPort(self, Extension=0):        
        intExt  = Extension;
        compExt = 0;
        
        dataType = self.Computation.GetDataType();
        if dataType > 0:
            compExt = Extension;
            intExt  = dataType;
        else:
            self.Computation.SetType('Raw');
    
        if self.cPortOpen == -1:
            if (compExt > 0):
                Data    =   zeros(3, dtype='uint32');
                Data[2] =   uint32(compExt);
            else:
                Data        =   zeros(2, dtype='uint32')
            Data[0]     =   uint32(intExt)
            Data[1]     =   uint32(self.cNumPackets)
            Ret         =   self.CmdSend(0, int('0x6140', 0), Data)
            Ret         =   self.CmdRecv()
                                    
            if (isinstance(Ret, str)):
                return;
            elif len(Ret) == 1 and Ret != -1:
                self.cPortOpen  =   1
                self.cPortNum   =   Ret
                NumVideo        = 0;
                #if self.hConDat == -1:
                #    self.OpenTcpIpDatCom(self.cIpAddr, Ret);
                #    self.cDataOpened = 1;
            elif len(Ret) > 1:
                self.cPortOpen = 1;
                self.cPortNum = Ret[0];
                
                if intExt >= 1:
                    self.cExtSize = Ret[1];
                    if len(Ret) > 3:
                        self.cExtMult = Ret[2];
                        NumVideo = Ret[3];
                    else:
                        self.cExtMult = self.cMult;
                        NumVideo = 0;
                else:
                    NumVideo = Ret[3];
                    #if len(Ret) == 2:
                    #    NumVideo = Ret[1];
                    #    self.cExtMult = 1;
                    #else:
                    #    self.cExtMult = 1;
                    #    self.cExtSize = Ret[1];
                    #    NumVideo = Ret[3];
                                   
                # video info must be called before connecting -> if called after, no video will be provided
                if ((NumVideo > 0) and (self.cDPVideo)):
                    self.cVideoPort     = zeros(NumVideo, dtype='uint32');
                    self.cVideoCols     = zeros(NumVideo, dtype='uint32');
                    self.cVideoRows     = zeros(NumVideo, dtype='uint32');
                    self.cVideoChn      = zeros(NumVideo, dtype='uint32');
                    self.cVideoRate     = zeros(NumVideo, dtype='uint32');
                    self.cVideoSize     = zeros(NumVideo, dtype='uint32');
                    self.cVideoFrames   = zeros(NumVideo, dtype='uint32');
                    self.cVideoFrmsColl = zeros(NumVideo, dtype='uint32');
                    self.cVideoPort     = zeros(NumVideo, dtype='uint32');
                    self.cVideoPortOpen = zeros(NumVideo, dtype='uint32');
                    self.cVideoName     = ["" for x in range(NumVideo)];
                    self.hConVideo      = zeros(NumVideo, dtype='int32');
                    self.cRadVideoSocket = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(NumVideo)]
                
                    for VidIdx in range(0, NumVideo):
                        Ret = self.CmdSend(0, int('0x6142',0), [uint32(VidIdx)]);
                        Ret = self.CmdRecv();
                
                        if (len(Ret) >= 6):
                            if (Ret[0] > 0):
                                self.cVideoPort[VidIdx]     = Ret[0];
                                self.cVideoCols[VidIdx]     = Ret[1];
                                self.cVideoRows[VidIdx]     = Ret[2];
                                self.cVideoChn[VidIdx]      = Ret[3];
                                self.cVideoRate[VidIdx]     = Ret[5];
                                self.cVideoSize[VidIdx]     = Ret[1]*Ret[2]*Ret[3];
                                self.cVideoPortOpen[VidIdx] =    1;
                                self.hConVideo[VidIdx]      =   -1;
                                
                                self.cVideoName[VidIdx] = numpy.array(Ret[6:], dtype=numpy.uint32).tostring().decode("utf-8").replace('\x00', '');
                
                self.OpenTcpIpDatCom(self.cIpAddr, self.cPortNum);

                if self.cDPVideo and (sum(self.cVideoPortOpen) >= 1):
                    for VidIdx in range(0, NumVideo):
                        self.OpenTcpIpVideoCom(VidIdx);
                
                self.cDataOpened = 1;
    
    def     CloseDataPort(self):   
        if self.cDataOpened > -1 and self.cPortOpen == 1:
            Ret     =   self.CmdSend(0, int('0x6143',0), [])
            Ret     =   self.CmdRecv()
            if Ret == 0:
                self.cPortOpen = -1;
                self.cDataOpened = -1;
                self.cExtSize = 0;
            
            self.PollDataPortClosed();

        self.CloseTcpipDataCom()
        
    def     PollDataPortClosed(self):
        if self.cOpened == 1:
            Ret = 1;
            # poll dataport closed?
            while (Ret == 1):
                Ret = self.CmdSend(0, int('0x6144',0), []);
                Ret = self.CmdRecv();

    def     RestartDataPort(self, NumPackets=0):
        if self.cPortOpen > -1:
            Data        =   zeros(1, dtype='uint32')
            if (NumPackets == 0):
                Data[0] = uint32(self.cNumPackets);
            else:
                Data[0]     =   uint32(NumPackets);
            Ret         =   self.CmdSend(0, int('0x6141', 0), Data)
            Ret         =   self.CmdRecv()
		
    def     GetExtensionPort(self, Extension):
        self.GetDataPort(Extension=Extension);
    # ----- end of data port functions --------------
        
    def     SetIndex(self, Idx):
        self.cDevIndex = Idx;
		
    def     ConAppendTimestamp(self, Val):
        Data        =   zeros(1,dtype='uint32')
        Data[0]     =   Val;
        Ret         =   self.CmdSend(0, int('0x610C',0), Data, 0)
        Ret         =   self.CmdRecv()
        
    def 	ConSetFileParam(self, stName, Val, DataType='STRING'):
       self.ConSetFileParam(stName, Val, DataType);
       
    def     ConSetFileParam(self, stName, Val, DataType='STRING'):
        if  self.cType == 'RadServe':
            Len    =   len(stName) % 4;
            if (Len != 0):
                for Idx in range(0,(4-Len)):
                    stName = stName + ' ';
            Name = fromstring(stName, dtype='uint32');
            
            if (DataType.upper() == 'INT' or isinstance(Val, int)):
                Data = zeros(3 + len(Name));
                Data[0] = 1; # type
                Data[1] = uint32(len(stName));
                for Idx in range(0,len(Name)):
                    Data[2 + Idx] = Name[Idx];
                Data[2 + len(Name)] = Val;
            elif (DataType.upper() == 'DOUBLE' or isinstance(Val, float)):
                Data = zeros(4 + len(Name));
                Data[0] = 2; # type
                Data[1] = uint32(len(stName));
                for Idx in range(0,len(Name)):
                    Data[2 + Idx] = Name[Idx];
                valArray = numpy.array(Val, dtype=numpy.float).tostring();
                Data[int(2 + len(Name)):int(2 + len(Name) + 2)] = fromstring(valArray, dtype=numpy.uint32);
            elif (DataType.upper() == 'ARRAY32'):
                Data = zeros(3 + len(Val) + len(Name));
                Data[0] = 3; # type
                Data[1] = uint32(len(stName));
                for Idx in range(0,len(Name)):
                    Data[2 + Idx] = Name[Idx];
                Data[int(2 + len(Name))] = uint32(len(Val)); # len of array
                for Idx in range(0,len(Val)):
                    Data[int(3 + len(Name) + Idx)] = uint32(Val[Idx]);
            elif (DataType.upper() == 'ARRAY64') or (DataType.upper() == 'DOUBLE_ARRAY'):
                Data = zeros(3 + len(Val)*2 + len(Name));
                Data[0] = 4; # type
                Data[1] = uint32(len(stName));
                for Idx in range(0,len(Name)):
                    Data[2 + Idx] = Name[Idx];
                Data[int(2 + len(Name))] = uint32(len(Val)); # len of array
                valArray = Val.tostring();
                Data[int(3 + len(Name)):int(3 + len(Name) + len(Val)*2)] = fromstring(numpy.ascontiguousarray(Val), dtype=numpy.uint32);
            else:
                Len    =   len(Val) % 4;
                stVal = Val;
                if (Len != 0):
                    for Idx in range(0,(4 - int(Len))):
                        stVal = stVal + ' ';
                Value = fromstring(stVal, dtype='uint32');
                Data = zeros(2 + len(Name) + len(Value));
                Data[0] = 0; # type
                Data[1] = uint32(len(stName));
                for Idx in range(0,len(Name)):
                    Data[2 + Idx] = Name[Idx];
                for Idx in range(0,len(Value)):
                    Data[2 + len(Name) + Idx] = Value[Idx];
            Ret         =   self.CmdSend(0,int('0x6105',0),Data)
            Ret         =   self.CmdRecv()
        
    def     ConGetFileParam(self, Key, DataType):
        if self.cType == 'RadServe':
            if Key == 'RangeProfile':
                Key = 'CfgRP';
                DataType = 'DOUBLE_ARRAY';
            elif Key == 'RangeDoppler':
                Key = 'CfgRD';
                DataType = 'DOUBLE_ARRAY';
            elif Key == 'TargetList':
                Key = 'CfgTL';
                DataType = 'DOUBLE_ARRAY';
        
            Len         =   (len(Key) % 4)
            for Idx in range (0, 4-Len):
                Key  =   Key + ' '
            
            Data        =   zeros(int(1 + len(Key)/4), dtype='uint32')
            if DataType == 'INT':
                Data[0] = 1
            elif DataType == 'DOUBLE':
                Data[0] = 2
            elif DataType == 'ARRAY32':
                Data[0] = 3
            elif DataType == 'ARRAY64' or DataType == 'DOUBLE_ARRAY':
                Data[0] = 4
            elif DataType == 'STRING':
                Data[0] = 0
            else:
                Data[0] = 5
            
            Data[1:]    =   fromstring(Key,dtype='uint32')
            Ret         =   self.CmdSend(0, int('0x6156',0), Data, 0);
            Ret         =   self.CmdRecv(DataType != 'STRING');
			
            if DataType == 'ARRAY64':
                Ret     =   fromstring(Ret, dtype='uint64')
            elif DataType == 'DOUBLE_ARRAY':
                Ret     =   fromstring(Ret, dtype='float');
            elif DataType == 'INT':
                Ret     = Ret[0];
            return Ret;    
            
    def     ConSetTimeout(self, Val):
        if (Val != self.cTimeout) and (Val > 0):
            if self.cType == 'Usb':
                self.cTimeout   =   Val
                USBnAny('timeout', int32(self.cTimeout))
            elif self.cType == 'RadServe':
                if (Val != self.cTimeout):
                    Data = zeros(1, 'uint32');
                    Data[0] = Val;
                    self.CmdSend(0, int('0x6107', 0), Data, 0);
                    self.CmdRecv();
                    self.cTimeout = Val;
                pass
                
    def     ConSetCfgTimeout(self, Val):
        if (Val != self.cCfgTimeout) and (Val > 0):
            if self.cType == 'RadServe':
                if (Val != self.cCfgTimeout):
                    Data = zeros(1, 'uint32');
                    Data[0] = Val;
                    self.CmdSend(0, int('0x6106', 0), Data, 0);
                    self.CmdRecv();
                    self.cCfgTimeout = Val;
                pass

    def     ConSetDatSockTimeout(self, Val):
        if self.cType == 'RadServe':
            self.hConDatTimeout = Val;
        
    def     ConGetData(self, Len):
        if self.hConDat > -1:
            ba = bytearray(int(Len))
            buf = memoryview(ba)
            
            try:
                RxBytesLen = 0;
                while RxBytesLen < Len:
                    RxBytesLen = RxBytesLen + self.cRadDatSocket.recv_into(buf[RxBytesLen:]);
                    
                Ret = ndarray((int(Len/2)), buffer=ba, dtype='int16')

            except socket.timeout:
                Ret     =   []
            except socket.error:
                Ret     =   []
            finally:
                pass
        else:
            Ret     =   []

        return Ret 
        
    def ConGetUsbData(self, Len):
        TxData          =   0
        if self.hCon > -1:
            TxData      =   1
        else:
            print('REC: USB Connection closed previously')
            
        if TxData > 0:
            RxData = self.usbRdEp.read(Len);
            Ret = numpy.frombuffer(RxData, numpy.int16);
            return Ret;
        
    # DOXYGEN ------------------------------------------------------
    #> @brief Display version information of USB mex driver
    #>
    #> Display version information in the Matlab command window
    #>  
    def     DispSrvVers(self):
        if self.cType == 'Usb':
            USBnAny('version')
        elif self.cType == 'RadServe':
            Ret         =   self.CmdSend(0, int('0x6100',0),[],0)
            Ret         =   self.CmdRecv()

    def     ListDev(self):
        if self.cType == 'RadServe':
            Ret         =   self.CmdSend(0, int('0x6110',0),[],0)
            Ret         =   self.CmdRecv();
    
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
    #>      -   <span style="color: #ff9900;"> 'BufSiz': </span> Set buffer size in RadServe <br>
    #>      -   <span style="color: #ff9900;"> 'Mult': </span> Set Packetsize for file streaming  <br>                    
    #>        
    #> e.g. Set BufSiz to 1024
    #>   @code
    #>      Brd =   Radarlog( )
    #>         
    #>      Brd.ConSet('BufSiz',1024)
    #>   @endcode           
    def     ConSet(self,*varargin):
        if len(varargin) > 0:
            stVal       =   varargin[0]
            if stVal == 'BufSiz':
                if len(varargin) > 1:
                    self.cBufSiz    =   varargin[1]
                    if self.cType == 'RadServe':
                        Ret         =   self.CmdSend(0, int('0x6108',0),[uint32(self.cBufSiz)], 0)
                        Ret         =   self.CmdRecv();
            elif stVal == 'Mult':
                if len(varargin) > 1:
                    self.cMult      =   varargin[1]
                    if self.cType == 'RadServe':
                        Ret         =   self.CmdSend(0, int('0x6109',0),[uint32(self.cMult)],0)
                        Ret         =   self.CmdRecv();
            elif stVal == 'KeepAlive':
                if len(varargin) > 1:
                    self.cDataPortKeepAlive  =   varargin[1]
                    if self.cType == 'RadServe':
                        Ret         =   self.CmdSend(0, int('0x610B',0),[uint32(self.cDataPortKeepAlive)],0)
                        Ret         =   self.CmdRecv();
            elif stVal == 'NumPackets':
                if len(varargin) > 1:
                    self.cNumPackets  =   varargin[1]
            elif stVal == 'UsbNrTx':
                if len(varargin) > 1:
                    self.cUsbNrTx  =   varargin[1]
                    if self.cType == 'RadServe':
                        Ret         =   self.CmdSend(0, int('0x610A',0),[uint32(self.cUsbNrTx)],0)
                        Ret         =   self.CmdRecv();
                        
    def     ConForceSet(self,*varargin):
        if len(varargin) > 0:
            stVal       =   varargin[0]
            if stVal == 'Mult':
                if len(varargin) > 1:
                    self.cMult      =   varargin[1]
                    if self.cType == 'RadServe':
                        Ret         =   self.CmdSend(0, int('0x6109',0),[uint32(self.cMult),1], 0)
                        Ret         =   self.CmdRecv();
        
    def     CfgRadServe(self, *varargin):
        if self.cType == 'RadServe' and len(varargin) > 0:
            stVal     =   varargin[0]
            if stVal == 'CreateCmdLogFile':
                stName = varargin[1];
                Len      =   (len(stName) % 4)
                for Idx in range (0, 4-Len):
                    stName  =   stName + ' '
                
                Type = 2;
                if len(varargin) > 2:
                    if varargin[2] == 'FPGA':
                        Type = 0;
                    elif varargin[2] == 'RadServe':
                        Type = 1;
                
                Data = zeros(int(2 + len(stName)/4), dtype='uint32');
                Data[0] = uint32(Type);
                Data[1] = uint32(len(stName));
                Data[2:] = fromstring(stName, dtype='uint32')
                
                Ret   =   self.CmdSend(0, int('0x6102',0), Data, 0)
                Ret   =   self.CmdRecv();
            elif stVal == 'AddVideoToFile':
                Add   =   varargin[1]
                Ret   =   self.CmdSend(0, int('0x6118',0), [uint32(Add)], 0)
                Ret   =   self.CmdRecv();
            elif stVal == 'AddVideoToDataPort':
                self.cDPVideo = varargin[1]
                Ret   =   self.CmdSend(0, int('0x6119',0), [uint32(self.cDPVideo)], 0)
                Ret   =   self.CmdRecv();
            elif stVal == 'AddTimStmpToFilename':
                Add   =   varargin[1]
                Ret   =   self.CmdSend(0, int('0x610E',0), [uint32(Add)], 0)
                Ret   =   self.CmdRecv();
            elif stVal == 'LogDataPortToFile':
                stName =  varargin[1];
                if (len(varargin) > 2):
                    if (varargin[2] == 'RangeProfile'):
                        level = 2;
                    elif (varargin[2] == 'RangeDoppler'):
                        level = 3;
                    elif (varargin[2] == 'DetectionList'):
                        level = 4;
                    elif (varargin[2] == 'TargetTracker'):
                        level = 5;
                    elif (varargin[2] == 'Extension'):
                        level = 6;
                    else:
                        level = 0;
                else:
                    level = 0;
                    
                if not stName:
                    Data     = zeros(3, dtype='uint32');
                    Data[2]  = uint32(level);
                else:
                    Len      =   (len(stName) % 4)
                    for Idx in range (0, 4-Len):
                        stName  =   stName + ' '
                    Data     =   zeros(int(3 + len(stName)/4), dtype='uint32')
                    Data[0]  = 1;
                    Data[1]  = uint32(len(stName));
                    Data[2:int(2 + len(stName)/4)] =   fromstring(stName, dtype='uint32')
                    Data[int(2 + len(stName)/4)] = uint32(level);
                                    
                Ret   =   self.CmdSend(0, int('0x610F',0), Data, 0)
                Ret   =   self.CmdRecv();                
            elif stVal == 'HdfPath':
                stPath   =   varargin[1]
                Len      =   (len(stPath) % 4)
                for Idx in range (0, 4-Len):
                    stPath  =   stPath + ' '
                Data     =   zeros(int(len(stPath)/4), dtype='uint32')
                Data[0:] =   fromstring(stPath, dtype='uint32')
            
                Ret   =   self.CmdSend(0, int('0x610D',0), Data, 0)
                Ret   =   self.CmdRecv();
            
    def     CfgRadServe_Extension(self, *varargin):
        if self.cType == 'RadServe' and len(varargin) > 0:
            stVal     =   varargin[0]
            if stVal == 'General':
                if len(varargin) > 3:
                    stPath    = varargin[1];
                    Selection = varargin[2];
                    Param     = varargin[3];
                    
                    Len         =   (len(stPath) % 4)
                    for Idx in range (0, 4-Len):
                        stPath  =   stPath + ' '
                        
                    Data        =   zeros(int(4 + len(stPath)/4 + len(Param)*2), dtype='uint32')
                    Data[0]     =   uint32(0) # level = 0
                    Data[1]     =   uint32(len(stPath))
                    Data[2:int(2 + len(stPath)/4)]    = fromstring(stPath,dtype='uint32')
                    Data[int(2 + len(stPath)/4)]      = uint32(Selection);
                    Data[int(2 + len(stPath)/4 + 1)]  = uint32(len(Param));
                    if (len(Param) > 0):
                        ParamStr                      = numpy.array(Param, dtype=numpy.float).tostring();
                        Data[int(2 + len(stPath)/4 + 2):int(2 + len(stPath)/4 + 2 + len(Param)*2)] = fromstring(ParamStr, dtype=uint32);
                                    
                    Ret         =   self.CmdSend(0, int('0x6160',0), Data, 0);
                    Ret         =   self.CmdRecv();
            elif stVal == 'File':
                if len(varargin) > 2:
                    Data        =   zeros(2, dtype='uint32')
                    Data[0]     =   uint32(varargin[1])
                    Data[1]     =   uint32(varargin[2])
                    
                    Ret         =   self.CmdSend(0, int('0x6161',0), Data, 0);
                    Ret         =   self.CmdRecv();       

    def     CfgRadServe_Camera(self, *varargin):
        if self.cType == 'RadServe' and len(varargin) > 0:
            stVal     =   varargin[0]
            if stVal == 'List':
                Ret         =   self.CmdSend(0, int('0x6114',0),[], 0)
                Ret         =   self.CmdRecv(True);
            elif stVal == 'DeselectAll':
                Ret         =   self.CmdSend(0, int('0x6115',0),[], 0)
                Ret         =   self.CmdRecv(True);
            elif stVal == 'Deselect':
                if len(varargin) > 1:
                    Data        =   zeros(int(1), dtype='uint32')
                    Data[0]     =   uint32(varargin[1])
                
                    Ret         =   self.CmdSend(0, int('0x6117',0), Data, 0)
                    Ret         =   self.CmdRecv();
            elif stVal == 'Select':
                if len(varargin) > 3:
                    stName = varargin[3];
                    Len         =   (len(stName) % 4)
                    for Idx in range (0, 4-Len):
                        stName  =   stName + ' '
                    
                    Data        =   zeros(int(5 + len(stName)/4), dtype='uint32')
                        
                    Data[0]     =   uint32(varargin[1])
                    Data[1]     =   uint32(varargin[2])
                    Data[2]     =   uint32(len(stName))
                    Data[3:int(3 + len(stName)/4)]    =   fromstring(stName,dtype='uint32')
                    Data[int(len(Data) - 2)] = uint32(varargin[4]);
                    Data[int(len(Data) - 1)] = uint32(varargin[5]);   
                
                    Ret         =   self.CmdSend(0, int('0x6116',0), Data, 0)
                    Ret         =   self.CmdRecv();
            elif stVal == 'AddOptris':
                if len(varargin) > 6:
                    stFile          = varargin[2];
                    stPalette       = varargin[5];
                    stScalingMethod = varargin[6];
                    
                    Len = (len(stFile) % 4)
                    for Idx in range (0, 4-Len):
                        stFile  = stFile + ' '
                        
                    Len = (len(stPalette) % 4)
                    for Idx in range (0, 4-Len):
                        stPalette  = stPalette + ' '
                    # extend to 12 bytes
                    Len = int(len(stPalette) /4);
                    for Idx in range(0, 3-Len):
                        stPalette = stPalette + '    ';
                        
                    Len = (len(stScalingMethod) % 4)
                    for Idx in range (0, 4-Len):
                        stScalingMethod  = stScalingMethod + ' '
                    #extend to 8 bytes
                    Len = int(len(stScalingMethod) /4);
                    for Idx in range(0, 2-Len):
                        stScalingMethod = stScalingMethod + '    ';
                        
                    Data      = zeros(int(9 + len(stFile)/4), dtype='uint32')
                    Data[0]   = uint32(varargin[1]);
                    Data[1]   = uint32(varargin[3]);
                    Data[2]   = uint32(varargin[4]);
                    
                    Data[3:6] = fromstring(stPalette, dtype='uint32');
                    Data[6:8] = fromstring(stScalingMethod, dtype='uint32');
                    Data[8:int(8+len(stFile)/4)] = fromstring(stFile, dtype='uint32');
                    Data[int(8+len(stFile)/4):]  = uint32(varargin[7]); #Raw
                
                    Ret         =   self.CmdSend(0, int('0x611A',0), Data, 0)
                    Ret         =   self.CmdRecv();
            elif stVal == 'UpdateOptris':
                if len(varargin) > 4:
                    stPalette       = varargin[4];
                    stScalingMethod = varargin[5];
                                            
                    Len = (len(stPalette) % 4)
                    for Idx in range (0, 4-Len):
                        stPalette  = stPalette + ' '
                    # extend to 12 bytes
                    Len = int(len(stPalette) /4);
                    for Idx in range(0, 3-Len):
                        stPalette = stPalette + '    ';
                        
                    Len = (len(stScalingMethod) % 4)
                    for Idx in range (0, 4-Len):
                        stScalingMethod  = stScalingMethod + ' '
                    #extend to 8 bytes
                    Len = int(len(stScalingMethod) /4);
                    for Idx in range(0, 2-Len):
                        stScalingMethod = stScalingMethod + '    ';
                        
                    Data      = zeros(9, dtype='uint32')
                    Data[0]   = uint32(varargin[1]);
                    Data[1]   = uint32(varargin[2]);
                    Data[2]   = uint32(varargin[3]);
                    Data[3:6] = fromstring(stPalette, dtype='uint32');
                    Data[6:8] = fromstring(stScalingMethod, dtype='uint32');
                    Data[8:]  = uint32(varargin[4]);
                
                    Ret         =   self.CmdSend(0, int('0x611B',0), Data, 0)
                    Ret         =   self.CmdRecv();
            elif stVal == 'RemoveOptris':
                    Data      = zeros(1, dtype='uint32')
                    Data[0]   = uint32(varargin[1]);
                
                    Ret         =   self.CmdSend(0, int('0x611C',0), Data, 0)
                    Ret         =   self.CmdRecv();
            
    def     AddVideo(self, Add):
        print('AddVideo is obsolete, please use RadServe_ListCameras() to receive camera list and RadServe_SelectCamera(<id>, <rate>, <name>) to select a camera');
        
    def     GetVideoProperties(self, VidIdx=0):
        Vid = dict();
        if (0 <= VidIdx and VidIdx <= len(self.hConVideo)):
            Vid['Rate'] = self.cVideoRate[VidIdx];
            Vid['Cols'] = self.cVideoCols[VidIdx];
            Vid['Rows'] = self.cVideoRows[VidIdx];
            Vid['Chns'] = self.cVideoChn[VidIdx];
            Vid['Name'] = self.cVideoName[VidIdx];
        else:
            Vid['Rate'] = 0;
            Vid['Cols'] = 0;
            Vid['Rows'] = 0;
            Vid['Chns'] = 0;
            Vid['Name'] = "";
        return Vid;
        
    def     GetAllVideoProperties(self):
        Ret = [];
        
        for VidIdx in range(0, len(self.hConVideo)):
            Vid = dict();
            Vid['Rate'] = self.cVideoRate[VidIdx];
            Vid['Cols'] = self.cVideoCols[VidIdx];
            Vid['Rows'] = self.cVideoRows[VidIdx];
            Vid['Chns'] = self.cVideoChn[VidIdx];
            Vid['Name'] = self.cVideoName[VidIdx];
            Ret.append(Vid);
    
        return Ret;
                    
    def     DispVideo(self, VidIdx=0):
        if (0 <= VidIdx and VidIdx < len(self.hConVideo)):
            if (self.hConVideo[VidIdx] > 0 and self.cVideoRate[VidIdx] != 0):
                if ((self.cDataIdx) % self.cVideoRate[VidIdx] == 0):
                    Len = self.cVideoSize[VidIdx];
                    inp = numpy.zeros(Len, dtype='uint8')
                    Idx = 0;
                
                    while (Len > 0):
                        tmp = self.cRadVideoSocket[VidIdx].recv(Len);
                        tmpLen = len(tmp);
                        if (tmpLen == 0):
                            Len = -1;
                        else:
                            inp[Idx:Idx+tmpLen] = fromstring(tmp, dtype='uint8');
                            Idx = Idx + tmpLen;
                            Len = Len - tmpLen;			
                
                    if (len(inp) == self.cVideoSize[VidIdx]):
                        inp = reshape(inp, (self.cVideoRows[VidIdx], self.cVideoCols[VidIdx], self.cVideoChn[VidIdx]));
#                        cv2.imshow(self.cVideoName[VidIdx], inp);
                        return True;
        return False;
                    
    def     DispAllVideos(self):
        dispVid = False;
        for VidIdx in range(0, len(self.hConVideo)):
            readVid = False;
            sockPoll = [ self.cRadVideoSocket[VidIdx] ];
            if (self.hConVideo[VidIdx] > 0 and self.cVideoRate[VidIdx] != 0):
                if self.cExtSize == 0:
                    ## cDataIdx is in mult frames, videoRate is in mult frames
                    if ((self.cDataIdx / self.cMult) % self.cVideoRate[VidIdx] == 0):
                        readVid = True;
                else:
                    ## cDataIdx is in extMult frames, videoRate is in mult frames
                    if ( ( ((self.cDataIdx + 1) * self.cExtMult) - self.cVideoFrmsColl[VidIdx] * self.cMult ) / (self.cVideoRate[VidIdx] * self.cMult) >= 1):
                        readVid = True;
                
                if readVid:
                    Len = self.cVideoSize[VidIdx];
                    inp = numpy.zeros(Len, dtype='uint8')
                    Idx = 0;
                    
                    rdSock, wrSock, errSock = sockSelect.select(sockPoll, [], [], 0);
                    if (len(rdSock) == 1 and rdSock[0] == self.cRadVideoSocket[VidIdx]):
                        while (Len > 0):
                            tmp = self.cRadVideoSocket[VidIdx].recv(Len);
                            tmpLen = len(tmp);
                            if (tmpLen == 0):
                                Len = -1;
                            else:
                                inp[Idx:Idx+tmpLen] = fromstring(tmp, dtype='uint8');
                                Idx = Idx + tmpLen;
                                Len = Len - tmpLen;				
                        
                        if (len(inp) == self.cVideoSize[VidIdx]):
                            self.cVideoFrmsColl[VidIdx] = self.cVideoFrmsColl[VidIdx] + 1;
                            inp = reshape(inp, (self.cVideoRows[VidIdx], self.cVideoCols[VidIdx], self.cVideoChn[VidIdx]));
#                            cv2.imshow(self.cVideoName[VidIdx], inp);
                            dispVid = True;
        return dispVid;

    def     GetVideo(self, VidIdx=0):
        if (0 <= VidIdx and VidIdx <= len(self.hConVideo)):
            if (self.hConVideo[VidIdx] > 0 and self.cVideoRate[VidIdx] != 0):
                if ((self.cDataIdx + 1) % self.cVideoRate[VidIdx] == 0):
                    Len = self.cVideoSize[VidIdx];
                    inp = numpy.zeros(Len, dtype='uint8')
                    Idx = 0;
                
                    while (Len > 0):
                        tmp = self.cRadVideoSocket[VidIdx].recv(Len);
                        tmpLen = len(tmp);
                        if (tmpLen == 0):
                            Len = -1;
                        else:
                            inp[Idx:Idx+tmpLen] = fromstring(tmp, dtype='uint8');
                            Idx = Idx + tmpLen;
                            Len = Len - tmpLen;				
                
                    if (len(inp) == self.cVideoSize[VidIdx]):
                        inp = reshape(inp, (self.cVideoRows[VidIdx], self.cVideoCols[VidIdx], self.cVideoChn[VidIdx]));
                        return inp;
        return [];
                    
    def     GetAllVideos(self):
        inp = [];
        for VidIdx in range(0, len(self.hConVideo)):
            if (self.hConVideo[VidIdx] > 0 and self.cVideoRate[VidIdx] != 0):
                if ((self.cDataIdx + 1) % self.cVideoRate[VidIdx] == 0):
                    Len = self.cVideoSize[VidIdx];
                    img = numpy.zeros(Len, dtype='uint8')
                    Idx = 0;
                    
                    while (Len > 0):
                        tmp = self.cRadVideoSocket[VidIdx].recv(Len);
                        tmpLen = len(tmp);
                        if (tmpLen == 0):
                            Len = -1;
                        else:
                            img[Idx:Idx+tmpLen] = fromstring(tmp, dtype='uint8');
                            Idx = Idx + tmpLen;
                            Len = Len - tmpLen;				
                    
                    if (len(img) == self.cVideoSize[VidIdx]):
                        img = reshape(img, (self.cVideoRows[VidIdx], self.cVideoCols[VidIdx], self.cVideoChn[VidIdx]));
                        inp.append(img);
                else:
                    inp.append([0]);
            else:
                inp.append([0]);
        return inp;
