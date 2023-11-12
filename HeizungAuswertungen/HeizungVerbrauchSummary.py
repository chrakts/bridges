import inspect, os
import yaml
from pathlib import Path
import setproctitle
import pandas as pd
setproctitle.setproctitle('py3-HeizungVerbrauchSummary')

path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/..'+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)

dataPath = dataMap["mqtt2FileBridge"]["dataFolder"]
targetPath = dataMap["auswertungen"]["dataFolder"]

files = list(Path(dataPath).rglob('????-??-??_Heizung_Stufe_1'))
files.sort()
resultData = pd.DataFrame()
for path in files:
  result = dict()
  result['Datum'] = pd.to_datetime(path.name[0:10], format='%Y-%m-%d')
  data = pd.read_csv(path, names=['Datum', 'Stufe 1'], sep=';')
  result['Stufe 1'] = data['Stufe 1'].sum()

  head_tail = os.path.split(path)
  fnName = head_tail[0] + "/" + head_tail[1][0:11] + "Heizung_Stufe_2"
  try:
    data2 = pd.read_csv(fnName, names=['Datum', 'Stufe 2'], sep=';')
    data['Stufe 2'] = data2['Stufe 2']
    result['Stufe 2'] = data['Stufe 2'].sum()
  except:
    result['Stufe 2'] = 0
  row = pd.Series([result['Datum'], result['Stufe 1'], result['Stufe 2']], index=['Datum', 'Stufe 1', 'Stufe 2'])
  resultData = pd.concat([resultData, row.to_frame().T])

resultData["Heizleistung [l]"] = 1.31 * (resultData['Stufe 1'] + resultData['Stufe 2'] * 0.6) / 3600.0
resultData.to_csv(targetPath+'/HeizungVerbrauchSummary.csv', sep=';')
