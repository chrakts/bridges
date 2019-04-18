import paho.mqtt.publish as publish
import yaml


import time

with open('/home/pi/repositories/bridges/config.yaml') as f:
  dataMap = yaml.safe_load(f)


auth = {'username':dataMap["mqtt"]["user"], 'password':dataMap["mqtt"]["password"]}



#t = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
t =  int( time.time() )
publish.single(dataMap["mqtt"]["timeAddress"],
  payload=str(t),
  hostname=dataMap["mqtt"]["serverIP"],
  auth=auth)
