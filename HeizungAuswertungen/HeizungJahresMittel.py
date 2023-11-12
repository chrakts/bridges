import inspect, os
import yaml
from pathlib import Path
import setproctitle
import pandas as pd
setproctitle.setproctitle('py3-HeizungJahresMittel')

path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/..'+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)

dataPath = dataMap["mqtt2FileBridge"]["dataFolder"]
targetPath = dataMap["auswertungen"]["dataFolder"]

resultData = pd.read_csv(path,  sep=';')
resultData = resultData.rolling(7).mean()
resultData.reset_index(level=0, inplace=True)
meanYear = resultData.groupby([resultData['Datum'].dt.month, resultData['Datum'].dt.day]).mean()
meanYear.drop('Stufe 1', axis=1, inplace=True)
meanYear.drop('Stufe 2', axis=1, inplace=True)
meanYear.to_csv(targetPath+'/meanYear.csv', sep=';')
