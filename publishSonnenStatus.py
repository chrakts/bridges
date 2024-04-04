import paho.mqtt.publish as publish
import yaml
import requests
import inspect, os
import time
from pytz import timezone
import datetime
import setproctitle
setproctitle.setproctitle('py3-publishEnergyStatus')


tz = timezone('Europe/Berlin')
utc_dt = datetime.datetime.utcfromtimestamp(time.time())
utc_dt + tz.utcoffset(utc_dt)
diff = tz.utcoffset(utc_dt).seconds

path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)

auth = {'username': dataMap["mqtt"]["user"], 'password': dataMap["mqtt"]["password"]}

var = dataMap["sonnenBatterie2"]["serverAPI"]

while True:
  if True:
    for req in dataMap["sonnenBatterie2"]["requests"]:
      url = "http://" + dataMap["sonnenBatterie2"]["serverAPI"]+":"+str(dataMap["sonnenBatterie2"]["serverPort"])+'/api/v2/'+req['request']
      headers = {'Auth-Token': '{}'.format(dataMap["sonnenBatterie2"]['Auth-Token'])}
      response = requests.get(url, headers=headers)
      data = response.json()
      for info in req["infoList"]:
        if "index" in info:
          result = data[info["index"]][info["parameter"]]
        else:
          result = data[info["parameter"]]
        if "sign" in info:
          strResult = str(result * info["sign"])
        else:
          strResult = str(result)
        print(info["parameter"] + ": " + strResult)
        publish.single(info["address"], payload=strResult, hostname=dataMap["mqtt"]["serverIP"], auth=auth)
  #except:
  #  pass
  time.sleep(dataMap["sonnenBatterie2"]["publishTime_s"])
