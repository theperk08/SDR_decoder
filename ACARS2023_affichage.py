#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Créé le 14 jan 2019

@author: manu_musy
"""


# POUR MISE EN FORME MESSAGE ACARS DANS FENETRE TKINTER

#  --- STRUCTURE D UN BLOC MESSAGE ACARS
# ATTENTION : LES BYTES SONT LUS/TRANSMIS A L'ENVERS
# si un byte commence par 1, remplacer ce bit par 0

# NB Bytes / Intitulé / caractère / binaire / décimal

# 1 / caractère de synchro / * / 00101010 / 42
# 2 / carac de synchro / SYN SYN / 00010110 00010110 / 22  22 
# 1 / Marqueur de départ / SOH / 00000001 / 1
# 1 / mode de transmission / 2 (si transmission à toutes les stations au sol, sinon un caractère entre "@" et "]" / 00110010 / 50
# 7 / numéro enregistrement avion /
# 1 / acknowledged or not acknowledged / ACK or NAK / 10000110 ou 00010101 / 6 ou 21
# 2 / label
# 1 / block ID
# 1 / si texte / STX / 00000010 / 2
# 4 / numero sequence
# 6 / numéro de vol
#  texte
# 1 / marqueur de fin / ETX / 10000011 / 3  ou plus rarement ETB si message contenu dans plusieurs blocs / 00010001 / 17
# 2 / Bloc Check Sequence /
# 1 / BCS Suffix / DEL / 01111111 / 127 ou SOH ? / 00000001 / 1


from subprocess import Popen, PIPE
from datetime import datetime

import ACARS2023_Labels as Alab
                  
asciitable = ["NUL","SOH","STX","ETX","EOT","ENQ","ACK","BEL","BS","TAB","LF","VT","FF","CR","SO","SI","DLE","DC1","DC2","DC3","DC4","NAK","SYN","ETB","CAN","EM","SUB","ESC","FS","GS","RS","US","SPACE"]
nbchif = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
carac = "_-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

#caractères habituels en en-tête avant message :
def entete(ch0):
    
    trouve = True
    for a in ch0:
        if not(a in carac):
            trouve = False
            
    return trouve

#controle du bit de parité
#codage sous 7 bits + 1 bit de parité :
#si nombre pair de 0 dans les 7 bits -> bit de parité =0, sinon, bit de parité =1

def parite(ch0, position): #controle du bit de parité ainsi que de certains elements précis (SYN, SOH, NAK...)
    #l'octet n'étant pas encore renversé, c'est le dernier des 8 bits qui est le bit de parité
    #print(ch0)
    
    pair = int(ch0[7])
    chaine0 = ""
    for k in range(8):
        chaine0 += ch0[k]
    s = 0
    lettre = chr(int("0b" + chaine0[::-1][1:], 2))
    for a in range(7):
        s += int(ch0[a])
    if s % 2 == pair:
        return False
    else:
        ch00 = non(chaine0)[::-1][1:]
        ch02 = ""
        for i in ch00:
            ch02 += i
            
        lettre2 = chr(int("0b" + ch02, 2)) #tenter le décodage par inversion des 0 et 1
        if position == 1 or position == 2:
            
            if not(chaine0 == "01101000"):
                return False
        if position == 3:
            if not(chaine0 == "10000000"):
                return False
        if position > 3 and position < 12:
            #print(position)
            return entete(lettre)
        if position == 12:
            if not(chaine0 == "10101000" or chaine0 == "01100001"):
                return False
        if position > 12 and position < 16:
            return entete(lettre)
        if position == 16:
            if not(chaine0 == "01000000"):
                return True
        if position > 16 and position < 27:
            return entete(lettre)
        return True
            

def non(ch0): #renverse une chaine de 0 en 1 et inversement
    
    d1 = []
    for k in ch0:
        if k == "1":
            d1 += ["0"]
        else:
            d1 += ["1"]
    return d1


def affichage(mess, liste_config): #bel affichage en html avec couleur

    colerreur = 'fuchsia'
    
    texte=['<table border="2" width="100%"><tr><td width="12%"><font color="red">Mode : </font><b>']
    if len(mess) > 4:
        if len(mess[4]) == 1:
            texte += ['<font color="green">'+ mess[4] + '</font></td>']
    texte2 = '</b><td width="22%"><font color="red">Avion : </font><font color="green" face="Arial Black"><b>'

    if len(mess) > 11:
        if len(mess[5]) == 1 and mess[5] in nbchif:
            texte2 += mess[5]

        for k in range(1, 7):
            if len(mess[5 + k]) == 1:
                if mess[5 + k] in carac:
                    texte2 += mess[5 + k]
                else:
                    texte2 += '<font color="' + colerreur + '">' + mess[5 + k] + '</font>'

    texte += [texte2 + '</b></font></td>']
    
    texte2 = '<td width="13%"><font color="red">Label : </font><font color="green"><b>'

    label = '' 
    if len(mess) > 15:
        
        for k in range(2):
            if len(mess[13 + k]) == 1 and mess[13 + k] in nbchif :
                texte2 += mess[13 + k]
                label += mess[13 + k]
    
    texte += [texte2 + '</b></font></td>']
    
    texte2 = '<td width="14%"><font color="red">Bloc Id : </font><font color="green"><b>'
    if len(mess) > 16:
        for k in range(1):
            if len(mess[15 + k]) == 1 and mess[15 + k] in nbchif :
                texte2 += mess[15 + k]

    texte += [texte2 + '</b></font>']

    texte2 = '<td width="19%"><font color="red">Msg n° : </font><font color="green"><b>'
    if len(mess) > 21:
        
        if len(mess[17]) == 1:
            if ord(mess[17]) > 64 and ord(mess[17]) < 91:
                texte2 += mess[17]
            else:
                texte2 += '<font color="' + colerreur + '">' + mess[17] + '</font>'
        if len(mess[18]) == 1:
            if ord(mess[18]) > 47 and ord(mess[18]) < 58:
                texte2 += mess[18]
            else:
                texte2 += '<font color="' + colerreur + '">' + mess[18] + '</font>'
        if len(mess[19]) == 1:
            if ord(mess[19]) > 47 and ord(mess[19]) < 58:
                texte2 += mess[19]
            else:
                texte2 += '<font color="' + colerreur + '">' + mess[19] + '</font>'

        if len(mess[20]) == 1:
            if ord(mess[20]) > 64 and ord(mess[20]) < 91:
                texte2 += mess[20]
            else:
                texte2 += '<font color="' + colerreur + '">' + mess[20] + '</font>'        

    texte += [texte2 + '</b></font>']
    texte2 = '<td width="22%"><font color="red">Vol Id : </font><font color="green" face="Arial Black"><b>'

    if len(mess) > 27:
       
        for k in range(6):
            if len(mess[21 + k]) == 1:
                if mess[21 + k] in carac:
                    texte2 += mess[21 + k]
                else:
                    texte2 += '<font color="' + colerreur + '">' + mess[21 + k] + '</font>'
                    
    texte += [texte2 + '</b></font>']
    texte2 = '</tr><tr><td colspan="6"><font color="red">Message : '   

    fintexte = False
    texte3 = ""
    texte3a = ""
    nespace = 0

    for k in range(27, len(mess)):
        if len(mess[k]) > 1:
            if mess[k] == "ETX" or mess[k] == "ETB":
                fintexte = True
                #texte2+="\n"
            texte3a += " " #on remplace les caractères spéciaux du message par des espaces
            nespace = 0
        else:
            if fintexte == False:
                if len(mess[k]) == 1:
                    texte3a += mess[k]
                    #texte3v+=mess[k]
                    if mess[k] == " ":
                        nespace = 0
                    else:
                        nespace += 1
        if nespace == 65:
            texte3 += texte3a + '<br>'
            texte3a = ""
            nespace = 0
    
    texte3b = texte3 + texte3a

    #si Label répertorié, alors on identifie et décode/interprète
    texte_label = Alab.mess_label(label, texte3a)

    if len(texte_label) > 0:
        texte2 += '(' + texte_label[0] + ')'

    if len(texte_label) == 2:
        texte2 += '<br>' + texte_label[1] 
    
    texte2 += '</font></td></tr><tr><td colspan="6"><font color="blue" face="Arial Black"><b>'
    
    texte += [texte2 + texte3b + '</b></font></td></tr>']
    texte2 = ''
    
    if "MSTEC7X" in texte3b:
        if ("AT1" in texte3b) or ("AP1" in texte3b) or ("AT0" in texte3b) or ("CR1" in texte3b) or ("DR1" in texte3b) or ("CC1" in texte3b) :
            
            argu = 'u "' + texte3b + '"'
            print(argu)
            chaines = liste_config[0] + ' ' + argu
        
            p = Popen(chaines, stdout = PIPE, bufsize = 1)
            FiniL = False
            texte2 += '<tr><td colspan="6">'

            while FiniL == False:
                line = p.stdout.readline()
                if str(line) != "b''": #on finit d'afficher lorsqu'on arrive à une ligne vide dans le buffer
                
                    st = str(line).replace("\\r\\n'", "")[2:]
                    print(st)
                    texte2 += st + "<br>"
                else:
                    FiniL = True

            texte2 += "</td></tr>"
            p.stdout.close()

            if p.wait() != 0:
                raise RuntimeError("%r failed,exit status: %d" % (chaines, p.returncode))
    texte += [texte2 + '</table>']
    return(texte)


# TEST EN COURS DE DEVELOPPEMENT
def brut(messaged):
    pass
    
    d2 = messaged

    message2 = [""] #message brut sans recherche d'erreurs
    i = 0
    for i in range(int(len(d2) / 8)):
        s1 = ""
        for k in range(7):
            s1 += d2[8*i+6-k]
        
        numero = int("0b"+s1,2)
        
        if numero <= 32:
                carac = asciitable[numero]
        else:
            if numero == 127:
                carac = "DEL"
            else:
                carac = chr(numero)
       
        message2+=[carac]
    return message2



def miseenforme(ch2, liste_config):
    pass
    
    d2=[]
    
    for k in ch2:
        d2+=[k]

    message2=brut(d2)
    
    if 0<0:
        d2m = []
    
        for k in ch2m:
            d2m += [k]
        message2m = brut(d2m)
    
        d2p = []
    
        for k in ch2p:
            d2p += [k]
        message2p = brut(d2p)

    #tentative recherche message avec correction d'erreurs        
    if False:
        d3 = non(d2)
        message = [""]
        numeronot = 0
        i = 0
        position = 1
        fini = False
        avantarriere = [1,0] #pour savoir de combien en avant ou en arrière on recherche les bits erreurs
            
        while i + 8 < len(d2) and fini == False:
            c = ""
            cnot = ""
            ok = parite(d2[i : i + 8], position)
            
            if ok == True:
        
                for k in range(8):
                    c += d2[i + k]
                    
                numero = int("0b" + c[::-1][1:], 2)
                
                if numero <= 32:
                    carac = asciitable[numero]
                else:
                    if numero == 127:
                        carac = "DEL"
                    else:
                        carac = chr(numero)
                
                message += [carac]
                i += 8
                position += 1
                avantarriere = [1,0]
            
                if False:
                    if numeronot <= 32:
                        carac = asciitable[numeronot]
                    else:
                        if numeronot == 127:
                            carac = "DEL"
                        else:
                            carac = chr(numeronot)
                    
                    messagenot += [carac]
            else:
                if i > 0 and i + 9 < len(d2):
                    if avantarriere[0] == 1:
                        i -= 1
                    else:
                        i += 1
                    avantarriere[0] = 0
                   
                    for n in range(len(d3)):
                        d2[n] = d3[n]
                    s1 = 0
                    for m in range(6):
                        s1 += int(d2[i + m + 1])
                    #on corrige pour avoir un bit de parité cohérent
                    if s1 % 2 == int(d2[i + 7]):
                        d2[i] = "1"
                    else:
                        d2[i] = "0"
                    faux1 = 1
                    
                else:
                    fini = True    

    print("Message brut")

    texteaff2 = affichage(message2, liste_config)

    return("", texteaff2)




