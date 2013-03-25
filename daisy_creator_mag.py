#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Autor: Joerg Sorge
Distributed under the terms of GNU GPL version 2 or later
Copyright (C) Joerg Sorge joergsorge at googel
2012-06-20

Dieses Programm 
- kopiert mp3-Files fuer die Verarbeitung zu Daisy-Buechern
- erzeugt die noetigen Dateien fuer eine Daisy-Struktur. 

This program
- makes copys of mp3-files from audiorecordings for daisy-production
- builds the daisy-struckture for digital audio books in daisy 2.02 standard

needs: 
python-mutagen
sudo apt-get install python-mutagen

update qt-GUI by development:
pyuic4 daisy_creator_mag.ui -o daisy_creator_mag_ui.py
""" 


from PyQt4 import QtGui, QtCore
import sys
import os
import shutil
import datetime
from datetime import timedelta
import ntpath
import subprocess
import types
import string
import re
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.id3 import ID3NoHeaderError
import ConfigParser
import daisy_creator_mag_ui

class DaisyCopy(QtGui.QMainWindow, daisy_creator_mag_ui.Ui_DaisyMain):
    """ 
    mainClass
    The second parent must be 'Ui_<obj. name of main widget class>'.
    """
 
    def __init__(self, parent=None):
        """Settings"""
        super(DaisyCopy, self).__init__(parent)
        # This is because Python does not automatically
        # call the parent's constructor.
        self.setupUi(self)
        # Pass this "self" for building widgets and
        # keeping a reference.
        self.app_debugMod = "yes"
        self.app_bhzItems = ["Zeitschrift"]        
        self.app_prevAusgItems = ["10",  "11",  "12",  "22",  "23",  "24"]
        self.app_currentAusgItems = ["I", "II", "III", "IV", "01", "02", "03",  "04",  "05",  "06",  "07",  "08",  "09",  "10",  "11",  "12",  "13",  "14",  "15",  "16",  "17",  "18",  "19",  "20",  "21",  "22",  "23",  "24"]
        self.app_nextAusgItems = ["I", "II", "01",  "02",  "03"]
        self.app_bhzPfad = QtCore.QDir.homePath() 
        self.app_bhzPfadMeta = QtCore.QDir.homePath() 
        self.app_bhzPfadAusgabeansage = QtCore.QDir.homePath() 
        self.app_bhzPfadIntro = QtCore.QDir.homePath() 
        self.connectActions()
    
    def connectActions(self):
        """define Actions """
        self.toolButtonCopySource.clicked.connect(self.actionOpenCopySource)
        self.toolButtonCopyDest.clicked.connect(self.actionOpenCopyDest)
        self.toolButtonCopyFile1.clicked.connect(self.actionOpenCopyFile1)
        self.toolButtonCopyFile2.clicked.connect(self.actionOpenCopyFile2)
        self.toolButtonMetaFile.clicked.connect(self.actionOpenMetaFile)
        self.commandLinkButton.clicked.connect(self.actionRunCopy)
        self.commandLinkButtonMeta.clicked.connect(self.metaLoadFile)
        self.commandLinkButtonDaisy.clicked.connect(self.actionRunDaisy)
        self.toolButtonDaisySource.clicked.connect(self.actionOpenDaisySource)
        self.pushButtonClose1.clicked.connect(self.actionQuit)
        self.pushButtonClose2.clicked.connect(self.actionQuit)

    def readConfig(self ):
        """read Config from file"""
        fileNotExist = None
        try:
            with open( "daisy_creator_mag.config" ) as f: pass
        except IOError as e:
            self.showDebugMessage(  u"File not exists" )
            self.textEdit.append("<b>Config-Datei konnte nicht geladen werden...</b>")   
            fileNotExist = "yes"
        
        if  fileNotExist is not None:
            return
        
        config = ConfigParser.RawConfigParser()
        config.read("daisy_creator_mag.config")
        self.app_bhzPfad = config.get('Ordner', 'BHZ')
        self.app_bhzPfadMeta = config.get('Ordner', 'BHZ-Meta')
        self.app_bhzPfadAusgabeansage  = config.get('Ordner', 'BHZ-Ausgabeansage')
        self.app_bhzPfadIntro  = config.get('Ordner', 'BHZ-Intro')
        self.app_bhzItems  = config.get('Blindenhoerzeitschriften', 'BHZ').split(",")

    def readHelp(self ):
        """read Readme from file"""
        fileNotExist = None
        try:
            with open( "README.md" ) as f: pass
        except IOError as e:
            self.showDebugMessage(  u"File not exists" )
            self.textEdit.append("<b>Help-Datei konnte nicht geladen werden...</b>")   
            fileNotExist = "yes"
        
        if  fileNotExist is not None:
            return
        
        fobj = open("README.md")
        for line in fobj:
            self.textEditHelp.append(line)
        # set cursor on top of helpfile
        cursor = self.textEditHelp.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor, 0)
        self.textEditHelp.setTextCursor(cursor)
        fobj.close()

    def actionOpenCopySource(self):
        """Source of copy"""
        # QtCore.QDir.homePath() 
        dirSource = QtGui.QFileDialog.getExistingDirectory(
                        self,
                        "Quell-Ordner",
                        self.app_bhzPfad
                    )
        # Don't attempt to open if open dialog
        # was cancelled away.
        if dirSource:
            self.lineEditCopySource.setText(dirSource)
            self.textEdit.append("Quelle:")
            self.textEdit.append(dirSource)
    
    def actionOpenDaisySource(self):
        """Source of daisy"""
        dirSource = QtGui.QFileDialog.getExistingDirectory(
                        self,
                        "Quell-Ordner",
                        self.app_bhzPfad
                    )
        # Don't attempt to open if open dialog
        # was cancelled away.
        if dirSource:
            self.lineEditDaisySource.setText(dirSource)
            self.textEdit.append("Quelle:")
            self.textEdit.append(dirSource)
    
    def actionOpenCopyDest(self):
        """Destination of Copy"""
        dirDest = QtGui.QFileDialog.getExistingDirectory(
                        self,
                        "Ziel-Ordner",
                        self.app_bhzPfad
                    )
        # Don't attempt to open if open dialog
        # was cancelled away.
        if dirDest:
            self.lineEditCopyDest.setText(dirDest)
            self.textEdit.append("Ziel:")
            self.textEdit.append(dirDest)
    
    def actionOpenCopyFile1(self):
        """Additional file 1 to copy"""
        file1 = QtGui.QFileDialog.getOpenFileName (
                        self,
                        "Datei 1",
                        QtCore.QDir.homePath()
                    )
        # Don't attempt to open if open dialog
        # was cancelled away.
        if file1:
            self.lineEditCopyFile1.setText(file1)
            self.textEdit.append("Zusatz-Datei 1:")
            self.textEdit.append(file1)

    def actionOpenCopyFile2(self):
        """Additional file 2 to copy"""
        file2 = QtGui.QFileDialog.getOpenFileName (
                        self,
                        "Datei 2",
                        QtCore.QDir.homePath()
                    )
        # Don't attempt to open if open dialog
        # was cancelled away.
        if file2:
            self.lineEditCopyFile2.setText(file2)
            self.textEdit.append("Zusatz-Datei 2:")
            self.textEdit.append(file2)
    
    def actionOpenMetaFile(self):
        """Metafile to load"""
        file = QtGui.QFileDialog.getOpenFileName (
                        self,
                        "Daisy_Meta",
                        self.app_bhzPfadMeta
                    )
        # Don't attempt to open if open dialog
        # was cancelled away.
        if file:
            self.lineEditMetaSource.setText(file)
    
    def actionRunCopy(self):
        """Mainfunction to copy"""
        if self.lineEditCopySource.text()== "Quell-Ordner":
            errorMessage = u"Quell-Ordner wurde nicht ausgewaehlt.."
            self.showDialogCritical( errorMessage )
            return
        
        if self.lineEditCopyDest.text()== "Ziel-Ordner":
            errorMessage = u"Ziel-Ordner wurde nicht ausgewaehlt.."
            self.showDialogCritical( errorMessage )
            return
        
        self.showDebugMessage(  self.lineEditCopySource.text() )
        self.showDebugMessage(  self.lineEditCopyDest.text() )
        
        # check for files in source
        try:
            dirsSource = os.listdir( self.lineEditCopySource.text())
        except Exception, e:
            errorMessage = u"Quelle: %s" % str(e)
            self.showDebugMessage( errorMessage)
            self.showDialogCritical( errorMessage )
            return
        
        # ceck dir of dest
        if os.path.exists(self.lineEditCopyDest.text() ) is False:
            errorMessage = u"Ziel-Ordner existiert nicht.."
            self.showDebugMessage( errorMessage)
            self.showDialogCritical( errorMessage )
            self.lineEditCopyDest.setFocus()
            return
        
        self.showDebugMessage( dirsSource )
        self.textEdit.append("<b>Kopieren:</b>")
        z = 0
        zList = len(dirsSource)
        self.showDebugMessage(  zList )
        dirsSource.sort()
        for item in dirsSource:
            if item[ len(item)-4:len(item) ] == ".MP3" or item[ len(item)-4:len(item) ] == ".mp3":
                fileToCopySource = self.lineEditCopySource.text() + "/" + item 
                # check if file exist
                fileNotExist = None
                try:
                    with open( fileToCopySource ) as f: pass
                except IOError as e:
                    self.showDebugMessage(  u"File not exists" )
                    fileNotExist = "yes"
                    # change max number and update progress
                    zList = zList -1
                    pZ = z *100 / zList 
                    self.progressBarCopy.setValue(pZ)
                
                self.showDebugMessage( fileToCopySource )
                
                if  fileNotExist is None:
                    # Bhz-Name dran
                    fileToCopyDest = self.lineEditCopyDest.text() + "/" + item[ 0:len(item)-4 ] + "_" + self.comboBoxCopyBhz.currentText() + "_" + self.comboBoxCopyBhzAusg.currentText() + "_" + item[ 0:len(item)-4 ] + ".mp3"

                    if self.checkBoxCopyChangeNr1001.isChecked():
                        # 1000.mp3 in 0100 umbenennen damit die Ansage weiter vorn einsortiert wird
                        if item[0:4] == "1001":
                            fileToCopyDest = self.lineEditCopyDest.text() + "/0100_" + self.comboBoxCopyBhz.currentText() + "_" + self.comboBoxCopyBhzAusg.currentText() + "_" + item[ 0:len(item)-4 ] + ".mp3"
                            self.textEdit.append(u"<b>1000.mp3 in 0100 umbenannt damit die Ansage weiter vorn einsortiert wird</b>")
                    
                    if self.checkBoxCopyChangeNr1000.isChecked():
                        # 1000.mp3 in 0100 umbenennen damit die Ansage weiter vorn einsortiert wird
                        if item[0:4] == "1000":
                            fileToCopyDest = self.lineEditCopyDest.text() + "/0100_" + self.comboBoxCopyBhz.currentText() + "_" + self.comboBoxCopyBhzAusg.currentText() + "_" + item[ 0:len(item)-4 ] + ".mp3"
                            self.textEdit.append(u"<b>1000.mp3 in 0100 umbenannt damit die Ansage weiter vorn einsortiert wird</b>")
                    
                    self.textEdit.append(fileToCopyDest)
                    self.showDebugMessage( fileToCopySource )
                    self.showDebugMessage( fileToCopyDest )
                    
                    # check bitrate, when necessary recode in new destination
                    isChangedAndCopy = self.checkChangeBitrateAndCopy( fileToCopySource,  fileToCopyDest )
                    # nothing to do, only copy
                    if  isChangedAndCopy is None: 
                        self.copyFile( fileToCopySource, fileToCopyDest)
                    
                    self.checkCangeId3( fileToCopyDest)
                    z +=1
                    self.showDebugMessage( z )
                    self.showDebugMessage( zList )
                    pZ = z *100 / zList 
                    self.showDebugMessage( pZ )
                    self.progressBarCopy.setValue(pZ)
                else:
                    self.textEdit.append("<b>Uebersprungen</b>:")
                    self.textEdit.append(fileToCopySource)
        
        self.showDebugMessage( z )
        if self.checkBoxCopyBhzIntro.isChecked():
            self.copyIntro()
        
        if self.checkBoxCopyBhzAusgAnsage.isChecked():
            self.copyAusgabeAnsage()
        
        if self.lineEditCopyFile1.text() != "Datei 1 waehlen":
            self.copyZusatzDatei( 1 )
        
        if self.lineEditCopyFile2.text() != "Datei 2 waehlen":
            self.copyZusatzDatei( 2 )
        
        # load metadata
        self.lineEditMetaSource.setText(self.app_bhzPfadMeta + "/Daisy_Meta_" + self.comboBoxCopyBhz.currentText()  )
        self.metaLoadFile()
        # enter path of source and destination 
        self.lineEditDaisySource.setText(self.lineEditCopyDest.text())
        
   
    def copyFile(self, fileToCopySource, fileToCopyDest):
       """copy file """
       try:
            shutil.copy( fileToCopySource, fileToCopyDest )
       except Exception, e:
            logMessage = u"copy_file Error: %s" % str(e)
            self.showDebugMessage(logMessage)
            self.textEdit.append(logMessage + fileToCopyDest)
    
    def copyIntro(self):
        """copy Intro"""
        fileToCopySource = self.app_bhzPfadIntro + "/Intro_" +  self.comboBoxCopyBhz.currentText()  + ".mp3"
        #if self.comboBoxCopyBhz.currentText() == "Bibel_fuer_heute":
        if self.checkBoxDaisyLevel.isChecked():
            # include level in filename
            fileToCopyDest = self.lineEditCopyDest.text() + "/0010_1_" +  self.comboBoxCopyBhz.currentText() + "_" + self.comboBoxCopyBhzAusg.currentText() + "_Intro.mp3"
        else:
            fileToCopyDest = self.lineEditCopyDest.text() + "/0010_" +  self.comboBoxCopyBhz.currentText() + "_" + self.comboBoxCopyBhzAusg.currentText() + "_Intro.mp3"
        self.showDebugMessage(fileToCopySource)
        self.showDebugMessage(fileToCopyDest)
        fileNotExist = None
        try:
            with open( fileToCopySource ) as f: pass
        except IOError as e:
            self.showDebugMessage(  u"File not exists" )
            # change from QTString to String
            self.textEdit.append("<font color='red'>Intro nicht vorhanden</font>: " + os.path.basename(str(fileToCopySource)))
            fileNotExist = "yes"
        
        if  fileNotExist is None:
            #shutil.copy( fileToCopySource, fileToCopyDest )
            self.copyFile( fileToCopySource, fileToCopyDest)
            self.checkCangeId3( fileToCopyDest)
    
    def copyAusgabeAnsage(self):
        """copy issue number"""
        pfadAusgabe = self.app_bhzPfadAusgabeansage + "_" + self.comboBoxCopyBhzAusg.currentText()[0:4] + "_" + self.comboBoxCopyBhz.currentText() 
        self.showDebugMessage(pfadAusgabe)
        fileToCopySource = pfadAusgabe + "/0001_" +  self.comboBoxCopyBhz.currentText() + "_" + self.comboBoxCopyBhzAusg.currentText() + "_Ausgabeansage.mp3"
        fileToCopyDest = self.lineEditCopyDest.text() + "/0001_" +  self.comboBoxCopyBhz.currentText() + "_" + self.comboBoxCopyBhzAusg.currentText() + "_Ausgabeansage.mp3"
        self.showDebugMessage(fileToCopySource)
        self.showDebugMessage(fileToCopyDest)
        fileNotExist = None
        try:
            with open( fileToCopySource ) as f: pass
        except IOError as e:
            self.showDebugMessage(  u"File not exists" )
            # change from QTString to String
            self.textEdit.append("<font color='red'>Ausgabeansage nicht vorhanden</font>: " + os.path.basename(str(fileToCopySource)))
            fileNotExist = "yes"
        
        if  fileNotExist is None:
            #shutil.copy( fileToCopySource, fileToCopyDest )
            self.copyFile( fileToCopySource, fileToCopyDest)
            self.checkCangeId3( fileToCopyDest)
    
    def copyZusatzDatei(self,  n ):
        """copy additional file kopieren"""
        if n == 1:
            filename = ntpath.basename( str(self.lineEditCopyFile1.text()) )
            patFilenameSource = str(self.lineEditCopyFile1.text())

        if n == 2:
            filename = ntpath.basename( str(self.lineEditCopyFile2.text()) )
            patFilenameSource = str(self.lineEditCopyFile2.text())
        
        self.showDebugMessage( u"Bitrate check: " + filename)
        fileToCopyDest = str(self.lineEditCopyDest.text()) +"/"+ filename
        # check bitrate, when necessary recode in new destination
        isChangedAndCopy = self.checkChangeBitrateAndCopy( patFilenameSource,  str(fileToCopyDest) )
        # nothing to do, only copy
        if  isChangedAndCopy is None: 
            #shutil.copy( fileToCopySource, fileToCopyDest )
            self.copyFile( patFilenameSource, fileToCopyDest)
            self.checkCangeId3( fileToCopyDest)

    def checkCangeId3(self, fileToCopyDest):
        """check id3 Tags, mayby kill it"""
        tag = None
        try:
            audio = ID3(fileToCopyDest)
            tag = "yes"
        except ID3NoHeaderError:
            self.showDebugMessage( u"No ID3 header found; skipping.")
        
        if tag is not None:
            if self.checkBoxCopyID3Change.isChecked():
                audio.delete()
                self.textEdit.append("<b>ID3 entfernt bei</b>: " + fileToCopyDest)
                self.showDebugMessage( u"ID3 entfernt bei " + fileToCopyDest)
            else:
                self.textEdit.append("<b>ID3 vorhanden, aber NICHT entfernt bei</b>: " + fileToCopyDest)
    
    def checkChangeBitrateAndCopy(self,  fileToCopySource, fileToCopyDest):
        """check bitrate, when necessary recode in new destination"""
        isChangedAndCopy = None
        audioSource = MP3( fileToCopySource )
        if audioSource.info.bitrate != int(self.comboBoxPrefBitrate.currentText())*1000:
            isEncoded = None
            self.textEdit.append( u"Bitrate Vorgabe: " + str(self.comboBoxPrefBitrate.currentText()) )
            self.textEdit.append( u"<b>Bitrate folgender Datei entspricht nicht der Vorgabe:</b> " + str(audioSource.info.bitrate/1000) + " " + fileToCopySource)
            
            if self.checkBoxCopyBitrateChange.isChecked():
                self.textEdit.append(u"<b>Bitrate aendern bei</b>: " + fileToCopyDest)
                isEncoded = self.encodeFile( fileToCopySource, fileToCopyDest )
                if isEncoded is not None:
                    self.textEdit.append(u"<b>Bitrate geaendert bei</b>: " + fileToCopyDest)
                    isChangedAndCopy = True
            else:
                self.textEdit.append(u"<b>Bitrate wurde NICHT geaendern bei</b>: " + fileToCopyDest)
        return isChangedAndCopy
    
    def encodeFile(self, fileToCopySource, fileToCopyDest ):
        """encode mp3-file """
        self.showDebugMessage( u"encode_file" )
        # characterset of commands is importand
        # encoding in the right manner
        c_lame_encoder = "/usr/bin/lame"
        self.showDebugMessage(  u"type c_lame_encoder" )
        self.showDebugMessage( type(c_lame_encoder) )
        self.showDebugMessage( u"fileToCopySource" )
        self.showDebugMessage( type(fileToCopySource) )
        self.showDebugMessage( fileToCopyDest )
        self.showDebugMessage( u"type(fileToCopyDest)" )
        self.showDebugMessage( type( fileToCopyDest ) )
        
        #p = subprocess.Popen([c_lame_encoder, "-b",  "64", "-m",  "m",  fileToCopySource, fileToCopyDest ],  stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(  )
        p = subprocess.Popen([c_lame_encoder, "-b",  self.comboBoxPrefBitrate.currentText(), "-m",  "m",  fileToCopySource, fileToCopyDest ],  stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(  )

        self.showDebugMessage( u"returncode 0" )
        self.showDebugMessage( p[0] )
        self.showDebugMessage( u"returncode 1" )
        self.showDebugMessage( p[1] )
    
        # search for success-message, when not found : -1
        n_encode_percent = string.find( p[1],  "(100%)" )
        n_encode_percent_1 = string.find( p[1],  "(99%)" )
        self.showDebugMessage( n_encode_percent )
        c_complete = "no"
    
        # if the file is very short, no 100% message appear, then also accept 99% 
        if n_encode_percent == -1:
            # no 100% 
            if n_encode_percent_1 != -1:
                #  but 99
                c_complete = "yes"
        else:
            c_complete = "yes"
    
        if c_complete == "yes" :
            log_message = u"recoded_file: " + fileToCopySource
            self.showDebugMessage( log_message )
            return fileToCopyDest
        else:
            log_message = u"recode_file Error: " + fileToCopySource
            self.showDebugMessage( log_message )
            return None
    
    def metaLoadFile(self ):
        fileNotExist = None
        try:
            with open( str(self.lineEditMetaSource.text()) ) as f: pass
        except IOError as e:
            self.showDebugMessage(  u"File not exists" )
            self.textEdit.append("<font color='red'>Meta-Datei konnte nicht geladen werden</font>: " + os.path.basename(str(self.lineEditMetaSource.text())))   
            fileNotExist = "yes"
        
        if  fileNotExist is not None:
            return
        
        config = ConfigParser.RawConfigParser()
        
        # change path from QTString to String
        config.read(str(self.lineEditMetaSource.text()))
        self.lineEditMetaProducer.setText(config.get('Daisy_Meta', 'Produzent'))
        self.lineEditMetaAutor.setText(config.get('Daisy_Meta', 'Autor'))
        self.lineEditMetaTitle.setText(config.get('Daisy_Meta', 'Titel'))
        self.lineEditMetaEdition.setText(config.get('Daisy_Meta', 'Edition'))
        self.lineEditMetaNarrator.setText(config.get('Daisy_Meta', 'Sprecher'))
        self.lineEditMetaKeywords.setText(config.get('Daisy_Meta', 'Stichworte'))
        self.lineEditMetaRefOrig.setText(config.get('Daisy_Meta', 'ISBN/Ref-Nr.Original'))
        self.lineEditMetaPublisher.setText(config.get('Daisy_Meta', 'Verlag'))
        self.lineEditMetaYear.setText(config.get('Daisy_Meta', 'Jahr'))
    
    def actionRunDaisy(self):
        """create daisy-fileset"""
        if self.lineEditDaisySource.text()== "Quell-Ordner":
            errorMessage = u"Quell-Ordner wurde nicht ausgewaehlt.."
            self.showDialogCritical( errorMessage )
            return
        
        # read audiofiles
        try:
            dirItems = os.listdir( self.lineEditDaisySource.text())
        except Exception, e:
            logMessage = u"read_files_from_dir Error: %s" % str(e)
            self.showDebugMessage( logMessage)
        
        self.progressBarDaisy.setValue(10)
        self.showDebugMessage( dirItems )
        self.textEditDaisy.append(u"<b>Folgende Audios werden bearbeitet:</b>")
        zMp3 = 0
        zList = len(dirItems)
        self.showDebugMessage(  zList )
        dirAudios = []
        dirItems.sort()
        for item in dirItems:
            if item[ len(item)-4:len(item) ] == ".MP3" or item[ len(item)-4:len(item) ] == ".mp3":
                dirAudios.append(item) 
                self.textEditDaisy.append(item)
                zMp3 +=1

        #totalAudioLength = self.calcAudioLengt(dirAudios)
        lTimes = self.calcAudioLengt(dirAudios)
        totalAudioLength = lTimes[0]
        lTotalElapsedTime = lTimes[1]
        lFileTime = lTimes[2]
        #print totalAudioLength
        totalTime = timedelta(seconds = totalAudioLength)
        # change from timedelta in to string
        # hours, minits and seconds must have 2 digits (zfill(8))

        lTotalTime = str(totalTime).split(".")
        cTotalTime = lTotalTime[0].zfill(8)
        #str(cTotalTime[0]).zfill(8) 
        self.textEditDaisy.append(u"Gesamtlaenge: " + cTotalTime)
        self.writeNCC( cTotalTime,  zMp3,  dirAudios)
        self.progressBarDaisy.setValue(20)
        self.writeMasterSmil( cTotalTime,  dirAudios)
        self.progressBarDaisy.setValue(50)
        self.writeSmil( lTotalElapsedTime,  lFileTime, dirAudios)
        self.progressBarDaisy.setValue(100)
    
    def calcAudioLengt(self,  dirAudios):
        """calc total length"""
        totalAudioLength =0
        lTotalElapsedTime = []
        lTotalElapsedTime.append(0)
        lFileTime = []
        for item in dirAudios:
            fileToCheck = os.path.join( str(self.lineEditDaisySource.text()), item) 
            audioSource = MP3( fileToCheck )
            self.showDebugMessage(item + " "+ str(audioSource.info.length))
            totalAudioLength += audioSource.info.length
            lTotalElapsedTime.append(totalAudioLength)
            lFileTime.append(audioSource.info.length)
            lTimes = []
            lTimes.append(totalAudioLength)
            lTimes.append(lTotalElapsedTime)
            lTimes.append(lFileTime)
        return lTimes
    
    def writeNCC(self, cTotalTime,  zMp3,  dirAudios):
        """write NCC-Page"""
        # Levels
        maxLevel = "1"
        # find max-level
        if self.checkBoxDaisyLevel.isChecked():
            for item in dirAudios:
                self.showDebugMessage("Level: " +  item[5:6] )
                if re.match("\d{1,}",item[5:6] ) is not None:
                    if  item[5:6] > maxLevel:
                        maxLevel = item[5:6]
        
        try:
            fOutFile = open( os.path.join( str(self.lineEditDaisySource.text()), "ncc.html")  , 'w')
        except IOError as (errno, strerror):
            self.showDebugMessage( "I/O error({0}): {1}".format(errno, strerror) )
        else:
            self.textEditDaisy.append(u"<b>NCC-Datei schreiben...</b>")
            fOutFile.write( '<?xml version="1.0" encoding="utf-8"?>'+ '\r\n' )
            fOutFile.write( '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'+ '\r\n')
            fOutFile.write( '<html xmlns="http://www.w3.org/1999/xhtml">'+ '\r\n')
            fOutFile.write( '<head>'+ '\r\n')
            fOutFile.write( '<meta http-equiv="Content-type" content="text/html; charset=utf-8"/>'+ '\r\n')
            fOutFile.write( '<title>' + self.comboBoxCopyBhz.currentText() + '</title>'+ '\r\n')

            fOutFile.write( '<meta name="ncc:generator" content="KOM-IN-DaisyCreator"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:revision" content="1"/>'+ '\r\n')
            today = datetime.date.today()
            fOutFile.write( '<meta name="ncc:producedDate" content="' + today.strftime("%Y-%m-%d") + '"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:revisionDate" content="' + today.strftime("%Y-%m-%d") + '"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:tocItems" content="' + str( zMp3 ) + '"/>'+ '\r\n')
            
            fOutFile.write( '<meta name="ncc:totalTime" content="' + cTotalTime+ '"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:narrator" content="' + self.lineEditMetaNarrator.text() + '"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:pageNormal" content="0"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:pageFront" content="0"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:pageSpecial" content="0"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:sidebars" content="0"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:prodNotes" content="0"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:footnotes" content="0"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:depth" content="' + maxLevel + '"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:maxPageNormal" content="0"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:charset" content="utf-8"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:multimediaType" content="audioNcc"/>'+ '\r\n')
            #fOutFile.write( '<meta name="ncc:kByteSize" content=" "/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:setInfo" content="1 of 1"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:sourceDate" content="' + self.lineEditMetaYear.text()+ '"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:sourceEdition" content="' + self.lineEditMetaEdition.text() + '"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:sourcePublisher" content="' + self.lineEditMetaPublisher.text()+ '"/>'+ '\r\n')

            #Anzahl files = Records 2x + ncc.html + master.smil
            fOutFile.write( '<meta name="ncc:files" content="' + str(zMp3 + zMp3 + 2) + '"/>'+ '\r\n')
            fOutFile.write( '<meta name="ncc:producer" content="' + self.lineEditMetaProducer.text()+ '"/>'+ '\r\n')

            fOutFile.write( '<meta name="dc:creator" content="' + self.lineEditMetaAutor.text()+ '"/>'+ '\r\n')
            fOutFile.write( '<meta name="dc:date" content="' + today.strftime("%Y-%m-%d")+ '"/>'+ '\r\n')
            fOutFile.write( '<meta name="dc:format" content="Daisy 2.02"/>'+ '\r\n')
            fOutFile.write( '<meta name="dc:identifier" content="' + self.lineEditMetaRefOrig.text()+ '"/>'+ '\r\n')
            fOutFile.write( '<meta name="dc:language" content="de" scheme="ISO 639"/>'+ '\r\n')
            fOutFile.write( '<meta name="dc:publisher" content="' + self.lineEditMetaPublisher.text()+ '"/>'+ '\r\n')
            fOutFile.write( '<meta name="dc:source" content="' +self.lineEditMetaRefOrig.text()+ '"/>'+ '\r\n')
            fOutFile.write( '<meta name="dc:subject" content="' + self.lineEditMetaKeywords.text()+ '"/>'+ '\r\n')
            fOutFile.write( '<meta name="dc:title" content="' +self.lineEditMetaTitle.text()+ '"/>'+ '\r\n')
            # Medibus-OK items
            fOutFile.write( '<meta name="prod:audioformat" content="wave 44 kHz"/>'+ '\r\n')
            fOutFile.write( '<meta name="prod:compression" content="mp3 ' + self.comboBoxPrefBitrate.currentText()  + '/ kb/s"/>'+ '\r\n')      
            fOutFile.write( '<meta name="prod:localID" content=" "/>'+ '\r\n')      
            fOutFile.write( '</head>'+ '\r\n')
            fOutFile.write( '<body>'+ '\r\n')
            z = 0
            for item in dirAudios:
                z +=1
                if z == 1:
                    fOutFile.write('<h1 class="title" id="cnt_0001"><a href="0001.smil#txt_0001">' + self.lineEditMetaAutor.text()+ ": " + self.lineEditMetaTitle.text() + '</a></h1>'+ '\r\n')
                    continue
                # splitting
                itemSplit = self.splitFilename( item)
                cTitle = self.extractTitle( itemSplit)
                
                # BHZ Specials
                # Date as title for Calendars like "Bibel fuer heute"
                #if self.comboBoxCopyBhz.currentText() == "Bibel_fuer_heute":
                if self.checkBoxDaisyDateCalendar.isChecked():
                    if cTitle[2:4] == "00":
                        # Month as title
                        cTitleDate = cTitle[0:2]+" - "+ self.comboBoxCopyBhzAusg.currentText()[0:4]
                    else:
                        if re.match("\d{4,}",cTitle ) is not None:
                            # Date as title
                            cTitleDate = cTitle[2:4]+"."+cTitle[0:2]+"."+ self.comboBoxCopyBhzAusg.currentText()[0:4]
                        else:
                            # Title unchanged
                            cTitleDate = cTitle                        
                
                # Levels
                if self.checkBoxDaisyLevel.isChecked():
                    # multible levels, extract level-no from digit in filename (1. digit after underline)
                    self.showDebugMessage( item[5:6] )
                    fOutFile.write('<h'+ item[5:6] +' id="cnt_'+str(z).zfill(4)+'"><a href="'+str(z).zfill(4)+'.smil#txt_'+str(z).zfill(4)+'">'+ cTitleDate + '</a></h' + item[5:6]+ '>'+ '\r\n')
                else:
                    fOutFile.write('<h1 id="cnt_'+str(z).zfill(4)+'"><a href="'+str(z).zfill(4)+'.smil#txt_'+str(z).zfill(4)+'">'+ cTitle + '</a></h1>'+ '\r\n')
                
            fOutFile.write( "</body>"+ '\r\n')
            fOutFile.write( "</html>"+ '\r\n')
            fOutFile.close
        self.textEditDaisy.append(u"<b>NCC-Datei geschrieben</b>")

    def writeMasterSmil(self, cTotalTime,  dirAudios):
        """write MasterSmil-page"""
        try:
            fOutFile = open( os.path.join( str(self.lineEditDaisySource.text()), "master.smil")  , 'w')
        except IOError as (errno, strerror):
            self.showDebugMessage( "I/O error({0}): {1}".format(errno, strerror) )
        else:
            self.textEditDaisy.append(u"<b>MasterSmil-Datei schreiben...</b>")
            fOutFile.write( '<?xml version="1.0" encoding="utf-8"?>'+ '\r\n' )
            fOutFile.write( '<!DOCTYPE smil PUBLIC "-//W3C//DTD SMIL 1.0//EN" "http://www.w3.org/TR/REC-smil/SMIL10.dtd">'+'\r\n')
            fOutFile.write( '<smil>'+'\r\n')
            fOutFile.write( '<head>'+'\r\n')
            fOutFile.write( '<meta name="dc:format" content="Daisy 2.02"/>'+'\r\n')
            fOutFile.write( '<meta name="dc:identifier" content="'+ self.lineEditMetaRefOrig.text()+ '"/>'+'\r\n')
            fOutFile.write( '<meta name="dc:title" content="' + self.lineEditMetaTitle.text() + '"/>'+'\r\n')
            fOutFile.write( '<meta name="ncc:generator" content="KOM-IN-DaisyCreator"/>'+'\r\n')
            fOutFile.write( '<meta name="ncc:format" content="Daisy 2.0"/>'+'\r\n')
            fOutFile.write( '<meta name="ncc:timeInThisSmil" content="' + cTotalTime +  '" />'+'\r\n')

            fOutFile.write( '<layout>'+'\r\n')
            fOutFile.write( '<region id="txt-view" />'+'\r\n')
            fOutFile.write( '</layout>'+'\r\n')
            fOutFile.write( '</head>'+'\r\n')
            fOutFile.write( '<body>'+'\r\n')
   
            #fOutFile.write( '<ref src="0001.smil" title="'+ self.lineEditMetaTitle.text() + '" id="smil_0001"/>'+'\r\n')            
            z = 0
            for item in dirAudios:
                z +=1
                # splitting
                itemSplit = self.splitFilename( item)
                cTitle = self.extractTitle( itemSplit)  
                fOutFile.write('<ref src="'+str(z).zfill(4)+'.smil" title="' + cTitle + '" id="smil_' + str(z).zfill(4) + '"/>'+'\r\n')
            
            fOutFile.write( '</body>'+'\r\n')
            fOutFile.write( '</smil>'+'\r\n')
            fOutFile.close
        self.textEditDaisy.append(u"<b>Master-smil-Datei geschrieben</b>")

    def writeSmil(self, lTotalElapsedTime, lFileTime, dirAudios):
        """write Smil-Pages"""
        self.textEditDaisy.append(u"<b>smil-Dateien schreiben...</b> ")
        z = 0
        for item in dirAudios:
            z +=1
            
            try:
                filename = str(z).zfill(4) +'.smil'
                fOutFile = open( os.path.join( str(self.lineEditDaisySource.text()), filename  ) , 'w')
            except IOError as (errno, strerror):
                self.showDebugMessage( "I/O error({0}): {1}".format(errno, strerror) )
            else:
                self.textEditDaisy.append( str(z).zfill(4) +u".smil - File schreiben")
                # splitting
                itemSplit = self.splitFilename( item)
                cTitle = self.extractTitle( itemSplit)  
                
                fOutFile.write( '<?xml version="1.0" encoding="utf-8"?>'+ '\r\n' )
                fOutFile.write( '<!DOCTYPE smil PUBLIC "-//W3C//DTD SMIL 1.0//EN" "http://www.w3.org/TR/REC-smil/SMIL10.dtd">'+'\r\n')
                fOutFile.write( '<smil>'+'\r\n')
                fOutFile.write( '<head>'+'\r\n')
                fOutFile.write( '<meta name="ncc:generator" content="KOM-IN-DaisyCreator"/>'+'\r\n')
                totalElapsedTime = timedelta(seconds = lTotalElapsedTime[z-1])
                splittedTtotalElapsedTime = str(totalElapsedTime).split(".")
                self.showDebugMessage( u"splittedTtotalElapsedTime: ")
                self.showDebugMessage( splittedTtotalElapsedTime )
                totalElapsedTimehhmmss = splittedTtotalElapsedTime[0].zfill(8)
                if z == 1:
                    # thirst item results in only one split
                    totalElapsedTimeMilliMicro = "000"
                else:
                    totalElapsedTimeMilliMicro = splittedTtotalElapsedTime[1][0:3] 
                #fOutFile.write( '<meta name="ncc:totalElapsedTime" content="' + str(lTotalElapsedTime[z-1] )+ '"/>')
                #fOutFile.write( '<meta name="ncc:totalElapsedTime" content="' + str( totalElapsedTime )+ '"/>'+'\r\n')
                fOutFile.write( '<meta name="ncc:totalElapsedTime" content="' +totalElapsedTimehhmmss + "." + totalElapsedTimeMilliMicro +'"/>'+'\r\n')
                
                fileTime = timedelta(seconds = lFileTime[z-1])
                self.showDebugMessage(u"filetime: " + str(fileTime))
                splittedFileTime = str(fileTime).split(".")
                FileTimehhmmss = splittedFileTime[0].zfill(8)
                # it's only one item in list when no milliseconds
                if len(splittedFileTime) >1:
                    if len(splittedFileTime[1]) >= 3:
                        fileTimeMilliMicro = splittedFileTime[1][0:3] 
                    elif len(splittedFileTime[1]) == 2:
                        fileTimeMilliMicro = splittedFileTime[1][0:2] 
                else:
                    fileTimeMilliMicro = "000"
                
                #fOutFile.write( '<meta name="ncc:timeInThisSmil" content="' + str(lFileTime[z-1]) + '" />'+'\r\n')

                fOutFile.write( '<meta name="ncc:timeInThisSmil" content="' + FileTimehhmmss + "." + fileTimeMilliMicro +'" />'+'\r\n')
                fOutFile.write( '<meta name="dc:format" content="Daisy 2.02"/>'+'\r\n')
                fOutFile.write( '<meta name="dc:identifier" content="' + self.lineEditMetaRefOrig.text() + '"/>'+'\r\n')
                fOutFile.write( '<meta name="dc:title" content="' +  cTitle  + '"/>'+'\r\n')
                fOutFile.write( '<layout>'+'\r\n')
                fOutFile.write( '<region id="txt-view"/>'+'\r\n')
                fOutFile.write( '</layout>'+'\r\n')
                fOutFile.write( '</head>'+'\r\n')
                fOutFile.write( '<body>'+'\r\n')
                #fOutFile.write( '<seq dur="' + FileTimehhmmss + '.' + fileTimeMilliMicro + 's">'+'\r\n')
                lFileTimeSeconds = str(lFileTime[z-1]).split(".")
                
                fOutFile.write( '<seq dur="' + lFileTimeSeconds[0] + '.' + fileTimeMilliMicro  +'s">'+'\r\n')
                fOutFile.write( '<par endsync="last">'+'\r\n')
                fOutFile.write( '<text src="ncc.html#cnt_' + str(z).zfill(4) + '" id="txt_' + str(z).zfill(4) + '" />'+'\r\n')
                fOutFile.write( '<seq>'+'\r\n')
                if fileTime < timedelta(seconds=45):
                    fOutFile.write( '<audio src="' + item + '" clip-begin="npt=0.000s" clip-end="npt=' + lFileTimeSeconds[0] + '.' + fileTimeMilliMicro + 's" id="a_' + str(z).zfill(4)  + '" />'+'\r\n')
                else:
                    fOutFile.write( '<audio src="' + item + '" clip-begin="npt=0.000s" clip-end="npt=' + str(15) + '.' + fileTimeMilliMicro + 's" id="a_' + str(z).zfill(4)  + '" />'+'\r\n')
                    zz=z+1
                    phraseSeconds = 15
                    while phraseSeconds <= lFileTime[z-1]-15:
                        fOutFile.write( '<audio src="' + item + '" clip-begin="npt='+ str(phraseSeconds)+ '.' + fileTimeMilliMicro + 's" clip-end="npt=' + str(phraseSeconds+15) + '.' + fileTimeMilliMicro + 's" id="a_' + str(zz).zfill(4)  + '" />'+'\r\n')
                        phraseSeconds +=15
                        zz +=1
                    fOutFile.write( '<audio src="' + item + '" clip-begin="npt='+ str(phraseSeconds)+ '.' + fileTimeMilliMicro + 's" clip-end="npt=' + lFileTimeSeconds[0] + '.' + fileTimeMilliMicro + 's" id="a_' + str(zz).zfill(4)  + '" />'+'\r\n')
                
                fOutFile.write( '</seq>'+'\r\n')
                fOutFile.write( '</par>'+'\r\n')
                fOutFile.write( '</seq>'+'\r\n')

                fOutFile.write( '</body>'+'\r\n')
                fOutFile.write('</smil>'+'\r\n')
                fOutFile.close
        self.textEditDaisy.append(u"<b>smil-Dateien geschrieben:</b> " +str(z))

    def splitFilename(self,  item):
        """split filename into list"""
        if self.comboBoxDaisyTrenner.currentText()=="Ausgabe-Nr.":
            itemSplit = item.split(self.comboBoxCopyBhzAusg.currentText()+"_")
            #itemSplit = item.split("_", 2)
        self.showDebugMessage( itemSplit )
        self.showDebugMessage( len(itemSplit))
        return itemSplit
    
    def extractTitle(self, itemSplit):
        """extract title """
        # last piece
        itemLeft = itemSplit[len(itemSplit)-1]
        # now split file-extention
        itemTitle = itemLeft.split(".mp3")
        cTitle = re.sub ("_", " ", itemTitle[0]  ) 
        return cTitle
    
    def showDialogCritical(self,  errorMessage):
        """show messagebox warning"""
        QtGui.QMessageBox.critical(self, "Achtung", errorMessage)
    
    def showDebugMessage(self,  debugMessage):
        """show messagebox """
        if self.app_debugMod == "yes":
            print debugMessage
    
    def actionQuit(self):
        """exit the application"""
        QtGui.qApp.quit()
    
    def main(self):
        """mainfunction"""
        self.showDebugMessage( u"let's rock" )
        self.readConfig()
        self.progressBarCopy.setValue(0)
        self.progressBarDaisy.setValue(0)
        # Bhz in Combo
        for item in self.app_bhzItems:
            self.comboBoxCopyBhz.addItem(item)
        # Combi-items: numbers according to years
        prevYear = str( datetime.datetime.now().year -1 )
        currentYear = str( datetime.datetime.now().year )
        nextYear = str( datetime.datetime.now().year +1 )
        for item in self.app_prevAusgItems:
            self.comboBoxCopyBhzAusg.addItem(prevYear + "_" + item)
        for item in self.app_currentAusgItems:
            self.comboBoxCopyBhzAusg.addItem(currentYear + "_" + item)
        for item in self.app_nextAusgItems:
            self.comboBoxCopyBhzAusg.addItem(nextYear + "_" + item)
        # Combo-items: string for splitting author and title in filenames
        self.comboBoxDaisyTrenner.addItem("Ausgabe-Nr.")
        self.comboBoxDaisyTrenner.addItem(prevYear)
        self.comboBoxDaisyTrenner.addItem(currentYear)
        self.comboBoxDaisyTrenner.addItem(nextYear)
        self.comboBoxDaisyTrenner.addItem("-")
        self.comboBoxDaisyTrenner.addItem("_")
        self.comboBoxDaisyTrenner.addItem("_-_")
        self.comboBoxPrefBitrate.addItem("64")
        self.comboBoxPrefBitrate.addItem("96")
        self.comboBoxPrefBitrate.addItem("128")
        # defaults for checkboxes
        self.checkBoxCopyBhzIntro.setChecked(True)
        self.checkBoxCopyBhzAusgAnsage.setChecked(True)
        self.checkBoxCopyID3Change.setChecked(True)
        self.checkBoxCopyBitrateChange.setChecked(True)
        # Help-Text
        self.readHelp()
        self.show()
 
if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    dyc = DaisyCopy()
    dyc.main()
    app.exec_()
    # This shows the interface we just created. No logic has been added, yet.
