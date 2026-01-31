import inspect, os
import yaml
import setproctitle
import pandas as pd
import numpy as np
import paho.mqtt.publish as publish
setproctitle.setproctitle('py3-HeizungÖlFüllstand')

def get_restDatum(resultData, restMenge):
    # 1️⃣ Heutiges Datum
    heute = pd.Timestamp.today().normalize()

    # 2️⃣ Nur zukünftige Daten betrachten
    future_data = resultData[resultData["Datum"] >= heute]

    # 3️⃣ Filter auf Restmenge
    unterschritten = future_data[future_data["Füllstand [l]"] < restMenge]

    # 4️⃣ Ergebnis prüfen
    if not unterschritten.empty:
        return unterschritten.iloc[0]["Datum"]  # erstes Datum der Unterschreitung
    else:
        return None  # Restmenge wird in Zukunft nie unterschritten


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

# --- Daten vorbereiten ---
data['Datum'] = pd.to_datetime(data['Datum']).dt.normalize()
data = data.set_index('Datum')

referenzen = referenzen.set_index('Datum')
referenzen.index = referenzen.index.normalize()
referenzen = referenzen.sort_index()  # sicherheitshalber

# 1. Füllstand-Spalte vorbereiten
data['Füllstand'] = np.nan

# 2. Referenzwerte an den entsprechenden Tagen eintragen
ref_dates = referenzen.index.intersection(data.index)
data.loc[ref_dates, 'Füllstand'] = referenzen.loc[ref_dates, 'Füllstand [l]']

# 3. Segment-Gruppen zwischen Referenzen erstellen
data['group'] = data['Füllstand'].notna().cumsum()

# 4. Segmentweise kumulativen Verbrauch berechnen
def fill_segment(segment):
    # Startwert: erster Wert der Gruppe, falls Referenz vorhanden
    start_val = segment['Füllstand'].iloc[0] if pd.notna(segment['Füllstand'].iloc[0]) else 0
    segment['Füllstand'] = start_val - segment['Heizleistung [l]'].cumsum()
    # Ersten Tag ggf. Referenzwert setzen
    segment.loc[segment.index[0], 'Füllstand'] = start_val
    return segment


data = data.groupby('group', group_keys=False).apply(fill_segment)

# letztes Datum
aktuellesDatum = data.index.max()

# Füllstand am letzten Datum
aktuellerFüllstand = data.loc[aktuellesDatum, 'Füllstand']

print("Letztes Datum:", aktuellesDatum)
print("Aktueller Füllstand:", aktuellerFüllstand)

(datumFutureList, fuellstandFutureList) = calcOilFuture(aktuellerFüllstand, aktuellesDatum)
plusJahrFüllstand = fuellstandFutureList[-1]

future_df = pd.DataFrame({'Füllstand': fuellstandFutureList}, index=pd.to_datetime(datumFutureList))
future_df.index = future_df.index.normalize()
data = pd.concat([data, future_df], sort=False)
data = data.sort_index()

resultData = pd.DataFrame()
resultData = data[['Füllstand']].copy()  # nur die Spalte Füllstand
resultData = resultData.rename(columns={'Füllstand': 'Füllstand [l]'})
resultData = resultData.reset_index()  # bringt 'Datum' als Spalte zurück
resultData = resultData.rename(columns={resultData.columns[0]: 'Datum'})
resultData.to_csv(targetPath+'/HeizungÖlFüllstand.csv', sep=';', decimal=',', index=False)

auth = {'username': dataMap["mqtt"]["user"], 'password': dataMap["mqtt"]["password"]}
publish.single('oelstand/aktuell', payload="%d" % aktuellerFüllstand, hostname=dataMap["mqtt"]["serverIP"], auth=auth)
publish.single('oelstand/plusJahr', payload="%d" % plusJahrFüllstand, hostname=dataMap["mqtt"]["serverIP"], auth=auth)


restMenge = 500
restDatum = get_restDatum(resultData, restMenge)

if restDatum is not None:
    publish.single('oelstand/restMenge', payload="<%dl am %s" % (restMenge, restDatum.strftime("%d.%m.%Y")), hostname=dataMap["mqtt"]["serverIP"], auth=auth)
else:
    publish.single('oelstand/restMenge', payload="<%dl > 1 Jahr" % restMenge, hostname=dataMap["mqtt"]["serverIP"], auth=auth)

