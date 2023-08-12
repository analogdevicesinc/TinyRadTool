import os
import sys
import re
import pickle
from PyQt5 import QtCore, QtGui, QtWidgets
import src.ui.ui_fwupgrd as ui_fwupgrd
import  src.logger.Logger as Logger
import hashlib
import threading
from numpy import *
import src.cmd_modules.FrmwImg
from src.cmd_modules.FrmwImg import FirmwareImage

""" Firmware Upgrade Dialog handler
Calls the UI Class Dialog
"""
class FwUpgrdDialog(QtWidgets.QDialog, ui_fwupgrd.Ui_UpgradeDialog):
    SigDoneUpgrade = QtCore.pyqtSignal()
    SigUpdateProgress = QtCore.pyqtSignal(int)

    def __init__(self, patre):
        super(FwUpgrdDialog, self).__init__()
        self.patre = patre
        self.setupUi(self)
        self.pushButton_start_upgrade.setEnabled(False)
        self.progressBar_progress.setValue(0)

        self.FilesAvailable = False
        self.lFile = list()
        self.TinyRad = self.patre.hTinyRad
        self.pushButton_start_upgrade.setDisabled(True)
        self.checkBox_agree.setDisabled(True)
        self.center()
        self.Log = Logger.Logger(self.textEdit_progress)
        self.progressBar_progress.setRange(0,64)
        self.SigDoneUpgrade.connect(self.SigActionUpgradeDone)
        self.SigUpdateProgress.connect(self.SigActionUpdateProgress)
        self.ListFiles()
        self.assignWidgets()

    def center(self):
        """ Moves the Dialog to the center of the screen """
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        self.move(centerPoint.x() - self.width() * 0.5, centerPoint.y() - self.height() * 0.5)

    def assignWidgets(self):
        """ Register close Button Signalhandler """
        self.pushButton_close.clicked.connect(self.pushButton_close_clicked)
        self.pushButton_start_upgrade.clicked.connect(self.pushButton_start_upgrade_clicked)
        self.checkBox_agree.clicked.connect(self.checkBox_agree_clicked)
        self.comboBox_select_image.currentIndexChanged.connect(self.comboBox_select_image_changed)

    def pushButton_close_clicked(self):
        """ Called when the "close" pushbutton was pressed.
        closes the window
        """
        self.accept()

    def comboBox_select_image_changed(self):
        if self.FilesAvailable:
            self.textBrowser_ReleaseNotes.clear()
            Idx = self.comboBox_select_image.currentIndex()
            with open(self.lFile[Idx], 'rb') as f:
                FwImage = pickle.load(f)
                try:
                    self.textBrowser_ReleaseNotes.append("Release Date: " + FwImage.ReleaseDate)
                    self.textBrowser_ReleaseNotes.append(
                        "Version: " + str(FwImage.VersInfo["SwMaj"]) + "." + str(FwImage.VersInfo["SwMin"]) + "." + str(
                            FwImage.VersInfo["SwPatch"]))
                    for Note in FwImage.ReleaseNotes:
                        self.textBrowser_ReleaseNotes.append(Note)
                except AttributeError:
                    print("Invalid Image selected")
                    self.Log.Append("Invalid Image selected")
                    self.Log.SigUpd.emit()

    def pushButton_start_upgrade_clicked(self):
        self.pushButton_start_upgrade.setDisabled(True)
        self.pushButton_close.setDisabled(True)
        self.progressBar_progress.setValue(0)
        self.Button_StartUpgrade()

    def checkBox_agree_clicked(self):
        self.pushButton_start_upgrade.setEnabled(self.checkBox_agree.isChecked())

    def start_upgrade(self):
        print("Start upgrade clicked")
        if self.FilesAvailable:
            Idx = self.comboBox_select_image.currentIndex()
            print("Using FW: " + self.lFile[Idx])
            VersInfo = self.TinyRad.BrdGetSwVers()
            self.Log.Append("=== FW Upgrade ===")
            self.Log.Append("Current Firmware Version: " + str(VersInfo["SwMaj"]) + "." + str(VersInfo["SwMin"]) + "." + str(VersInfo["SwPatch"]))
            self.Log.SigUpd.emit()
            setattr(sys.modules["__main__"], "FirmwareImage", type(FirmwareImage()))
            with open(self.lFile[Idx], 'rb') as f:
                FwImage = pickle.load(f)
                try:
                    # Check if Firmware Version, if it is the same, do not upgrade.
                    self.Log.Append("Selected Firmware Version: " + str(FwImage.VersInfo["SwMaj"]) + "." + str(FwImage.VersInfo["SwMin"]) + "." + str(FwImage.VersInfo["SwPatch"]))
                    self.Log.SigUpd.emit()
                    if VersInfo["SwMaj"] == FwImage.VersInfo["SwMaj"] and VersInfo["SwMin"] == FwImage.VersInfo["SwMin"] and VersInfo["SwPatch"] == FwImage.VersInfo["SwPatch"]:
                        self.Log.Append("Board Firmware Version is same as selected Image.")
                        self.Log.Append("Aborting...")
                        self.Log.SigUpd.emit()
                        self.SigDoneUpgrade.emit()
                        return
                    elif VersInfo["SwMaj"] == -1:
                        self.Log.Append("Board not found or responding.")
                        self.Log.Append("Aborting...")
                        self.Log.SigUpd.emit()
                        self.SigDoneUpgrade.emit()
                        return
                    elif VersInfo["SwMaj"] <= 1 and VersInfo["SwMin"] < 2:
                        self.Log.Append("Board Firmware does not support Firmware Updates.")
                        self.Log.Append("Aborting...")
                        self.Log.SigUpd.emit()
                        self.SigDoneUpgrade.emit()
                        return

                    # Compare Hash (Calculated and stored in Image
                    self.Log.Append("Verifying Image Data...")
                    hFwImage = hashlib.sha256()
                    for Block in FwImage.ImageData:
                        for Sector in Block:
                            hFwImage.update(Sector)
                    self.Log.Append("Calculated Hash: " + hFwImage.hexdigest())
                    self.Log.Append("Stored Hash: " + FwImage.ImageSha256)
                    if hFwImage.hexdigest() != FwImage.ImageSha256:
                        self.Log.Append("Hash mismatch!")
                        self.Log.Append("Aborting...")
                        self.Log.SigUpd.emit()
                        self.SigDoneUpgrade.emit()
                        return
                    self.Log.Append("Hash Ok.")
                    self.Log.SigUpd.emit()
                    # Backup Calibration Data
                    self.Log.Append("Backing up Calibration Data...")
                    self.Log.SigUpd.emit()
                    self.TmpCalDat = self.TinyRad.BrdGetCalDat()
                    self.Log.Append("CalData Ok.")
                    # Erase Chip
                    self.Log.Append("Erasing Flash Memory...")
                    self.Log.SigUpd.emit()
                    self.TinyRad.Dsp_FmwrUpdtRmFlsh()
                    self.Log.Append("Erase Ok.")
                    # Write Data to Board
                    self.Log.Append("Writing Firmware, do not unplug...")
                    self.Log.SigUpd.emit()
                    self.WriteImage(FwImage.ImageData)
                    self.Log.Append("Write complete.")
                    # Read Back Image Data
                    self.Log.Append("Reading Firmware from Device...")
                    self.Log.SigUpd.emit()
                    self.SigUpdateProgress.emit(0)
                    TmpImage = self.ReadImage()
                    self.Log.Append("Read complete.")
                    self.Log.Append("Verifying Flash Device Data...")
                    self.Log.SigUpd.emit()
                    # Verify Device Data from Hash
                    hTmpImage = hashlib.sha256()
                    for Block in TmpImage:
                        for Sector in Block:
                            hTmpImage.update(Sector)
                    if hTmpImage.hexdigest() != FwImage.ImageSha256:
                        self.Log.Append("Hash mismatch!")
                        self.Log.Append("Aborting...")
                        self.Log.SigUpd.emit()
                        self.SigDoneUpgrade.emit()
                        return
                    self.Log.Append("Hash Ok.")
                    self.Log.SigUpd.emit()
                    # Restore Calibration Data
                    #self.Log.Append("Restoring Calibration Data...")
                    #self.Log.SigUpd.emit()
                    #self.TinyRad.BrdSetCalDat(self.TmpCalDat)
                    #self.Log.Append("CalData Ok.")
                    self.Log.Append("=== Upgrade Complete ===")
                    self.Log.Append("You can now reset the device.")
                    self.Log.SigUpd.emit()
                    # Re-Enable Buttons
                    self.SigDoneUpgrade.emit()

                except AttributeError:
                    self.Log.Append("Invalid Image Data")
                    self.Log.SigUpd.emit()
                    self.SigDoneUpgrade.emit()

    def SigActionUpgradeDone(self):
        self.progressBar_progress.setValue(64)
        self.pushButton_start_upgrade.setDisabled(False)
        self.pushButton_close.setDisabled(False)

    def SigActionUpdateProgress(self, value):
        self.progressBar_progress.setValue(value)

    def Button_StartUpgrade(self):
        self.WriteThread = threading.Thread(target=self.start_upgrade)
        self.WriteThread.start()

    def ListFiles(self):
        print("Reading Files in Directory")
        UpgrdFiles = False
        
        if len(sys.argv) > 2:
            print(sys.argv[2])
            print("Path argument specified: " + sys.argv[2])
            if os.path.exists(sys.argv[2]):
                stCfgPath   = sys.argv[2]
                lDir        = os.listdir(stCfgPath)
                RegExp      = re.compile(r"(?P<Name>([a-zA-Z0-9\-_]+))[.]{1,1}(?P<Ext>(img))")
                for Elem in lDir:
                    Match = RegExp.search(Elem)
                    if Match:
                        self.FilesAvailable     = True
                        stName                  = Match.group("Name")
                        stExt                   = Match.group("Ext")
                        stFileDesc              = self.ParseForDescription(stCfgPath + "/" + Elem)
                        self.comboBox_select_image.addItem(stName + " : " + stFileDesc)
                        self.lFile.append(stCfgPath + "/" + Elem)
                    else:
                        print("No Match: " + Elem)

        if len(self.lFile) > 0:
            UpgrdFiles = True
            self.textBrowser_ReleaseNotes.clear()
            Idx = 0
            with open(self.lFile[Idx], 'rb') as f:
                FwImage = pickle.load(f)
                try:
                    self.textBrowser_ReleaseNotes.append("Release Date: " + FwImage.ReleaseDate)
                    self.textBrowser_ReleaseNotes.append(
                        "Version: " + str(FwImage.VersInfo["SwMaj"]) + "." + str(FwImage.VersInfo["SwMin"]) + "." + str(
                            FwImage.VersInfo["SwPatch"]))
                    for Note in FwImage.ReleaseNotes:
                        self.textBrowser_ReleaseNotes.append(Note)
                except AttributeError:
                    print("Invalid Image selected")
                    self.Log.Append("Invalid Image selected")
                    self.Log.SigUpd.emit()

            self.checkBox_agree.setDisabled(False)

        if not UpgrdFiles:
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.darkRed)
            self.label_info.setPalette(palette)
            self.label_info.setText("No Firmware Image Files found.")


    def ParseForDescription(self, stFile):
        if len(stFile) > 1:
            setattr(sys.modules["__main__"], "FirmwareImage", type(FirmwareImage()))
            with open(stFile, 'rb') as f:
                image = pickle.load(f)
                try:
                    self.Title = str(image.VersInfo["SwMaj"]) + "." + str(image.VersInfo["SwMin"]) + "." + str(image.VersInfo["SwPatch"])
                except AttributeError:
                    print("Invalid Image Data")
                    self.Title = "No Title"
        return self.Title

    def ReadSector(self, block, sector):
        TmpData = zeros(self.TinyRad.FrmwrFlshSzSctrByts, dtype='uint8')
        for i in range(0, self.TinyRad.FrmwrFlshSzSctrByts, self.TinyRad.FrmwrRdSz):
            rd_data = self.TinyRad.Dsp_FmwrUpdtRdPt(block, sector, i)
            TmpData[i:i + self.TinyRad.FrmwrRdSz] = rd_data[1]
        return TmpData

    def ReadBlock(self, block):
        TmpData = [[] for _ in range(self.TinyRad.FrmwrFlshNrSctrs)]
        for Sector in range(self.TinyRad.FrmwrFlshNrSctrs):
            TmpData[Sector] = self.ReadSector(block, Sector)
        return TmpData

    def ReadImage(self):
        TmpData = [[] for _ in range(self.TinyRad.FrmwrFlshNrBlcks)]
        for Block in range(self.TinyRad.FrmwrFlshNrBlcks):
            TmpData[Block] = self.ReadBlock(Block)
            self.Log.Append("Read Block " + str(Block + 1) + "/" + str(self.TinyRad.FrmwrFlshNrBlcks) + " ...")
            self.Log.SigUpd.emit()
            self.SigUpdateProgress.emit(Block + 1)
        return TmpData

    def WriteSector(self, block, sector, sector_data):
        if len(sector_data) != self.TinyRad.FrmwrFlshSzSctrByts:
            print("Invalid Sector Data")
            return -1
        for SectorPart in range(0, self.TinyRad.FrmwrFlshSzSctrByts, self.TinyRad.FrmwrRdSz):
            self.TinyRad.Dsp_FmwrUpdtWrPt(block, sector, SectorPart, sector_data[SectorPart:SectorPart + self.TinyRad.FrmwrRdSz])
        return 0

    def WriteBlock(self, block, block_data):
        if len(block_data) != self.TinyRad.FrmwrFlshNrSctrs:
            print("Invalid Block Data")
            return -1
        for Sector in range(self.TinyRad.FrmwrFlshNrSctrs):
            self.WriteSector(block, Sector, block_data[Sector])
        return 0

    def WriteImage(self, image_data):
        if len(image_data) != self.TinyRad.FrmwrFlshNrBlcks:
            print("Invalid Image Data")
            return -1
        for Block in range(self.TinyRad.FrmwrFlshNrBlcks):
            self.WriteBlock(Block, image_data[Block])
            self.Log.Append("Wrote Block " + str(Block + 1) + "/" + str(self.TinyRad.FrmwrFlshNrBlcks) + " ...")
            self.Log.SigUpd.emit()
            self.SigUpdateProgress.emit(Block + 1)
        return 0
