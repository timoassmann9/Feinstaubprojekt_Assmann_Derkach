from calendar import monthrange
from datetime import datetime
from csv import DictReader
import requests
import gzip
import shutil
import os
import sqlite3 as sql
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class Analyticsdata():
	def __init__(self, sensor_ID: str, start_year: int, end_year: int, start_month: int, end_month: int):
		self.sensor_type = 'sds011'
		self.sensor_ID = sensor_ID
		self.start_year = start_year
		self.end_year = end_year
		self.start_month = start_month
		self.end_month = end_month
		self.urls = []
		self.downloads = None

		# Formatierung Variablen
		self.sensor_ID = str(self.sensor_ID)
		self.sensor_ID = self.sensor_ID.strip()

		self.start_year = int(self.start_year)
		self.end_year = int(self.end_year)
		self.start_month = int(self.start_month)
		self.end_month = int(self.end_month)

	def generate_urls(self):
		# Datumsvariablen
		now = datetime.now()
		current_year = now.year
		current_month = now.month
		current_day = now.day

		# Prüfungen
		if (self.start_year or self.end_year) < 2015 or (self.start_year or self.end_year) > current_year:
			print('start_year und end_year muss zwischen 2015 und aktuellem Jahr sein')
			return

		if (self.start_month or self.end_month) < 1 or (self.start_month or self.end_month) > 12:
			print('start_month und end_month müssen zwischen 1 und 12 sein')
			return

		if self.end_year == current_year and self.end_month > current_month:
			print('end_month darf bei aktuellem Jahr nicht größer als der aktuelle Monat sein')
			return

		if self.start_year == 2015 and self.start_month < 10:
			print('start_month darf im Jahr 2015 nicht kleiner als 10 sein')
			return

		# Ausführen der Funktion
		self.urls = []
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
				for day in range(1, end_day + 1):
					if year > 2023:
						link = f'https://archive.sensor.community/{year}-{month:02d}-{day:02d}/{year}-{month:02d}-{day:02d}_{self.sensor_type}_sensor_{self.sensor_ID}.csv'
					if year <= 2023:
						link = f'https://archive.sensor.community/{year}/{year}-{month:02d}-{day:02d}/{year}-{month:02d}-{day:02d}_{self.sensor_type}_sensor_{self.sensor_ID}.csv.gz'
					self.urls.append(link)
		print(f'{len(self.urls)} urls generiert')

	def download_csv(self):
		self.downloads = 0

		for url in self.urls:
			url_end = url.rfind('/')
			file_name = url[url_end:]
			file_Path = 'Feinstaubprojekt_Assmann_Derkach/files' + file_name
			if os.path.exists(file_Path):
				print(f'Datei {file_name} existiert bereits')
				continue

			try:
				response = requests.get(url)
				response.raise_for_status()

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

				self.downloads += 1
				print(f'Datei {file_name} erfolgreich heruntergeladen')

			except requests.exceptions.HTTPError as http_err:
				print(f'HTTP-Fehler bei {url}: {http_err}')
			except requests.exceptions.ConnectionError as conn_err:
				print(f'Verbindungsfehler bei {url}: {conn_err}')
			except requests.exceptions.Timeout as timeout_err:
				print(f'Zeitüberschreitung bei {url}: {timeout_err}')
			except requests.exceptions.RequestException as req_err:
				print(f'Allgemeiner Fehler bei {url}: {req_err}')
			except Exception as e:
				print(f'Anderer Fehler bei {url}: {e}')

