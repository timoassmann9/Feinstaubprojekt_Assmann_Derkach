class analyticsdata():
	def __init__(self, sensor_ID: str, start_year: int, end_year: int, start_month: int, end_month: int):
		self.sensor_type = 'sds011'
		self.sensor_ID = sensor_ID
		self.start_year = start_year
		self.end_year = end_year
		self.start_month = start_month
		self.end_month = end_month
		self.urls = []

		# Formatierung Variablen
		self.sensor_ID = str(self.sensor_ID)
		self.sensor_ID = self.sensor_ID.strip()

		self.start_year = int(self.start_year)
		self.end_year = int(self.end_year)
		self.start_month = int(self.start_month)
		self.end_month = int(self.end_month)

	def GenerateUrls(self):
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
			self.urls = urls
		else: return return_text

	def download_csv(self):
		for url in self.urls:
			response = requests.get(url)
			url_end = url.rfind('/')
			file_name = url[url_end:]
			file_Path = 'Feinstaubprojekt_Assmann_Derkach/files' + file_name

			if response.status_code == 200:
				# Datei herunterladen
				with open(file_Path, 'wb') as file:
					file.write(response.content)
				# Wenn komprimierte Datei, dann entpacken und kopieren
				if file_Path.endswith('.gz'):
					with gzip.open(file_Path, 'rb') as f_in:
						with open(file_Path[:-3], 'wb') as f_out:
							shutil.copyfileobj(f_in, f_out)
					# Komprimierte Datei löschen
					if os.path.exists(file_Path):
						os.remove(file_Path)
					else:
						print('The file does not exist')
				print(f'File {file_name} downloaded successfully')
			else:
				print(f'Download fehlgeschlagen; url {url} existiert nicht')