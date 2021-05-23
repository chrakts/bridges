import paho.mqtt.publish as publish
import yaml

import inspect,os
import time
from pytz import timezone
import datetime
import setproctitle
setproctitle.setproctitle('py3-publishTime')
import requests




tz = timezone('Europe/Berlin')
utc_dt = datetime.datetime.utcfromtimestamp(time.time())
utc_dt + tz.utcoffset(utc_dt)
diff = tz.utcoffset(utc_dt).seconds


path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)

auth = {'username':dataMap["mqtt"]["user"], 'password':dataMap["mqtt"]["password"]}

dataMap["sonnenBatterie"]["serverAPI"]

while(True):
  try:
    r = requests.get("http://"+dataMap["sonnenBatterie"]["serverAPI"]+":"+str(dataMap["sonnenBatterie"]["serverPort"])+dataMap["sonnenBatterie"]["requestStatus"])
    data = r.json()

    for info in dataMap["sonnenBatterie"]["infoList"]:
      print(info["name"]+": "+str(data[info["name"]]*info["sign"]))
      
      publish.single(info["address"],
        payload=str(data[info["name"]]*info["sign"]), hostname=dataMap["mqtt"]["serverIP"], auth=auth)
  except:
    pass
  time.sleep(10)
