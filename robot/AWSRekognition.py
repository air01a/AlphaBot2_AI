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
		self.commands = ['aws-reco','aws-face','aws-read','read','face']
		self.img = io.BytesIO()
		self.thread = None
		self.response = []
		self.idFace=[]
		self.mode=0
		self.activated=False
		self.lastReadCmd=''

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
		idFace=[]
		response = self.aws_client.detect_faces(Image={'Bytes':self.imageToBytes(frame)},Attributes=['DEFAULT'])
		if response != None:
			for faceDetail in response['FaceDetails']:
				L1=max(0,int((faceDetail['BoundingBox']['Left']-0.1)*640))
				R1=max(0,int((faceDetail['BoundingBox']['Top']-0.1)*480))
				H1=min(int((faceDetail['BoundingBox']['Height']+0.1)*480)+R1,480)
				W1=min(int((faceDetail['BoundingBox']['Width']+0.1)*640)+L1,640)

				found=False
				for f in self.idFace:
					if f[0]>L1 and f[0]<W1 and f[1]>R1 and f[1]<H1:
						idFace.append([(L1+W1)/2,(R1+H1)/2,f[2]])
						self.response.append([f[2],1,L1+(W1-L1)/2,R1+(H1-R1)/2,W1-L1,H1-R1,'face'])
						found=True
						break

				if not found:

					cropped = (L1,R1,W1,H1)
					try:
						response2 = self.aws_client.search_faces_by_image(CollectionId='BETTERAVE_FACES',Image={'Bytes':self.imageToBytes(frame,cropped)})
						if len(response2['FaceMatches'])==0:
							self.response.append(['unknown',1,L1+(W1-L1)/2,R1+(H1-R1)/2,W1-L1,H1-R1,'face'])
						else:
							for record in response2['FaceMatches']:
								face = record['Face']['ExternalImageId']
								x=int(record['Face']['BoundingBox']['Left']*(W1-L1))+L1
								y=int(record['Face']['BoundingBox']['Top']*(H1-R1))+R1
								w= int(record['Face']['BoundingBox']['Width']*(W1-L1))
								h=int(record['Face']['BoundingBox']['Height']*(H1-R1))
								self.response.append([face,1,x+w/2,y+h/2,w,h,'face'])
								idFace.append([(L1+W1)/2,(R1+H1)/2,face])

					except:
						self.response.append(['unknown',1,L1+(W1-L1)/2,R1+(H1-R1)/2,W1-L1,H1-R1,'face'])
		self.idFace=idFace


	def read(self,context,frame):
		self.response=[]
		response = self.aws_client.detect_text(Image={'Bytes':self.imageToBytes(frame)})
		for txt in response['TextDetections']:
			if txt['Confidence']>90 and 'ParentId' not in txt.keys():
				detected=txt['DetectedText']
				box = txt['Geometry']['BoundingBox']
				x=box['Left']*640
				y=box['Top']*480
				w=box['Width']*640
				h=box['Height']*480
				self.response.append([detected,1,x+w/2,y+h/2,w,h,'read'])

				if detected.upper()=='SAY YES' and self.lastReadCmd!='YES':
					self.lastReadCmd='YES'
					context['controller'].sayyes()

				if detected.upper()=='SAY NO' and self.lastReadCmd!='NO':
					self.lastReadCmd='NO'
					print(context['controller'])
					context['controller'].sayno()

				if detected.upper() == 'MAKE 360' and self.lastReadCmd!='360':
					self.lastReadCmd='360'
					context['controller'].turn360()

				if detected.upper() == 'PLAY MUSIC' and self.lastReadCmd!='musik':
					self.lastReadCmd='musik'
					self.playMusik()

	def playMusik(self):
		from musik import Musik

		mus = Musik()
		mus.play()

	# Object recognition
	def recognize(self,frame,visionContext,bbox):
		if self.thread!=None and self.thread.isAlive():
			return bbox

		bbox=self.response
		if self.mode==0:
			self.thread = threading.Thread(target=self.labelDetection,args=(frame,))
		elif self.mode==1:
			self.thread = threading.Thread(target=self.faceDetection,args=(frame,))
		elif self.mode==2:
			self.thread = threading.Thread(target=self.read,args=(visionContext,frame,))

		self.thread.start()
		return bbox

	def isModuleCommand(self,cmd):
		if cmd in self.commands:
			return True
		return False

	def manageCommand(self,cmd,visionContext,results,rc):
		if cmd in self.commands:
			if cmd=="aws-reco":
				self.mode=0
			if cmd=="aws-face" or cmd=='face':
				self.mode=1
			if cmd=="aws-read" or cmd=='read':
				self.mode=2
				self.lastReadCmd=''
		return True
