import inspect, os
import yaml
import setproctitle
import pandas as pd
import paho.mqtt.publish as publish
setproctitle.setproctitle('py3-HeizungÖlFüllstand')


def calcOilFuture(actual, date):
    meanData = pd.read_csv(targetPath + "/HeizungJahresMittel.csv", sep=';')
    todayIndex = date.timetuple().tm_yday
    futureOil = []
    datumfuture = []
    for i in range(0, 365):
        dayIndex = todayIndex + i
        if dayIndex > 365:
            dayIndex = dayIndex - 365
        actual = actual - meanData["Heizleistung [l]"][dayIndex]
        futureOil.append(actual)
        datumfuture.append(date + pd.Timedelta(days=i+1))
    return datumfuture, futureOil


path = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
with open(path+'/..'+'/config.yaml') as f:
  dataMap = yaml.safe_load(f)

dataPath = dataMap["mqtt2FileBridge"]["dataFolder"]
targetPath = dataMap["auswertungen"]["dataFolder"]
referenzenPath = (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
data = pd.read_csv(targetPath + "/HeizungVerbrauchSummary.csv", parse_dates=["Datum"], sep=';', decimal='.')
referenzen = pd.read_csv(referenzenPath + "/ÖlReferenzen.csv", parse_dates=["Datum"], sep=';', decimal=',', dayfirst=True)

referenzen = referenzen.set_index('Datum')
füllstand = [6000.0]
datumList = [data['Datum'][0].date()]
for (verbrauch, datum) in zip(data["Heizleistung [l]"], data["Datum"]):
    try:
        füllstand.append(referenzen[referenzen.index.isin([datum.date()])]['Füllstand [l]'][0])
    except:
        füllstand.append(füllstand[-1] - verbrauch)
    datumList.append(datum.date())

print(füllstand)

aktuellerFüllstand = füllstand[-1]

(datumFutureList, future) = calcOilFuture(füllstand[-1], datumList[-1])
plusJahrFüllstand = future[-1]

datumList = datumList + datumFutureList
füllstand = füllstand + future

resultData = pd.DataFrame()
resultData['Datum'] = datumList
resultData['Füllung[l]'] = füllstand
resultData.to_csv(targetPath+'/HeizungÖlFüllstand.csv', sep=';')

auth = {'username': dataMap["mqtt"]["user"], 'password': dataMap["mqtt"]["password"]}
publish.single('oelstand/aktuell', payload="%d" % aktuellerFüllstand, hostname=dataMap["mqtt"]["serverIP"], auth=auth)
publish.single('oelstand/plusJahr', payload="%d" % plusJahrFüllstand, hostname=dataMap["mqtt"]["serverIP"], auth=auth)

restMenge = 500
if plusJahrFüllstand <= restMenge:
    restDatum = resultData[resultData["Füllung[l]"] < restMenge].iloc[0]["Datum"]
    publish.single('oelstand/restMenge', payload="<%dl am %s" % (restMenge, str(restDatum)), hostname=dataMap["mqtt"]["serverIP"], auth=auth)
else:
    publish.single('oelstand/restMenge', payload="<%dl > 1 Jahr" % restMenge, hostname=dataMap["mqtt"]["serverIP"], auth=auth)

