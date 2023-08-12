from PyQt5 import QtCore, QtGui, QtWidgets
import  pyqtgraph as pg
import  src.ui.ui_Strtup as ui_Strtup
import  re
import  os
from    os import listdir
import  src.cmd_modules.StrConv as StrConv
import  sys


class StrtupBrd(QtWidgets.QDialog, ui_Strtup.Ui_Strtup):

    def __init__(self, patre):
        super(StrtupBrd, self).__init__()
        self.patre  = patre
        self.setupUi(self)
        #self.initLabels()
        self.assignWidgets()
        self.CenterWindow()
        self.lFile              =   list()
        self.FilesAvailable     =   False

        self.ListFiles()
        
    def ListFiles(self):

        stCfgPath   =   self.patre.stFolderCfg
        AnaFiles    =   False  
        if len(sys.argv) > 2:
            print("Path argument spefified: ", sys.argv[2])
            if os.path.exists(sys.argv[2]):
                stCfgPath   =   sys.argv[2]   
                lDir        =   listdir(stCfgPath)     
                print("Dir:", lDir)
                RegExp      =   re.compile(r"(?P<Name>([a-zA-Z0-9\-_]+))[.]{1,1}(?P<Ext>(rtc))")
                for Elem in lDir:
                    Match           =               RegExp.search(Elem)
                    if Match:
                        self.FilesAvailable     =   True
                        stName                  =   Match.group("Name")
                        stExt                   =   Match.group("Ext")

                        stFileDesc              =   self.ParseForDescription(stCfgPath + "/" + Elem)

                        self.ComboBox_Select.addItem("Local: " + stName + " : " + stFileDesc)
                        self.lFile.append(stCfgPath + "/" + Elem)
                    else:
                        print("No Match:", Elem)   

        if os.path.exists(self.patre.stFolderCfg):
            stCfgPath   =   self.patre.stFolderCfg   
            lDir        =   listdir(stCfgPath)     
            print("Dir:", lDir)
            RegExp      =   re.compile(r"(?P<Name>([a-zA-Z0-9\-_]+))[.]{1,1}(?P<Ext>(rtc))")
            for Elem in lDir:
                Match           =               RegExp.search(Elem)
                if Match:
                    self.FilesAvailable     =   True
                    stName                  =   Match.group("Name")
                    stExt                   =   Match.group("Ext")

                    stFileDesc              =   self.ParseForDescription(stCfgPath + Elem)

                    self.ComboBox_Select.addItem("Tools: " + stName + " : " + stFileDesc)
                    self.lFile.append(stCfgPath + Elem)
                else:
                    print("No Match:", Elem)  



        if len(self.lFile) > 0:
            AnaFiles    =   True

        if not AnaFiles:
            palette     = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.darkRed)
            self.label.setPalette(palette)             
            self.label.setText("No configuration files and configuration folder c:/Tools/TinyRadTool/ does not exist !")
            self.ComboBox_Select.setDisabled(True)
            
    def ParseForDescription(self, stFile):
        if len(stFile) > 1:
            File        =   open(stFile, "r", encoding="utf-8", errors="ignore")
            
            lCmd        =   list()
            self.Title  =   "No Title"

            lCmd.append((r"Gui_SetTitle\((?P<Val>('[a-zA-Z0-9 \-]+'))\)", "self.Title", "Var"))
            lCmd.append((r"Gui_SetIPAddr\((?P<Val>('[0-9]{1,3}[.]{1,1}[0-9]{1,3}[.]{1,1}[0-9]{1,3}[.]{1,1}[0-9]{1,3}'))\)", "self.IpAddr", "Var"))
            for stLine in File:
                Ret     =   StrConv.ConvStrToCmd(stLine, lCmd)
                if Ret[0]:
                    exec(Ret[1])          

            return self.Title

    def assignWidgets(self):
        self.Button_Ok.clicked.connect(self.ActionButtonOkay)
        self.Button_Cancel.clicked.connect(self.ActionButtonCancel)

        #self.setStyleSheet("background-color: white;")
        path = os.path.join("src", "ressource", "img", "adi.png")
        self.Image_Logo     = QtGui.QImage(path)
        self.Label_Logo     = QtWidgets.QLabel()
        self.Logo_Layout    = QtWidgets.QHBoxLayout()
        # self.Label_Logo.setMaximumSize(400,200)
        # self.Image_Logo.scaledToWidth(200)
        self.pixmap = QtGui.QPixmap(self.Image_Logo)
        self.pixmap.scaled(400,200)
        self.Label_Logo.setPixmap(self.pixmap)
        self.Logo_Layout.addWidget(self.Label_Logo)
        self.WidgetPic.setLayout(self.Logo_Layout)

    def CenterWindow(self):
        screen              = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint         = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        self.move(centerPoint.x() - self.width() * 0.5, centerPoint.y() - self.height() * 0.5)

    def ActionButtonOkay(self):
        if self.FilesAvailable:
            Idx                     =   self.ComboBox_Select.currentIndex()
            self.patre.GuiSelIni    =   True
            self.patre.stFileCfg    =   self.lFile[Idx] 
        else:
            self.patre.GuiSelIni    =   False
        self.patre.GuiAgree         =   self.ChkBox_Agree.isChecked() 
        self.accept()
    


    def ActionButtonCancel(self):
        self.patre.GuiSelIni        =   False
        self.patre.GuiAgree         =   False
        self.reject()


