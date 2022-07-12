import paho.mqtt.publish as publish
import yaml
from fritzconnection import FritzConnection
import inspect
import os
import setproctitle
setproctitle.setproctitle('py3-publishFritzbox')


path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)

auth = {'username': dataMap["mqtt"]["user"], 'password': dataMap["mqtt"]["password"]}
fc = FritzConnection(dataMap["fritzBoxMain"]["ip"], user=dataMap["fritzBoxMain"]["user"], password=dataMap["fritzBoxMain"]["password"])

for info in dataMap["fritzBoxMain"]["switches"]:
  wlan = str(int(fc.call_action(info["command"], 'GetInfo')["NewEnable"]))
  publish.single(info["getTopic"], payload=wlan, hostname=dataMap["mqtt"]["serverIP"], auth=auth)
