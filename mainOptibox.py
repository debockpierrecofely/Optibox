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
gpioValues = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

for gpioFile in range(2,13):
    print('range is '+ str(gpioFile))
    filesStore.append('data/f'+str(gpioFile)+'.txt')

x = 0
for i in filesStore:
    if os.path.exists(i):
        opFile = open(i, 'r')
        gpioValues[x]=opFile.read()
        opFile.close()
    else:
        opFile = open(i, 'w')
        opFile.write('0')
        #gpioValues=0


for gpioNum in range(2,13):
    GPIO.setup(gpioNum, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

somethingchanged=False

def sendDataToSigfox():
    message = '0101'+hex(gpioValues[1])+hex(gpioValues[2])
    print("Message sended to sigfox : "+message)
    logger.info("Trying sending sigfox data : "+ message)
    sgfx.sendMessage(message)

#def sendDataToElk():

def gpio_callback(channel):
    global gpioValues
    print "falling edge detected on GPIO "+channel
    gpioValues[channel] = int(gpioValues[channel])
    gpioValues[channel] += 1


for gpioNum in range(2,13):
    print('Configuring GPIO '+str(gpioNum))
    GPIO.add_event_detect(gpioNum, GPIO.FALLING, callback=gpio_callback, bouncetime=300)


schedule.every(30).minutes.do(sendDataToSigfox)

try:
    while True:
        #print "start boucle"
        #logger.info("==> Starting sending index to Sigfox")
        #sendDataToSigfox(A20)
        schedule.run_pending()
        print "End schedule"
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    f16.close()
    f19.close()
    f20.close()
    f26.close()

GPIO.cleanup()           # clean up GPIO on normal exit
f16.close()
f19.close()
f20.close()
f26.close()
