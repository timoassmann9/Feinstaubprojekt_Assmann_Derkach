import sqlite3 as sql
import math
from csv import DictReader

con = sql.connect('Feinstaubprojekt_Assmann_Derkach/testdb.db')
cur = con.cursor()
file_name = '2023-01-01_sds011_sensor_92.csv'

# with open('Feinstaubprojekt_Assmann_Derkach/2023-01-01_sds011_sensor_92.csv', 'r') as file:
# 	reader = DictReader(file, delimiter=';')
# 	next(reader)
# 	count = 1
# 	for row in reader:
# 		sensor_id = int(row['sensor_id'])
# 		datumzeit = row['timestamp']
# 		pm2_5 = row['P1']
# 		pm10 = row['P2']
# 		standort = int(row['location'])
# 		lat = row['lat']
# 		lon = row['lon']

# 		uid = f'{file_name}_{count}'

# 		data = {
# 			'UID': uid,
# 			'SensorID': sensor_id,
# 			'DatumZeit': datumzeit, 
# 			'PM2_5': pm2_5, 
# 			'PM10': pm10, 
# 			'Standort': standort, 
# 			'lat': lat, 
# 			'lon': lon
# 		}
# 		# Nur Insert von neuen Datensätzen
# 		check_exists = cur.execute('SELECT 1 FROM Feinstaubanalyse WHERE UID = ?', (uid,))
# 		result_exists = check_exists.fetchone()
# 		print(result_exists)
# 		if result_exists is None:
# 			cur.execute('INSERT INTO Feinstaubanalyse VALUES(:UID, :SensorID, :DatumZeit, :PM2_5, :PM10, :Standort, :lat, :lon)', data)
# 			con.commit()

# 		count += 1

result = cur.execute('''
	SELECT * FROM Feinstaubanalyse WHERE PM2_5 < ? AND PM10 > ? ORDER BY PM10 ASC
''', (10,5)).fetchall()

pm2_5 = []
pm10 = []
for x in result:
	pm2_5.append(x[3])
	pm10.append(x[4])
print(sum(pm2_5)/len(pm2_5))
print(min(pm2_5))
print(max(pm2_5))
print(sum(pm10)/len(pm10))
print(min(pm10))
print(max(pm10))

isit = (1,5,)
print(f'it is: {isit[0]}')