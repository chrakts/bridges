import inspect, os
import paho.mqtt.client as mqtt
from PyCRC.CRCCCITT import CRCCCITT
import yaml
import serial
import time

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  global dataMap
  print("Connected with result code "+str(rc))

  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  client.subscribe(dataMap["Mqtt2cmultiBridge"]["listenTo"])

# The callback for when a PUBLISH message is received from the server.
# Mqtt/Quelle/Function/Address/Job/Target/Datatype
# 0    1      2        3       4   5      6
def on_message(client, userdata, msg):
  sep = msg.topic.split('/')
  st = 'D'+sep[5]+sep[1]+'S'+sep[2]+sep[3]+sep[4]+sep[6]+(msg.payload).decode('ascii')
  if sep[6] != '?':
    st = st +'<'
  l = len(st)+6
  st = "#%02x"%(l)+st
  crcString = ("%04x" % (CRCCCITT().calculate(st)))
  st = st + crcString + "\r\n"
  CmultiServer.write(st.encode('utf-8'))
  print("Write to CMultiServer: "+st)

path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)

time.sleep(10)

client = mqtt.Client( )
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username=dataMap["mqtt"]["user"],password=dataMap["mqtt"]["password"])
client.connect(dataMap["mqtt"]["serverIP"], port=int(dataMap["mqtt"]["port"]),  keepalive=60)
CmultiServer = serial.Serial(dataMap["Mqtt2cmultiBridge"]["comPort"], dataMap["Mqtt2cmultiBridge"]["baudRate"], timeout=10)



# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
CmultiServer.close()
