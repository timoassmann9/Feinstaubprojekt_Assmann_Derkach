# year, sensor_type, sensor_ID, start_month, end_month einlesen
# URL Ausgabe
# jeder Monat hat 31 Tage
# Struktur: 'archive.sensor.community/YYYY-MM-DD/YYYY-MM-DD_sensor_type_sensor_sensor_ID.csv'
# bei Jahr <= 2023: 'archive.sensor.community/YYYY/YYYY-MM-DD/YYYY-MM-DD_sensor_type_sensor_sensor_ID.csv.gz'
# Vorgehensweise: Funktion definieren, 5 parameter
# for month
# for day
# if month, day < 10 mit 0 davor
# liste hinzufügen

# Anforderungen Feinstaubprojekt
# sensor_type = 'sds011'
# Was passiert, wenn eine url nicht gefunden wurde?

from calendar import monthrange
from datetime import datetime

def GenerateUrl(sensor_type: str, sensor_ID: str, start_year: int, end_year: int, start_month: int, end_month: int):
    # Datumsvariablen
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    current_day = now.day

    # Prüfungen, müssen noch implementiert werden
    # Prüfungsvariable, muss nach allen Prüfungen True sein, damit Funktion ausgeführt wird
    flag_continue = True
    return_text = 'Ungültige Eingabe'
    # start year <= end_year
    if start_year > end_year:
        flag_continue = False
    # start_month <= end_month
    if start_month > end_month:
        flag_continue = False
    # start_year und end_year muss zwischen 2015 und aktuellem Jahr sein
    if start_year < 2015 or start_year > current_year:
        flag_continue = False

    if end_year < 2015 or end_year > current_year:
        flag_continue = False
    # start_month und end_month müssen zwischen 1 und 12 sein; wenn end_year = aktuelles Jahr, muss end_month <= aktueller Monat
    if start_month < 1 or start_month > 12:
        flag_continue = False

    if end_month < 1 or end_month > 12:
        flag_continue = False

    if end_year == current_year and end_month > current_month:
        flag_continue = False

    # frühestes Datum: 2015-10-01
    if start_year == 2015 and start_month < 10:
        flag_continue = False

    # Ausführen der Funktion
    if flag_continue:
        urls = []
        start = start_month
        end = end_month
        for year in range(start_year, end_year + 1):
            if start_year < end_year:
                if year == start_year:
                    end = 12
                if start_year < year < end_year:
                    start = 1
                    end = 12
                if year == end_year:
                    start = 1
                    end = end_month        
            for month in range(start, end + 1):
                end_day = monthrange(year, month)[1]
                # Wenn year = aktuelles Jahr und month = aktueller Monat, darf for day in range() nur bis zum vorherigen Tag gehen
                if year == current_year and month == current_month:
                    end_day = current_day - 1
                for day in range (1, end_day + 1):
                    if year > 2023:
                        link = f'archive.sensor.community/{year}-{month:02d}-{day:02d}/{year}-{month:02d}-{day:02d}_{sensor_type}_sensor_{sensor_ID}.csv'
                    if year <= 2023:
                        link = f'archive.sensor.community/{year}/{year}-{month:02d}-{day:02d}/{year}-{month:02d}-{day:02d}_{sensor_type}_sensor_{sensor_ID}.csv.gz'
                    urls.append(link)
        return urls
    else: return return_text

print(GenerateUrl('bme280', 250, 2025, 2025, 4, 5))


