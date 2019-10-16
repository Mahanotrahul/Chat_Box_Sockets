import socket
import sys
import os
import subprocess
import threading
from queue import Queue
import time

host = '127.0.0.1'
port = 5561
NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
TTL = 10


def connect_to_server():
    global TTL
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            return s
        except:
            print('Unable to connect to server. Waiting to connect. TTL = ' + str(TTL))
            TTL -= 1
            time.sleep(5)


s = connect_to_server()
print('Connected to the server')


def receive_data(s):
    while True:
        #print('Inside the Thread - recieve data()')
        data = s.recv(1024)
        if not data:
            print('Server was reset or closed. \n Waiting to connect to the server')
            s = connect_to_server()
        elif(data[:2].decode('utf-8') == 'cd'):
            os.chdir(data[3:].decode('utf-8'))
        if(len(data) > 0):
            print('root> ')
            print(data.decode('utf-8'))

def send_data(s):
    while True:
        #print('Inside the Thread - send data()')
        message = input('> ')
        s.send(str.encode(message))





def create_workers():
    for _ in range(NUMBER_OF_THREADS):
            t = threading.Thread(target = work)
            t.daemon = True
            t.start()

def create_jobs():
    for i in JOB_NUMBER:
        queue.put(i)
    queue.join()


# Do next job that is in the queue (handle connections, send commands)
def work():
    while True:
        x = queue.get()
        if(x == 1):
            receive_data(s)
        elif(x==2):
            message = input('Turtle> Type your name>>')
            s.send(str.encode(message))
            send_data(s)
        queue.task_done()


create_workers()
create_jobs()

