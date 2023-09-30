import inspect
import os
from fritzconnection import FritzConnection
import yaml
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import setproctitle
setproctitle.setproctitle('py3-switchWLANFritzbox')


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  global dataMap
  print("Connected with result code "+str(rc))
  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  for info in dataMap["fritzBoxMain"]["switches"]:
    client.subscribe(info["setTopic"])
    print("Connected to "+info["setTopic"])


def on_message(client, userdata, msg):
  auth = {'username': dataMap["mqtt"]["user"], 'password': dataMap["mqtt"]["password"]}
  topic = str(msg.topic)
  payload = msg.payload.decode("utf-8")
  state = int(payload)
  print(topic + " : " + payload)
  for info in dataMap["fritzBoxMain"]["switches"]:
    if info["setTopic"] == topic:
      command = info["command"]
      print(command+": "+str(state))
      fc = FritzConnection(dataMap["fritzBoxMain"]["ip"], user=dataMap["fritzBoxMain"]["user"], password=dataMap["fritzBoxMain"]["password"])
      fc.call_action(command, 'SetEnable', NewEnable=state)
      state = str(int(fc.call_action(command, 'GetInfo')["NewEnable"]))
      print("State: "+state)
      try:
        publish.single(info["getTopic"], payload=state, hostname=dataMap["mqtt"]["serverIP"], auth=auth)
      except Exception as e:
        print('Failed: ' + str(e))
      print("published")


path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)
  
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username=dataMap["mqtt"]["user"], password=dataMap["mqtt"]["password"])
client.connect(dataMap["mqtt"]["serverIP"], port=int(dataMap["mqtt"]["port"]),  keepalive=60)
client.loop_forever()
