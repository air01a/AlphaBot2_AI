#!/usr/bin/python
# -*- coding:utf-8 -*-
import threading
import traceback
from PCA9685 import PCA9685


class CameraServo:
 
	ROLL_MIN = 550
	ROLL_MID = 1250
	ROLL_MAX = 1950
	ROLL_DEG = float(ROLL_MAX - ROLL_MIN) / 180.0
	PITCH_MIN = 1550
	PITCH_MID = 2100
	PITCH_MAX = 2300
	PITCH_DEG = ROLL_DEG

	def __init__(self):
		self.pwm = PCA9685(0x40)
		self.pwm.setPWMFreq(50)
		self.timer=None
		self.currentPosition = [self.ROLL_MID,self.PITCH_MID]
		self.home_x_y()

	def home_x_y(self):
		self.set_position(0, self.ROLL_MID, self.ROLL_MIN, self.ROLL_MAX)
		self.set_position(1, self.PITCH_MID, self.PITCH_MIN, self.PITCH_MAX)

	def getxmin(self):
		return self.ROLL_MIN

	def getxmax(self):
		return self.ROLL_MAX

	def getxcurrent(self):
		return self.currentPosition[0]

	def roll_percent(self, percent):
		self.set_position_percent(0, percent, self.ROLL_MIN, self.ROLL_MAX)

	def pitch_percent(self, percent):
		self.set_position_percent(1, percent, self.PITCH_MIN, self.PITCH_MAX)

	def set_position(self, servo, position, position_min, position_max):
		if self.timer!=None:
			self.timer.cancel()
		original = position
		if position > position_max: position = position_max
		if position < position_min: position = position_min
		self.currentPosition[servo]=position
		#percent = 100 - int(float(position - position_min) * 100.0 / float(position_max - position_min))
		self.pwm.setServoPulse(servo, position)
		self.timer = threading.Timer(3, self.stop)
		self.timer.start()

	def set_x_min(self):
		self.set_position(0,self.ROLL_MAX,self.ROLL_MIN,self.ROLL_MAX)

	def set_x_max(self):
		self.set_position(0,self.ROLL_MIN,self.ROLL_MIN,self.ROLL_MAX)

	def increase_x(self,step=100):
		self.set_position(0,self.currentPosition[0]-step,self.ROLL_MIN,self.ROLL_MAX)

	def decrease_x(self,step=100):
		self.set_position(0,self.currentPosition[0]+step,self.ROLL_MIN,self.ROLL_MAX)

	def increase_y(self,step=100):
		self.set_position(1,self.currentPosition[1]-step,self.PITCH_MIN,self.PITCH_MAX)

	def decrease_y(self,step=100):
		self.set_position(1,self.currentPosition[1]+step,self.PITCH_MIN,self.PITCH_MAX)

	def set_y_min(self):
		self.set_position(1,self.PITCH_MAX,self.PITCH_MIN,self.PITCH_MAX)

	def set_y_max(self):
		self.set_position(1,self.PITCH_IN,self.PITCH_MIN,self.PITCH_MAX)

	def set_position_percent(self, servo, percent, position_min, position_max):
		if percent > 100: percent = 100
		if percent < 0: percent = 0
		position = position_min + int((100.0 - float(percent)) * float(position_max - position_min) / 100.0)
		self.set_position(servo, position, position_min, position_max)

	def set_position_degrees(self, servo, degrees, mid, position_min, position_max, points_per_degree):
		position = int(degrees * points_per_degree + mid)
		self.set_position(servo, position, position_min, position_max)

	def stop(self):
		# Stop PWM for annoying vibration, will be reactivated if command is sent (code in the module itself)
		self.pwm.stop(0)
		self.pwm.stop(1)
		
if __name__ == '__main__':
	import time
	Cs = CameraServo()
	time.sleep(1)
