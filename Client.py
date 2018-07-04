import socket
import time
import inspect
import sys
import datetime

CONSUMER_ID = 2000000000000
host = '127.0.0.1'
port = 5560

retry_idx = 10000
def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return s
    except Exception as e:
        print(e)
        print("Error initializing the socket.")
s = create_socket()
connect_try = 1

def connect_to_server(s = create_socket(), connect_try = retry_idx):
    while True:
        try:
            #print("%i" % lineno())
            s.connect((host, port))
            s.settimeout(2.0)
            print("##....Connected to the Server....##\n")
        except Exception as e:
            #print(e)
            #print("%i" %lineno())
            time.sleep(0.5)
            if connect_try > 0:
                print(str(connect_try) + ":  Error connecting to the Server. Trying again")
                connect_try -= 1
                connect_to_server(s, connect_try)
            else:
                print(str(connect_try) + ":  Unable to Connect to the Server Right now. Please Try to Connect Again later")
                sys.exit()
                break
            break
        break
connect_to_server(s, connect_try = retry_idx)

def send_command(s):
    
    while True:
        i = 0
        weight = i      # function included in weight.py
        read_time = time.time()
        read_date = datetime.datetime.fromtimestamp(read_time).strftime('%Y/%m/%d')
        read_time = datetime.datetime.fromtimestamp(read_time).strftime('%H:%M:%S')
        command = "SEND " + str(CONSUMER_ID) + " " + str(read_date) + " " + str(read_time) + " " + str(weight)
        print(command)
        time.sleep(5)
        i += 1


        
        command1 = command.split(' ', 1)[0]
        try:
            if command1 == "KILL":       # Client Exits
                s.send(str.encode(command))
                break
            elif command1 == "GET" or command1 == "SEND":
                s.send(str.encode(command))
            else:
                print("Unknown Command")
                send_command(s)
                break
        except Exception as e:
            print(e)
            if command1 != "GET" and command1 != "SEND":
                break
            else:
                s.close()
                s = create_socket()
                connect_to_server(s,  connect_try = retry_idx)
                send_command(s)
                break

        try:
            s.settimeout(2.0)   # waits 2 secs to receive data, throws "timedout" exception otherwise
            reply = s.recv(1024)
            print(reply.decode('utf-8'))
            del reply
        except socket.error as msg:
            print(msg)
            s.settimeout(4.0)
            try:
                reply = s.recv(1024)
            except:
                send_command(s)
                break
            print(reply)
            del reply
send_command(s)
