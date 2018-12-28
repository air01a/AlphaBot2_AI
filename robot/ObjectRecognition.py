from network import SockHandler
import time
import cv2
import json

class ObjectRecognition:
	sock = None
	commands = ['yolo','sauterelle']

	# Socket init
	def __init__(self, SERVER,PORT):
		self.PORT=PORT
		self.SERVER=SERVER
		self.activated=False
		self.iacontext='sauterelle'

	def activate(self):
		self.sock = SockHandler(self.SERVER,self.PORT)
		self.sock.connect()
		self.activated=True
		time.sleep(4)

	def desactivate(self):
		self.sock=None
		self.activated=False

	def isActivated(self):
		return self.activated

	def canFollow(self):
		if self.iacontext!='sauterelle':
			sock.send(b'sauterel')
			time.sleep(6)
			iacontext='sauterelle'
		return True


	# Object recognition
	def recognize(self,frame,visionContext,bbox):
		if self.activated:
			if visionContext['framecount']%visionContext['DEEPFRAMERATE']==0 or visionContext['deeplearningt0']:  # do we send the image to the deep learning server (one frame every 10) or t0 when search or follow command are executed
				sBytes = cv2.imencode('.jpg', frame)[1].tobytes()   # compress to jpg
				self.sock.send(sBytes)  # Send
				bbox = json.loads(self.sock.recv().decode()) # recevie result
		return bbox

	def isModuleCommand(self,cmd):
		if cmd in self.commands:
			return True
		return False

	def manageCommand(self,cmd):
		if cmd=='yolo':
			sock.send(b'yoloyolo')
			time.sleep(4)
			self.iacontext='yolo'
			return True

		if cmd=='sauterelle':
			self.iacontext='sauterelle'
			sock.send(b'sauterel')
			time.sleep(4)
			return True

