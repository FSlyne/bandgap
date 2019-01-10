from random import choice
import string
import time
import sys
import socket
import threading

delimiter='$$$'
testing=False
dest='10.10.10.56'
dest='10.0.0.44'
dest='10.0.0.3'
dest='10.10.10.91'
port=9090
# port=2000
max=1000000
debug=1
packetsize=1000;
delay=0.0005; delayms = delay*1000;
sendevery=1/delay;
totalbytes=0
count=0
totbytes=0

linerate=100000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

remoteaddress = (dest, port)

print remoteaddress

t= time.time();

def threaded(fn):
    def wrapper(*args, **kwargs):
        t=threading.Thread(target=fn, args=args, kwargs=kwargs)
        t.daemon=True
        t.start()
    return wrapper

@threaded
def calcstats():
  global delay
  global totbytes
  global linerate
  cnt=0; secbytes=0
  while True:
    setbytes = linerate*(0.2/8)
    pcdelta=(totbytes-setbytes)/setbytes
    if pcdelta >= 2:
        delay=delay*5
    elif pcdelta >=1:
        delay=delay*2
    else:
        delay=delay/(1-pcdelta)
    cnt+=1; secbytes+=totbytes
    if cnt % 5 == 0:
       print cnt,"\t",secbytes*8
#       print delay,pcdelta,totbytes*40,setbytes*40
       secbytes=0
    totbytes=0
    time.sleep(0.2)


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
   r=msg+p+':'+cks+':'+delimiter
   return r

def setInterval(intt):
   global totalbytes
   global packetsize
   global count
   global sock
   global remoteaddress
   msg="RSTTMR:%s:%s:" % (str(intt),str(time.time()))
   msg=createMsg(msg)
   try:
      sock.sendto(msg,remoteaddress)
   except:
      pass
   totalbytes+=packetsize

def sendpacket():
   global totalbytes
   global totbytes
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
   try:
      sock.sendto(msg,remoteaddress)
   except:
      pass
   totalbytes+=packetsize
   totbytes+=packetsize

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

calcstats()

while True:
   sendpacket()
   time.sleep(delay)

