#!/usr/bin/env python3
# -*- coding: utf-8 -*-



# POUR DECODAGES SPECIFIQUES DES MESSAGES AVEC LABELS

#H2, 1L, 44....

#en entrée : array : label + message
#sortie : array : description label + message décodé/interprété


fich_label = open("C:/Users/thepe/Documents/RTL-SDR/Prog_RTL_SDR/Labels_Codes.txt","r")

lignes = fich_label.readlines()
labels =[]
labels_mess = []
for ligne in lignes:
    l1, l2 = ligne.split(":")
    labels += [l1[:-1]] #car espace à supprimer avant les :
    labels_mess += [l2]

alpha_clair = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ,.'

alpha_cry01 = "lA~S'ELq(?    6        _            bO"
alpha_cry02 = ',3-0mQ9]A)    X        r            IT'
alpha_cry03 = 'xt(J-De 9V    +        L            q$'
alpha_cry04 = "'\!mHFX  +/   (        N     D      V#"
alpha_cry05 = 'jx9duCo`eB    X        ]            )7'
alpha_cry06 = 'g. C9) (:`    L        M            7,'
alpha_cry07 = '.;40m U Dk    ]        E            )+'
alpha_cry08 = 'LYe}`vaKct:   =  f|  Pxqs, dum      Z['
alpha_cry09 = '48h6NB,s1Z    G        +            c5'
alpha_cry = [alpha_clair, alpha_cry01, alpha_cry02, alpha_cry03, alpha_cry04, alpha_cry05, alpha_cry06, alpha_cry07, alpha_cry08,alpha_cry09]


def labelSA(texte):
    media_abr = ['V', 'S', 'H', 'G', 'C', '2', 'X', 'I']
    medias = ['VHF-ACARS', 'Default Satcom', 'HF', 'Global Star Satcom', 'ICO Satcom', 'VDL Mod2', 'Inmarsat Aero', 'Iridium Satcom']
    retour =''
    if len(texte) >= 10:
        retour += 'Version N°'+texte[0]
        if texte[1] == 'E':
            retour += '/Establish flag'
        if texte[1] == 'L':
            retour += '/Loss flag'
        try:
            retour += '/' + medias[media_abr.index(texte[2])]
        except:
            retour += ''
        retour += '/' + texte[3:5] + 'h' + texte[5:7] + 'm' + texte [7:9] + 'UTC'
        if texte[9] == 'V':
            retour += '/Available'

    return retour
    
def label44(texte):
    '''
    Message type décrypté :
    01POS03,N49148E004206,402,LFPB,LKPR,0205,0937,1040,009.7
    01 : numéro du cryptage (de 01 à 09), en clair
    POS : 3 lettres (POS, ETA, ...)
    03 : 2 chiffres
    N49148E004206 : coordonnées
    402 : niveau d'altitude (en centaines de pieds ?, GRD = au sol ?)
    LFPB : aéroport de départ
    LKPR : aéroport d'arrivée
    0205 : MMJJ du jour
    0937 : HHMM heure actuelle
    1040 : ETA
    009.7 : ? (carburant restant ?)
    '''
      
    
    mess_clair  = ''
    numero=int(texte[1])
    # PROBLEME AVEC MESSAGE CONTENANT DES \ : texte = str.replace(texte,'\\','\\\\')
    
    for k in range(len(texte)-2):
        try:
            mess_clair += alpha_clair[alpha_cry[numero].index(texte[k+2])]
        except:
            mess_clair +=' '
    if len(texte)>56 and texte[56]==' ':
        mess_clair = mess_clair[:57]
        
    return mess_clair

def labelH1(texte):
    '''
    #avion en approche de Paris CDG :
    #M1BPRG/FNTHY5XD/DTLFPG,27R,87,143558,300304
    # puis seulement 20 secondes plus tard
    #M1BPRG/FNTHY5XD/DTLFPG,27R,104,141530,2EB9AF
    
    #M1 B
    PRG : PROGRESS ?
    FN THY5XD : Flight Number THY5XD
    DT LFPG : Destination aéroport LFPG (Paris De Gaulle)
    27R
    104 : Fuel restant à l'atterrissage ?
    141560 : ETA
    2E B9AF :
    '''
    print(texte)
    retour = ''
    prov = ['Central Fault Data Indicator', 'flight data recorder', 'flight management computer', 'flight management computer', 'I2']
    prov_let = ['CF', 'DF', 'M1', 'M2', 'I2']
    info_let = ['FLR', 'WRN', 'TKO', 'CRZ', 'WOB','PIREP', 'EDA', 'ENG', 'AEP', 'PWD', 'REQPWI']
    info = ['Equipment failure', 'Equipment failure', 'Take off performance data', 'Take off performance data', 'Cruise performance data', 'Cruise performance data', 'Weather observation', 'Weather observation', 'Pilot Report', 'Engine Data',  'Engine Data', 'Position/Weather Report', 'Flight plan predicted wind data', 'Predicted wind info request'] 
    try:
        retour += prov[prov_let.index(texte[1:3])]
    except:
        retour +=' '
    if texte[3] == 'A':
        retour += ' : conventional'
    if texte[3] == 'B':
        retour += ' : conversational'
    txt2 = texte.split('/')[0][4:]
    print(txt2)
    try:
        retour += info[info_let.index(txt2)]
    except:
        retour +=' '

    return retour

def mess_label(label, message):
    #on commence par regarder si le label fait partie des labels connus
    retour = []
    if label in labels:
        retour += [labels_mess[labels.index(label)]]

    if label == 'H1':
        retour += [labelH1(message)]

    if label in ['40', '41', '42', '44']:
        retour +=[label44(message)]

    if label == 'SA':
        retour += [labelSA(message)]
        
    return retour
    
