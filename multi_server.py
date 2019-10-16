import socket
import sys
import time
import threading
from queue import Queue
import subprocess


host = ''
port = 5563
NUMBER_OF_THREADS = 2
CURRENT_CLIENTS = 0
JOB_NUMBER = [1, 2]
all_connections = []
all_address = []
all_names = []
queue = Queue()

def change_cmd_title():
    title = "title Server | Clients Connected " + str(CURRENT_CLIENTS)
    cmd = subprocess.Popen(title[:],  shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE)

def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket Created")
        s.bind((host, port))
        s.listen(5)
        return s
    except socket.error as e:
        print("Socket creation error " + str(e))

    

#Handling multiple connections and saving the connections in a list
# CLosing previous connections when server.py file is restarted

def accepting_connections(s):
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_address[:]
    global CURRENT_CLIENTS

    while True:
        print('Waiting to accept connections')
        try:
            conn, address = s.accept()
            s.setblocking(1)    # A server times out and the connection is closed if no task is performed for a certain time. setblocking prevents that from happening i.e. it prevents timeout
            print("Client Connected : " + address[0] + " Port : " + str(address[1]))
            conn.send(str.encode(str(CURRENT_CLIENTS)))
            CURRENT_CLIENTS += 1
            change_cmd_title()
            all_connections.append(conn)
            all_address.append(address)
            all_names.append('<unknown>')
            t = threading.Thread(target = receive_data, args=(CURRENT_CLIENTS - 1,))
            t.daemon = True
            t.start()

        except Exception as e:
            print("Error accepting connections. Error : " + str(e))

def receive_data(CLIENT_ID):
    conn = all_connections[CLIENT_ID]
    print('Waiting for name of the client')

    data = conn.recv(1024)
    
    name = data.decode('utf-8')
    print('Recieved the name of the client. Client ID = ' + str(CLIENT_ID) + '. Name =  ' + str(name))
    all_names[CLIENT_ID] =  name
    
    while True:
        #print('Inside the thread - receive_data()')
        data = conn.recv(1024)
        data = data.decode('utf-8')
        if not data:
            print('Client' + str(name) + 'got disconnected')
            del all_connections[CLIENT_ID]
            del all_names[CLIENT_ID]
            break
        elif(data[0] == '@'):
            id = data.split(' ')
            id = int(id[0][1:])
            send_conn = all_connections[id]
            send_conn.send(str.encode(data))
        else:
            print(str(CLIENT_ID) + ' - ' + str(all_names[CLIENT_ID]) +  '> ', end = '')
            print(data)
            for i, conn in enumerate(all_connections):
                if(i is not CLIENT_ID):
                    conn.send(str.encode(str(CLIENT_ID) + ' - ' + all_names[CLIENT_ID] + '> ' + data))


# 2nd Thread
# Functions - 
#   1. See all the clients
#   2. Select a client
#   3. Send or receive command to or from the client

def start_turtle():
    while True:
        #print('Inside Turtle')
        cmd = input("Turtle> ")
        if(cmd == 'list'):
            list_connections()
        elif('select' in cmd):
            conn = get_target(cmd)
            if(conn is not None):
                send_target_command(conn)
        elif(cmd == 'chat'):
            ## Loop for sending data to clients
            print('-----Starting chat room-----')
            while True:
                try:
                    message = input('Turtle> ')
                    if(message == 'exit'):
                        break
                    elif(message == 'list'):
                        list_connections()
                    elif('select' in cmd):
                        conn = get_target(cmd)
                        if(conn is not None):
                            send_target_command(conn)
                    elif(message[0] == '@'):
                        id = message.split(' ')
                        id = int(id[0][1:])
                        conn = all_connections[id]
                        conn.send(str.encode(message))
                    elif(len(str.encode(message)) > 0):
                        #print('Trying to send the command. Please wait')
                        ## Sending data to all the clients
                        for conn in all_connections:
                            conn.send(str.encode('root> ' + message))
                except Exception as e:
                    print('Error sending command' + str(e))
        else:
            print('Command not recognised')

def list_connections():
    results = ''
    for i, conn in enumerate(all_connections):
        results += str(i) + " " + str(all_address[i][0]) + " " + str(all_address[i][1]) + '\n'
    print("-----Clients-----" + '\n' + results)


def get_target(cmd):
    try:
        target = cmd.replace('select ', '')
        target = int(target)
        conn = all_connections[target]
        print('You are now connected to ' + str(all_address[target][0]))
        print(str(all_address[target][0]) + ">", end="")
        return conn
    except:
        print('Selection not valid')



def send_target_command(conn):
    while True:
        try:
            message = input("")
            if(message == 'exit'):
                break
            elif(len(str.encode(message)) > 0):
                print('Trying to send the command. Please wait')
                conn.send(str.encode(message))
                client_response = str(conn.recv(20480), 'utf-8')
                if not client_response:
                    print('Client got disconnected')
                    break
                else:
                    print(client_response, end="")
        except Exception as e:
            print('Error sending command' + str(e))


    
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
            s = create_socket()
            accepting_connections(s)
        elif(x==2):
            start_turtle()
        queue.task_done()


create_workers()
create_jobs()