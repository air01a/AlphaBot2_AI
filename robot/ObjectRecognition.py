from network import SockHandler
import time
import cv2
import json
import threading


class ObjectRecognition:
	sock = None
	commands = ['yolo','sauterelle']

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
		time.sleep(7)
		self.thread = threading.Thread(target=self.getDescriptionThread,args=())
		return True

	def desactivate(self):
		self.sock=None
		self.activated=False

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
			if self.tFrame!=None:
				frame=self.tFrame
				self.tFrame=None
				self.tFinish=False
				self.response = self.getDescription(frame)
				self.tFinish=True

	# Object recognition
	def recognize(self,frame,visionContext,bbox):
		if self.activated:
			if visionContext['deeplearningt0']:
				return self.getDescription(frame)
			else:
				if self.tFinish:
					bbox =  self.response
					self.tFrame=frame
					return bbox

		return bbox


	def isModuleCommand(self,cmd):
		if cmd in self.commands:
			return True
		return False

	def manageCommand(self,cmd):
		if self.activated:
			if cmd=='yolo':
				self.sock.send(b'yoloyolo')
				time.sleep(4)
				self.iacontext='yolo'
				return True

			if cmd=='sauterelle':
				self.iacontext='sauterelle'
				self.sock.send(b'sauterel')
				time.sleep(4)
				return True
