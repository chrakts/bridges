#!/usr/bin/env python
import inspect, os
import yaml
import datetime
import time
import zipfile
import ftplib

def zipdir(sourcePath,destPath,zipFileName):
  zipf = zipfile.ZipFile(destPath+'/'+zipFileName, 'w', zipfile.ZIP_DEFLATED)
  for root, dirs, files in os.walk(sourcePath+'/'):
    for singleFile in files:
      zipf.write(os.path.join(root, singleFile) , singleFile)
  zipf.close()

path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)
  
zipdir(dataMap["zipAndSaveData"]["sourcePath"],dataMap["zipAndSaveData"]["destPath"],
  dataMap["zipAndSaveData"]["zipFile"])

ftp = ftplib.FTP()
ftp.connect(dataMap["cloudFtpServer"]["ftpServer"],dataMap["cloudFtpServer"]["port"])
ftp.login(dataMap["cloudFtpServer"]["user"], dataMap["cloudFtpServer"]["password"])
ftp.cwd(dataMap["zipAndSaveData"]["remotePath"])
ftp.storbinary("STOR " + dataMap["zipAndSaveData"]["zipFile"], open(dataMap["zipAndSaveData"]["destPath"]+'/'+dataMap["zipAndSaveData"]["zipFile"], 'rb'))
ftp.quit()

