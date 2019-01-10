from random import choice
import string
import time
import sys
import socket
import threading

testing=True
dest='10.10.10.56'
dest='10.0.0.44'
dest='127.0.0.1'
port=9090
max=1000000
debug=1
packetsize=100;
delay=0.001; delayms = delay*1000;
sendevery=1/delay;
totalbytes=0
count=0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

remoteaddress = (dest, port)

t= time.time();

def threaded(fn):
    def wrapper(*args, **kwargs):
        t=threading.Thread(target=fn, args=args, kwargs=kwargs)
        t.daemon=True
        t.start()
    return wrapper


def chksum(string):
  checksum=0
  for c in string:
     checksum ^=ord(c)
  return "%02X" % checksum

def randPayload(size):
   return (''.join(choice(string.ascii_letters) for i in range(size)))

def createMsg(msg):
   p=payload[0:packetsize-len(msg)]
   cks=chksum(p)
   r=msg+p+':'+cks
   return r

def setInterval(intt):
   global totalbytes
   global packetsize
   global count
   global sock
   global remoteaddress
   msg="RSTTMR:%s:%s:" % (str(intt),str(time.time()))
   msg=createMsg(msg)
   sock.sendto(msg,remoteaddress)
   totalbytes+=packetsize

def sendpacket():
   global totalbytes
   global packetsize
   global count
   global sock
   global remoteaddress
   global sendevery
   msg="DATA:%s:%s:" % (str(count),str(time.time()))
   count+=1
   if count % sendevery == 1:
      setInterval(delayms)
   msg=createMsg(msg)
   sock.sendto(msg,remoteaddress)
   totalbytes+=packetsize;

class testmode(object):
   def __init__(self,uptime,downtime):
      self.uptime=uptime
      self.downtime=downtime
      self.updest=dest
      self.downdest='1.1.1.1'
      self.port=port
      self.worker()

   @threaded
   def worker(self):
      global remoteaddress
      while True:
         remoteaddress=(self.updest,self.port)
         time.sleep(self.uptime)
         remoteaddress=(self.downdest,self.port)
         time.sleep(self.downtime)


payload=randPayload(1500)

if testing:
   testmode(2,1.456)

while True:
   sendpacket()
   time.sleep(delay)
