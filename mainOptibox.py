#!/usr/bin/python

import time
import schedule
import serial
import sys
import pandas as pd
import numpy as np
from time import sleep
import RPi.GPIO as GPIO
from sendSigfox import Sigfox
import logging
from logging.handlers import TimedRotatingFileHandler
import os.path
import configparser
from helper import configHelper


config = configparser.ConfigParser()
config.read("./conf/config.ini")
logging.basicConfig(level=logging.INFO)

handler = TimedRotatingFileHandler("gpio.log",
                                       when="d",
                                       interval=1,
                                       backupCount=30)



formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger=logging.getLogger(__name__)
logger.addHandler(handler)
logger.info("HI From Logger...")

sgfx = Sigfox('/dev/serial0')

GPIO.setmode(GPIO.BCM)


print "CLEAN UP"
#GPIO.cleanup()

filesStore = []
gpioValues = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

for gpioFile in range(2,14):
    #print('range is '+ str(gpioFile))
    filesStore.append('data/f'+str(gpioFile)+'.txt')

x = 2
for i in filesStore:
    if os.path.exists(i):
        opFile = open(i, 'r')
        gpioValues[x]=int(opFile.read())
        logger.info(i+" exist, value is "+ str(gpioValues[x]))
        opFile.close()
    else:
        opFile = open(i, 'w')
        opFile.write('0')
        logger.info(i + " was created")
        #gpioValues=0
    x+=1


for gpioNum in range(2,14):
    GPIO.setup(gpioNum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    logger.info("GPIO "+ str(gpioNum) + " is setting up")

somethingchanged=False

def sendDataToSigfox():
    message = '0101'+hex(gpioValues[1])+hex(gpioValues[2])
    #print("Message sended to sigfox : "+message)
    logger.info("Trying sending sigfox data : "+ message)
    sgfx.sendMessage(message)

def sendDataToElk():
    logger.info("Sending message to ELK")

def gpio_callback(channel):
    global gpioValues
    global somethingchanged
    logger.info("falling edge detected on GPIO "+str(channel))
    gpioValues[channel] = int(gpioValues[channel])
    logger.info("gpioValue is "+str(gpioValues[channel]))
    gpioValues[channel] += 1
    logger.info("gpioValue is now "+str(gpioValues[channel]))
    somethingchanged = True

def rewriteFiles():
    global gpioValues
    global filesStore
    global somethingchanged
    logger.info("Rewrite file")
    x = 2
    if somethingchanged:
        logger.info("Something has changed")
        x=2
        for i in filesStore:
            logger.info("Trying to write value "+ str(gpioValues[x]) + " in file "+i)
            opFile = open(i, 'w')
            opFile.write(str(gpioValues[x]))
            opFile.close()
            x+=1
    somethingchanged = False



for gpioNum in range(2,14):
    logger.info('Configuring event on GPIO '+str(gpioNum))
    GPIO.add_event_detect(gpioNum, GPIO.FALLING, callback=gpio_callback, bouncetime=300)

useElk = configHelper.GetVariable('main', 'sendToElk')
useSigfox = configHelper.GetVariable('main', 'sendToSigfix')

if useSigfox:
    schedule.every(30).minutes.do(sendDataToSigfox)

if useElk:
    schedule.every(10).minutes.do(sendDataToElk)

schedule.every(1).minutes.do(rewriteFiles)
logger.info("schedule configured")

try:
    while True:
        #print "start boucle"
        #logger.info("==> Starting sending index to Sigfox")
        #sendDataToSigfox(A20)
        schedule.run_pending()
        #print "End schedule"
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit


GPIO.cleanup()           # clean up GPIO on normal exit
