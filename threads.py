#!/usr/bin/python


import random
import sys
import time


i = 0

while i < 20:
    sys.stdout.write("1")
    sys.stdout.flush()
    attente = 0.2
    attente += random.randint(1, 60)/100
    time.sleep(attente)
    i += 1
