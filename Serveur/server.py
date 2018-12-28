#!/usr/bin/python3

# -*- coding: utf-8 -*-

from socket import *      # Import necessary modules
import cv2
import numpy as np
from pydarknet import Detector, Image
import json
from network import SockHandler

# =============================================================================
# 			Function to detect grasshopper
# =============================================================================

def vision() :
	#net = Detector(bytes("yolo/yolov3-sauterelle.cfg", encoding="utf-8"), bytes("yolo/yolov3-sauterelle_17000.weights", encoding="utf-8"), 0, bytes("yolo/yolov3-sauterelle.data", encoding="utf-8"))
	#net =  Detector(bytes("yolo/yolov3.cfg", encoding="utf-8"), bytes("yolo/yolov3.weights", encoding="utf-8"), 0, bytes("yolo/coco.data", encoding="utf-8"))
	UDP_IP = "0.0.0.0"
	UDP_PORT = 5006
	sock = SockHandler(UDP_IP,UDP_PORT)
	sock.listen()
	bbox=[]
	while True:
		sock.accept()
		print("accepted")
		#net =  Detector(bytes("yolo/yolov3.cfg", encoding="utf-8"), bytes("yolo/yolov3.weights", encoding="utf-8"), 0, bytes("yolo/coco.data", encoding="utf-8"))
		net = Detector(bytes("yolo/yolov3-sauterelle.cfg", encoding="utf-8"), bytes("yolo/yolov3-sauterelle_17000.weights", encoding="utf-8"), 0, bytes("yolo/yolov3-sauterelle.data", encoding="utf-8"))
		trackingMode = True
		while True:
			try:
				sBytes=sock.recv()
				if len(sBytes)==8:
					model = sBytes.decode("utf-8")
					print(model)
					if model=='sauterel':
						net = Detector(bytes("yolo/yolov3-sauterelle.cfg", encoding="utf-8"), bytes("yolo/yolov3-sauterelle_17000.weights", encoding="utf-8"), 0, bytes("yolo/yolov3-sauterelle.data", encoding="utf-8"))
						trackingMode=True
					else:
						net =  Detector(bytes("yolo/yolov3.cfg", encoding="utf-8"), bytes("yolo/yolov3.weights", encoding="utf-8"), 0, bytes("yolo/coco.data", encoding="utf-8"))
						trackingMode = False
				else:
					npJpg = np.frombuffer(sBytes, dtype=np.uint8)
					frame = cv2.imdecode(npJpg,1)

					if trackingMode and len(bbox)>0:
						ok,bboxtmp = tracker.update(frame)
						print(ok,bboxtmp)
						if ok:
							x,y,w,h = bboxtmp
							bbox=[(bbox[0][0],bbox[0][1],x+w/2,y+h/2,w,h,'recognition')]
						else:
							bbox=[]

					if not trackingMode or len(bbox)==0:
						dark_frame = Image(frame)
						results = net.detect(dark_frame)
						del dark_frame
						bbox=[]
						for cat, score, bounds in results :
							x, y, w, h = bounds
							bbox.append([cat.decode("utf-8") ,score,x,y,w,h,'recognition'])
							if trackingMode:
								tracker = cv2.TrackerMedianFlow_create()
								tracker.init(frame, (x-w/2,y-h/2,w,h))
					sock.send((json.dumps(bbox)).encode('utf-8'))
			except:
				print("connection lost ?")
				net = None
				break

# =============================================================================
# 				Main function
# =============================================================================

def main():
	vision()

if __name__ == '__main__':
	main()
