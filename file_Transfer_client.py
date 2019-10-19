import socket

host = '127.0.0.1'
port = 5560
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.send(str.encode('Ready to receive file'))
file_name = s.recv(1024)
file_ext = file_name.decode('utf-8').split('.')[-1]
with open('received_file2.' + str(file_ext), 'wb') as f:
    print('file opened')
    while True:
        print('receiving data')
        data = s.recv(1024)
        print('data=%s', (data))
        if not data:
            break;
        f.write(data)
    f.close()
print('Successfully received file.')
s.close()
print('connection closed')
