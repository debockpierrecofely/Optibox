#!/usr/bin/python

import time
import datetime
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
import pika
import threading
from uuid import getnode as get_mac

################################################################################
# NOTE: Pin 2 and 3 has been replaced by 20 and 21 because the voltage of GPIO 2
# and 3 is lower than the other ones and it created issues with the protection
# circuit
################################################################################


################################################################################
# v0.1 30May2017 PDE FIRST VERSION
################################################################################

logging.basicConfig(level=logging.INFO)

handler = TimedRotatingFileHandler("gpio.log",
                                       when="d",
                                       interval=1,
                                   backupCount=30)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger=logging.getLogger(__name__)
logger.addHandler(handler)
logger.info("Starting Optibox v0.1")


################################################################################
# Create Buffer
################################################################################
def createBuffer():
    logger.info(">>>>>> Enter into createbuffer")
    global gpioValues
    global messIndex
    byte0 = '01'
    byte1 = ''
    byte2 = ''
    byte3 = '0b'
    for i in range(8,14):
        if GPIO.input(i) == 1:
            byte3 += '0'
        else:
            byte3 += '1'

    byte3+='00'
    byte3 = '%02X' % (int(byte3, 2))
    ident1 = ''
    ident2 = ''
    index1 = ''
    index2 = ''
    buffIndex = 0
    logger.info("BYTE 3 : "+byte3)

    for gpioNum in range (2,14):
        if usedentries[gpioNum] == 1 or gpiohours[gpioNum] == 1:
            logger.info("treating GPIO number "+ str(gpioNum))
            value = int(gpioValues[gpioNum])
            if (buffIndex % 2)==0 :
                ident1 = bin(gpioNum)
                index1 = bin(value)
                logger.info("Ident1 : "+ ident1 + "index1 : "+index1)
            else:
                ident2 = bin(gpioNum)[2:].zfill(4)
                index2 = bin(value)
                logger.info("Ident2 : "+ ident2 + "index2 : "+index2)
                byte1 = '%02X' % (int((ident1+ident2),2))
                if messIndex == 256:
                    messIndex = 0
                byte2 = '%02X' % messIndex
                index1 = '%08X' % (int(index1, 2))
                index2 = '%08X' % (int(index2, 2))
                logger.info('BYTE 1 (SUB TYPE):' + byte1)
                logger.info('BYTE 2 (SEQ):' + byte2)
                logger.info('BYTE 3 (STATES):' + byte3)
                logger.info('INDEX 1 :' + index1)
                logger.info('INDEX 2 :' + index2)
                message = byte0+byte1+byte2+byte3+index1+index2
                logger.info("Message ready to be send : "+message)
                sendDataToSigfox(message)
                messIndex += 1
            buffIndex +=1

################################################################################
# Creating threads
################################################################################

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

################################################################################
# Create buffer for invoice called by event
################################################################################

def createRelayBuffer(gpioNum):
    logger.info(">>>>> Enter into event createbuffer")
    global gpioValues
    global messIndex

    logger.info("Mess Index="+str(messIndex))
    if messIndex == 256:
        messIndex = 0
    byte0 = '01'
    byte1 = ''
    byte2 = ''
    byte3 = '0b'
    for i in range(8,14):
        if GPIO.input(i) == 1:
            byte3 += '0'
        else:
            byte3 += '1'
    byte3+='00'
    logger.info("Realy states:"+byte3)
    byte3 = '%02X' % (int(byte3, 2))
#    messIndex = 0
    ident1 = ''
    ident2 = ''
    index1 = ''
    index2 = ''
    buffIndex = 0
    value = int(gpioValues[gpioNum])
    ident = bin(gpioNum)+'0000'
    index1 = bin(value)
    logger.info("Ident1 : "+ ident1 + "index1 : "+index1)
    index2 = '0b00000000'
    byte1 = '%02X' % (int((ident),2))
    byte2 = '%02X' % messIndex
    index1 = '%08X' % (int(index1, 2))
    index2 = '%08X' % (int(index2, 2))
    logger.info('BYTE 1 (SUB TYPE):' + byte1)
    logger.info('BYTE 2 (SEQ):' + byte2)
    logger.info('BYTE 3 (RELAYS):' + byte3)
    logger.info('INDEX 1 :' + index1)
    logger.info('INDEX 2 :' + index2)
    message = byte0+byte1+byte2+byte3+index1+index2
    logger.info("Message ready to be send : "+message)
    sendDataToSigfox(message)
    messIndex += 1
    logger.info("Mess Index="+str(messIndex))


