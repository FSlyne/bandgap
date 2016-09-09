import socket
import sys
import time

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('0.0.0.0', 9090)
sock.bind(server_address)


threshold=5; logthreshlower = 0; logthreshupper = 10000;
interval=1; debug=0
print_jitter_interval=5

expcount=1;exptime=time.time()
lasttime=time.time();lastpacket=0;

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

while True:
   text, address = sock.recvfrom(1500)
   (instr,var1,var2,var3,var4) = text.split(':')
   if instr == 'DATA':
      (count,tme,payload,cks) = (int(var1),float(var2),var3,var4)
      if cks != cksum(payload):
         print "checksum error [%s] %s %s %s %s" % (str(cks), str(cksum(payload)),str(count), str(tme), str(payload))
      if expcount != count:
         dropped = count-expcount
         intt = dropped * interval
         now = time.time()
         if dropped > threshold:
            if debug:
               print "%s Gap: %s packets, %s ms (%s, %s %s)" % (str(now),str(dropped),str(intt),str(tme),str(count),str(expcount))
            localtgap = (now - lasttime)*1000
            localpgap = count - lastpacket
            if debug:
               print "Gap seen locally is %s (%s - %s), %s (%s - %s)" % (str(localtgap), str(now), str(lasttime), str(localpgap), str(count), str(lastpacket)
)
         if localtgap > logthreshlower and localtgap < logthreshupper:
            print localtgap
      else:
         lasttime=time.time()
         lastpacket=count
         gap=tme-exptime
         if count % (1000 *print_jitter_interval/interval) == 1:
            if debug:
               print "jitter gap %s (%s - %s)"% (str(gap),str(count),str(tme))
      expcount=count+1
      exptime=time.time()+interval/1000
   elif instr == 'RSTTMR':
      if debug:
         print "Settimg Time Interval to %s" % interval
      interval=float(var1)
   else:
      print "Unknown Instruction %s" % instr

