#!/usr/bin/env python2.7
# script by Alex Eames http://RasPi.tv
# http://RasPi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3
import RPi.GPIO as GPIO
import time
import logging
from logging.handlers import TimedRotatingFileHandler


logging.basicConfig(level=logging.INFO)

handler = TimedRotatingFileHandler("gpio.log",
                                       when="d",
                                       interval=1,
                                       backupCount=30)



logger=logging.getLogger(__name__)
logger.addHandler(handler)
logger.info("HI From Logger...")




GPIO.setmode(GPIO.BCM)

# GPIO 23 & 17 set up as inputs, pulled up to avoid false detection.
# Both ports are wired to connect to GND on button press.
# So we'll be setting up falling edge detection for both
#GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)i


print "CLEAN UP"
GPIO.cleanup()

A17=0
A18=0
A16=0
A20=0
A21=0
A27=0

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# now we'll define two threaded callback functions
# these will run in another thread when our events are detected
def my_callback1(channel):
    global A17
#    print "falling edge detected on 17"
    A17+=1

def my_callback2(channel):
    global A18
#    print "falling edge detected on 18"
    A18+=1

def my_callback3(channel):
    global A16
#    print "falling edge detected on 16"
    A16+=1

def my_callback4(channel):
    global A20
#    print "falling edge detected on 20"
    A20+=1


def my_callback5(channel):
    global A21
#    print "falling edge detected on 21"
    A21+=1


def my_callback6(channel):
    global A27
#    print "falling edge detected on 27"
    A27+=1



print "Make sure you have a button connected so that when pressed"
print "it will connect GPIO port 23 (pin 16) to GND (pin 6)\n"
print "You will also need a second button connected so that when pressed"
print "it will connect GPIO port 24 (pin 18) to 3V3 (pin 1)\n"
print "You will also need a third button connected so that when pressed"
print "it will connect GPIO port 17 (pin 11) to GND (pin 14)"
#raw_input("Press Enter when ready\n>")

# when a falling edge is detected on port 17, regardless of whatever
# else is happening in the program, the function my_callback will be run
GPIO.add_event_detect(17, GPIO.FALLING, callback=my_callback1, bouncetime=100)

# when a falling edge is detected on port 23, regardless of whatever
# else is happening in the program, the function my_callback2 will be run
# 'bouncetime=300' includes the bounce control written into interrupts2a.py
GPIO.add_event_detect(18, GPIO.FALLING, callback=my_callback2, bouncetime=100)
GPIO.add_event_detect(16, GPIO.FALLING, callback=my_callback3, bouncetime=100)
GPIO.add_event_detect(20, GPIO.FALLING, callback=my_callback4, bouncetime=100)
GPIO.add_event_detect(21, GPIO.FALLING, callback=my_callback5, bouncetime=100)
GPIO.add_event_detect(27, GPIO.FALLING, callback=my_callback6, bouncetime=10)

try:
#    print "Waiting for rising edge on port 17"
#    GPIO.wait_for_edge(17, GPIO.RISING)
#    print "Rising edge detected on port 17. Here endeth the third lesson."
	while True:
             time.sleep(10)
	     logger.info("===> %d %d %d %d %d %d" %(A16,A17,A18,A20,A21,A27))
             A17=0
             A18=0
             A16=0
             A20=0
             A21=0
             A27=0

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
GPIO.cleanup()           # clean up GPIO on normal exit