################################################################################
# Send Data To Sig Fox
################################################################################
def sendDataToSigfox(message):
    #message = createBuffer()
    #print("Message sended to sigfox : "+message)
    logger.info("Trying sending sigfox data : "+ message)
    sgfx.sendMessage(message)

################################################################################
# Send Data ELK
################################################################################
def sendDataToElk():
    logger.info("Sending message to ELK")
    global credentials
    rbmqconnection = pika.BlockingConnection(pika.ConnectionParameters(host=rbmqaddr, credentials=credentials))
    channel = rbmqconnection.channel()
    channel.queue_declare(queue='FROMOPTIBOX')
    logger.info(">>>>>> Enter into createbuffer")
    global gpioValues
    global messIndex
    global idDevice
    global optiboxID
    byte0 = '01'
    byte1 = ''
    byte2 = ''
    byte3 = '0b'
    for i in range(8,14):
        if GPIO.input(i) == 1:
            byte3 += '0'
        else:
            byte3 += '1'

    byte3+='00'
    byte3 = '%02X' % (int(byte3, 2))
    ident1 = ''
    ident2 = ''
    index1 = ''
    index2 = ''
    buffIndex = 0
    logger.info("BYTE 3 : "+byte3)

    for gpioNum in range (2,14):
        if usedentries[gpioNum] == 1 or gpiohours[gpioNum] == 1:
            logger.info("treating GPIO number "+ str(gpioNum))
            value = int(gpioValues[gpioNum])
            if (buffIndex % 2)==0 :
                ident1 = bin(gpioNum)
                index1 = bin(value)
                logger.info("Ident1 : "+ ident1 + "index1 : "+index1)
            else:
                ident2 = bin(gpioNum)[2:].zfill(4)
                index2 = bin(value)
                logger.info("Ident2 : "+ ident2 + "index2 : "+index2)
                byte1 = '%02X' % (int((ident1+ident2),2))
                if messIndex == 256:
                    messIndex = 0
                byte2 = '%02X' % messIndex
                index1 = '%08X' % (int(index1, 2))
                index2 = '%08X' % (int(index2, 2))
                logger.info('BYTE 1 :' + byte1)
                logger.info('BYTE 2 :' + byte2)
                logger.info('BYTE 3 :' + byte3)
                logger.info('INDEX 1 :' + index1)
                logger.info('INDEX 2 :' + index2)
                message = byte0+byte1+byte2+byte3+index1+index2
                actualTime = int(time.time())
                messageComplete = '{"message":"'+message+'", "source":"rmq", "id":"'+optiboxID+'", "time":"'+str(actualTime)+'", "messType":"'+byte0+'", "messSubType":"'+byte1+'", "sequence":"'+byte2+'", "relays":"'+byte3+'", "index1":"'+index1+'", "index2":"'+index2+'"}'
                logger.info("Message ready to be send : "+message)
                channel.basic_publish(exchange='FROMOPTIBOX',
                                      routing_key='',
                                      body=messageComplete)
                messIndex += 1
            buffIndex +=1
    rbmqconnection.close()

################################################################################
# gpio callback
################################################################################
def gpio_callback(channel):
    global gpioValues
    global somethingchanged
    global gpioindexs
    if channel >= 20:
        channel -= 18
    logger.info("falling edge detected on GPIO "+str(channel))
    gpioValues[channel] = int(gpioValues[channel])
    index = int(gpioindexs[channel])
    logger.info("gpioValue is "+str(gpioValues[channel])+" and is index is" + str(index))
    gpioValues[channel] += (1*index)
    logger.info("gpioValue is now "+str(gpioValues[channel]))
    somethingchanged = True

