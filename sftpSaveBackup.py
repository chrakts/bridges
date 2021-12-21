import pysftp
import inspect,os
import yaml


path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)


ftp = pysftp.Connection('dataMap["getFtp"]["ip"]', username=dataMap["getFtp"]["user"], private_key=dataMap["getFtp"]["publicKey"])

for directory in dataMap["getFtp"]["directories"]:
  print(directory["remotePath"])

  ftp.cwd(directory["remotePath"])

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
    if remoteFile in locFiles:
      print("skip: %s"%remoteFile)
    else:
      print("copy: %s"%remoteFile)
      ftp.retrbinary("RETR " + remoteFile, open(localPath+'/'+remoteFile, 'wb').write)

ftp.close()
