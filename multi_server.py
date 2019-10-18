import socket
import sys
import time
import threading
from queue import Queue
import subprocess


host = ''
port = 5561
NUMBER_OF_THREADS = 3
CURRENT_CLIENTS = 0
JOB_NUMBER = [1, 2, 3]
all_connections = []
all_address = []
all_names = []
all_lock_objects = []
queue = Queue()
chat = 0
active_flags = []
select_flags = []

def active_clients():
    return sum([1 for i in active_flags if i == 1])

def change_cmd_title():
    while True:
        title = "title Server - Clients Connected " + str(active_clients())
        cmd = subprocess.Popen(title[:],  shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE)
        time.sleep(5)

def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket Created")
        s.bind((host, port))
        s.listen(5)
        return s
    except socket.error as e:
        print("Socket creation error " + str(e))

    

# Handling multiple connections and saving the connections in a list
# CLosing previous connections when server.py file is restarted

def accepting_connections(s):
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_address[:]
    global CURRENT_CLIENTS
    global select_flags

    while True:
        print('Waiting to accept connections')
        try:
            conn, address = s.accept()
            s.setblocking(1)    # A server times out and the connection is closed if no task is performed for a certain time. setblocking prevents that from happening i.e. it prevents timeout
            print("Client Connected : " + address[0] + " Port : " + str(address[1]))
            conn.sendall(str.encode(str(CURRENT_CLIENTS)))
            CURRENT_CLIENTS += 1
            #change_cmd_title()
            all_connections.append(conn)
            all_address.append(address)
            active_flags.append(1)
            select_flags.append(0)
            all_names.append('<unknown>')
            all_lock_objects.append(threading.Lock())
            t = threading.Thread(target = receive_data, args=(CURRENT_CLIENTS - 1,))
            t.daemon = True
            t.start()


        except Exception as e:
            print("Error accepting connections. Error : " + str(e))

def receive_data(CLIENT_ID):
    global chat
    global active_flags
    conn = all_connections[CLIENT_ID]
    print('Waiting for name of the client')

    try:
        data = conn.recv(1024)
    except socket.error as e:
        if(e.errno == 10054):
            print('Message : Client ' + str(CLIENT_ID) + ' has left the connection.')
            active_flags[CLIENT_ID] = 0
            conn.close()
            return
    
    name = data.decode('utf-8')
    print('Received name of the client. Client ID = ' + str(CLIENT_ID) + '. Name =  ' + str(name))
    all_names[CLIENT_ID] =  name
    
    all_lock_objects[CLIENT_ID].acquire()
    while True:
        #print('Inside the thread - receive_data()')
        
        try:
            data = conn.recv(1024)
        except socket.error as e:
            if(e.errno == 10054):
                print('Message : Client ' + str(CLIENT_ID) + ' - ' + str(name) + ' has left the connection.')
                active_flags[CLIENT_ID] = 0
                conn.close()
                break
        data = data.decode('utf-8')
        if not data:
            print('Client' + str(name) + 'got disconnected')
            del all_connections[CLIENT_ID]
            del all_names[CLIENT_ID]
            break
        elif(chat == 1):
            if(data[0] == '@'):
                id = data.split(' ')
                id = int(id[0][1:])
                send_conn = all_connections[id]
                send_conn.sendall(str.encode(data))
            else:
                print(str(CLIENT_ID) + ' - ' + str(all_names[CLIENT_ID]) +  '> ', end = '')
                print(data)
                for i, conn in enumerate(all_connections):
                    if(i is not CLIENT_ID and active_flags[i] == 1):
                        conn.sendall(str.encode(str(CLIENT_ID) + ' - ' + all_names[CLIENT_ID] + '> ' + data))
        elif(select_flags[CLIENT_ID] == 1):
            print(str(CLIENT_ID) + ' - ' + str(all_names[CLIENT_ID]) +  '> ', end = '')
            print(data)
        else:
            conn.sendall(str.encode('-- Message: Chat room not yet started. Please wait. --'))


# 2nd Thread
# Functions - 
#   1. See all the clients
#   2. Select a client
#   3. sendall or receive command to or from the client

