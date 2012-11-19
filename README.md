daisy-creator-magazin
=====================

Create digital talking books of audio magazins for blind people in the daisy 2.02 standard.

Basics
------
The workflow is as follows:
- Record your articles with a digital recorder, like the marantz PMD 661
- The produced audiofiles are stored as mp3 in a flat struckture with numbered filenames up to 1000
- Mount the recordet media-card to your PC
- Now start the daisy-creator-magazin-application to create the daisy-fileset

If finished, you will find in the destinationfolder your audiofiles
and the daisy-structure for your daisy-player 
The audiofiles are renamend like your metadata.

General work steps
------------------
1. Choose the folder of your recordet audiofiles as "Source-Folder"
2. Choose the folder for your dtb as "Destination-Folder"
3. Choose the title and number of your magazin
4. Select the options if necessary (see options-section)
5. Run "Copy"
6. Select tab two
7. Control and edit your metadata if necessary
8. Select tab three
9. Edit options if necessary
10. Run "Daisy"
Done! 

Additional audiofiles-section
-----------------------------
With this, you can load and insert in the daisystruckture one or two separate redordet audiofiles, 
they not are on your mediacard. To sort the audiofiles before your audios from the mediacard, 
lets the filename begin with the number "0101".

Options-Section on tab one
--------------------------
Here, you can select:
1. Copy Magazin-Number
This will copy a audiofile, with e.g. a separate produced announcement of your magazin-number, in the daisy-structure
2. Copy Intro
This will copy a audiofile with a separate produced jingle or intro
3. Change bitrate
This check the bitrate of each audiofile and changes it to the choosen rate on the "Preferences-Tab"
4. Rename 1000 (or 1001) to 0100 (0101)
This is used, when the first recordet audiofile (e.g. with a special announcement) 
must sorted before the additive audiofiles (see Additional audiofiles)

Preferences
-----------
- The titels and available numbers of your magazins will be load from the configfile: daisy_creator_mag.config.
See daisy_creator_mag.config.sample for the syntax.
- The metadata for each magazin will be load from a file in the folder (set in config-file) by the name of the magazin.
See Daisy_Meta_My_Magazin.sample for the syntax

Remark
------
The daisy_creator_mag is written by Joerg Sorge for KOM-IN-Netzwerk e.V. www.kom-in.de


