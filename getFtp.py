import ftplib
import inspect,os
import yaml
from datetime import datetime


path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)


ftp = ftplib.FTP()
ftp.connect(dataMap["getFtp"]["ip"],dataMap["getFtp"]["port"])
ftp.login(dataMap["getFtp"]["user"], dataMap["getFtp"]["password"])

ftpCloud = ftplib.FTP()
ftpCloud.connect(dataMap["cloudFtpServer"]["ftpServer"],dataMap["cloudFtpServer"]["port"])
ftpCloud.login(dataMap["cloudFtpServer"]["user"], dataMap["cloudFtpServer"]["password"])

for directory in dataMap["getFtp"]["directories"]:

  ftp.cwd(directory["remotePath"])
  ftpCloud.cwd(directory["remoteCloudPath"])
  localPath = directory["localPath"]
  locFiles = os.listdir(localPath)
  files = []
  try:
    files = ftp.nlst()
  except (ftplib.error_perm, resp):
    if str(resp) == "550 No files found":
      print ("No files in this directory")
    else:
      raise

  for remoteFile in files:
    jetzt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if remoteFile in locFiles:
      pass
      #print("%s -> skip: %s"%(jetzt,remoteFile))
    else:
      print("%s -> copy: %s"%(jetzt,remoteFile))
      ftp.retrbinary("RETR " + remoteFile, open(localPath+'/'+remoteFile, 'wb').write)
      print("%s -> mv to cloud: %s"%(jetzt,remoteFile))
      ftpCloud.storbinary("STOR " + remoteFile, open(localPath+'/'+remoteFile, 'rb'))

ftpCloud.quit()
ftp.quit()
