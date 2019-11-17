import paho.mqtt.publish as publish
import yaml


import time
from pytz import timezone
import datetime

tz = timezone('Europe/Berlin')
utc_dt = datetime.datetime.utcfromtimestamp(time.time())
utc_dt + tz.utcoffset(utc_dt)
diff = tz.utcoffset(utc_dt).seconds


path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)

auth = {'username':dataMap["mqtt"]["user"], 'password':dataMap["mqtt"]["password"]}

#t = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
t =  int( time.time() )-946684800+diff
publish.single(dataMap["mqtt"]["timeAddress"],
  payload=str(t),
  hostname=dataMap["mqtt"]["serverIP"],
  auth=auth)
