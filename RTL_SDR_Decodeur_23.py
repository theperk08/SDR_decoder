#!/usr/bin/env python3.9 anaconda

import threading #très important pour ne pas bloquer le GUI
verrou=threading.RLock()

import time
from datetime import datetime
import wx
import wave
from wx.html2 import WebView as web2
import pyaudio 
import struct 
import math
from scipy.io.wavfile import read, write
import numpy as np

import ACARS2023 as AC23
import POCSAG_2023_Decodage_En_Direct as POC23

REPERTOIRE="C:/Users/thepe/Documents/RTL-SDR/Enregistrements_Python/"

global nfichtest
nfichtest=0

global entetehtml
entetehtml='<!doctype html><html><head><title="Info-bulles dispos sur messages alpha">Début<br></title><meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" /><style type="text/css">* {   font-size: 13px; /* On définit les propriétés de texte pour toutes les balises. */   font-family: Tahoma, Verdana, Arial, serif;}a.info {   position: relative;   color: black;   text-decoration: none;   border-bottom: 1px gray dotted; /* On souligne le texte. */}a.info span {   display: none; /* On masque l infobulle. */}a.info:hover {   background: none; /* Correction d un bug d Internet Explorer. */   z-index: 500; /* On définit une valeur pour l ordre d affichage. */   cursor: help; /* On change le curseur par défaut par un curseur d aide. */}a.info:hover span {   display: inline; /* On affiche l infobulle. */   position: absolute;     top: 30px; /* On positionne notre infobulle. */   left: 20px;   background: white;   color: green;   padding: 3px;   border: 1px solid green;   border-left: 4px solid green;}</style> </head>'
global finhtml
finhtml='<br></html>'
 
#THRESH = 0.002 
SAMPLE_PERIOD = 0.05 
RATE=48000
SAMPLE_CYCLES = int(RATE*SAMPLE_PERIOD) 
SHORT_NORMALIZE = (1.0/32768.0) 
CHANNELS = 2 
FORMAT=pyaudio.paInt16

pa=pyaudio.PyAudio()         

stream = pa.open(format = FORMAT,      
     channels = CHANNELS,       
     rate = RATE,         
     input = True,         
     frames_per_buffer = SAMPLE_CYCLES)

#thresh_final=THRESH


