#!/usr/bin/env python3

############################################################
# Includes
############################################################
import RPi.GPIO as GPIO
from video_dir import CameraServo
#import car_dir
#import motor
#from socket import *
from time import ctime          # Import necessary modules   
import threading
import multiprocessing as mp
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import cgi
import json
import urllib.request
import queue
import cv2
import asyncio
import websockets
from AlphaBot import AlphaBot
from PCA9685 import PCA9685
#import compass
import time
from mpu9250 import SL_MPU9250
# =============================================================================
#       Function to manage command
# =============================================================================
class RobotController:

	def __init__(self,queue):
		self.magsensor  = SL_MPU9250(0x68,1)
		self.magsensor.resetRegister()
		self.magsensor.powerWakeUp()
		self.magsensor.setAccelRange(8,True)
		self.magsensor.setGyroRange(1000,True)
		self.magsensor.setMagRegister('100Hz','16bit')
		self.queue=queue
		self.busnum=1
		self.Cs = CameraServo()
		self.isRunning=False
		self.Ab = AlphaBot()
		self.command = {'centering':self.centering,'iayolo':self.switchyolo,'iasauterelle':self.switchsauterelle,'left':self.left,'right':self.right,'forward':self.forward,'speed':self.speed,'backward':self.backward,'straight':self.straight,'find':self.find,'follow':self.follow,'hold':self.hold,'xp':self.xplus,'xm':self.xminus,'ym':self.yminus,'yp':self.yplus,'homexy':self.homexy,'xmin':self.xmin,'xmax':self.xmax}
		self.threadWSS = threading.Thread(target = self.runWSClient)
		self.threadWSS.start()

	def distanceFromCenter(self,x):
		return (x-320)


	# Find the target
	def objectFind(self,context,results):
		if 'angle' not in context.keys():
			context['angle']=self.getxmin()
			context['frame']=0
			self.xmin()
		else:
			if len(results)>0:
				cat,prob,x,y,w,h,module = results[0]
				dx = self.distanceFromCenter(x)
				if 'odx' in context.keys():
					odx = context['odx']
				else:
					odx = 1000

				if dx < 75 or dx > odx:
					print('found')
					context.clear()
					return False
				else:
					context['odx']=dx

			context['frame']+=1
			if context['frame']%3!=0:
				return True

			angle = context['angle']

			context['angle']+=100
			if context['angle']>=self.getxmax():
				print('not found')
				context.clear()
				self.homexy()
				return False
			self.xplus()
		return True


	# Goto the object
	def objectFollow(self,context,results):
		if 'align' not in context.keys():
			self.align()
			context['align']=True
			context['frame']=0
			self.speed(50)
			self.forward()
			return True
		else:
			# TODO -> Avancer, si pas de visu, compteur jusque 5, et si y est inférieur à 80 % -> stop et clear
			if len(results)==1:
				self.forward()
				cat,prob,x,y,w,h,module = results[0]
				#print("Following %r %r %r" %(x,y,distanceFromCenter(x)))
				if self.distanceFromCenter(x)<-40:
					self.left(0.9)
					#print('following - left')
				elif self.distanceFromCenter(x)>40:
					#print('following - right')
					self.right(0.9)
				else:
					#print('following - forward')
					self.forward()

				if y > 350 and self.Cs.get_position_degree_y()>55:
					self.yminus()
				#print(y)
				context['frame']=0

			else:
				context['frame']+=1
				if context['frame']>4:
					print('Object lost')
					self.hold()
					context.clear()
					return False
			return True
			#context.clear()

	def getAngleDifference(self,a,b):
		c = a-b
		if c<0:
			c+=360
		if c>360:
			c-=360
		return c

	def turn360(self):
		speed,speed = self.getSpeed()
		self.speed(30)
		turndone = False
		current = self.magsensor.getDirection()
		self.right()
		print (current)
		while  self.getAngleDifference(current,self.magsensor.getDirection())>20 or turndone==False:
			print (abs(current - self.magsensor.getDirection()))
			time.sleep(0.01)
			if self.getAngleDifference(current,self.magsensor.getDirection()) > 40:
				turndone=True
		self.hold()
		self.speed(speed)


	def getCorrectDirection(self,angle):
		if angle<0:
			return self.left
		else:
			return self.right

	def align(self):
		angle = self.getCameraAngle()
		speed,speed = self.getSpeed()
		self.speed(50)

		current = self.magsensor.getDirection()
		print("current %f / angle %f" %(current,angle))
		target = current + angle
		if target<0:
			target +=360
		if target>360:
			target -=360
		print("target %f" % (target))
		self.getCorrectDirection(angle)()
		self.homexy()
		delta = (self.magsensor.getDirection() - target)
		
		while abs(delta) > 20 :
			absdelta=abs(delta)
			if absdelta<40 and absdelta>20 :
				self.speed(30)
				#self.getCorrectDirection(-delta)()
			if absdelta<20:
				self.speed(20)
				#self.getCorrectDirection(-delta)()
			delta = self.magsensor.getDirection()-target
			print("compass %f, delta %f" % (self.magsensor.getDirection(),delta))
		self.hold()
		self.speed(speed)


	def switchyolo(self):
		print('Switch IA context to yolo')
		self.queue.put('yolo')
		print("Ok")

	def switchsauterelle(self):
		print('Switch IA context to custom weight')
		self.queue.put('sauterelle')

	def left(self,percent=0.7):
		if self.isRunning:
			self.Ab.forward_left(percent)
		else:
			self.Ab.left()
		print ('recv left cmd')

	def right(self,percent=0.7):
		print ('recv right cmd')
		if self.isRunning:
                        self.Ab.forward_right(percent)
		else:
			self.Ab.right()

	def forward(self):
		self.isRunning=True
		print ('motor moving forward')
		self.Ab.forward()

	def backward(self):
		self.isRunning=False
		print ('recv backward cmd')
		self.Ab.backward()

	def straight(self):
		print ('recv home cmd')
		if self.isRunning:
			self.Ab.forward()
		else:
			self.Ab.stop()

	def hold(self):
		print ('recv stop cmd')
		self.Ab.stop()
		self.isRunning=False


	def xminus(self):
		print ('recv x- cmd')
		print (self.Cs.get_position_degree())
		self.Cs.decrease_x()

	def xplus(self):
		print ('recv x+ cmd')
		print (self.Cs.get_position_degree())
		self.Cs.increase_x()

	def yminus(self):
		print ('recv y- cmd')
		self.Cs.decrease_y()

	def yplus(self):
		print ('recv y+ cmd')
		self.Cs.increase_y()


	def homexy(self):
		print ('home_x_y')
		self.Cs.home_x_y()

	def xmin(self):
		print ('xmin')
		self.Cs.set_x_min()

	def xmax(self):
		print('xmax')
		self.Cs.set_x_max()


	def ymax(self):
		self.Cs.set_y_max()

	def ymin(self):
		self.Cs.set_y_min()

	def find(self):
		self.queue.put('find')

	def follow(self):
		self.queue.put('follow')

	def getSpeed(self):
		return self.Ab.getSpeed()

	def getCameraAngle(self):
		return self.Cs.get_position_degree()

	def speed(self,speed):
		self.Ab.setPWMA(int(speed))
		self.Ab.setPWMB(int(speed))

	def setPWMB(self,value):
		self.PB = value
		self.PWMB.ChangeDutyCycle(self.PB)	

	def getxmin(self):
		return self.Cs.getxmin()

	def getxmax(self):
		return self.Cs.getxmax()

	def getcurrent(self):
		return self.Cs.getxcurrent()

	def centering(self,center):
		center = float(center)
		center -= 100
		print(center)
		if center<0:
			self.Ab.PACorrector=abs(100+center)/100
			self.Ab.PBCorrector=1
		else:
			self.Ab.PACorrector=1
			self.Ab.PBCorrector=(100-center)/100
		(a,b)=self.Ab.getSpeed()
		self.Ab.setPWMA(a)
		self.Ab.setPWMB(b)
		print("Corrector (PA/PB) %f %f" % (self.Ab.PACorrector,self.Ab.PBCorrector))


	def sayno(self):
		self.xmin()
		time.sleep(0.5)
		self.xmax()
		time.sleep(0.5)
		self.xmin()
		time.sleep(0.5)
		self.xmax()
		time.sleep(0.5)
		self.homexy()


	def sayyes(self):
		self.ymin()
		time.sleep(0.5)
		self.ymax()
		time.sleep(0.5)
		self.ymin()
		time.sleep(0.5)
		self.ymax()
		time.sleep(0.5)
		self.homexy()



	def executeCommand(self,cmd,variable=None):
		if not cmd in self.command.keys():
			self.queue.put(cmd)
			return False
		if variable!=None:
			self.command[cmd](variable)
		else:
			self.command[cmd]()

# =============================================================================
#       Function to listen the websocket (message from Alexa)
# =============================================================================

	async def tapit(self) :
		async with websockets.connect('wss://7nrl9bn74h.execute-api.eu-west-1.amazonaws.com/dev') as websocket:
			while 1 :
				receive = await websocket.recv()
				todo = json.loads(receive)
				if todo['author'] == "tapit" :
					self.executeCommand(todo['message'])

	def runWSClient(self) :
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		asyncio.get_event_loop().run_until_complete(self.tapit())

############################################################
# Main
############################################################
def main():
	cmd = queue.Queue()
	rc = RobotController(cmd)
	#rc.sayyes()
	#rc.sayno()
	rc.turn360()
	rc.runWSClient()

if __name__ == '__main__':
        main()
