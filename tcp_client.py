import socket
import sys
import time
import threading

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('0.0.0.0', 9090)
sock.bind(server_address)

threshold=5; logthreshlower = 0; logthreshupper = 10000;
interval=1; debuglevel=2
print_jitter_interval=5

expcount=1;exptime=time.time()
lasttime=time.time();lastpacket=0;

def threaded(fn):
    def wrapper(*args, **kwargs):
        t=threading.Thread(target=fn, args=args, kwargs=kwargs)
        t.daemon=True
        t.start()
    return wrapper

@threaded
def printstats():
    global tme, bytecountsec
    global count, totaldropped
    lastpkts=0
    while (True):
       gap=tme-exptime
       totalpkts=count-lastpkts
       if totaldropped<0:
           totaldropped=0
       print "%10ld %7d %7d %7d" % (time.time(),totalpkts, totaldropped, bytecountsec*8)
#       print "jitter gap %s (%s - %s) %d"% (str(gap),str(count),str(tme), bytecountsec*8)
       bytecountsec=0
       lastpkts=count
       time.sleep(1)

def cksum(string):
  checksum=0
  for c in string:
     checksum ^=ord(c)
  return "%02X" % checksum

def convms(sec):
  return "%.3f" % (sec*1000)

def convspeed(bytes):
  bits=bytes*8
  units = "bps"
  if bits < 1e3:
     units = "bps"
  elif bits < 1e6:
     bits = bits/1e3
     units = "kbps"
  elif bits < 1e9:
     bits = bits/1e6
     units = "Mbps"
  elif bits < 1e12:
     bits = bits/1e9
     units = "Gbps"
  bits= "%.1f" % bits
  return "%s %s" % (str(bits), str(units))

localtgap=0; localpgap=0; count=0; tme =0; bytecountsec=0
totaldropped=0

# ---------------- main () ---------------------

debugfile=open("debug.txt","w")

printstats()

sock.listen(1)
connection,client_address=sock.accept()
while True:
   text = connection.recv(1500)
   bytecountsec+=len(text)
   (instr,var1,var2,var3,var4) = text.split(':')
   if instr == 'DATA':
      (count,tme,payload,cks) = (int(var1),float(var2),var3,var4)
      if cks != cksum(payload):
         if debuglevel>0:
             debugfile.write("checksum error [%s] %s %s %s %s\n" % (str(cks), str(cksum(payload)),str(count), str(tme), str(payload)))
      if expcount != count:
         dropped = count-expcount
         totaldropped+=dropped
         intt = dropped * interval
         now = time.time()
         if dropped > threshold:
            if debuglevel>0:
               debugfile.write("%s Gap: %s packets, %s ms (%s, %s %s)\n" % (str(now),str(dropped),str(intt),str(tme),str(count),str(expcount)))
            localtgap = (now - lasttime)*1000
            localpgap = count - lastpacket
            if debuglevel>0:
               debugfile.write("Gap seen locally is %s (%s - %s), %s (%s - %s)\n" % (str(localtgap), str(now), str(lasttime), str(localpgap), str(count), str(lastpacket))
)
         if localtgap > logthreshlower and localtgap < logthreshupper:
            if debuglevel>0:
               debugfile.write("%d" % localtgap)
      else:
         lasttime=time.time()
         lastpacket=count
         # tme = packet time; exptime = expected time of next packet
         gap=tme-exptime
#         if count % (1000 *print_jitter_interval/interval) == 1:
#            if debuglevel>0:
#               print "jitter gap %s (%s - %s)"% (str(gap),str(count),str(tme))
      expcount=count+1
      exptime=time.time()+interval/1000
   elif instr == 'RSTTMR':
      if debuglevel>1:
         debugfile.write("Settimg Time Interval to %s\n" % interval)
      interval=float(var1)
   else:
      if debuglevel>0:
         debugfile.write("Unknown Instruction %s\n" % instr)

debugfile.close()

