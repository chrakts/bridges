#!/usr/bin/env python
import inspect, os
import yaml
from datetime import datetime
import time
import zipfile
import ftplib

def zipdir(sourcePath,destPath,zipFileName):
  zipf = zipfile.ZipFile(destPath+'/'+zipFileName, 'w', zipfile.ZIP_DEFLATED)
  for root, dirs, files in os.walk(sourcePath+'/'):
    i = 0
    for singleFile in files:
      i += 1
      zipf.write(os.path.join(root, singleFile) , singleFile)
  zipf.close()
  return i

path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)
  
numFiles = zipdir(dataMap["zipAndSaveData"]["sourcePath"],dataMap["zipAndSaveData"]["destPath"],
  dataMap["zipAndSaveData"]["zipFile"])

pathToZipFile = dataMap["zipAndSaveData"]["destPath"]+'/'+dataMap["zipAndSaveData"]["zipFile"]
jetzt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
sizeOfZip = os.path.getsize(pathToZipFile)
print("%s -> Saved mqtt-Data. %d bytes in %d files "%(jetzt,sizeOfZip,numFiles))

ftp = ftplib.FTP()
ftp.connect(dataMap["cloudFtpServer"]["ftpServer"],dataMap["cloudFtpServer"]["port"])
ftp.login(dataMap["cloudFtpServer"]["user"], dataMap["cloudFtpServer"]["password"])
ftp.cwd(dataMap["zipAndSaveData"]["remotePath"])
ftp.storbinary("STOR " + dataMap["zipAndSaveData"]["zipFile"], open(dataMap["zipAndSaveData"]["destPath"]+'/'+dataMap["zipAndSaveData"]["zipFile"], 'rb'))
ftp.quit()
jetzt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("%s -> Moved mqtt-Data to Server. "%jetzt)

