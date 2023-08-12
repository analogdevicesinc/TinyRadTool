import  src.proc_modes.ModFmcw as ModFmcw
import  src.proc_modes.ModRangeDoppler as ModRangeDoppler
import  src.proc_modes.ModBpa as ModBpa
import  src.proc_modes.ModTarDet as ModTarDet
import  src.proc_modes.ModCal as ModCal
import  src.proc_modes.ModPerf as ModPerf
import  src.proc_modes.CfgStatus as CfgStatus
import  src.cmd_modules.StrConv as StrConv

import  src.ui.setupBoard as setupBoard
import  src.ui.about as aboutdialog
import  src.ui.StrtupBrd as StrtupBrd
import  src.ui.fwupgrd as FwUpgrdDialog
import  src.cmd_modules.TinyRad as TinyRad

from PyQt5 import QtCore, QtGui, QtWidgets

import  numpy as np

__version__ = "0.0.1"

class   StackGui(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(StackGui, self).__init__(parent)

        self.GuiTitle = "TinyRadTool GUI"
        self.stFileCfg = "c:/Tools/TinyRadTool/Default.rtc"
        self.stFolderCfg = "c:/Tools/TinyRadTool/"
        self.GuiEnaViewFmcw = True
        self.GuiEnaViewRangeDoppler =   True
        self.GuiEnaViewDBF = True
        self.GuiEnaViewStatus = True
        self.GuiEnaViewPerf = True
        self.GuiEnaViewTarDet = False
        self.GuiEnaViewCal = False
        self.LicenseIsValid = False
        self.GuiFontSiz = 14
        self.GuiViewIdx = 0
        self.GuiSelIni = False
        self.GuiAgree = False

        self.Lim_fMin = 24.010e9
        self.Lim_fMax = 24.240e9

        self.hTinyRad = TinyRad.TinyRad()
        
        Dialog = StrtupBrd.StrtupBrd(self)
        Dialog.exec_()
        
        if self.GuiAgree:

            if self.GuiSelIni:
                print("Parse configuration file")
                self.GuiParseCfgFile(self.stFileCfg)

        else:
            self.GuiEnaViewFmcw = False
            self.GuiEnaViewRangeDoppler =   False
            self.GuiEnaViewDBF = False
            self.GuiEnaViewCal = False
            self.GuiEnaViewTarDet = False

        # --------------------------------------------------------------------------------------
        # License Check is removed in newer versions
        # --------------------------------------------------------------------------------------
        self.LicenseIsValid = True

        self.InitMenu()
        self.StackedWidget_Form = QtWidgets.QStackedWidget()
        self.lView = list();


        #--------------------------------------------------------------------------------------
        # FMCW
        #--------------------------------------------------------------------------------------
        if self.GuiEnaViewFmcw and self.LicenseIsValid:
            self.PageFmcw = ModFmcw.ModFmcw(self)
            self.StackedWidget_Form.addWidget(self.PageFmcw.TabContWidget)
            self.lView.append(('Fmcw', 'self.setFmcwWindow()'))

        #--------------------------------------------------------------------------------------
        # Range Doppler
        #--------------------------------------------------------------------------------------
        if self.GuiEnaViewRangeDoppler and self.LicenseIsValid:
            self.PageRangeDoppler = ModRangeDoppler.ModRangeDoppler(self)
            self.StackedWidget_Form.addWidget(self.PageRangeDoppler.TabContWidget)
            self.lView.append(('RangeDoppler', 'self.setRangeDopplerWindow()'))

        #--------------------------------------------------------------------------------------
        # Mimo with BPA
        #--------------------------------------------------------------------------------------
        if self.GuiEnaViewDBF and self.LicenseIsValid:
            print("DBF:", self.GuiEnaViewDBF)
            self.PageBpa = ModBpa.ModBpa(self)
            self.StackedWidget_Form.addWidget(self.PageBpa.TabContWidget)
            self.lView.append(('DBF', 'self.setDBFWindow()'))

        #--------------------------------------------------------------------------------------
        # Mimo with TarDet
        #--------------------------------------------------------------------------------------
        if self.GuiEnaViewTarDet and self.LicenseIsValid:
            print("TarDet:", self.GuiEnaViewTarDet)
            self.PageTarDet = ModTarDet.ModTarDet(self)
            self.StackedWidget_Form.addWidget(self.PageTarDet.TabContWidget)
            self.lView.append(('TarDet', 'self.setTarDetWindow()'))

        #--------------------------------------------------------------------------------------
        # Performance Analysis
        #--------------------------------------------------------------------------------------
        if self.GuiEnaViewPerf and self.LicenseIsValid:
            print("OPerf:", self.GuiEnaViewTarDet)
            self.PagePerf = ModPerf.ModPerf(self)
            self.StackedWidget_Form.addWidget(self.PagePerf.TabContWidget)
            self.lView.append(('Perf', 'self.SetPerfWindow()'))

        #--------------------------------------------------------------------------------------
        # Set Configuration an Status Page
        #--------------------------------------------------------------------------------------
        if self.GuiEnaViewStatus:
            self.PageStatus = CfgStatus.CfgStatus(self)
            self.StackedWidget_Form.addWidget(self.PageStatus.TabContWidget)
            self.lView.append(('Status', 'self.setStatusWindow()'))

        #--------------------------------------------------------------------------------------
        # Set Calibration Page
        #--------------------------------------------------------------------------------------
        if self.GuiEnaViewCal and self.LicenseIsValid:
            self.PageCal = ModCal.ModCal(self)
            self.StackedWidget_Form.addWidget(self.PageCal.TabContWidget)
            self.lView.append(('Cal', 'self.SetCalWindow()'))

        #--------------------------------------------------------------------------------------
        # Define Main Window
        #--------------------------------------------------------------------------------------

        Layout_Form = QtWidgets.QVBoxLayout()
        Layout_Form.addWidget(self.StackedWidget_Form)

        centralWidget               = QtWidgets.QWidget()
        centralWidget.setLayout(Layout_Form)
        self.setCentralWidget(centralWidget)

        #self.StackedWidget_Form.resize(800,800)
        self.center()
        if self.GuiViewIdx  < 0:
            self.GuiViewIdx = 0
        if self.GuiViewIdx >= len(self.lView):
            self.GuiViewIdx = len(self.lView) - 1
            
        Elem = self.lView[self.GuiViewIdx]

        exec(Elem[1])

    def GuiParseCfgFile(self, stFile):
        if len(stFile) > 1:
            File = open(stFile, "r", encoding="utf-8", errors="ignore")
            lCmd = list()
            lCmd.append((r"Gui_SetTitle\((?P<Val>('[a-zA-Z0-9 \-\(\)_?!]+'))\)", "self.GuiTitle", "Var"))
            lCmd.append((r"Gui_EnaViewFmcw\((?P<Val>(True|False))\)", "self.GuiEnaViewFmcw", "Var"))
            lCmd.append((r"Gui_EnaViewRangeDoppler\((?P<Val>(True|False))\)", "self.GuiEnaViewRangeDoppler", "Var"))
            lCmd.append((r"Gui_EnaViewDBF\((?P<Val>(True|False))\)", "self.GuiEnaViewDBF", "Var"))
            lCmd.append((r"Gui_EnaViewStatus\((?P<Val>(True|False))\)", "self.GuiEnaViewStatus", "Var"))
            lCmd.append((r"Gui_EnaViewCal\((?P<Val>(True|False))\)", "self.GuiEnaViewCal", "Var"))
            lCmd.append((r"Gui_SetFontSiz\((?P<Val>([0-9]{1,2}))\)", "self.GuiFontSiz", "Var"))
            #lCmd.append((r"Gui_SetViewIdx\((?P<Val>([0-9]{1,1}))\)", "self.GuiViewIdx", "Var"))
            for stLine in File:
                Ret = StrConv.ConvStrToCmd(stLine, lCmd)
                if Ret[0]:
                    exec(Ret[1])

                                                        
    def SetWidgetMode(self, Txt):
        pass
        print("Mode changed: %s" % Txt)

    def InitMenu(self):
        exitAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtWidgets.qApp.quit)

        if self.GuiEnaViewStatus:
            SysAction      = QtWidgets.QAction('System Config',self)
            SysAction.triggered.connect(self.setStatusWindow)

        menubar = self.menuBar()
        sysMenu = menubar.addMenu('&System')
        if self.GuiEnaViewStatus:
            sysMenu.addAction(SysAction)
        fwUpdate = QtWidgets.QAction('&Firmware Upgrade', self)
        fwUpdate.triggered.connect(self.openFwUpgrdDialog)
        sysMenu.addAction(fwUpdate)
        sysMenu.addAction(exitAction)
        modMenu = menubar.addMenu('&Modes')

        if self.GuiEnaViewFmcw and self.LicenseIsValid:
            modFMCW         = QtWidgets.QAction('&FMCW',self)
            modFMCW.setShortcut('Ctrl+2')
            modFMCW.triggered.connect(self.setFmcwWindow)
        if self.GuiEnaViewRangeDoppler and self.LicenseIsValid:
            modRangeDoppler = QtWidgets.QAction('&Range-Doppler',self)
            modRangeDoppler.setShortcut('Ctrl+3')
            modRangeDoppler.triggered.connect(self.setRangeDopplerWindow)
        if self.GuiEnaViewDBF and self.LicenseIsValid:
            modDBF          = QtWidgets.QAction('&DBF',self)
            modDBF.setShortcut('Ctrl+4')
            modDBF.triggered.connect(self.setDBFWindow)
        if self.GuiEnaViewTarDet and self.LicenseIsValid:
            modTarDet       = QtGui.QAction('&Target-Detection',self)
            modTarDet.setShortcut('Ctrl+5')
            modTarDet.triggered.connect(self.setTarDetWindow)            
        if self.GuiEnaViewCal and self.LicenseIsValid:
            modCal          = QtWidgets.QAction('&Calibration',self)
            modCal.triggered.connect(self.SetCalWindow)
        if self.GuiEnaViewPerf and self.LicenseIsValid:
            modPerf          = QtWidgets.QAction('&Performance Estimation',self)
            modPerf.triggered.connect(self.SetPerfWindow)            

        if self.GuiEnaViewFmcw and self.LicenseIsValid:
            modMenu.addAction(modFMCW)
        if self.GuiEnaViewRangeDoppler and self.LicenseIsValid:
            modMenu.addAction(modRangeDoppler)
        if self.GuiEnaViewDBF and self.LicenseIsValid:
            modMenu.addAction(modDBF)
        if self.GuiEnaViewTarDet and self.LicenseIsValid:
            modMenu.addAction(modTarDet)            
        if self.GuiEnaViewCal and self.LicenseIsValid:
            modMenu.addAction(modCal)
        if self.GuiEnaViewPerf and self.LicenseIsValid:
            modMenu.addAction(modPerf)


        infoAbout = QtWidgets.QAction('&About',self)
        infoAbout.triggered.connect(self.openAboutDialog)
        infoMenu = menubar.addMenu('&Info')
        infoMenu.addAction(infoAbout)



    def openSetupDialog(self):
        u = setupBoard.SetupBoard(self)
        if u.exec_() == QtGui.QDialog.Accepted:
            pass
            #print("dialog accept")
            # update view/info:
    def FindViewIdx(self, stWin):
        Idx = 0
        FindIdx = 0 
        for Elem in self.lView:
            if Elem[0]  == stWin:
                FindIdx = Idx
            Idx = Idx + 1   
        
        return FindIdx


    def setFmcwWindow(self):
        self.StackedWidget_Form.setCurrentIndex(self.FindViewIdx('Fmcw'))
        self.PageFmcw.IniForm()
        self.PageFmcw.IniGui()


    def setRangeDopplerWindow(self):
        self.StackedWidget_Form.setCurrentIndex(self.FindViewIdx('RangeDoppler'))
        self.PageRangeDoppler.IniForm()
        self.PageRangeDoppler.IniGui()


    def setDBFWindow(self):
        self.StackedWidget_Form.setCurrentIndex(self.FindViewIdx('DBF'))
        self.PageBpa.IniForm()
        self.PageBpa.IniGui()

    def setTarDetWindow(self):
        self.StackedWidget_Form.setCurrentIndex(self.FindViewIdx('TarDet'))
        self.PageTarDet.IniForm()
        self.PageTarDet.IniGui()

    def setStatusWindow(self):
        self.StackedWidget_Form.setCurrentIndex(self.FindViewIdx('Status'))
        self.PageStatus.IniForm()
        self.PageStatus.IniGui()

    def SetCalWindow(self):
        self.StackedWidget_Form.setCurrentIndex(self.FindViewIdx('Cal'))
        self.PageCal.IniForm()
        self.PageCal.IniGui()

    def SetPerfWindow(self):
        self.StackedWidget_Form.setCurrentIndex(self.FindViewIdx('Perf'))
        self.PagePerf.IniForm()
        self.PagePerf.IniGui()        

    def openAboutDialog(self):
        u = aboutdialog.AboutDialog()
        u.exec_()

    def openFwUpgrdDialog(self):
        u = FwUpgrdDialog.FwUpgrdDialog(self)
        u.exec_()

    def center(self):
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        self.move(centerPoint.x() - self.width() * 0.5, centerPoint.y() - self.height() * 0.5)

    def cleanUp(self):
        for i in self.__dict__:
            item = self.__dict__[i]
            clean(item)

def clean(item):
    if isinstance(item, list) or isinstance(item, dict):
        for Idx in range(len(item)):
            pass
            #clean(item.popitem())
    else:
        try:
            item.close()
        except (RuntimeError, AttributeError):
            pass
