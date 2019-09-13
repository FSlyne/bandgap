import redis
import time
import datetime

hostname = '54.229.160.231' # AWS

port = '9999'
timeout=70
logfile='error.log'
tbps=12345678

qos_level=3

r = redis.Redis(
    host=hostname,
    port=port )

def timestamp():
  return '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

try:
  r.hset('udp_server_function','trafficbps',tbps)
  r.hset('udp_server_function','datetime',timestamp())
  r.hset('qos_level','qos',qos_level)
  r.hset('qos_level','datetime',timestamp())
  r.hset('qos_level','status','written')

#  r.expire('keep-alive',timeout)
except:
  with open(logfile, "a") as myfile:
     myfile.write('%s redis write failed\n' % timestamp())

