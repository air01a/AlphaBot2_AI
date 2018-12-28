#!/usr/bin/python3
import os
import RPi.GPIO as GPIO
import time

CTR = 7
A = 8
B = 9
C = 10
D = 11
BUZ = 4

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(CTR,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(A,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(B,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(C,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(D,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(BUZ,GPIO.OUT)

try:
	while True:
		if GPIO.input(CTR) == 0:
			print("center")
			os.system('sudo halt')
			while GPIO.input(CTR) == 0:
				time.sleep(0.01)
		elif GPIO.input(A) == 0:
			print("up")
			while GPIO.input(A) == 0:
				time.sleep(0.01)
		elif GPIO.input(B) == 0:
			print("right")
			while GPIO.input(B) == 0:
				time.sleep(0.01)
		elif GPIO.input(C) == 0:
			print("left")
			while GPIO.input(C) == 0:
				time.sleep(0.01)
		elif GPIO.input(D) == 0:
			print("down")
			while GPIO.input(D) == 0:
				time.sleep(0.01)
		time.sleep(0.3)
except KeyboardInterrupt:
	GPIO.cleanup()