def start_turtle():
    global chat
    global active_flags
    while True:
        #print('Inside Turtle')
        cmd = input("Turtle> ")
        if(cmd == 'list'):
            list_connections()
        elif('select' in cmd):
            conn, cl_id = get_target(cmd)
            if(conn is not None):
                send_target_command(conn, cl_id)
        elif(cmd == 'chat'):
            if(active_clients() > 0):
                chat = 1
                for i, conn in enumerate(all_connections):
                    if(active_flags[i] == 1):
                        conn.sendall(str.encode('-----Chat room started-----'))
                ## Loop for sending data to clients
                print('-----Starting chat room-----')

                while True:
                    if(active_clients() == 0):
                        print('Message : No clients in the chat room. Closing the chat room.')
                        break
                    try:
                        message = input('Turtle> ')
                        if(message == 'exit'):
                            chat = 0
                            for i, conn in enumerate(all_connections):
                                if(active_flags[i] == 1):
                                    conn.sendall(str.encode('-- Message: Chat room closed --'))
                            break
                        elif(message == 'list'):
                            list_connections()
                        elif('select' in cmd):
                            conn, cl_id = get_target(cmd)
                            if(conn is not None):
                                send_target_command(conn, cl_id)

                        elif(message[0] == '@'):
                            id = message.split(' ')
                            id = int(id[0][1:])
                            conn = all_connections[id]
                            conn.sendall(str.encode(message))
                        elif(len(str.encode(message)) > 0):
                            #print('Trying to sendall the command. Please wait')
                            ## Sending data to all the clients
                            for i, conn in enumerate(all_connections):
                                if(active_flags[i] == 1):
                                    conn.sendall(str.encode('root> ' + message))
                    except Exception as e:
                        print('Error sending command. ' + str(e))
            else:
                print('Message : No clients connected. Cannot start the chat room.')
        else:
            print('Command not recognised')

def list_connections():
    results = ''
    for i, conn in enumerate(all_connections):
        if(active_flags[i] == 1):
            results += str(i) + " " + str(all_address[i][0]) + " " + str(all_address[i][1]) + '\n'
    if(results == ''):
        print('No clients connected')
    else:
        print("-----Clients-----" + '\n' + results)


def get_target(cmd):
    global select_flags
    try:
        target = cmd.replace('select ', '')
        target = int(target)
        conn = all_connections[target]
        if(active_flags[target] == 1 and conn is not None):
            print('You are now connected to ' + str(all_address[target][0]))
            print(str(all_address[target][0]) + "> ", end="")
            select_flags[target] = 1
            return conn, target
        else:
            print('Selection not valid. Client not connected.')
            return None, None
    except Exception as e:
        print('Selection not valid ' + str(e))
        return None, None



def send_target_command(conn, cl_id):
    global select_flags
    if(select_flags[cl_id] == 1):
        while True:
            #print('Type command> ')
            try:
                message = input("")
                if(message == 'exit'):
                    select_flags[cl_id] = 0
                    break
                elif(len(str.encode(message)) > 0):
                    #print('Trying to sendall the command. Please wait')
                    conn.sendall(str.encode(message))
                    client_response = str(conn.recv(20480), 'utf-8')
                    if not client_response:
                        print('Client got disconnected')
                        break
                    #else:
                        #print(client_response, end="")
                        #print('Response printed. Going somewhere else')
            except Exception as e:
                print('Error sending command' + str(e))
    else:
        select_flags[cl_id] = 0     # updated because it was set to 1 in get_target()
        print('Message: Invalid Operation. Client cannot be selected')


    
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
            t = threading.Thread(target = work)
            t.daemon = True
            t.start()

def create_jobs():
    for i in JOB_NUMBER:
        queue.put(i)
    queue.join()


# Do next job that is in the queue (handle connections, sendall commands)
def work():
    while True:
        x = queue.get()
        if(x == 1):
            s = create_socket()
            accepting_connections(s)
        elif(x==2):
            start_turtle()
        elif(x == 3):
            change_cmd_title()
        queue.task_done()


create_workers()
create_jobs()