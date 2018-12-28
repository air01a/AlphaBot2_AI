class ObjectRecognition:
    sock = None

    # Socket init
    def __init__(self, SERVER,PORT):
		self.sock = SockHandler(SERVER,PORT)
		self.sock.connect()
		time.sleep(4)
	
    # Object recognition
    def recognize(frame,visionContext,bbox):
	    if visionContext['DEEP']:
		    if visionContext['framecount']%visionContext['DEEPFRAMERATE']==0 or visionContext['deeplearningt0']:  # do we send the image to the deep learning server (one frame every 10) or t0 when search or follow command are executed
			    sBytes = cv2.imencode('.jpg', frame)[1].tobytes()   # compress to jpg
			    sock.send(sBytes)  # Send
			    bbox = json.loads(sock.recv().decode()) # recevie result
	    return bbox

