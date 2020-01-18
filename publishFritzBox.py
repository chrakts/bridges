import paho.mqtt.publish as publish
import yaml
from fritzconnection import FritzConnection
import inspect,os
import time
import datetime
import setproctitle
setproctitle.setproctitle('py3-publishFritzbox')




path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)

auth = {'username':dataMap["mqtt"]["user"], 'password':dataMap["mqtt"]["password"]}
fc = FritzConnection(dataMap["fritzBoxMain"]["ip"],password=dataMap["fritzBoxMain"]["password"])

for info in dataMap["fritzBoxMain"]["switches"]:
  wlan = str(  int( fc.call_action(info["command"], 'GetInfo')["NewEnable"] )  )
  publish.single(info["getTopic"], payload=wlan, hostname=dataMap["mqtt"]["serverIP"], auth=auth)

"""
state = fc.call_action('WLANConfiguration2', 'GetInfo')
wlan2 = state["NewEnable"]
state = fc.call_action('WLANConfiguration3', 'GetInfo')
wlan3 = state["NewEnable"]
#fc.call_action('WLANConfiguration1', 'SetEnable', NewEnable=1)
#fc.call_action('WLANConfiguration2', 'SetEnable', NewEnable=1)



publish.single(dataMap["fritzBoxMain"]["wlan2"],
  payload=str(int(wlan2)),
  hostname=dataMap["mqtt"]["serverIP"],
  auth=auth)
publish.single(dataMap["fritzBoxMain"]["wlan3"],
  payload=str(int(wlan3)),
  hostname=dataMap["mqtt"]["serverIP"],
  auth=auth)
"""
