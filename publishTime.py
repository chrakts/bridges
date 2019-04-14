import paho.mqtt.publish as publish
import yaml


import datetime

with open('config.yaml') as f:
  dataMap = yaml.safe_load(f)


auth = {'username':dataMap["mqtt"]["user"], 'password':dataMap["mqtt"]["password"]}



t = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
publish.single(dataMap["mqtt"]["timeAddress"],
  payload=t,
  hostname=dataMap["mqtt"]["serverIP"],
  auth=auth)