################################################################################
# gpio callback
################################################################################
def gpio_callback_relay(channel):
    global eventmessageavailable
    if eventmessageavailable<=0:
        logger.info("No more event message.")
        return
    eventmessageavailable-=1
    logger.info("Using an event message. Left:"+str(eventmessageavailable))

    global gpioValues
    global gpioindexs
    if channel >= 20:
        channel -= 18
    logger.info("falling edge detected on Relay GPIO "+str(channel))
    gpioValues[channel] = int(gpioValues[channel])
    index = int(gpioindexs[channel])
    logger.info("gpioValue is "+str(gpioValues[channel])+" and is index is" + str(index))
#    gpioValues[channel] += (1*index)
    logger.info("gpioValue is now "+str(gpioValues[channel]))
    createRelayBuffer(channel)

################################################################################
# gpio start count
################################################################################
def gpio_startCount(channel):
    global gpioHoursStart
    global somethingchanged
    logger.info("rising edge detected on GPIO "+str(channel))
    timestamp = time.time()
    gpioHoursStart[channel] = timestamp
    logger.info("startcount of channel "+ str(channel)+" is now "+ str(gpioHoursStart[channel]))
    somethingchanged = True

################################################################################
# gpio stop count
################################################################################
def gpio_stopCount(channel):
    global gpioHoursStart
    global gpioHoursValues
    global somethingchanged
    logger.info("falling edge detected on GPIO "+str(channel))
    timestamp = time.time()
    gpioHoursValues[channel] += (timestamp - gpioHoursStart[channel])
    logger.info("value of channel "+ str(channel)+" is now "+ str(gpioHoursValues[channel]))
    somethingchanged = True

################################################################################
# Rewrite files
################################################################################
def rewriteFiles():
    global gpioValues
    global filesStore
    global somethingchanged
    global gpiohours
    logger.info("Rewrite file")
    x = 2
    for gpioNum in range(2,14):
        if gpiohours[gpioNum] == 1:
             if GPIO.input(gpioNum) == 0:
                logger.info("GPIO is UP"+str(gpioNum))
                gpioValues[gpioNum] += 1
                somethingchanged= True

#            if GPIO.input(gpioNum) == 0:
#                logger.info("GPIO is UP"+str(gpioNum))
#                if gpioLastState[gpioNum] == 0:
#                    logger.info("Start counter")+str(gpioNum)
#                    gpioHoursStart[gpioNum] == int(time.time())
#                    gpioLastState[gpioNum] = 1
#            else:
#		logger.info("GPIO is Down"+str(gpioNum))
#                if gpioLastState[gpioNum] == 1:
#		    logger.info("Stop counter"+str(gpioNum))
#                    index = int(time.time()) - gpioHoursStart[gpioNum]
#                    logger.info("Adding:"+str(index))
#                    gpioValues[gpioNum] += index
#                    gpioLastState[gpioNum] = 0
#                    somethingchanged = True

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

################################################################################
# Translate GPIO pins see this file header
################################################################################
def translateGpioNum(num):
    if num == 2 or num == 3:
        num += 18
    return num

################################################################################
# MAIN
################################################################################

rbmqpasswd = configHelper.GetVariable('main', 'rabbitmq_password')
rbmqaddr = configHelper.GetVariable('main', 'rabbitmq_address')
optiboxID = configHelper.GetVariable('main', 'optiboxid')
logger.info('rmqaddr : '+str(rbmqaddr))
credentials = pika.PlainCredentials("rabbitmq", rbmqpasswd)

sgfx = Sigfox('/dev/serial0')

curday=datetime.datetime.today().day
eventmessageavailable=28

logger.info("Cur day is:"+str(curday))

usedentries=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
gpioindexs=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
gpiohours=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
x=2
messIndex = 0

