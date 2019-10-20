import socket
import time
import threading
from queue import Queue


host = '127.0.0.1'
port = 5686
NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
print('Connected to the server')
user_id = input('Type your id: ')
g_name = input('Type your name: ')

s.send(str.encode(user_id))
time.sleep(0.1)
s.send(str.encode(g_name))

def receive_data():
	while True:
		data = s.recv(1024)
		print(data.decode('utf-8'))


def send_data():
	while True:
		message = input('Type> ')
		s.send(str.encode(message))


for i in JOB_NUMBER:
	if i == 1:
		t = threading.Thread(target = send_data)
		t.daemon = True
		t.start()
	else:
		t = threading.Thread(target = receive_data)
		t.daemon = True
		t.start()



