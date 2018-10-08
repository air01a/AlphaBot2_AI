#!/usr/bin/python3
############################################################
# Includes
############################################################
from robotcontroller import *
import queue
import threading
import json
import urllib.request
import queue
import multiprocessing as mp
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import cgi
import numpy as np
import time
import cv2
from network import SockHandler
from io import StringIO
from picamera.array import PiRGBArray
from picamera import PiCamera
import os

############################################################
# Global Vars
############################################################
def readWSFile(filename):
	return open(filename,'rb').read()

extensionTab={'.html':['text/html',readWSFile('html/index.html')],
		'.js':['application/javascript',readWSFile('html/jquery.js')],
		'.css':['text/css',readWSFile('html/bootstrap.min.css')],
		'.woff':['font/woff',readWSFile('html/glyphicons-halflings-regular.woff')],
		'.woff2':['font/woff2',readWSFile('html/glyphicons-halflings-regular.woff2')],
		'.ttf':['font/ttf',readWSFile('html/glyphicons-halflings-regular.eot')]
		}

cmd = queue.Queue()
rc = RobotController(cmd)
gframe = queue.Queue()
DEEP=True

############################################################
# Web handler to stream mjpeg
############################################################
class WebHandler(BaseHTTPRequestHandler):
	# Manage POST request for command
	def do_POST(self):
		#print(self.path)
		form = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
           		environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type'],
                    })

		action = form.getvalue("action","")
		self.send_response(200)
		self.end_headers()
		rc.executeCommand(action)

	# Manage Get request for command
	def do_GET(self):
		#print(self.path)
		global gframe

		# Stream mjpeg
		if self.path.endswith('/stream.mjpg'):
			self.send_response(200)
			self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			gframe.empty()
			while True:
				try:
					while gframe.empty():
						time.sleep(0.001)
					frame = gframe.get()

					r, buf = cv2.imencode(".jpg", frame)
					self.wfile.write("--jpgboundary\r\n".encode())
					self.end_headers()
					self.wfile.write(bytearray(buf))
				except KeyboardInterrupt:
					break

		# Manage html
		if self.path=='/':
			self.path='index.html'

		filename, file_extension = os.path.splitext(self.path)

		if file_extension in extensionTab.keys():
			mimetype=extensionTab[file_extension][0]
			content=extensionTab[file_extension][1]
			self.send_response(200)
			self.send_header(b'Content-type', mimetype)
			self.end_headers()
			self.wfile.write(content)
			return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
 	"""Handle requests in a separate thread."""


############################################################
# Manage special command
############################################################

def sayno():
	rc.xmin()
	time.sleep(0.5)
	rc.xmax()
	time.sleep(0.5)
	rc.xmin()
	time.sleep(0.5)
	rc.xmax()
	time.sleep(0.5)
	rc.homexy()	

# Calculate if the target is close to the center
def distanceFromCenter(x):
	return (x-320)


# Find the target
def find(context,results,sock):
	if 'angle' not in context.keys():
		context['angle']=rc.getxmin()
		context['frame']=0
		rc.xmin()
	else:
		if len(results)>0:
			cat,prob,x,y,w,h = results[0]
			print(distanceFromCenter(x))
			if abs(distanceFromCenter(x))<75:
				print('found')
				context.clear()
				return False

		context['frame']+=1
		if context['frame']%5!=0:
			return True

		angle = context['angle']

		context['angle']+=15
		if context['angle']>rc.getxmax():
			print('not found')
			context.clear()
			rc.homexy()
			return False
		rc.xplus()
	return True



# Manage special command and send to the correct method
def manageCommand(cmd,context,results,sock):
	if not cmd in ['follow','find']:
		return False
	context['command']=cmd

	if cmd=='find':
		return find(context,results,sock)

	return True


#########################################################################
# Webcam reading and DL management
#########################################################################

def vision():
	# Cam init
	global gFrame
	framecount = 0
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = 10
	rawCapture = PiRGBArray(camera, size=camera.resolution)


	# Socket init
	if DEEP:
		SERVER = '172.27.5.58'
		PORT=5006
		sock = SockHandler(SERVER,PORT)
		sock.connect()


	# Command and deep leaning
	framecount=0
	deeplearningt0 = False
	bbox=[]
	context={}
	DEEPFRAMERATE=10
	# Main Loop
	for frameR in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		frame = frameR.array
		if DEEP:
			if framecount%DEEPFRAMERATE==0 or deeplearningt0:  # do we send the image to the deep learning server (one frame every 10) or t0 when search or follow command are executed
				sBytes = cv2.imencode('.jpg', frame)[1].tobytes()   # compress to jpg
				sock.send(sBytes)  # Send
				bbox = json.loads(sock.recv().decode()) # recevie result

		framecount+=1  

		# Draw rect for display
		for box in bbox:
			cat,prob,x,y,w,h = box
			cv2.rectangle(frame, (int(x-w/2), int(y-h/2)), (int(x+w/2), int(y+h/2)), (255, 0, 0))
			cv2.putText(frame, cat, (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))

		# manage the execution of special command using deep learning
		command=None
		if not cmd.empty():
			command=cmd.get(0)

		if 'command' in context.keys():
			command=context['command']
		if command:
			deeplearningt0 = manageCommand(command,context,bbox,sock)


		# put the image to the display thread if gframe queue is not full
		if gframe.qsize()<50:
			gframe.put(frame)

		# clear the stream in preparation for the next frame
		rawCapture.truncate(0)

############################################################
# Main
############################################################
def main():

	# Start thread for Websocket listenning (used by alexa)
	wsThread = threading.Thread(target = rc.runWSClient)
	wsThread.start()

	# Start thread for streaming http and mjpeg
	server = ThreadedHTTPServer(('0.0.0.0', 8080), WebHandler)
	print("starting server")
	target = threading.Thread(target=server.serve_forever,args=())
	target.start()

	# Start the webcam reader and Deep Learning 
	vision()

if __name__ == '__main__':
        main()