gpioCount = 0
for pin in range(2,14):
    cfg = configHelper.GetVariable('impulses', 'use_impulse_'+str(pin))
    index = configHelper.GetVariable('coefficients', 'coefficient_'+str(pin))
    hour = configHelper.GetVariable('hours', 'use_hour_'+str(pin))
    logger.info('impulse : '+cfg + ' hour : ' + hour)
    if(cfg=='1'):
#        print(str(x))
        usedentries[x]=1
        logger.info("PIN "+ str(x) + " is Impulse")
        gpioCount += 1
    elif hour=='1':
        gpiohours[x] = 1
        logger.info("PIN "+ str(x) + " is Hour")
        gpioCount += 1
    gpioindexs[x] = int(index)
    x+=1

logger.info(str(gpioCount)+" GPIOs are set")

GPIO.setmode(GPIO.BCM)

idDevice = str(get_mac())
logger.info("MAC address device : "+idDevice)
filesStore = []
gpioValues = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
gpioHoursStart = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
gpioLastState = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

for gpioFile in range(2,14):
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

try:
    print('step')
    for gpioNum in range(2,14):
        logger.info("Setting up GPIO "+ str(gpioNum) )
        GPIO.setup(translateGpioNum(gpioNum), GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if gpiohours[gpioNum] == 1:
            logger.info("GPIO " + str(translateGpioNum(gpioNum)) + " is hours datalogger")
            if GPIO.input(translateGpioNum(gpioNum)):
                logger.info("A")
                #gpioHoursStart[translateGpioNum(gpioNum)] = int(time.time())
                gpioHoursStart[gpioNum] = int(time.time())
                logger.info("AA")
                #gpioLastState[translateGpioNum(gpioNum)] = 1
                gpioLastState[gpioNum] = 1
                logger.info("AB")
                logger.info("State 1 and time is "+ str(gpioHoursStart[gpioNum]))
            else:
                logger.info("B")
                #gpioLastState[translateGpioNum(gpioNum)]= 0
                gpioLastState[gpioNum]= 0
                logger.info("State is 0")
except Error as er:
    logger.error(er)

somethingchanged=False

for gpioNum in range(2,14):
    logger.info('Configuring event on GPIO '+str(gpioNum))
    if usedentries[(gpioNum)] == 1:
        logger.info("Adding call back to "+str(gpioNum))
        GPIO.add_event_detect(translateGpioNum(gpioNum), GPIO.FALLING, callback=gpio_callback, bouncetime=300)
    if gpiohours[(gpioNum)] == 1:
        logger.info("Adding call back to relay "+str(gpioNum))
        GPIO.add_event_detect(translateGpioNum(gpioNum), GPIO.BOTH, callback=gpio_callback_relay, bouncetime=300)
#	GPIO.add_event_detect(translateGpioNum(gpioNum), GPIO.RISING, callback=gpio_callback_relay, bouncetime=300)


useElk = configHelper.GetVariable('main', 'sendtoelk')
useSigfox = configHelper.GetVariable('main', 'sendtosigfox')

if useSigfox == '1':
    timer = 0
    gpioCount
    if gpioCount >= 11:
        timer = 120
    elif gpioCount >= 9:
        timer = 90
    elif gpioCount >= 7:
        timer = 60
    elif gpioCount >= 5:
        timer = 45
    elif gpioCount >= 3:
        timer = 30
    else:
        timer = 15

    logger.info("SigfoxTimer is : "+ str(timer))
    schedule.every(timer).minutes.do(createBuffer)

if useElk == '1':
    schedule.every(1).minutes.do(sendDataToElk)

schedule.every(1).minutes.do(run_threaded, rewriteFiles)
logger.info("schedule configured")

try:
    while True:
        #print "start boucle"
        #logger.info("==> Starting sending index to Sigfox")
        #sendDataToSigfox(A20)
        schedule.run_pending()
        #print "End schedule"
        if(curday !=datetime.datetime.today().day):
            logger.info("Resetting event messages to 28.")
            eventmessageavailable=28
            curday=datetime.datetime.today().day

        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit


GPIO.cleanup()           # clean up GPIO on normal exit
