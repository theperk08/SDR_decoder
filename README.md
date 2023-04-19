# SDR_decoder
--> SDR decoder for POCSAG and ACARS messages

---------
> __Warning__:  
<b>Only for personal use  
This is only an amateur and personal project</b>  
---------

## REQUIREMENTS
```
- SDR USB Dongle (with of course an antenna) : RTL-SDR with the RTL2832U chipset
- SDR software : CubicSDR, HDSDR, SDR#, GQRX...
- Virtual Audio Cable
- Python (v3)
```

## **INSTALLATION**

Copy and paste the files in a directory

Then, be sure to have all these libraries in your python environment : 
```
  - sys
  - datetime
  - math
  - numpy
  - scipy
  - wave
  - pyaudio
  - wx
  - subprocess
```  
**IMPORTANT** : you also need to download a special library to decode some specifics ACARS messages :
  
  [libacars](https://github.com/szpajder/libacars/releases/tag/v1.2.0) which contains the executable file : decode_arinc.exe :  
  
  libacars, Copyright (c) 2018-2021 Tomasz Lemiech szpajder@gmail.com
 
 
<b>Then, edit the Config.ini file to set up paths and names for your files</b>


## USAGE

**Launch your SDR software,** 
  and tune in on a frequency (some examples for Western Europe) :
  - for ACARS (in AM mode, 10kHz bandwidth) : 131.525MHz, 131.725MHz, 131.825MHz
  - for POCSAG (in NBFM mode, 20kHz bandwidth or 6500 for Infirmier) :  
    Belgique : 169.625MHz  
    France : 466.025MHz, 466.05MHz, 466.075MHz, 466.175MHz, 466.2063MHz  
    Infirmier : 26.695MHz, 26.745MHz, 28.66523MHz, 29.30519MHz  

**Launch : RTL_SDR_Decodeur_23.py**
```
  - Select the type of Message (ACARS or POCSAG)
  - then click on 'Démarrer'  
  - If you choose POCSAG, you have to choose the Bitrate option (the 1200-Infirmier is still in development)
  - You can choose to save the audio files (Enreg fichiers audios : Oui/Yes or Non/No)
  ```
(sometimes, changing between ACARS and POCSAG may cause troubleshooting, so click on 'stopper' before changing, or re-run the program if it fails)  

## EXAMPLE :
![Screenshot des exemples de messages reçus](/POCSAG_ACARS_Messages_Exemples.jpg)


## NOTES
- If reception is good, you can tune in on 2 differents ACARS frequencies at one time (only one for POCSAG messages)
- Due to some bad reception conditions, I introduced some offset decoding with the POCSAG messages : you can see it by pointing your mouse over the 'Message alphanumérique' 
- I don't use the CRC check, that's the reason why a lot of messages have errors, sorry for that.
- Some of the ACARS messages (Label : 44) are encrypted (with a very low encryption mode, ie simple substitution) : I discovered it recently so I don't have yet all the 10 complete substistutions alphabets.
- ACARS messages with Label 1L are also encrypted : If you know how, don't hesitate to tell me.
- Sorry for my english, I'm just a frenchman :smiley:
