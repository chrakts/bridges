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

resultData = pd.read_csv(targetPath+'/HeizungVerbrauchSummary.csv',  sep=';', parse_dates={'Date': [1]})
resultData['Heizleistung [l]'] = resultData['Heizleistung [l]'].rolling(7).mean()
meanYear = resultData.groupby([resultData['Date'].dt.month, resultData['Date'].dt.day]).mean()
meanYear.to_csv(targetPath+'/HeizungJahresMittel.csv',  sep=';', columns=['Heizleistung [l]'])
print(meanYear)
 