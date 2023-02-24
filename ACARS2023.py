#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Créé le 14 jan 2019

@author: manu_musy
"""

from scipy.io.wavfile import read, write
import numpy as np
from datetime import datetime
from datetime import date
import time
from scipy import signal

import ACARS2023_affichage as AC


# SET UP your path here :

PATH="C:/Users/thepe/Documents/RTL-SDR/Enregistrements_Python/"
ACARS_SIGNAL = "ACARS_signal_"
ACARS_RECORD = "_enreg_analyse_ACARS_"

#-----------------------------

sequencesynchro0="011010000110100010000000"
sequencesynchro1="100101111001011101111111"

RATE=48000
CHANNELS = 2
FREQ = 2400


global nfich #pour numéroter les fichiers d'enregistrements
nfich=0

def trouvesignal(chaine):
    #Un bon signal ACARS se détache facilement du bruit de fond
    #par une valeur très haute ou très basse
    #du coup valeur aux alentours de 127-128
    #donc entre 120 et 140 ça devrait être bon

    trouve = False
    i = 0    

    while i < int(len(chaine) / 2) - 1 and trouve == False:    
        
        valeur = chaine[2 * i + 1]
        if valeur > 75 and valeur < 128:
            for b in range(15, 30):
                if (2*(i + b) + 1 < len(chaine)):
                    if chaine[2*(i + b) + 1] > 65 and chaine[2*(i + b) + 1] < 128:
                        trouve=True
        i += 1
    if trouve == True:
        return("ok")
    else:
        return("rien")

def inv01(chaine): #inverse les valeurs 0 et 1 d'une chaine
    result=""
    for b in chaine:
        if b == "0":
            result += "1"
        else:
            result += "0"
    return result

def lance1(stream1, sample_c, rb, rb2, numero, heure):
    #print('lance1')
    fini = False
    
    dernierheure = heure
    while fini == False:    

        affiche = False        
        try: 
         chaine0 = stream1.read(sample_c) 
        except IOError: 
         print("Error Recording")

        result = trouvesignal(chaine0)  
        
        if not(result == "rien"):
            if time.time() - dernierheure > 0.9: #pour éviter de prendre plusieurs fois le même signal

                print("Ok :", numero)
                #if rb2.GetSelection()==0:
                #    chainefic=np.fromstring(chaine0, np.int16) # 'Int16')
                #    write(PATH+str(datetime.today())[:10]+"_enreg_analyse_ACARS_"+str(nfich)+"f.wav",RATE,chainefic)
            
                return("Ok :")
                fini = True
        if rb.GetSelection() == 1:
            fini = True

def lance2a(stream2, sample_c, rb2):
    global nfich
    try: 
     # maintenant qu'on a trouvé un signal,
     # on récupère une bonne longueur pour avoir le signal complet
     chaine0 = stream2.read(sample_c * 12)
     
     if rb2.GetSelection() == 0:
         chainefic = np.fromstring(chaine0, np.int16) 
         write(PATH + str(datetime.today())[:10] + ACARS_RECORD + str(nfich) + ".wav", RATE, chainefic)
    except IOError: 
     print("Error Recording")
    
    nfich += 1

    return chaine0


def lancetest1(stream0, heure):
    #on analyse le signal complet
    print("lancetest1")
    st2 = ''
    dateaffiche = ''
    
    signal1 = np.fromstring(stream0, np.int16)
    #print(signal1[:200])

    signal0 = []
    #on réechelonne entre -40 et 40 pour plus simple à analyser
    for each in signal1:
        signal0 += [np.interp(each, [-32768, 32767], [-40, 40])]        
   
    Tdebut = 0  
    Nbval = len(signal0)
    RATE
    Tfin = Nbval / RATE
    Pas = 1 / RATE
    #Amplitude=20
    
    valmin = 0
    imax = 0
    for i in range(50):
        vsign = signal0[i]
        if vsign < valmin:
            valmin = vsign
            imax = i
    
    Decalage = imax / RATE    

    listeslice = ""    

    PERIODE = int(CHANNELS * RATE / FREQ)    
    k2 = imax

    while k2 < Nbval - PERIODE / 2:
        sommepart = 0
        for a in range(int(PERIODE / 4)):
            sommepart += signal0[k2 + a]
        if sommepart > 0 :
            listeslice += "0"
        else:
            listeslice += "1"
        #if z[k2]-signal0[k2]>20:
        #    listeslice+="1"
        #else:
        #    listeslice+="0"
        
        k2 += PERIODE #40=N_channels * RATE / FREQ
    affiche = False
    #print(listeslice)

    if sequencesynchro0 in listeslice:
        i = listeslice.index(sequencesynchro0)
        test01 = listeslice[i:]  
        affiche = True

    else:
        if sequencesynchro1 in listeslice:
            i = listeslice.index(sequencesynchro1)
            test01 = inv01(listeslice[i:])  
            affiche = True

    if affiche:
        print(str(datetime.now()))
        retour = AC.miseenforme(test01) 
        date1 = date.today()
        fichier = open(PATH + ACARS_SIGNAL + str(date1) + ".html","a")
        dateaffiche = str(date1) + " à " + str(heure.hour) + "h" + str(heure.minute) + "m" + str(heure.second) + "s"
        st2 = '<font color="black">' + str(date1) + " à " + str(heure.hour) + "h" + str(heure.minute) + "m" + str(heure.second) + "s" + '</font>' + '<br>'

        for a in retour[1]:
            st2 += a + " "
        st2 += '<br>'
        fichier.write(st2)
        fichier.close()
             
        print("-----------")
    return st2, dateaffiche


