import time
import cv2
import json
import boto3
import io
from PIL import Image
import threading


class AWSRekognition:

	# Socket init
	def __init__(self):
		self.aws_client = boto3.client("rekognition")
		self.commands = {}
		self.img = io.BytesIO()
		self.thread = None
		self.response = []

	def activate(self):
		self.activated=True

	def desactivate(self):
		self.activated=False

	def isActivated(self):
		return self.activated

	def canFollow(self):
		return False


	def labelDetection(self,frame):
		self.response=[]
		response = self.aws_client.detect_labels(Image={'Bytes':self.imageToBytes(frame)},MaxLabels=20)
		for label in response['Labels']:
			cat=label['Name']
			for instance in label['Instances']:
				w=instance['BoundingBox']['Width']*640
				h=instance['BoundingBox']['Height']*480
				x=instance['BoundingBox']['Left']*640+w/2
				y=instance['BoundingBox']['Top']*480+h/2
				prob=instance['Confidence']
				self.response.append((cat,prob,x,y,w,h,'awsreko'))

	def imageToBytes(self,frame,crop=None):
		self.img.seek(0)
		pil_img = Image.fromarray(frame)

		if crop!=None:
			cropped = pil_img.crop(crop)
			cropped.save(self.img,'JPEG')
		else:
			pil_img.save(self.img,'JPEG')
		return self.img.getvalue()

	def faceDetection(self,frame):
		self.response=[]
		response = self.aws_client.detect_faces(Image={'Bytes':self.imageToBytes(frame)},Attributes=['DEFAULT'])
		if response != None:
			for faceDetail in response['FaceDetails']:
				L1=max(0,int((faceDetail['BoundingBox']['Left']-0.1)*640))
				R1=max(0,int((faceDetail['BoundingBox']['Top']-0.1)*480))
				H1=min(int((faceDetail['BoundingBox']['Height']+0.1)*480)+R1,480)
				W1=min(int((faceDetail['BoundingBox']['Width']+0.1)*640)+L1,640)

				cropped = (L1,R1,W1,H1)
				#self.response.append(['test',1,L1+W1/2,R1+H1/2,W1,H1,'face'])
				try:
					response2 = self.aws_client.search_faces_by_image(CollectionId='BETTERAVE_FACES',Image={'Bytes':self.imageToBytes(frame,cropped)})
					for record in response2['FaceMatches']:
							face = record['Face']['ExternalImageId']
							x=int(record['Face']['BoundingBox']['Left']*(W1-L1))+L1
							y=int(record['Face']['BoundingBox']['Top']*(H1-R1))+R1
							w= int(record['Face']['BoundingBox']['Width']*(W1-L1))
							h=int(record['Face']['BoundingBox']['Height']*(H1-R1))
							self.response.append([face,1,x+w/2,y+h/2,w,h,'face'])
				except:
					self.response.append(['unknown',1,L1+(W1-L1)/2,R1+(H1-R1)/2,W1-L1,H1-R1,'face'])


	# Object recognition
	def recognize(self,frame,visionContext,bbox):

		if self.thread!=None and self.thread.isAlive():
			return bbox

		bbox=self.response
		#self.thread = threading.Thread(target=self.labelDetection,args=(frame,))
		self.thread = threading.Thread(target=self.faceDetection,args=(frame,))
		self.thread.start()
		return bbox

	def isModuleCommand(self,cmd):
		if cmd in self.commands:
			return True
		return False

	def manageCommand(self,cmd):
		return True
