# Mimo77 -- Class for 77-GHz Radar with Waveguide transition 
#
# Copyright (C) 2015-11 Inras GmbH Haderer Andreas
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.
#import  src.cmd_modules.Radarbook   as Radarbook

# import  h5py
from    numpy import *


class FileStore():
    """ Mimo77 class object:
        (c) Haderer Andreas Inras GmbH
    """
    def __init__(self, stFile):
        self.stFile     =   stFile

    def     ReadDict(self, stDict):
        print("Read Dict: ", stDict, self.stFile)

        hFile   =   h5py.File(self.stFile, 'r')
        dRes    =   dict()  
        for Key in hFile.keys():
            print('Key: ', Key)
            if Key == stDict:
                for Vals    in  hFile[Key].items():  
                    if isinstance(Vals[1], h5py.Dataset):
                        FileEntry       =   (hFile.get(Key + '/' + Vals[0]))
                        if FileEntry.size == 1:
                            with FileEntry.astype('double'):
                                dRes[Vals[0]]   =   double(FileEntry)
                        else:
                            dRes[Vals[0]]       =   array(FileEntry)
                    if isinstance(Vals[1], h5py.Group):
                        print('Is group')
                        dTmp        =   dict()
                        for GVals   in  hFile[Key + '/' + Vals[0]].items(): 
                            if isinstance(GVals[1], h5py.Dataset):
                                FileEntry       =   hFile.get(Key + '/' + Vals[0] + '/' + GVals[0])
                                if FileEntry.dtype == object:
                                    print("Is object")
                                else:
                                    if FileEntry.size == 1:
                                        with FileEntry.astype('double'):
                                            dTmp[GVals[0]]   =   double(FileEntry)
                                    else:
                                        TmpArray            =   array(FileEntry)
                                        TmpArray            =   TmpArray.reshape(FileEntry.shape)
                                        dTmp[GVals[0]]      =   TmpArray.transpose()

                        dRes[Vals[0]]       =   dTmp

        return dRes
        # for G1 in hFile.keys():
        #     print(": ", G1)
        #     print("Name: ", hFile[G1])
        #     for G2 in hFile[G1].keys():
        #         print("::", G2) 
        #         for G3 in hFile[G1 + '/' + G2].keys():
        #             print("  ::: ", G3) 

    def     Store(self, *varargin):

        # Check if number of arguments is even
        if (len(varargin) % 2) == 1:
            return None

        NArg    =   int(len(varargin)/2)

        with h5py.File(self.stFile,'w') as hFile:

            for Idx in range(0,NArg):
                if isinstance(varargin[2*Idx],str):
                    stName  =   varargin[2*Idx]

                    if isinstance(varargin[2*Idx+1], dict):
                        dCfg    =   varargin[2*Idx+1]
                        
                        for Key in dCfg:
                            print("Store Key: ", stName + '/' + str(Key))
                            if isinstance(dCfg[Key], dict):
                                dEntr       =   dCfg[Key]
                                for Key1 in dEntr:
                                    if isinstance(dEntr[Key1], ndarray):
                                        hFile.create_dataset(stName + '/' + str(Key) + '/' + str(Key1), data = dEntr[Key1].transpose())           
                                    else:
                                        print("Store Key: ", stName + '/' + str(Key) + '/' + str(Key1))
                                        hFile.create_dataset(stName + '/' + str(Key) + '/' + str(Key1), data = dEntr[Key1])    
                            elif isinstance(dCfg[Key], ndarray):
                                print("Store Array")
                                hFile.create_dataset(stName + '/' + str(Key), data = dCfg[Key].transpose())
                            else:
                                hFile.create_dataset(stName + '/' + str(Key), data = dCfg[Key])
                    else:
                        print("Store Data: ", stName)
                        Data    =   varargin[2*Idx+1]
                        hFile.create_dataset(stName, data = Data.transpose)
                        