class EingabeGUI():
	def __init__(self):
		self.root = tk.Tk()
		self.root.title('Feinstaubdaten - Zeitraum auswählen')
		self.root.geometry('500x400')
		self.root.resizable(False, False)

		# Speicherung Analyticsdata object
		self.analytics_data = None

		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)

		# Hauptframe
		main_frame = ttk.Frame(self.root, padding=20)
		main_frame.grid(row=0, column=0, sticky='nsew')
		main_frame.columnconfigure(1, weight=1)

		# Titel
		title_label = ttk.Label(main_frame, text='Feinstaubdaten Analyse', font=('Arial', 16, 'bold'))
		title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

		# Eingabe SensorID
		ttk.Label(main_frame, text='SensorID', font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=(0, 5))
		
		self.sensor_entry = ttk.Entry(main_frame, width=30)
		self.sensor_entry.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(0, 20))

		# Startdatum Frame
		start_frame = ttk.Labelframe(main_frame, text='Startdatum', padding=10)
		start_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 10))
		start_frame.columnconfigure(1, weight=1)
		start_frame.rowconfigure(3, weight=1)

		# Combobox Startjahr
		ttk.Label(start_frame, text='Jahr:').grid(row=0, column=0, sticky='w', padx=(0, 5))
		self.start_year_combo = ttk.Combobox(start_frame, width=10, state='readonly')
		self.start_year_combo['values'] = [str(x) for x in range(2015, datetime.now().year + 1)]
		self.start_year_combo.grid(row=0, column=1, sticky='w', padx=(0, 15))
		self.start_year_combo.bind('<<ComboboxSelected>>', self.on_start_year_change)

		# Combobox Startmonat
		ttk.Label(start_frame, text='Monat:').grid(row=0, column=2, sticky='w', padx=(0, 5))
		self.start_month_combo = ttk.Combobox(start_frame, width=10, state='readonly')
		self.start_month_combo.grid(row=0, column=3, sticky='w')

		# Enddatum Frame
		end_frame = ttk.Labelframe(main_frame, text='Enddatum', padding=10)
		end_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(0, 10))
		end_frame.columnconfigure(1, weight=1)
		end_frame.rowconfigure(3, weight=1)

		# Combobox Endjahr
		ttk.Label(end_frame, text='Jahr:').grid(row=0, column=0, sticky='w', padx=(0, 5))
		self.end_year_combo = ttk.Combobox(end_frame, width=10, state='readonly')
		self.end_year_combo['values'] = [str(x) for x in range(2015, datetime.now().year + 1)]
		self.end_year_combo.grid(row=0, column=1, sticky='w', padx=(0, 15))
		self.end_year_combo.bind('<<ComboboxSelected>>', self.on_end_year_change)

		# Combobox Endmonat
		ttk.Label(end_frame, text='Monat:').grid(row=0, column=2, sticky='w', padx=(0, 5))
		self.end_month_combo = ttk.Combobox(end_frame, width=10, state='readonly')
		self.end_month_combo.grid(row=0, column=3, sticky='w')

		# Button Frame
		button_frame = ttk.Frame(main_frame)
		button_frame.grid(row=5, column=0, columnspan=2, pady=10)

		self.create_button = ttk.Button(button_frame, text='Analyseobjekt erstellen', command=self.create_analytics_object)
		self.create_button.grid(row=0, column=1, sticky='nsew')

		self.download_button = ttk.Button(button_frame, text='Daten herunterladen', command=self.download_data, state='disabled')
		self.download_button.grid(row=1, column=1, sticky='nsew')

		# Status Label
		self.status_label = ttk.Label(main_frame, text='Bereit für Eingabe', foreground='blue')
		self.status_label.grid(row=6, column=0, columnspan=2, pady=10)

		# Monatslisten initialisieren
		self.update_month_combos()
		
		# Standard-Werte setzen
		self.start_year_combo.set('2023')
		self.end_year_combo.set('2023')
		self.start_month_combo.set('1')
		self.end_month_combo.set('12')

	def update_month_combos(self):
		# Aktualisiert die Monat-Comboboxen basierend auf den ausgewählten Jahren
		current_year = datetime.now().year
		current_month = datetime.now().month

		start_year = self.start_year_combo.get()
		if start_year:
			if  int(start_year) == 2015:
				start_months = [str(x) for x in range(10, 13)]
			elif int(start_year) == current_year:
				start_months = [str(x) for x in range(1, current_month + 1)]
			else:
				start_months = [str(x) for x in range(1, 13)]
			self.start_month_combo['values'] = start_months

		end_year = self.end_year_combo.get()
		if end_year:
			if  int(end_year) == 2015:
				end_months = [str(x) for x in range(10, 13)]
			elif int(end_year) == current_year:
				end_months = [str(x) for x in range(1, current_month + 1)]
			else:
				end_months = [str(x) for x in range(1, 13)]
			self.end_month_combo['values'] = end_months

	def on_start_year_change(self, event):
		# Callback für die Änderung des Startjahres
		self.update_month_combos()
		if self.start_month_combo.get() not in self.start_month_combo['values']:
			if self.start_month_combo['values']:
				self.start_month_combo.set(self.start_month_combo['values'][0])

	def on_end_year_change(self, event):
		# Callback für die Änderung des Endjahres
		self.update_month_combos()
		if self.end_month_combo.get() not in self.end_month_combo['values']:
			if self.end_month_combo['values']:
				self.end_month_combo.set(self.end_month_combo['values'][0])

	def validate_input(self):
		# Validiert die Benutzereingaben
		# Sensor ID prüfen
		sensor_id = self.sensor_entry.get().strip()
		if not sensor_id or sensor_id == 'SensorID':
			messagebox.showerror('Fehler', 'Bitte geben Sie eine gültige Sensor ID ein.')
			return False
		
		# Prüfen, ob alle Felder ausgefüllt sind
		if not all([self.start_year_combo.get(), self.start_month_combo.get(),
					self.end_year_combo.get(), self.end_month_combo.get()]):
			messagebox.showerror('Fehler', 'Bitte füllen Sie alle Datumfelder aus.')
			return False
		
		# Datum-Logik prüfen
		try:
			start_year = int(self.start_year_combo.get())
			start_month = int(self.start_month_combo.get())
			end_year = int(self.end_year_combo.get())
			end_month = int(self.end_month_combo.get())
			
			# Startdatum darf nicht nach Enddatum liegen
			if start_year > end_year or (start_year == end_year and start_month > end_month):
				messagebox.showerror('Fehler', 'Das Startdatum darf nicht nach dem Enddatum liegen.')
				return False
			
			return True
			
		except ValueError:
			messagebox.showerror('Fehler', 'Ungültige Datumswerte.')
			return False

	def create_analytics_object(self):
		# Erstellt das analyticsdata Objekt nach Validierung
		if not self.validate_input():
			return
		
		try:
			sensor_id = self.sensor_entry.get().strip()
			start_year = int(self.start_year_combo.get())
			start_month = int(self.start_month_combo.get())
			end_year = int(self.end_year_combo.get())
			end_month = int(self.end_month_combo.get())
			
			# Analyticsdata Objekt erstellen
			self.analytics_data = Analyticsdata(sensor_id, start_year, end_year, start_month, end_month)
			
			# URLs generieren
			self.analytics_data.generate_urls()
			
			# Status aktualisieren
			self.status_label.config(text=f'Analyseobjekt erstellt für Sensor {sensor_id} '
									f'({start_month}/{start_year} - {end_month}/{end_year})', 
									foreground='green')
			
			# Download-Button aktivieren
			self.download_button.config(state='normal')
			
			messagebox.showinfo('Erfolg', 
							   f'Analyseobjekt erfolgreich erstellt!\n'
							   f'Sensor ID: {sensor_id}\n'
							   f'Zeitraum: {start_month}/{start_year} - {end_month}/{end_year}\n'
							   f'Anzahl URLs: {len(self.analytics_data.urls)}')
			
		except Exception as e:
			messagebox.showerror('Fehler', f'Fehler beim Erstellen des Objekts: {str(e)}')
			self.status_label.config(text='Fehler beim Erstellen des Objekts', foreground='red')
	
	def download_data(self):
		# Startet den Download der Daten
		if self.analytics_data is None:
			messagebox.showerror('Fehler', 'Erstellen Sie zuerst ein Analyseobjekt.')
			return
		
		try:
			self.status_label.config(text='Download läuft...', foreground='orange')
			self.download_button.config(state='disabled')
			self.create_button.config(state='disabled')
			
			# Download in separatem Thread wäre besser, aber für Einfachheit hier direkt
			self.analytics_data.download_csv()
			
			self.status_label.config(text='Download abgeschlossen!', foreground='green')
			messagebox.showinfo('Download', f'{self.analytics_data.downloads} Dateien wurden erfolgreich heruntergeladen!')
			
		except Exception as e:
			messagebox.showerror('Fehler', f'Fehler beim Download: {str(e)}')
			self.status_label.config(text='Download fehlgeschlagen', foreground='red')
		finally:
			self.download_button.config(state='normal')
			self.create_button.config(state='normal')

EingabeGUI().root.mainloop()