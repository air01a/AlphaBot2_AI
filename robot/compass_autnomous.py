# Simple demo of of the LSM303 accelerometer & magnetometer library. Will print the accelerometer & magnetometer X, Y, Z 
# axis values every half second. Author: Tony DiCola License: Public Domain
import time

import compass

while True:
	heading = compass.getmag()
	print(heading)


	time.sleep(0.5)

