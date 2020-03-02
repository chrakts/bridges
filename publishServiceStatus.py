import paho.mqtt.publish as publish
import yaml

import inspect,os
import time
import datetime
import setproctitle
setproctitle.setproctitle('py3-publishServiceStatus')
import subprocess


service = "cmulti-bridge"
p =  subprocess.Popen(["systemctl", "is-active",  service], stdout=subprocess.PIPE)
(output, err) = p.communicate()
output = output.decode('utf-8').strip()
if output=="active":
  print(output)
else:
  print("<<not active>>")
  print(output)
"""
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
"""
