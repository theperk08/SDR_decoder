#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Créé le 28 déc 2018

@author: manu_musy
"""

#*** -------------- POUR DECODAGE EN DIRECT AVEC CUBIC SDR

import sys
from datetime import datetime
from scipy.io.wavfile import read, write
import numpy as np
import POCSAG2023decodagechaine as pcs


RATE = 48000
SPEED1 = 2400
SPEED2 = 4800
SPEED3 = 1200

list1="" 
counter=0

index01="0101010101010101010101010101010101010101"
adentete0="01111100110100100001010111011000"
adentete1="10000011001011011110101000100111"
adidle="01111010100010011100000110010111"

adidle_belge = "01111010100110100100100111000000"

adentete_infirmier = "10101010101010101010101011010010"

global nfich
nfich=0

def bits01_inf(liste, speed):
    #print('longueur liste',len(liste))
    cnt = int(RATE/speed)
    starts = []
    start = 0
    #print('longueur boucle', 50*cnt)
    nb = 3
    for k in range(nb):
        for p in range(start + 1, start + 50*cnt):
            if liste[p] < -150 and liste[p+1] > 150:
                starts += [p]
                start = p
                break

    #print(starts)
    data3 = ""
    if len(starts) == nb:
        moyenne = (starts[-1] - starts[0])/(nb-1)
        #print('moyenne écarts', moyenne)
        moyenne_val_brut = np.mean(liste[starts[0]:starts[-1]])
        #print('moyenne valeurs', moyenne_val_brut)
        
        nb_par_tranche = 10
        slicer = int(moyenne/(2*nb_par_tranche))

        data2 = []

        for i in range(starts[0], len(liste)-slicer, slicer):
            somme = 0
            for j in range(slicer):
                somme += liste[i+j]
            somme -= (moyenne_val_brut * slicer)
            if somme > 0:
                data2 += [1]
            else:
                data2 += [0]

        
        uns = True
        compte = 0
        for k in data2:
           
            if uns == True:
                num = 1
            else:
                num = 0
            if k == num:
                compte +=1
            else:
                nb = round(compte/nb_par_tranche)
                data3 += str(num) * nb
                uns = not(uns)
                compte = 0
    #print(data3)
    return data3
    
def bits01(liste, speed):
    # convertit fichier wav en chaine de bits 0 et 1, suivant le bitrate=speed  
            
    CNT = int(RATE/speed)
    start = 0
           
    for p in range(0, 2*CNT):
        if liste[p] < -150 and liste[p+1] > 150:
            start = p
            break

    if start == 2*CNT - 1:
        return ''
    
    bits = np.zeros(liste.size)
    bits_deco = np.zeros(liste.size)
    bits_01 = ''

    for p in range(0, liste.size - CNT, CNT):
        bits[start + p] = 500
    
    for k in range(start+1, liste.size):
        if liste[k] > 1000:
            bits_deco[k] = 20000
        elif liste[k] < -1000 :
            bits_deco[k] = -20000
        
    compte = 0
    for j in range(start + 1, liste.size - 4 * CNT, 4 * CNT):
        somme = 0
        for i in range(4 * CNT):
            somme += bits_deco[j + i]
        if somme > 0:
            #bits_01[compte] = 1
            bits_01 += "1"
        else:
            #bits_01[compte] = 0
            bits_01 += "0"
        compte += 1
    #print(bits_01)
    return bits_01


def lancePOC(stream1,sample_c1, rb, rb2, rb3, liste_config):   
    
    ab = 0
    trouve = False

    while trouve == False:

        try: 
         chaine0 = stream1.read(sample_c1 * 3) 
        except IOError: 
         print("Error Recording") 
    
                
        global nfich
        
        #a priori ce sont les valeurs de rang impaire de liste qui donnent la hauteur
        # de 0 à 125 = 0
        # de 126 à 254 = 1

        # TRAITEMENT
        if rb3.GetSelection() == 0:
            SPEED = SPEED1
            idle = adidle
        elif rb3.GetSelection() == 1:
            SPEED = SPEED2
            idle = adidle_belge
        else:
            SPEED = SPEED3
            idle = adidle


        #SPEED = 450

        chainefic=np.fromstring(chaine0, np.int16)

        if SPEED == SPEED3:
            bits_str = bits01_inf(chainefic, SPEED)
        else:
            bits_str = bits01(chainefic, SPEED)

        

        #on recherche d'abord la fréquence des premiers 0 et 1
        
        trouve = False        
        
        if len(bits_str) > 20 and (index01 in bits_str): #parfois échantillon trop petit ou inexistant à cause du try error
            trouve = True
            print('trouvé')
            print(bits_str)
            
        if trouve:
            chaine2 = ''
    
        # Logiquement, on obtient une fréquence de base d'environ 80, donc entre 70 et 90

            try: 
             chaine0 = stream1.read(sample_c1 * 60) 
            except IOError: 
             print("Error Recording")
            #global nfich
            nfich += 1
            chainefic = np.fromstring(chaine0, np.int16)
            if rb2.GetSelection() == 0:
                 #chainefic=np.fromstring(chaine0, np.int16)
                 write(liste_config[3] + str(datetime.today())[:10] + liste_config[4] + str(nfich)+".wav",RATE,chainefic)
                        

            chaine = ""
            chainenot = ""

            #on recherche d'abord la fréquence des premiers 0 et 1
            #et on traduit en bits de 0 et 1
            
            #chaine = bits01(chainefic, SPEED)

            if SPEED == SPEED3:
                chaine = bits01_inf(chainefic, SPEED)
            else:
                chaine = bits01(chainefic, SPEED)
                
            print('chaine de 0 et 1')
            print(chaine)
            fini=False            
      
            if adentete0 in chaine:

                chaine2 = chaine[chaine.index(adentete0)-3:]
            #Si on a bien une succession de 0 et de 1, reste plus qu'à trouver trouver le début du message
            if adentete1 in chaine:

                chaine2 = chaine[chaine.index(adentete1) - 3:]
                chaine2 = chaine2.replace("0", "2")
                chaine2 = chaine2.replace("1", "0")
                chaine2 = chaine2.replace("2", "1")

            if adentete_infirmier in chaine:
                chaine2 = chaine[chaine.index(adentete_infirmier):]

            print('')
            print(chaine2)
            print('')
            
            return pcs.decodagepocsag(chaine2, idle, rb3, liste_config)
        
        if rb.GetSelection() == 0:
            fini = True
            return ''

