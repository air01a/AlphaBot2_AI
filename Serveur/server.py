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
	net = Detector(bytes("yolo/yolov3-sauterelle.cfg", encoding="utf-8"), bytes("yolo/yolov3-sauterelle_17000.weights", encoding="utf-8"), 0, bytes("yolo/yolov3-sauterelle.data", encoding="utf-8"))
	#net =  Detector(bytes("yolo/yolov3.cfg", encoding="utf-8"), bytes("yolo/yolov3.weights", encoding="utf-8"), 0, bytes("yolo/coco.data", encoding="utf-8"))
	UDP_IP = "0.0.0.0"
	UDP_PORT = 5006
	sock = SockHandler(UDP_IP,UDP_PORT)
	sock.listen()

	while True:
		sock.accept()
		while True:
			try:
				sBytes=sock.recv()
				npJpg = np.frombuffer(sBytes, dtype=np.uint8)
				frame = cv2.imdecode(npJpg,1)
				dark_frame = Image(frame)
				results = net.detect(dark_frame)
				del dark_frame
				sockresult=[]
				for cat, score, bounds in results :
					x, y, w, h = bounds
					sockresult.append([cat.decode("utf-8") ,score,x,y,w,h])

				sock.send((json.dumps(sockresult)).encode('utf-8'))
			except:
				print("connection lost ?")
				break

# =============================================================================
# 				Main function
# =============================================================================

def main():
	vision()

if __name__ == '__main__':
	main()
