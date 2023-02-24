#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Créé le 28 déc 2018

@author: manum
"""

import sys
#try: color = sys.stdout.shell
#except AtributeError: raise RuntimeError("Use IDLE")
from datetime import datetime
from datetime import date

"""
Code couleur de color.write:
"COMMENT" = rouge
"STRING"  = vert


****  POUR DECODAGE POCSAG D UNE CHAINE DE BITS 0 1

# Structure d'un message POCSAG
# des frames de 32 bits :

# première frame = entete
# suivie de 8 duos de frames (numérotés de 0 à 7)
# si frame (autre que entete et idle) commence par 0 = Adresse du pager
# sinon (commence par 1) = corps du message

# structure frame d'adresse :
# bit n°1 =0
# bits n°2 à n°19 = début d'adresse (complétée par les 3 bits du numéro de duo de la frame où se situe cette frame d'adresse
# bits n°20 et 21 = bits de fonction
# bits n°22 à 31 = BCH bits de contrôle
# bit n°32 : even parity

# structure frame corps message :
# bit n°1 = 1
# bits n°2 à 21 = succession de paquets de 7 bits codant les caractères du message
# (comme il n'y a que 20 bits de caractères par frame et qu'un caractère est codé sur 7 bits, certains caractèrs sont codés sur 2 frames consécutives
# bits n°22 à 31 = BCH bits de contrôle
# bit n°32 : even parity

