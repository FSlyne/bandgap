import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import re
# from matplotlib import style

interface=sys.argv[1]
LABEL=sys.argv[2]

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
       ax1.set_title("Interface Tx/Rx traffic %s" % LABEL, weight='bold')
       rx_bytes_last=rx_bytes
       tx_bytes_last=tx_bytes

# style.use('fivethirtyeight')

fig = plt.figure()

ax1 = fig.add_subplot(1,1,1)

# https://stackoverflow.com/questions/31117984/pyplot-x-axis-being-sorted
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()

