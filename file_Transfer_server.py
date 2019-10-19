import socket

host = ''
port = 5560

def create_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    return s

s = create_socket()
s.listen(1)
conn, addr = s.accept()
s.setblocking(1)
print('Client connected' + str(addr[0]) + ' ' + str(addr[1]))
data = conn.recv(1024)
print(data.decode('utf-8'))
filename = 'client.py'
conn.send(str.encode(filename))
f =  open(filename, 'rb')
l = f.read(1024)
while(l):
    conn.send(l)
    l = f.read(1024)
f.close()
print('Done sending')
conn.send(str.encode('Thank you'))
conn.close()




