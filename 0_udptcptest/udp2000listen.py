import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 2000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
pktcount=0
while True:
        data, address = sock.recvfrom(4096)
        print pktcount,data,"\r",
        pktcount+=1