"""

entete = "01111100110100100001010111011000"
entete_infirmier = "10101010101010101010101011010010"
idle_fr = "01111010100010011100000110010111"
idle_belge = "01111010100110100100100111000000"
idle_infirmier = "10101010101010101010101011010010"

listebizarre=["10000000000000000000000000000000","11111111111111111111111111111111","10101010101010101010101010101010"]

asciispecial=["NUL","SOH","STX","ETX","EOT","ENQ","ACK","BEL","BS","HT","LF","VT","FF","CR","SO","SI","DLE","DC1","DC2","DC3","DC4","NAK","SYN","ETB","CAN","EM","SUB","ESC","FS","GS","RS","US","SP"]

numeriq=["0","1","2","3","4","5","6","7","8","9","*","U"," ","-",")","("]
tablec="0123456789*U -)("
typemessage=["Numérique","null1","null2","Message"]
couleur=["COMMENT","COMMENT","COMMENT","STRING"]

direc="C:/Users/thepe/Documents/RTL-SDR/Enregistrements_Python/"

def decibin(nbd):
    #prend un entier nbd (entre 0 et 7) et le convertit en chaine binaire sur 3 bits : exemple : 3-> "011"
    listedb=["000","001","010","011","100","101","110","111"]
    if nbd<8:
        return (listedb[nbd])
    else:        
        return "000"
    
    
def bit4(nb1):
    #transforme nombre décimal en format binaire sur 4 bits
    a=str(bin(nb1))[2:]
    if len(a)<4:
        for k in range(4-len(a)):
            a="0"+a
    return a

def deco_infirmier(message):
    retour =["","",""]

    retour0 = ''
    retour1 = ""
    retour1b = ""
    ch_message = message.split(idle_infirmier)
    
    for chaine1 in ch_message:
        if len(chaine1)== 64 or (len(chaine1) >= 72 and (chaine1[64:72] == "00000000" or chaine1[64:72] == "11111111")):
            retour1b = ""
            for b in range(8):
                morceau = chaine1[8*b : 8*(b+1)]
                carac = int(morceau,2)
                if carac >= 32:
                    retour0 += morceau + chr(carac) + ' '
                    retour1 += morceau + ' '
                    retour1b += "&#" + str(carac) + ";"
                else:
                    retour0 += morceau + '  '
                    retour1 += morceau + ' '
                    retour1b += ' '
            retour0 += '\n'
            retour1 += '<br>' + retour1b + '<br>'
        
            
    print(retour0)            
    retour[0]= retour0
    retour[1] = retour1

    return retour

def decomess(frch,typemess):
    #prend une liste de frames (de longueur 32) pour en extraire les bits 2 à 21 et regrouper en paquets de 7(alpha) ou 4(numérique) bits
    #typemess= 0 (numérique) ou 3 (alpha)

    listemessage=[] #car parfois faux message, donc recommencer un nouveau message
    clair=""
    messclair="" #message avec caractères spéciaux bruts
    messclairf="" #message sans caractères spéciaux (sauf espace)
    messclairt=""
    messclairft=""
    numclair=""
    numclairt=""

    print('liste des frames')
    print(frch)
    
    for k in frch:
        
        if not (k in listebizarre):
            clair += k[1:21] #on concatène tous les bits utiles du message
            fin=False
        else:
            listemessage+=[clair]
            clair=""
            fin=True
    if fin==False:
        listemessage+=[clair]
        
    for clairij in listemessage:
        
        messclair=""
        messclairf=""
        numclair=""
                
        fini = False
        fini_nul = 0
        j = 0
        offset = 0
        while not(fini):
            
            morceau = clairij[offset + 7*j: offset + 7*(j+1)][::-1]
            if not(morceau == ''):
               
                num=int(morceau, 2) #on coupe en paquets de 7 bits pour décodage
            
                if num<33:
                    if num==32:
                        messclairf+=" "
                    messclair+="<"+asciispecial[num]+">"
                    if num==4: #EOT : fin de transmission donc les caractère suivants ne correspondraient à rien, inutile de les décoder
                        fini=True
                    if num==0:
                        fini_nul += 1
                    if fini_nul ==2:
                        messclairf += "<br>"
                else:
                    messclair += chr(num)
                    
                    messclairf += "&#" + str(num) + ";" #pour que les caractères, mêmes spéciaux, soient bien affichés à travers la page html
                if fini_nul == 2: #messages belges se coupent quand 2 fois de suite le caractère <NUL>
                    #les portions de messages étant regroupées par paquets de 20 bits...
                    offset = 20 - ((offset + 7*(j+1)) % 20)
                    fini_nul =0
                    
                j += 1
                if offset + 7*(j+1) >= len(clairij)-7:
                    fini = True
            else:
                fini = True
    
        if not clairij=='':            
            for j in range(int(len(clairij)/4)):
                num=int(clairij[4*j:4*(j+1)][::-1],2)
                numclair+=numeriq[num]       

        print(messclair)
        print(messclairf)
        print(numclair)
        
        messclairt += " " + messclair
        messclairft += " " + messclairf
        numclairt += " " + numclair
        
    return [messclairt,messclairft,numclairt]


def affichage_html(retour, infobulle, rb3, date1):
        
    date_affiche= str(date1)+' à '+str(datetime.now().hour)+"h"+str(datetime.now().minute)+"m"+str(datetime.now().second)+"s"

    st2='<font color=#000066 face="Yu Gothic UI"><b>'+str(date1)+' à '+str(datetime.now().hour)+"h"+str(datetime.now().minute)+"m"+str(datetime.now().second)+"s"+'</font></b>'+'<br>'

    #avec infobulle :
    st2+='<table border="3" ><tr><td width="50%" ><font color="black" face="Courier New"><a title="'+infobulle+'">Message alphanumérique</a></font></td><td width="10%"></td><td width="40%"><font color="black">Message numérique</font></td></tr>'
    #sans infobulle :
    #st2+='<table border="3" ><tr><td width="50%" ><font color="black" face="Courier New">Message alphanumérique</font></td><td width="10%"></td><td width="40%"><font color="black">Message numérique</font></td></tr>'
    
    if retour[2][0:2]=='(0' or len(retour[2])==5: #typiquement si message numérique commence par '(0' (donc par 11110000), ou de longueur 5 (donc une seule frame de données) alors il s'agit d'un Tone Only
        st2+='<tr><td   bgcolor=#C0C0C0 width="50%"><b>'+retour[1]+'</b></td><td bgcolor=#808080 width="10%"><font color="yellow">Tone Only</font></td><td  bgcolor=#C0C0C0 width="40%"><b>'+retour[2]+'</b></td></tr></table> '
        
    else:
        if rb3.GetSelection() == 0:
            st2+='<tr><td   bgcolor=#99ff99 width="50%"><b>'+retour[1]+'</b></td><td width="10%"></td><td  bgcolor="red" width="40%"><b>'+retour[2]+'</b></td></tr></table> '
        else:
            # pas d'affichage du numérique si pocsag belge (ou infirmier), car trop longs en général
            st2+='<tr><td   bgcolor=#99ff99 width="70%"><b>'+retour[1]+'</b></td><td width="10%"></td><td  bgcolor="red" width="20%"><b>'+ ' ' +'</b></td></tr></table> '


    return date_affiche, st2


def enregistre_fichier(chaine, date1):
    fichier=open(direc+"POCSAG_signal_"+str(date1)+".html","a")
    fichier.write(chaine)
    fichier.close()
    
def decodagepocsag(chaine, idle, rb3):
    #recherche d'en tête
    #puis de idle
    #pour décoder ce qu'il reste (adresse, corps du message...)
    if chaine=="":
       return'<br>'

    date1 = date.today()

    if rb3.GetSelection() == 2:
        retour_chaine = deco_infirmier(chaine)
        infobulle = ''
        date_affiche, st2 = affichage_html(retour_chaine, infobulle, rb3, date1)
            
        # ENREGISTREMENT FICHIER HTML
        enregistre_fichier(st2, date1)
                
        return st2,date_affiche
        
    else:
        chliste=chaine.split(entete)   

        message=[]
        messagef=[]
        tpms=0
        for a in range(len(chliste)-1):
            
            frame=chliste[a+1].split(idle)
           
            for b in range(len(frame)):
                if len(frame[b])>=32:
                    f=frame[b][::-1]
                    
                    for i in range(int(len(frame[b])/32)):
                        if frame[b][32*i]=="0":
                            tpms=int(str(frame[b][32*i+19:32*i+21]),2)
                            nd=decibin(int((b+i)/2))
                            
                            if nd=="null":
                                print("Idle only - trop de frames")
                            else:
                                print("Adresse:",str(int(frame[b][32*i+1:32*i+19]+nd,2)), ' type:',typemessage[tpms])
                                
                        if frame[b][32*i]=="1":
                            message+=[frame[b][32*i:32*(i+1)]]
                            print('Message', frame[b][32*i+1:32*i+21])
                            
                        if f[32*(i+1)-1]=="1":
                            messagef+=[f[32*i:32*(i+1)]][::-1]                    

                else:
                    if len(frame[b])>0:
                        
                        print('')
                        print('')
                    
        if len(message)>0:
            
            retour = decomess(message,tpms)
            
            
            infobulle = "&#013"+retour[1]+"&#013"

            #teste les 7 décodages possibles alphanumériques (en décalant simplement le bit de départ
            chaine2 = retour[2]
            transcript = ""
            
            for t in chaine2:
                transcript += bit4(tablec.index(t))[::-1]
                
            espacemax = retour[1].count(" ") #a priori message clair contient un max d'espaces
            resultclair = ""
            print("espacemax=", espacemax)
            
            for j in range(7):
                nespace = 0
                result = ""
                for k in range(int(len(transcript)/7)-1):
                    nint = int(transcript[j+7*k:j+7*(k+1)][::-1],2)
                    if nint > 31:
                        result += "&#" + str(nint) + ";"
                    if nint == 32:
                        nespace += 1
                if nespace > espacemax:
                    espacemax = nespace
                    resultclair = result
                infobulle += result + "&#013"

            if not(resultclair == ""):
                retour1 = resultclair
                print("espacemaxc=", espacemax)
            else:
                retour1 = retour[1]

            #PROBLEME AFFICHAGE INFOBULLE : pas avec wx.html en python mais OK quand lance page sous firefox !!

            # MISE EN FORME AFFICHAGE HTML :
            retour_chaine = [retour[0], retour1, retour[2]]
            date_affiche, st2 = affichage_html(retour_chaine, infobulle, rb3, date1)
            
            # ENREGISTREMENT FICHIER HTML
            enregistre_fichier(st2, date1)
                    
            return st2,date_affiche
            
                
        else:
            return '<br>',''
                          
