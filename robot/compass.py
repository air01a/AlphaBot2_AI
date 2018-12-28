# Simple demo of of the LSM303 accelerometer & magnetometer library. Will print the accelerometer & magnetometer X, Y, Z 
# axis values every half second. Author: Tony DiCola License: Public Domain
import time

# Import the LSM303 module.
import Adafruit_LSM303
import math


# Create a LSM303 instance.
lsm303 = Adafruit_LSM303.LSM303(True)

# Alternatively you can specify the I2C bus with a bus parameter:
#lsm303 = Adafruit_LSM303.LSM303(busum=2)

def getmag():
	accel, mag = lsm303.read()
	mag_x, mag_z, mag_y = mag
	mag_x-=36.02499999999999
	mag_y-=61
	mag_y*=0.9854
	heading = 180*(math.atan2(mag_y,mag_x)) / math.pi
	if heading<0:
		heading += 360
	return heading