class DemoPanel(wx.Panel):
    
    def __init__(self, parent, *args, **kwargs):    
        
        wx.Panel.__init__(self, parent, *args, **kwargs)
        
        self.parent = parent  

        NothingBtn = wx.ToggleButton(self, label="Démarrer")
        NothingBtn.Bind(wx.EVT_TOGGLEBUTTON, self.DoNothing )

        TestBtn = wx.ToggleButton(self, label="Test fichier")
        TestBtn.Bind(wx.EVT_TOGGLEBUTTON, self.DoTest )
        
        self.Textb=web2.New(self,size =(850,850)) #pour html2
      
        self.Textb.Bind(wx.EVT_CONTEXT_MENU,self.MenuC)
        
        global scrolposition
        
        scrolposition='' #pour html2        

        global source2
        global entetehtml
        global finhtml
        source2=''
        self.Textb.SetPage(entetehtml+source2+finhtml,"") #pour html2       
                
        global backcolor
        backcolor='gris'        

        global comptemessage
        comptemessage=0
        self.MsgBtn = wx.Button(self, label="Nombre de messages : 0",size=(160,30))
        
        heuredepart=str(datetime.now().time())[:8]
        heuredepart=heuredepart.replace(":","h",1)
        heuredepart=heuredepart.replace(":","m")
        heuredepart+="s"

        self.Test1=wx.Button(self,label="depuis : "+str(heuredepart) ,size=(115,30))
        self.MsgBtnTest=wx.Button(self,label="(zone de test)",size=(250,90))
        self.Rb1=wx.RadioBox(self,label="Type de Messages",choices=["Acars","POCSAG"],style=wx.RA_SPECIFY_COLS)
        #les choix de RadioBox ont pour base index=0, à récupérer avec evt.GetInt() ou GetSelection(self.Rb1)
        self.Rb1.Bind(wx.EVT_RADIOBOX,self.RadioChoix)

        self.Rb2=wx.RadioBox(self,label="Enreg fichiers audios",choices=["Oui","Non"],style=wx.RA_SPECIFY_COLS)
        self.Rb2.SetSelection(1)
        self.Rb2.Bind(wx.EVT_RADIOBOX,self.RadioChoix)
        
        self.Rb3=wx.RadioBox(self,label="Bitrate (POCSAG)",choices=["1200-France","2400-Belgique", "1200-Infirmier"],style=wx.RA_SPECIFY_COLS)
        self.Rb3.SetSelection(0)
        self.Rb3.Bind(wx.EVT_RADIOBOX,self.RadioChoix)
                
        Sizer = wx.BoxSizer(wx.VERTICAL)
        RbSizer=wx.BoxSizer(wx.HORIZONTAL)
        RbSizer.Add(self.Rb1,0,wx.ALIGN_CENTER|wx.ALL, 5)
        RbSizer.Add(self.MsgBtn,0,wx.ALIGN_CENTER|wx.ALL, 5)
        RbSizer.Add(self.Test1,0,wx.ALIGN_CENTER|wx.ALL, 5)
        RbSizer.Add(self.Rb2,0,wx.ALIGN_CENTER|wx.ALL,5)        
        RbSizer.Add(self.Rb3,0,wx.ALIGN_CENTER|wx.ALL,5)
                    
        MSizer=wx.BoxSizer(wx.HORIZONTAL)
        MSizer.Add(NothingBtn, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        MSizer.Add(TestBtn,0,wx.ALIGN_CENTER|wx.ALL,5)
        MSizer.Add(self.MsgBtnTest,0,wx.ALIGN_CENTER|wx.ALL,5)

        Sizer.Add(MSizer, 0, wx.ALIGN_CENTER|wx.ALL)
        Sizer.Add(RbSizer,0,wx.ALIGN_CENTER|wx.ALL)
        Sizer.Add(self.Textb,0,wx.ALIGN_CENTER|wx.ALL)        

        self.SetSizerAndFit(Sizer)
        
        
    def MenuC(self, event):
        
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()            
            self.Bind(wx.EVT_MENU, self.onPopup, id=self.popupID1)
            
        menu = wx.Menu()
        itemOne = menu.Append(self.popupID1, "Copier Sélection")
        
        self.PopupMenu(menu)
        menu.Destroy()
        
        
    def onPopup(self,event):
        
        self.dataObj = wx.TextDataObject()        
        self.dataObj.SetText(self.Textb.SelectionToText())
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(self.dataObj)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Unable to open the clipboard", "Error") 
       

    def RadioChoix(self,evt):
        numero=evt.GetInt()
        print("numero=",numero)
        

    def DoNothing(self, evt):
       
        clickedToggleButton = evt.GetEventObject()
        if clickedToggleButton.GetValue():
            clickedToggleButton.SetLabel("Stopper")
            self.thread = MyThread(self)
            self.thread.start()            
        else:
            self.thread.ToKill = True
            clickedToggleButton.SetLabel("Démarrer")

       
    def DoTest(self,evt):        

        try: 
         chaine0=stream.read(SAMPLE_CYCLES*60) 
        except IOError: 
         print("Error Recording")
        global nfichtest
        nfichtest+=1
        chainefic=np.fromstring(chaine0, 'Int16')
        write(direc+"20190226_enreg_analyse_POCSAG_double_"+str(nfichtest)+"a.wav",RATE,chainefic)

   
    def update(self,texte01,mode):
        
        global source2
        global entetehtml
        global backcolor
        global scrolposition

        if mode=="POCSAG":
            source2=texte01+'<hr>'+source2
        else:
            source2='<table style="width:100%;">'+texte01+'</table><hr>'+source2

        self.Textb.SetPage(entetehtml+source2+finhtml,"") #pour html2
        
        self.Textb.BackgroundColour=wx.Colour(220,220,220)
        scrolposition='rage'
        if not scrolposition=='':
            self.Textb.Find(scrolposition) #pour html2           
        
        global comptemessage

        comptemessage +=1        

        self.MsgBtn.SetLabel("Nombre de messages : "+str(comptemessage))


class DemoFrame(wx.Frame):
    """Main Frame holding the Panel."""
    def __init__(self, *args, **kwargs):
        """Create the DemoFrame."""
        wx.Frame.__init__(self, *args, **kwargs)

        MenuBar = wx.MenuBar()

        FileMenu = wx.Menu()

        item = FileMenu.Append(wx.ID_EXIT, "&Quitter")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)

        MenuBar.Append(FileMenu, "&Fichier")
        self.SetMenuBar(MenuBar)

        self.Panel = DemoPanel(self)
        
        self.Fit()


    def OnQuit(self, event=None):
        """Exit application."""
        self.Close()

   
