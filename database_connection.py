import sqlite3 as sql
from csv import DictReader

con = sql.connect('Feinstaubprojekt_Assmann_Derkach/testdb.db')
cur = con.cursor()
file_name = '2023-01-01_sds011_sensor_92.csv'

with open('Feinstaubprojekt_Assmann_Derkach/2023-01-01_sds011_sensor_92.csv', 'r') as file:
	reader = DictReader(file, delimiter=';')
	next(reader)
	count = 1
	for row in reader:
		sensor_id = int(row['sensor_id'])
		datumzeit = row['timestamp']
		pm2_5 = row['P1']
		pm10 = row['P2']
		standort = int(row['location'])
		lat = row['lat']
		lon = row['lon']

		uid = f'{file_name}_{count}'

		data = {
			'UID': uid,
			'SensorID': sensor_id,
			'DatumZeit': datumzeit, 
			'PM2_5': pm2_5, 
			'PM10': pm10, 
			'Standort': standort, 
			'lat': lat, 
			'lon': lon
		}
		# Nur Insert von neuen Datensätzen
		# result_exists ist 1, wenn der Datensatz existiert, ansonsten 0
		check_exists = cur.execute(f"SELECT 1 FROM Feinstaubanalyse WHERE UID = '{uid}'")
		result_exists = check_exists.fetchone()
		if result_exists[0] == 0:
			cur.execute('INSERT INTO Feinstaubanalyse VALUES(:UID, :SensorID, :DatumZeit, :PM2_5, :PM10, :Standort, :lat, :lon)', data)
			con.commit()

		count += 1