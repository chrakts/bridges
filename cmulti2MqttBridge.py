import paho.mqtt.publish as publish
import serial
import signal
from PyCRC.CRCCCITT import CRCCCITT
import yaml

#publish.single("home-assistant/window/contact", "ON", hostname="192.168.178.27")

def _readline(self):
  eol = b'>'
  leneol = len(eol)
  line = bytearray()
  while True:
    c =  self.interface.read(1)
    if c:
      line += c
      if line[-leneol:] == eol:
        break
    else:
      break
  return bytes(line)
 
 
def input(self):
  inTime = True
  hello = self._readline().decode('utf-8')
  if len(hello) == 0:
   return("",False,False,False)
  crcState = True
  crcString = ""
  if hello[0] != '<':
   print("!! start character error")
  if hello[-1] != '>':
   print("!! end character error")
  if self.crc != cmulti_crc_constants_t.noCRC:
   crcString = hello[-5:-1]
   signString = hello[-6:-5]
   answerString = hello[1:-5]
   if crcString == ("%04x" % (CRCCCITT().calculate(answerString))):
    crcState = True
   else:
    crcState = False
    print("!! CRC error")
   answerString = answerString[0:-1] # das sign abtrennen
  else:
   answerString = hello[1:-2]
   signString = hello[-2:-1]
  if signString == '.':
   return(answerString,True,crcState,inTime)
  elif signString == '!':
   return(answerString,False,crcState,inTime)
  else:
   print("!! sign character error")
   return(answerString,False,crcState,inTime)

NO_MESSAGE = 0
START_MESSAGE = 1
LENGTH2_MESSAGE = 2
COUNT_MESSAGE = 3

with open('config.yaml') as f:
  dataMap = yaml.safe_load(f)

interface = serial.Serial(dataMap["cmulti2MqttBridge"]["comPort"], dataMap["cmulti2MqttBridge"]["baudRate"], timeout=3)
status = NO_MESSAGE
try:
  while(1):
    try:
      test = interface.read(1).decode("utf-8") 
      if(test=='#'):
        status = START_MESSAGE
        actLength = 0
        actCommand = test
      if status == START_MESSAGE and test != '#':
        length = 16*int(test,16)
        status = LENGTH2_MESSAGE
        actLength += 1
        actCommand += test
      elif status == LENGTH2_MESSAGE:
        length += int(test,16)
        status = COUNT_MESSAGE
        actLength += 1
        actCommand += test
      elif status == COUNT_MESSAGE:
        actLength += 1
        actCommand += test
        if(actLength==length):
          crcString = ("%04x" % (CRCCCITT().calculate(actCommand[:-4])))
          if crcString==actCommand[-4:]:
            print(actCommand)
            print("crc-ok")
            Ziel = actCommand[4:6]            
            Quelle = actCommand[6:8]
            Function = actCommand[9]
            Address = actCommand[10]
            Job = actCommand[11]
            dataType = actCommand[12]
            Inhalt = actCommand[13:-6]
            mqqtAddress = ("Cmulti/%s/%s/%s/%s/%s/%s"%(Quelle,Function,Address,Job,Ziel,dataType))
            print("%s/%s/%s/%s/%s:%s"%(Ziel,Quelle,Function,Address,Job,Inhalt))
            publish.single(mqqtAddress, Inhalt, hostname=dataMap["mqtt"]["serverIP"],auth = {"username":dataMap["mqtt"]["user"], "password":dataMap["mqtt"]["password"]})
          status = NO_MESSAGE
    except Exception as e: 
      print(e)
      status = NO_MESSAGE

except KeyboardInterrupt:
  pass

