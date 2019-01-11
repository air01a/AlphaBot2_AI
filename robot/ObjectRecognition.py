from network import SockHandler
import time
import cv2
import json
import threading


class ObjectRecognition:
	sock = None
	commands = ['yolo','sauterelle','find','follow']

	# Socket init
	def __init__(self, SERVER,PORT):
		self.PORT=PORT
		self.SERVER=SERVER
		self.activated=False
		self.iacontext='sauterelle'
		self.response=[]
		self.tFrame=None
		self.tFinish=False
		self.thread=None

	def activate(self):
		self.sock = SockHandler(self.SERVER,self.PORT)
		if not self.sock.isPortOpened():
			print("Port not reachable, module ObjectRecognition could not be activated")
			return False
		self.sock.connect()
		self.activated=True
		self.tFrame=None
		self.hasFrame=False
		self.thread = threading.Thread(target=self.getDescriptionThread,args=())
		self.thread.start()
		self.tFinish=True
		time.sleep(7)
		return True

	def desactivate(self):
		print("desactivating")
		self.activated=False
		if self.thread!=None:
			while self.thread.isAlive():
				time.sleep(0.1)
		self.sock = None
		self.thread = None
		print("Object desactivated")

	def isActivated(self):
		return self.activated

	def canFollow(self):
		if self.iacontext!='sauterelle':
			self.sock.send(b'sauterel')
			time.sleep(6)
			self.iacontext='sauterelle'
		return True


	def getDescription(self,frame):
		sBytes = cv2.imencode('.jpg', frame)[1].tobytes()   # compress to jpg
		self.sock.send(sBytes)
		return json.loads(self.sock.recv().decode())

	def getDescriptionThread(self):
		while self.activated:
			if self.hasFrame:
				self.hasFrame=False
				frame=self.tFrame
				self.tFrame=None
				self.tFinish=False
				self.response = self.getDescription(frame)
				self.tFinish=True

	# Object recognition
	def recognize(self,frame,visionContext,bbox):
		if self.activated:
			if visionContext['deeplearningt0'] or not self.thread.isAlive():
				return self.getDescription(frame)
			else:
				if self.tFinish:
					bbox =  self.response
					self.tFrame=frame
					self.hasFrame=True
					return bbox

		return bbox


	def isModuleCommand(self,cmd):
		if cmd in self.commands:
			return True
		return False

	def manageCommand(self,cmd,visionContext,results,rc):
		if self.activated:
			if cmd=='yolo':
				if self.iacontext!='yolo':
					self.sock.send(b'yoloyolo')
					time.sleep(9)
				self.iacontext='yolo'
				return False

			if cmd=='find':
				visionContext['command']='find'
				rc.objectFind(visionContext,results)
				return True

			if cmd=='follow':
				visionContext['command']='follow'
				rc.objectFollow(visionContext,results)
				return True

			if cmd=='sauterelle':
				if self.iacontext!='sauterelle':
					self.sock.send(b'sauterel')
					time.sleep(9)
				self.iacontext='sauterelle'
				return False
		return False
