import socket

import struct

class SockHandler:

	def __init__(self,IP,PORT):
		self.IP = IP
		self.PORT = PORT

	def connect(self):
		# Create a TCP/IP socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = (self.IP, self.PORT)
		self.sock.connect(server_address)
		self.connection = self.sock

	def send(self,message):
		size = len(message)
		self.sock.sendall(struct.pack('!I', size))
		self.sock.sendall(message)


	def recvall(self,sock, count):
		buf = b''
		while count:
			newbuf = sock.recv(count)
			if not newbuf: return None
			buf += newbuf
			count -= len(newbuf)
		return buf

	def listen(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = (self.IP, self.PORT)
		self.sock.bind(server_address)
		self.sock.listen(1)

	def accept(self):
		self.connection, client_address = self.sock.accept()

	def recv(self):
		lengthbuf = self.recvall(self.connection, 4)
		length, = struct.unpack('!I', lengthbuf)
		return self.recvall(self.connection, length)

