import inspect, os
import signal
from PyCRC.CRCCCITT import CRCCCITT
import yaml
import datetime
import paho.mqtt.client as mqtt
import time
import setproctitle
setproctitle.setproctitle('py3-mqtt2FileBridge')


#publish.single("home-assistant/window/contact", "ON", hostname="192.168.178.27")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  global dataMap
  print("Connected with result code "+str(rc))
  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  for info in dataMap["mqtt2FileBridge"]["infos"]:
    client.subscribe(info["topic"])
    print("Connected to "+info["topic"])

def on_message(client, userdata, msg):
  topic = str(msg.topic)
  payload= (msg.payload).decode("utf-8")
  print((topic)+" : "+(payload))
  for info in dataMap["mqtt2FileBridge"]["infos"]:
    if info["topic"]==topic:
      fileName = dataMap["mqtt2FileBridge"]["dataFolder"]+"/"+str(datetime.datetime.now().date())+"_"+info["name"]
      print(fileName)
      with open(fileName, 'a',encoding='utf8') as file:
        file.write((str(datetime.datetime.now())+";"+payload+"\n"))
        print("now writeing")

  
path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)
  
#time.sleep(10)

client = mqtt.Client( )
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username=dataMap["mqtt"]["user"],password=dataMap["mqtt"]["password"])
client.connect(dataMap["mqtt"]["serverIP"], port=int(dataMap["mqtt"]["port"]),  keepalive=60)
client.loop_forever()


