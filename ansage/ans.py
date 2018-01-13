#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time



import playsnd
from gtts import gTTS
from fileinput import input

import platform

def downloadMP3(text,outputFile):
	try:
		tts = gTTS(text=text, lang='pl', slow=False)
		tts.save(outputFile)
		return True
	except Exception:
		return False



def playAnnoucement(filePath):	
	
	tab = [17,27]
	try:

		#GPIO.setmode(GPIO.BCM) #(GPIO.BOARD)
		GPIO.setup(17,GPIO.OUT)
		time.sleep(1)
		GPIO.setup(27,GPIO.OUT)
		time.sleep(1)
		playsnd.playsound("gong.wav")		
		time.sleep(1)
		GPIO.cleanup(27)
		time.sleep(2)	
		GPIO.cleanup(tab)
		return "ok"
	
	except KeyboardInterrupt:
		GPIO.cleanup(tab)
		return "nio"
	
	
input =  "Pociąg osobowy do Grodziska Wielkopolskiego odjedzie z toru pierwszego przy peronie drugim"

stra  = input.decode("'UTF-8")
downloadMP3(stra,"output.mp3")
playAnnoucement("output.mp3")