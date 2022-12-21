import paho.mqtt.publish as publish
import yaml

import inspect,os
import time
import datetime
import setproctitle
setproctitle.setproctitle('py3-publishServiceStatus')
import subprocess


path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)

auth = {'username':dataMap["mqtt"]["user"], 'password':dataMap["mqtt"]["password"]}

for service in dataMap["serviceStatus"]:
  
  p =  subprocess.Popen(["systemctl", "is-active",  service["serviceName"]], stdout=subprocess.PIPE)
  (output, err) = p.communicate()
  output = output.decode('utf-8').strip()
  if output=="active":
    result = True
  else:
    result = False
  print(service["serviceName"]+": "+str(result))

  publish.single(service["serviceAddress"],
    payload=str(result),
    hostname=dataMap["mqtt"]["serverIP"],
    auth=auth)
