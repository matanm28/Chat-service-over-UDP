from socket import socket, AF_INET,SOCK_DGRAM


s = socket(AF_INET,SOCK_DGRAM)
dest_ip = '127.0.0.1'
dest_port = 1234
msg = ""
while not msg == '4':
	msg = input("")
	s.sendto(msg.encode(), (dest_ip, dest_port))
	data, sender_info = s.recvfrom(2048)
	if len(data) > 0:
		print(data.decode())

s.close()
