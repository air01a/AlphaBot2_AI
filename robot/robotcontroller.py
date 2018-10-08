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

# =============================================================================
#       Function to manage command
# =============================================================================
class RobotController:

	def __init__(self,queue):
		self.queue=queue
		self.busnum=1
		self.Cs = CameraServo()

		self.Ab = AlphaBot()
		self.command = {'left':self.left,'right':self.right,'forward':self.forward,'backward':self.backward,'straight':self.straight,'find':self.find,'follow':self.follow,'hold':self.hold,'xp':self.xplus,'xm':self.xminus,'ym':self.yminus,'yp':self.yplus,'homexy':self.homexy,'xmin':self.xmin,'xmax':self.xmax}
		self.threadWSS = threading.Thread(target = self.runWSClient)
		self.threadWSS.start()

	def left(self):
		print ('recv left cmd')
		self.Ab.left()

	def right(self):
		print ('recv right cmd')
		self.Ab.right()

	def forward(self):
		print ('motor moving forward')
		self.Ab.forward()

	def backward(self):
		print ('recv backward cmd')
		self.Ab.backward()

	def straight(self):
		print ('recv home cmd')
		self.Ab.stop()

	def hold(self):
		print ('recv stop cmd')
		self.Ab.stop()


	def xminus(self):
		print ('recv x- cmd')
		self.Cs.decrease_x()

	def xplus(self):
		print ('recv x+ cmd')
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
		self.Cs.xmax()

	def find(self):
		self.queue.put('find')

	def follow(self):
		self.queue.put('follow')


	def getxmin(self):
		return self.Cs.getxmin()

	def getxmax(self):
		return self.Cs.getxmax()

	def getcurrent(self):
		return self.Cs.getxcurrent()

	def executeCommand(self,cmd):
		if not cmd in self.command.keys():
			print(cmd)
			return False
		self.command[cmd]()


# =============================================================================
#       Function to listen the websocket (message from Alexa)
# =============================================================================

	async def tapit(self) :
		async with websockets.connect('wss://') as websocket:
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
	rc.runWSClient()

if __name__ == '__main__':
        main()