class ThreadAcars(threading.Thread):
    
    def __init__(self,stream,sample,panela,numero):
        
        threading.Thread.__init__(self)
        
        self.panela=panela
        self.num=numero
        self.ToKill = False
        thr=threading.Thread(target=self.run)
        thr.start()


    def run(self):
        
        #CHANNELS = 2
        #FORMAT=pyaudio.paInt16
        #RATE=48000
        #SAMPLE_PERIOD=0.06
        #SAMPLE_CYCLES = int(RATE*SAMPLE_PERIOD)
        self.pa2=pyaudio.PyAudio()
        self.stream2 = self.pa2.open(format = FORMAT, channels = CHANNELS, rate = RATE, input = True, frames_per_buffer = SAMPLE_CYCLES)
        self.stream0=AC23.lance2a(self.stream2,SAMPLE_CYCLES,self.panela.Rb2)
        heure=datetime.now()
        
        global scrolposition
        with verrou:
            retour1= AC23.lancetest1(self.stream0,heure)
            
            if not(retour1[0]==''):
                scrolposition=retour1[1]
                wx.CallAfter(self.panela.update,retour1[0],"ACARS")
                
            print("ac19lance ok",str(self.num))
            self.stream2.stop_stream()
            self.stream2.close()


class MyThread(threading.Thread ):
    
    def __init__(self,panel):
        
        threading.Thread.__init__(self)
        self.panel=panel
        self.numero=0 #par défaut on ecoute messages Acars
        self.ToKill = False

        
    def run(self):
        
        while True:
            self.FooHandler()
            
            if self.ToKill:
                return None

            
    def FooHandler(self):
        
        global scrolposition
        mode="RIEN"
        if self.panel.Rb1.GetSelection()==0:
            self.numero+=1
            heure=time.time()

            retour1=AC23.lance1(stream,SAMPLE_CYCLES,self.panel.Rb1,self.panel.Rb2,self.numero,heure)
            if not(retour1==''):
                t=ThreadAcars(stream,SAMPLE_CYCLES,self.panel,self.numero)
        else:
            retour1=POC23.lancePOC(stream,SAMPLE_CYCLES,self.panel.Rb1,self.panel.Rb2, self.panel.Rb3)
            mode="POCSAG"
            if not(retour1[0]==''):
                scrolposition=retour1[1]
                wx.CallAfter(self.panel.update,retour1[0],mode)


    def __run(self):
        self.FooHandler()
        if self.ToKill:
            return None

if __name__ == '__main__':
    app = wx.App()
    frame = DemoFrame(None, title="RTL-SDR Affichage")
    frame.Show()
    app.MainLoop()
