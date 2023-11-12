import inspect, os
import yaml
from pathlib import Path
import setproctitle
import pandas as pd
setproctitle.setproctitle('py3-HeizungVerbrauchSummary')


def calcOilFuture(actual, date):
    meanData = pd.read_csv(targetPath + "/HeizungJahresMittel.csv", sep=';')
    todayIndex = date.timetuple().tm_yday
    future = []
    datumfuture = []
    for i in range(0, 365):
        dayIndex = todayIndex + i
        if dayIndex > 365:
            dayIndex = dayIndex - 365
        actual = actual - meanData["Heizleistung [l]"][dayIndex]
        future.append(actual)
        datumfuture.append(date + pd.Timedelta(days=i+1))
    return datumfuture, future


path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/..'+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)

dataPath = dataMap["mqtt2FileBridge"]["dataFolder"]
targetPath = dataMap["auswertungen"]["dataFolder"]
referenzenPath = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

data = pd.read_csv(targetPath + "/HeizungVerbrauchSummary.csv", parse_dates={'Date': [1]}, sep=';', decimal='.')
referenzen = pd.read_csv(referenzenPath + "/ÖlReferenzen.csv", parse_dates={'Date': [0]}, sep=';', decimal=',', dayfirst=True)

referenzen = referenzen.set_index('Date')
füllstand = [6000.0]
datumList = [data['Date'][0].date()]
for (verbrauch, datum) in zip(data["Heizleistung [l]"], data["Date"]):
    try:
        füllstand.append(referenzen[referenzen.index.isin([datum.date()])]['Füllstand [l]'][0])
    except:
        füllstand.append(füllstand[-1] - verbrauch)
    datumList.append(datum.date())

(datumFutureList, future) = calcOilFuture(füllstand[-1], datumList[-1])
datumList = datumList + datumFutureList
füllstand = füllstand + future

resultData = pd.DataFrame()
resultData['Datum'] = datumList
resultData['Füllung[l]'] = füllstand
resultData.to_csv(targetPath+'/Füllstand Aktuell.csv', sep=';')
