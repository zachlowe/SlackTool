import wx
import tkinter.filedialog as tk
from shutil import copyfile
import os
import SlackParser

class BearFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super(BearFrame, self).__init__(*args, **kw)

        self.panelDirectories = wx.Panel(self)

        self.txt1 = ""
        self.st = wx.StaticText(self.panelDirectories, label=self.txt1, pos=(25,25))
        self.font = self.st.GetFont()
        self.font.PointSize += 10
        self.font = self.font.Bold()
        self.st.SetFont(self.font)

        self.makeMenuBar()

        self.CreateStatusBar(2)
        self.SetStatusWidths([-1,100])
        self.SetStatusText("Please select your Slack export directory.",0)

    def timerMethod(self):
        pass

    def makeMenuBar(self):

        fileMenu = wx.Menu()
        addDirItem = fileMenu.Append(-1, "&Select Directory...\tCtrl-A", "Open to the location of your slack export.")
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        helpMenu = wx.Menu()
        
		
        aboutMenu = wx.Menu()
        aboutItem = aboutMenu.Append(wx.ID_ABOUT)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(aboutMenu, "&About")

        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnAddDir, addDirItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def OnExit(self, event):
        self.Close(True)
        

    def OnAddDir(self, event):
        slackDir = wx.DirDialog(self, "Open your unzipped Slack export directory.", style = wx.DD_DEFAULT_STYLE)
        if slackDir.ShowModal() == wx.ID_OK:
            print("You chose: " + slackDir.GetPath())
        exportDir = slackDir.GetPath()
        slackDir.Destroy()
        
        absDirArg = exportDir
        exportDir += "\SlackTool.py"

        SlackParser.slackMain(absDirArg)
        
        
    def OnAbout(self, event):
        wx.MessageBox("SlackTool\nCopyright 2019\nCreated by Zachary Lowe and Michael Slettevold for Lighthouse eDiscovery.\nDirect questions to lowez@uw.edu", "About", wx.OK|wx.ICON_INFORMATION)

if __name__ == '__main__':
    app = wx.App()
    frm = BearFrame(None, title='SlackTool')
    frm.Show()
    app.MainLoop()
