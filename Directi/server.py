import socket
import threading

host = ''
port = 5686
group_names = []
all_connections = []
all_names = []

def create_socket():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	s.listen(5)
	return s

s = create_socket()
s.setblocking(1)

def accept_connections(s):
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
		

		if(g_name in group_names):
			t = threading.Thread(target = receive_data, args = (g_name, conn, u_name))
			t.daemon = True
			t.start()
		else:
			group_names.append(g_name)
			t = threading.Thread(target = receive_data, args = (g_name, conn, u_name))
			t.daemon = True
			t.start()

def receive_data(g_name, conn, u_name):
	while True:
		try:
			data = conn.recv(1024)
			data = data.decode('utf-8')
			if(conn is None or data == ''):
				print('Client' + str(u_name) + 'got disconnected. ')
				break
			
			print('Client:  ' + str(u_name) + ' > ' + str(data))
			conn.send(str.encode(data))
		except Exception as e:
			print('Client got disconnected. ')
			break


accept_connections(s)