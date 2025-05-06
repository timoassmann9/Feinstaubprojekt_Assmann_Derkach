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

from calendar import monthrange

def url(sensor_type: str, sensor_ID: str, start_year: int, end_year: int, start_month: int, end_month: int):
    urls = []
    start = start_month
    end = end_month
    for year in range(start_year, end_year + 1):
        if start_year < end_year:
            if start_year < year < end_year:
                start = 1
                end = 12
            if year == end_year:
                start = 1
                end = end_month        
        for month in range(start, end + 1):
            for day in range (1, monthrange(year, month)[1] + 1):
                if year > 2023:
                    link = f'archive.sensor.community/{year}-{month:02d}-{day:02d}/{year}-{month:02d}-{day:02d}_{sensor_type}_sensor_{sensor_ID}.csv'
                if year <= 2023:
                    link = f'archive.sensor.community/{year}/{year}-{month:02d}-{day:02d}/{year}-{month:02d}-{day:02d}_{sensor_type}_sensor_{sensor_ID}.csv.gz'
                urls.append(link)
    return urls

print(url('bme280', 250, 2022, 2024, 1, 5))


