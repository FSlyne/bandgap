from ona.zmqbroker import *
from random import choice
import argparse
import string
import time
import sys
import socket
import threading
import numpy as np

delimiter='$$$'
testing=False
defaultdest='172.16.0.2'
defaultport=2000 # UDP port
defaultredis_server='54.229.160.231'
defaultredis_port=9999
defaultzmqbroker='10.10.10.41'
max=1000000 # packets to send
debug=0
packetsize=1000;
delay=0.0005; delayms = delay*1000;
sendevery=1/delay;
totalbytes=0
count=0
totbytes=0

linerate=1000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

def timestamp():
   import datetime
   return '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

@threaded
def dblogger():
   import redis
   hostname = redishost
   port = redisport
   r=redis.Redis(host=hostname, port=port)
   global linerate
   while True:
      try:
         r.hset('udp_server_function','trafficbps',int(linerate))
         r.hset('udp_server_function','datetime',timestamp())
      except:
         print "Error writing to remote database"
      time.sleep(1)


class tbpssub(zmqSubscriber):
   def process(self,mst,msg):
      global linerate
      # tbps_level=1000000
      print mst, msg
      if 'tbps' in msg:
          try:
            a,v=msg.split('=')
            linerate=float(v)
          except:
            pass

class TBPSThread(threading.Thread):
   def run(self):
     b=tbpssub("TBPS",defaultzmqbroker)

@threaded
def wavefunction(fntype='sawtooth', low=1000000, high=20000000, step=1000000,wait=1):
    global linerate
    # linelist=[10000,100000,1000000,10000000]
    if fntype == 'sawtooth':
       linelist=list(range(low,high,step)) # list of line rates to cycle through
       # wait=1 # how long to wait between changes in linerate
       while True:
         for linerate in linelist:
             time.sleep(wait)
         for linerate in reversed(linelist):
             time.sleep(wait)
    elif fntype == 'sine':
         steps=180; deg_inc=2*np.pi/steps
         amp= (high-low)/2
         trans=(high+low)/2
         angle=-np.pi/2
         while True:
             linerate=trans+amp*np.sin(angle)
             angle+=deg_inc
             time.sleep(wait)
    elif fntype == 'flat':
         while True:
             linerate = low
             time.sleep(10)
    elif fntype == 'square':
         while True:
             linerate = 1000000
             time.sleep(25)
             linerate = 5000000
             time.sleep(25)
             linerate = 10000000
             time.sleep(25)
             linerate = 15000000
             time.sleep(25)
             linerate = 5000000
             time.sleep(25)
             linerate = 1000000
             time.sleep(25)

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

if __name__ == '__main__':
#    global dest, port, func, debug, mode, testing, remoteaddress, t
#   https://realpython.com/command-line-interfaces-python-argparse/
   my_parser=argparse.ArgumentParser(description='Generate Local and Remote traffic profiles')
   my_parser.add_argument('-d', '--dest', action='store', metavar='dest', help='Destination UDP IP address', default=defaultdest)
   my_parser.add_argument('-p', '--port', action='store', metavar='port', type=int, help='Destination UDP port address', default=defaultport)
   my_parser.add_argument('-f', '--func', action='store', metavar='func', help='Waveform function: sawtooth sine flat square remote', default='sine')
   my_parser.add_argument('-b', '--debug',action='store', metavar='debug',type=int, help='Debugging: 0 1', default=0)
   my_parser.add_argument('-m', '--mode', action='store', metavar='mode', help='Mode: local remote', default='local')
   my_parser.add_argument('-t', '--test', action='store', metavar='test', type=int, help='Test Mode: 0 1', default=0)
   my_parser.add_argument('-e', '--dbadd', action='store', metavar='dbadd', help='DB address', default=defaultredis_server)
   my_parser.add_argument('-g', '--dbport',action='store', metavar='dbport',help='DB port', default=defaultredis_port)

   args = my_parser.parse_args()
   print args
   dest = args.dest
   port = args.port
   func = args.func
   debug= args.debug
   mode = args.mode
   testing = args.test
   redishost=args.dbadd
   redisport=args.dbport
   

   remoteaddress = (dest, port); 
#   print "Func: %s, dest: %s, port: %d, mode: %s, testing: %d" % (func, dest, port, mode, testing)
   t=time.time()

   payload=randPayload(1500)

   if testing:
      testmode(2,1.456)

   if mode == 'remote':
      if func == 'remote':
         print "conflict: remote function and remote logging"
         exit()
      dblogger()
   calcstats()
   if func =='remote':
       TBPSThread().start()
   else:
       wavefunction(func)

   while True:
      sendpacket()
      time.sleep(delay)
