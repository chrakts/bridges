import psutil
import paho.mqtt.publish as publish
import yaml
import inspect,os
import setproctitle
setproctitle.setproctitle('py3-publishFreeDiskSpace')

hdd = psutil.disk_usage('/')

path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)

auth = {'username': dataMap["mqtt"]["user"], 'password': dataMap["mqtt"]["password"]}

result = str(hdd.free//(1000**2))

publish.single(dataMap["mqtt"]["diskFreeAddress"],
  payload=result,
  hostname=dataMap["mqtt"]["serverIP"],
  auth=auth)

print(result)
