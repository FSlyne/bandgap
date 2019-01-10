import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 9090)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

sock.listen(1)
connection,client_address=sock.accept()
print "Connection accepted"
pktcount=0; buffer=''; d=0
while True:
        data = connection.recv(4096)
        for i in range(0, len(data)-1):
           buffer+=data[i]
           if data[i] == '$':
              d+=1
           if data[i] == ':':
              d=0
           if d==3:
              print pktcount,buffer,"\n"
              d=0
              buffer=''
              pktcount+=1


