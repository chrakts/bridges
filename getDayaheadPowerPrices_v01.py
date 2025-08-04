import requests
import pandas as pd
from datetime import datetime, timedelta

def get_day_ahead_prices_for(date_target: datetime):
    # SMARD verwendet Monatsdateien, z. B. "2025_06_01.json"
    year = date_target.year
    month = date_target.month
    date_string = f"{year}_{month:02d}_01"
    
    # Lade Monatsdaten
    url = f"https://www.smard.de/app/chart_data/122/DE/{date_string}.json"
    response = requests.get(url)
    if not response.ok:
        raise Exception(f"Daten konnten nicht geladen werden: {url}")
    
    data = response.json()
    df = pd.DataFrame(data["dataset"], columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["date"] = df["timestamp"].dt.date

    # Filtere nur den gewünschten Tag
    target_date = date_target.date()
    df_day = df[df["date"] == target_date].copy()
    df_day.drop(columns=["date"], inplace=True)

    if df_day.empty:
        print(f"Keine Daten für {target_date}")
    else:
        print(f"Day-Ahead-Preise für {target_date}:")
        print(df_day)

    return df_day

# Morgen berechnen
tomorrow = datetime.now() + timedelta(days=1)
get_day_ahead_prices_for(tomorrow)
