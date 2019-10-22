import socket
import time
import threading

host = '127.0.0.1'
port = 5701

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
print('Connected to the server')
user_id = input('Type your id: ')
g_name = input('Type your name: ')

s.send(str.encode(user_id))
time.sleep(0.1)
s.send(str.encode(g_name))

while True:
	data = input('Client : ')
	s.send(str.encode(data))
	data = s.recv(1024)
	print(data.decode('utf-8'))

