# 06.06.2025
# Nach der Eingabe in die Felder der Benutzeroberfläche wird ein Objekt der Klasse erzeugt
# Auf dieses Objekt können die Methoden generate_ulrs, download_csv usw. angewendet werden

class analyticsdata():
	def __init__(self, sensor_type: str, sensor_ID: str, start_year: int, end_year: int, start_month: int, end_month: int):
		self.sensor_type = sensor_type
		self.sensor_ID = sensor_ID
		self.start_year = start_year
		self.end_year = end_year
		self.start_month = start_month
		self.end_month = end_month

		# Formatierung Variablen
		self.sensor_type = str(self.sensor_type)
		self.sensor_type = self.sensor_type.strip()

		self.sensor_ID = str(self.sensor_ID)
		self.sensor_ID = self.sensor_ID.strip()

		self.start_year = int(self.start_year)
		self.end_year = int(self.end_year)
		self.start_month = int(self.start_month)
		self.end_month = int(self.end_month)

	def GenerateUrls(self):
		from calendar import monthrange
		from datetime import datetime
		
		# Datumsvariablen
		now = datetime.now()
		current_year = now.year
		current_month = now.month
		current_day = now.day

		# Prüfungsvariable, muss nach allen Prüfungen True sein, damit Funktion ausgeführt wird
		flag_continue = True
		return_text = 'Ungültige Eingabe'

		# Prüfungen
		# start year <= end_year
		if self.start_year > self.end_year:
			flag_continue = False
		# start_month <= end_month
		if self.start_month > self.end_month:
			flag_continue = False
		# start_year und end_year muss zwischen 2015 und aktuellem Jahr sein
		if self.start_year < 2015 or self.start_year > current_year:
			flag_continue = False

		if self.end_year < 2015 or self.end_year > current_year:
			flag_continue = False
		# start_month und end_month müssen zwischen 1 und 12 sein; wenn end_year = aktuelles Jahr, muss end_month <= aktueller Monat
		if self.start_month < 1 or self.start_month > 12:
			flag_continue = False

		if self.end_month < 1 or self.end_month > 12:
			flag_continue = False

		if self.end_year == current_year and self.end_month > current_month:
			flag_continue = False

		# frühestes Datum: 2015-10-01
		if self.start_year == 2015 and self.start_month < 10:
			flag_continue = False

		# Ausführen der Funktion
		if flag_continue:
			urls = []
			start = self.start_month
			end = self.end_month
			for year in range(self.start_year, self.end_year + 1):
				if self.start_year < self.end_year:
					if year == self.start_year:
						end = 12
					if self.start_year < year < self.end_year:
						start = 1
						end = 12
					if year == self.end_year:
						start = 1
						end = self.end_month        
				for month in range(start, end + 1):
					end_day = monthrange(year, month)[1]
					# Wenn year = aktuelles Jahr und month = aktueller Monat, darf for day in range() nur bis zum vorherigen Tag gehen
					if year == current_year and month == current_month:
						end_day = current_day - 1
					for day in range (1, end_day + 1):
						if year > 2023:
							link = f'https://archive.sensor.community/{year}-{month:02d}-{day:02d}/{year}-{month:02d}-{day:02d}_{self.sensor_type}_sensor_{self.sensor_ID}.csv'
						if year <= 2023:
							link = f'https://archive.sensor.community/{year}/{year}-{month:02d}-{day:02d}/{year}-{month:02d}-{day:02d}_{self.sensor_type}_sensor_{self.sensor_ID}.csv.gz'
						urls.append(link)
			return urls
		else: return return_text