import socket
import threading
from collections import defaultdict as df
import atexit

def exiting(groups):
	f = open('data.txt', 'wb')
	for g in chats:
		f.write(str.encode('{' + str(g) + ':'))
		for x in chats[g]:
			f.write(str.encode(x))
		f.write(str.encode('}'))
	f.close()

host = ''
port = 5701
group_names = []
all_connections = []
all_names = []
groups = df(list)
chats = df(list)
atexit.register(exiting, groups)

def create_socket():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	s.listen(10)
	return s

s = create_socket()
s.setblocking(1)

def accept_connections(s):
	global groups
	global chats
	while True:
		conn, addr = s.accept()
		print('New client connected. Address = ' + str(addr[0]) + ' ' + str(addr[1]))
		u_name = conn.recv(1024)
		u_name = u_name.decode('utf-8')
		u_name = u_name.replace('USER ', '')
		print('user id = ' + str(u_name))
		g_name = conn.recv(1024)
		g_name = g_name.decode('utf-8')
		g_name = g_name.replace('JOIN ', '')
		print('group_id = ' + str(g_name))
		all_connections.append(conn)
		all_names.append(u_name)
		
		if(g_name not in groups):
			conn.send(str.encode('New group has been created'))
		groups[g_name].append(conn)
		if(len(chats[g_name]) > 0):
			conn.send(str.encode('Earlier Messages in this chat - \n'))
			for message in chats[g_name]:
				conn.send(str.encode(message))
		t = threading.Thread(target = receive_data, args = (g_name, conn, u_name))
		t.daemon = True
		t.start()
		# if(g_name in group_names):
		# 	for i, g in enumerate(group_names):
		# 		if(g == g_name):
		# 			gr_id = i
		# 	t = threading.Thread(target = receive_data, args = (g_name, conn, u_name, gr_id))
		# 	t.daemon = True
		# 	t.start()
		# else:
		# 	group_names.append(g_name)
		# 	gr_id = len(group_names) - 1
		# 	t = threading.Thread(target = receive_data, args = (g_name, conn, u_name, gr_id))
		# 	t.daemon = True
		# 	t.start()

def receive_data(g_name, conn, u_name):
	global groups
	global chats
	while True:
		try:
			data = conn.recv(1024)
			data = data.decode('utf-8')
			if(conn is None or data == ''):
				print('Client ' + str(u_name) + 'got disconnected. ')
				break
			
			print('Client:  ' + str(u_name) + ' > ' + str(data))
			# conn.send(str.encode(data))
			message = 'Client ' + str(u_name) + '> ' + data
			chats[g_name].append(message)
			for i, conn in enumerate(groups[g_name]):
				conn.send(message.encode('utf-8'))

		except Exception as e:
			print(e.errno)
			print('Client had got disconnected earlier. You may have lost some messages')
			print('Client got disconnected. ' + str(e))
			break


accept_connections(s)


