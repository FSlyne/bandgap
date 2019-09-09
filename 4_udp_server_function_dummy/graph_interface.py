import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import re
import argparse

# from matplotlib import style

default_interface="eth0"
default_label="Label"

defaultredis_server='54.229.160.231'
defaultredis_port=9999

# interface="sw1"

first_run=True
rx_bytes_last=0; tx_bytes_last=0
xs = []
ys = []
zs = []
ays = []

def animate(i):
    global first_run,xs,ys,zs,ays,rx_bytes_last,tx_bytes_last
    f = open("/proc/net/dev", "r")
    rx_bytes=0; tx_bytes=0
    for line in f:
       if re.search(interface, line):
          fields=line.split()
          rx_bytes=int(fields[1])
          tx_bytes=int(fields[10])
    f.close()
    
    if first_run:
       first_run=False
       rx_bytes_last=rx_bytes
       tx_bytes_last=tx_bytes
    else:
       rx_bytes_delta=(rx_bytes - rx_bytes_last)/1000000
       tx_bytes_delta=(tx_bytes - tx_bytes_last)/1000000
       rx_bits_delta=rx_bytes_delta*8
       tx_bits_delta=tx_bytes_delta*8
       if rx_bits_delta < 0:
          rx_bits_delta =0
       if tx_bits_delta < 0:
          tx_bits_delta =0
       ys.append(rx_bits_delta) ; ays.append(950000000-rx_bits_delta)
       zs.append(tx_bits_delta)
#       print rx_bytes, tx_bytes, rx_bits_delta, tx_bits_delta
       ys=ys[-100:] ; ays=ays[-100:]
       zs=zs[-100:]
       xs= [i for i in range(0, len(ys))]
       ax1.clear()
       ax1.plot(xs,ys,xs,zs)
       ax1.set_xlabel('Older << time(sec) >> Newer')
       ax1.set_ylabel('Mbps')
       # http://maravelias.info/2011/01/reverse-axis-in-matplotlib/
       # https://www.oreilly.com/learning/simple-line-plots-with-matplotlib
       #    ax1.set_xlim(ax1.set_xlim()[::-1])
       #    ax1.set_yticks(weight='bold')
       ax1.set_title("Interface Tx/Rx traffic %s" % label, weight='bold')
       rx_bytes_last=rx_bytes
       tx_bytes_last=tx_bytes

def animate_remote(i):
    global first_run,xs,ys,zs,ays,rx_bytes_last,tx_bytes_last
    try:
       rx_bits_delta=int(r.hget('udp_server_function','trafficbps'))/1000000
       tx_bits_delta=int(r.hget('udp_server_function','trafficbps'))/1000000
    except:
       rx_bits_delta=0
       tx_bitss_delta=0
    ys.append(rx_bits_delta)
    zs.append(tx_bits_delta)
    ys=ys[-100:] 
    zs=zs[-100:]
    xs= [i for i in range(0, len(ys))]
    ax1.clear()
    ax1.plot(xs,ys,xs,zs)
    ax1.set_xlabel('Older << time(sec) >> Newer')
    ax1.set_ylabel('Mbps')
    # http://maravelias.info/2011/01/reverse-axis-in-matplotlib/
    # https://www.oreilly.com/learning/simple-line-plots-with-matplotlib
    #    ax1.set_xlim(ax1.set_xlim()[::-1])
    #    ax1.set_yticks(weight='bold')
    ax1.set_title("Interface Tx/Rx traffic %s" % label, weight='bold')


# style.use('fivethirtyeight')
if __name__ == '__main__':
   my_parser=argparse.ArgumentParser(description='Monitor Local and Remote traffic profiles')
   my_parser.add_argument('-m', '--mode', action='store', metavar='mode', help='Mode: local remote', default='local')
   my_parser.add_argument('-e', '--dbadd', action='store', metavar='dbadd', help='DB address', default=defaultredis_server)
   my_parser.add_argument('-g', '--dbport',action='store', metavar='dbport',help='DB port', default=defaultredis_port)
   my_parser.add_argument('-i', '--int',action='store', metavar='int', help='Inferface',default=default_interface)
   my_parser.add_argument('-l', '--label',action='store', metavar='label', help='label', default=default_label)

   args = my_parser.parse_args()
   print args
   mode = args.mode
   redishost=args.dbadd
   redisport=args.dbport
   interface=args.int
   label=args.label

   fig = plt.figure()

   ax1 = fig.add_subplot(1,1,1)

   # https://stackoverflow.com/questions/31117984/pyplot-x-axis-being-sorted
   if mode == 'local':
      ani = animation.FuncAnimation(fig, animate, interval=1000)
   else:
      import redis
      hostname = redishost
      port = redisport
      r=redis.Redis(host=hostname, port=port)
      ani = animation.FuncAnimation(fig, animate_remote, interval=1000)

   plt.show()

