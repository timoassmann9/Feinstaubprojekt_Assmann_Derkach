from calendar import monthrange
from datetime import datetime
import time
from csv import DictReader
import requests
import threading
import gzip
import shutil
import os
import sqlite3 as sql
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
from tkinter import filedialog
import numpy as np


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
		self.database_path = 'Feinstaubprojekt_Assmann_Derkach/feinstaubdaten.db'

		# Formatierung Variablen
		self.sensor_ID = str(self.sensor_ID)
		self.sensor_ID = self.sensor_ID.strip()

		self.start_year = int(self.start_year)
		self.end_year = int(self.end_year)
		self.start_month = int(self.start_month)
		self.end_month = int(self.end_month)

	def create_database_table(self):
		#Erstellt die Datenbanktabelle falls sie noch nicht existiert
		try:
			con = sql.connect(self.database_path)
			cur = con.cursor()
			
			cur.execute('''
				CREATE TABLE IF NOT EXISTS Feinstaubanalyse (
					UID TEXT PRIMARY KEY,
					SensorID TEXT,
					DatumZeit TEXT,
					PM2_5 REAL,
					PM10 REAL,
					Standort INTEGER,
					lat REAL,
					lon REAL
				)
			''')
			
			con.commit()
			con.close()
			print('Datenbanktabelle erstellt/überprüft')
			
		except Exception as e:
			print(f'Fehler beim Erstellen der Datenbanktabelle: {e}')

	def import_csv_to_database(self, csv_file_path):
		# Importiert eine CSV-Datei in die SQLite-Datenbank
		try:
			con = sql.connect(self.database_path)
			cur = con.cursor()
			
			file_name = os.path.basename(csv_file_path)
			imported_count = 0
			skipped_count = 0
			
			with open(csv_file_path, 'r', encoding='utf-8') as file:
				reader = DictReader(file, delimiter=';')
				count = 1
				
				for row in reader:
					try:
						sensor_id = row['sensor_id']
						datumzeit = row['timestamp']
						pm2_5 = float(row['P1']) if row['P1'] else None
						pm10 = float(row['P2']) if row['P2'] else None
						standort = int(row['location']) if row['location'] else None
						lat = float(row['lat']) if row['lat'] else None
						lon = float(row['lon']) if row['lon'] else None

						uid = f'{file_name}_{count}'

						# Prüfen, ob der Datensatz bereits existiert
						result_exists = cur.execute('SELECT 1 FROM Feinstaubanalyse WHERE UID = ?', (uid,)).fetchone()
						
						if result_exists is None:
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
							
							cur.execute('INSERT INTO Feinstaubanalyse VALUES(:UID, :SensorID, :DatumZeit, :PM2_5, :PM10, :Standort, :lat, :lon)', data)
							imported_count += 1
						else:
							skipped_count += 1

						count += 1
						
					except (ValueError, KeyError) as e:
						print(f'Fehler beim Verarbeiten von Zeile {count} in {file_name}: {e}')
						count += 1
			
			con.commit()
			con.close()
			
			print(f'Import von {file_name} abgeschlossen: {imported_count} neue Datensätze, {skipped_count} übersprungen')
			return imported_count, skipped_count
			
		except Exception as e:
			print(f'Fehler beim Importieren der Datei {csv_file_path}: {e}')
			return 0, 0

	def import_all_csv_files(self):
		# Importiert alle CSV-Dateien aus dem files-Ordner in die Datenbank
		files_directory = 'Feinstaubprojekt_Assmann_Derkach/files'
		
		if not os.path.exists(files_directory):
			print('Files-Verzeichnis existiert nicht')
			return 0, 0
		
		# Datenbanktabelle erstellen
		self.create_database_table()
		
		total_imported = 0
		total_skipped = 0
		processed_files = 0
		
		# Alle CSV-Dateien im Verzeichnis durchgehen
		for filename in os.listdir(files_directory):
			if filename.endswith('.csv'):
				file_path = os.path.join(files_directory, filename)
				imported, skipped = self.import_csv_to_database(file_path)
				total_imported += imported
				total_skipped += skipped
				processed_files += 1
		
		print(f'Gesamtimport abgeschlossen: {processed_files} Dateien verarbeitet, {total_imported} neue Datensätze importiert, {total_skipped} übersprungen')
		return total_imported, total_skipped

	def get_data_for_analysis(self):
    # Lädt die Daten aus der Datenbank für die Analyse
		try:
			con = sql.connect(self.database_path)
			
			# SQL-Query um Daten für den spezifischen Sensor und Zeitraum zu holen
			query = '''
			SELECT DatumZeit, PM2_5, PM10 
			FROM Feinstaubanalyse 
			WHERE SensorID = ? 
			AND DATE(DatumZeit) BETWEEN ? AND ?
			ORDER BY DatumZeit
			'''
			
			# Zeitraum-Strings erstellen
			start_date = f'{self.start_year}-{self.start_month:02d}-01'
			end_date = f'{self.end_year}-{self.end_month:02d}-31'
			
			df = pd.read_sql_query(query, con, params=(self.sensor_ID, start_date, end_date))
			con.close()
			
			# Datum-Spalte konvertieren
			df['DatumZeit'] = pd.to_datetime(df['DatumZeit'])
			
			# Null-Werte entfernen
			df = df.dropna()
			
			return df
			
		except Exception as e:
			print(f'Fehler beim Laden der Daten: {e}')
			return pd.DataFrame()

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

		# wenn directory 'files' noch nicht existiert, dann erstellen
		try:
			os.mkdir('Feinstaubprojekt_Assmann_Derkach/files')
			print('Directory "files" wurde erstellt')
		except FileExistsError:
			print('Directory "files" existiert bereits')
		except Exception as e:
			print(f'Ein Fehler ist aufgetreten: {e}')

		for url in self.urls:
			url_end = url.rfind('/')
			file_name = url[url_end:]
			file_Path = 'Feinstaubprojekt_Assmann_Derkach/files' + file_name
			file_path_unpacked = file_Path[:-3]
			if os.path.exists(file_Path) or os.path.exists(file_path_unpacked):
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
						with open(file_path_unpacked, 'wb') as f_out:
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

class AnalysisWindow:
    def __init__(self, parent, analytics_data):
        self.parent = parent
        self.analytics_data = analytics_data
        self.data = None
        
        # Neues Fenster erstellen
        self.window = tk.Toplevel(parent)
        self.window.title('Feinstaubdaten Analyse')
        self.window.geometry('1200x800')
        
        # Daten laden
        self.load_data()
        
        # GUI erstellen
        self.create_widgets()
        
        # Erstes Diagramm anzeigen
        self.update_plot()
    
    def load_data(self):
        # Lädt die Daten für die Analyse
        self.data = self.analytics_data.get_data_for_analysis()
        
        if self.data.empty:
            messagebox.showwarning('Warnung', 'Keine Daten für den ausgewählten Zeitraum gefunden!')
            self.window.destroy()
            return
    
    def create_widgets(self):
        # Erstellt die GUI-Elemente
        # Hauptframe
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Kontroll-Frame oben
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Diagrammtyp-Auswahl
        ttk.Label(control_frame, text='Diagrammtyp:').pack(side='left', padx=(0, 5))
        self.plot_type = tk.StringVar(value='line')
        plot_combo = ttk.Combobox(control_frame, textvariable=self.plot_type, 
                                 values=['line', 'scatter', 'bar', 'histogram'], 
                                 state='readonly', width=15)
        plot_combo.pack(side='left', padx=(0, 20))
        plot_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plot())
        
        # Parameter-Auswahl
        ttk.Label(control_frame, text='Parameter:').pack(side='left', padx=(0, 5))
        self.parameter = tk.StringVar(value='both')
        param_combo = ttk.Combobox(control_frame, textvariable=self.parameter,
                                  values=['both', 'PM2_5', 'PM10'],
                                  state='readonly', width=15)
        param_combo.pack(side='left', padx=(0, 20))
        param_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plot())
        
        # Export-Buttons
        ttk.Button(control_frame, text='Als PNG exportieren', 
                  command=self.export_png).pack(side='right', padx=(5, 0))
        ttk.Button(control_frame, text='Als PDF exportieren', 
                  command=self.export_pdf).pack(side='right', padx=(5, 0))
        
        # Matplotlib Figure und Canvas
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, main_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Toolbar für Zoom/Pan
        toolbar = NavigationToolbar2Tk(self.canvas, main_frame)
        toolbar.update()
        
        # Statistik-Frame unten
        stats_frame = ttk.LabelFrame(main_frame, text='Statistiken', padding=10)
        stats_frame.pack(fill='x', pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text='', font=('Arial', 10))
        self.stats_label.pack()
    
    def calculate_statistics(self):
        # Berechnet Statistiken für die Daten
        if self.data.empty:
            return 'Keine Daten verfügbar'
        
        stats_text = ''
        
        if self.parameter.get() == 'both' or self.parameter.get() == 'PM2_5':
            pm25_data = self.data['PM2_5'].dropna()
            if not pm25_data.empty:
                stats_text += f'PM2.5: Min={pm25_data.min():.2f}, Max={pm25_data.max():.2f}, '
                stats_text += f'Durchschnitt={pm25_data.mean():.2f}, Median={pm25_data.median():.2f}\n'
        
        if self.parameter.get() == 'both' or self.parameter.get() == 'PM10':
            pm10_data = self.data['PM10'].dropna()
            if not pm10_data.empty:
                stats_text += f'PM10: Min={pm10_data.min():.2f}, Max={pm10_data.max():.2f}, '
                stats_text += f'Durchschnitt={pm10_data.mean():.2f}, Median={pm10_data.median():.2f}'
        
        return stats_text
    
    def update_plot(self):
        # Aktualisiert das Diagramm
        if self.data.empty:
            return
        
        # Figure leeren
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        plot_type = self.plot_type.get()
        parameter = self.parameter.get()
        
        # Titel setzen
        sensor_id = self.analytics_data.sensor_ID
        start_date = f'{self.analytics_data.start_month}/{self.analytics_data.start_year}'
        end_date = f'{self.analytics_data.end_month}/{self.analytics_data.end_year}'
        title = f'Feinstaubdaten Sensor {sensor_id} ({start_date} - {end_date})'
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Daten plotten basierend auf Auswahl
        if plot_type == 'line':
            if parameter == 'both':
                ax.plot(self.data['DatumZeit'], self.data['PM2_5'], label='PM2.5', color='blue', alpha=0.7)
                ax.plot(self.data['DatumZeit'], self.data['PM10'], label='PM10', color='red', alpha=0.7)
            elif parameter == 'PM2_5':
                ax.plot(self.data['DatumZeit'], self.data['PM2_5'], label='PM2.5', color='blue')
            else:
                ax.plot(self.data['DatumZeit'], self.data['PM10'], label='PM10', color='red')
                
        elif plot_type == 'scatter':
            if parameter == 'both':
                ax.scatter(self.data['DatumZeit'], self.data['PM2_5'], label='PM2.5', color='blue', alpha=0.6, s=1)
                ax.scatter(self.data['DatumZeit'], self.data['PM10'], label='PM10', color='red', alpha=0.6, s=1)
            elif parameter == 'PM2_5':
                ax.scatter(self.data['DatumZeit'], self.data['PM2_5'], label='PM2.5', color='blue', s=1)
            else:
                ax.scatter(self.data['DatumZeit'], self.data['PM10'], label='PM10', color='red', s=1)
                
        elif plot_type == 'histogram':
            if parameter == 'both':
                ax.hist(self.data['PM2_5'].dropna(), bins=50, alpha=0.7, label='PM2.5', color='blue')
                ax.hist(self.data['PM10'].dropna(), bins=50, alpha=0.7, label='PM10', color='red')
                ax.set_xlabel('Konzentration (µg/m³)')
                ax.set_ylabel('Häufigkeit')
            elif parameter == 'PM2_5':
                ax.hist(self.data['PM2_5'].dropna(), bins=50, color='blue', label='PM2.5')
                ax.set_xlabel('PM2.5 Konzentration (µg/m³)')
                ax.set_ylabel('Häufigkeit')
            else:
                ax.hist(self.data['PM10'].dropna(), bins=50, color='red', label='PM10')
                ax.set_xlabel('PM10 Konzentration (µg/m³)')
                ax.set_ylabel('Häufigkeit')
                
        elif plot_type == 'bar':
            # Für Bar-Chart: Tagesdurchschnitte berechnen
            daily_data = self.data.copy()
            daily_data['Date'] = daily_data['DatumZeit'].dt.date
            daily_avg = daily_data.groupby('Date').agg({'PM2_5': 'mean', 'PM10': 'mean'}).reset_index()
            
            if parameter == 'both':
                x = np.arange(len(daily_avg))
                width = 0.35
                ax.bar(x - width/2, daily_avg['PM2_5'], width, label='PM2.5', color='blue', alpha=0.7)
                ax.bar(x + width/2, daily_avg['PM10'], width, label='PM10', color='red', alpha=0.7)
                ax.set_xticks(x[::max(1, len(x)//10)])  # Nur jeden 10. Tick anzeigen
                ax.set_xticklabels([str(d) for d in daily_avg['Date'].iloc[::max(1, len(daily_avg)//10)]], rotation=45)
            elif parameter == 'PM2_5':
                ax.bar(range(len(daily_avg)), daily_avg['PM2_5'], color='blue', label='PM2.5')
                ax.set_xticks(range(0, len(daily_avg), max(1, len(daily_avg)//10)))
                ax.set_xticklabels([str(d) for d in daily_avg['Date'].iloc[::max(1, len(daily_avg)//10)]], rotation=45)
            else:
                ax.bar(range(len(daily_avg)), daily_avg['PM10'], color='red', label='PM10')
                ax.set_xticks(range(0, len(daily_avg), max(1, len(daily_avg)//10)))
                ax.set_xticklabels([str(d) for d in daily_avg['Date'].iloc[::max(1, len(daily_avg)//10)]], rotation=45)
        
        # Achsenbeschriftungen und Legende (außer für Histogram)
        if plot_type != 'histogram' and plot_type != 'bar':
            ax.set_xlabel('Datum')
            ax.set_ylabel('Konzentration (µg/m³)')
            # X-Achse formatieren
            self.fig.autofmt_xdate()
        elif plot_type == 'bar':
            ax.set_xlabel('Datum')
            ax.set_ylabel('Tagesdurchschnitt (µg/m³)')
        
        # Legende hinzufügen
        if parameter == 'both' or plot_type == 'histogram':
            ax.legend()
        
        # Grid hinzufügen
        ax.grid(True, alpha=0.3)
        
        # Layout optimieren
        self.fig.tight_layout()
        
        # Canvas aktualisieren
        self.canvas.draw()
        
        # Statistiken aktualisieren
        self.stats_label.config(text=self.calculate_statistics())
    
    def export_png(self):
        # Exportiert das Diagramm als PNG
        filename = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG files', '*.png'), ('All files', '*.*')],
            title='PNG speichern unter...'
        )
        if filename:
            try:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo('Export', f'Diagramm erfolgreich als PNG gespeichert:\n{filename}')
            except Exception as e:
                messagebox.showerror('Fehler', f'Fehler beim Speichern der PNG-Datei:\n{str(e)}')
    
    def export_pdf(self):
        # Exportiert das Diagramm als PDF
        filename = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF files', '*.pdf'), ('All files', '*.*')],
            title='PDF speichern unter...'
        )
        if filename:
            try:
                self.fig.savefig(filename, format='pdf', bbox_inches='tight')
                messagebox.showinfo('Export', f'Diagramm erfolgreich als PDF gespeichert:\n{filename}')
            except Exception as e:
                messagebox.showerror('Fehler', f'Fehler beim Speichern der PDF-Datei:\n{str(e)}')

class GUI():
	def __init__(self):
		self.root = tk.Tk()
		self.root.title('Feinstaubdaten - Zeitraum auswählen')
		self.root.geometry('500x400')
		# self.root.resizable(False, False)

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
		
		self.sensor_entry_text = tk.StringVar()
		self.sensor_entry_text.trace_add('write', self.create_or_update_analytics_object_and_label)
		self.sensor_entry_text.trace_add('write', self.reset_status_label_and_download_button)
		self.sensor_entry = ttk.Entry(main_frame, width=30, textvariable=self.sensor_entry_text)
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
		self.start_year_combo.bind('<<ComboboxSelected>>', self.create_or_update_analytics_object_and_label, add='+')
		self.start_year_combo.bind('<<ComboboxSelected>>', self.reset_status_label_and_download_button, add='+')

		# Combobox Startmonat
		ttk.Label(start_frame, text='Monat:').grid(row=0, column=2, sticky='w', padx=(0, 5))
		self.start_month_combo = ttk.Combobox(start_frame, width=10, state='readonly')
		self.start_month_combo.grid(row=0, column=3, sticky='w')
		self.start_month_combo.bind('<<ComboboxSelected>>', self.create_or_update_analytics_object_and_label)
		self.start_month_combo.bind('<<ComboboxSelected>>', self.reset_status_label_and_download_button, add='+')

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
		self.end_year_combo.bind('<<ComboboxSelected>>', self.create_or_update_analytics_object_and_label, add='+')
		self.end_year_combo.bind('<<ComboboxSelected>>', self.reset_status_label_and_download_button, add='+')

		# Combobox Endmonat
		ttk.Label(end_frame, text='Monat:').grid(row=0, column=2, sticky='w', padx=(0, 5))
		self.end_month_combo = ttk.Combobox(end_frame, width=10, state='readonly')
		self.end_month_combo.grid(row=0, column=3, sticky='w')
		self.end_month_combo.bind('<<ComboboxSelected>>', self.create_or_update_analytics_object_and_label)
		self.end_month_combo.bind('<<ComboboxSelected>>', self.reset_status_label_and_download_button, add='+')

		# Objektstatus Frame
		object_frame = ttk.Labelframe(main_frame, text='Daten', padding=10)
		object_frame.grid(row=5, column=0, columnspan=1, sticky='ew', pady=(0, 5))

		self.analytics_label = ttk.Label(object_frame)
		self.analytics_label.grid(row=0, column=0, sticky='w')

		# Button Frame
		button_frame = ttk.Frame(main_frame)
		button_frame.grid(row=5, column=0, columnspan=2, pady=10)

		self.validate_button = ttk.Button(button_frame, text='Daten überprüfen', command=self.validate_input)
		self.validate_button.grid(row=0, column=1, sticky='nsew')

		self.download_button = ttk.Button(button_frame, text='Dateien herunterladen', command=self.download_data, state='disabled')
		self.download_button.grid(row=1, column=1, sticky='nsew')

		self.import_button = ttk.Button(button_frame, text='Datenbank aktualisieren', command=self.import_data, state='disabled')
		self.import_button.grid(row=2, column=1, sticky='nsew')

		self.analysis_button = ttk.Button(button_frame, text='Daten analysieren', command=self.open_analysis_window)
		self.analysis_button.grid(row=3, column=1, sticky='nsew')

		# Status Label
		self.status_label = ttk.Label(main_frame, text='Bereit für Eingabe', foreground='blue')
		self.status_label.grid(row=6, column=0, columnspan=2, pady=10)
		
		# Standard-Werte setzen
		self.start_year_combo.set('2023')
		self.end_year_combo.set('2023')
		self.start_month_combo.set('1')
		self.end_month_combo.set('12')

		# Monatslisten initialisieren
		self.update_month_combos()

	def reset_status_label_and_download_button(self, event, *args):
		# Setzt statuslabel und downloadbutton zurück, wenn Einträge geändert werden
		self.status_label.config(text='Bereit für Eingabe', foreground='blue')
		self.download_button.config(state='disabled')
		self.import_button.config(state='disabled')

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
		sensor_id = self.sensor_entry_text.get().strip()
		if not sensor_id or sensor_id == 'SensorID':
			self.status_label.config(text='Ungültige Werte', foreground='red')
			self.download_button.config(state='disabled')
			self.import_button.config(state='disabled')
			messagebox.showerror('Fehler', 'Bitte geben Sie eine gültige Sensor ID ein.')
			return False
		
		# Prüfen, ob alle Felder ausgefüllt sind
		if not all([self.start_year_combo.get(), self.start_month_combo.get(),
					self.end_year_combo.get(), self.end_month_combo.get()]):
			self.status_label.config(text='Ungültige Werte', foreground='red')
			self.download_button.config(state='disabled')
			self.import_button.config(state='disabled')
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
				self.status_label.config(text='Ungültige Werte', foreground='red')
				self.download_button.config(state='disabled')
				self.import_button.config(state='disabled')
				messagebox.showerror('Fehler', 'Das Startdatum darf nicht nach dem Enddatum liegen.')
				return False
			
			self.status_label.config(text='Bereit für Download', foreground='green')
			self.download_button.config(state='normal')

			# URLs generieren
			self.analytics_data.generate_urls()
			self.update_analytics_label()

		except ValueError:
			self.status_label.config(text='Ungültige Werte', foreground='red')
			self.download_button.config(state='disabled')
			self.import_button.config(state='disabled')
			messagebox.showerror('Fehler', 'Ungültige Datumswerte.')
			return False

	def create_or_update_analytics_object_and_label(self, event, *args):		
		try:
			sensor_id = self.sensor_entry_text.get().strip()
			start_year = int(self.start_year_combo.get())
			start_month = int(self.start_month_combo.get())
			end_year = int(self.end_year_combo.get())
			end_month = int(self.end_month_combo.get())
			
			# Analyticsdata Objekt erstellen/updaten
			self.analytics_data = Analyticsdata(sensor_id, start_year, end_year, start_month, end_month)
						
			self.update_analytics_label()
			
		except Exception as e:
			messagebox.showerror('Fehler', f'Fehler beim Erstellen des Objekts: {str(e)}')
			self.status_label.config(text='Fehler beim Erstellen des Objekts', foreground='red')

	def update_analytics_label(self):
		sensor_id = self.analytics_data.sensor_ID
		start_year = self.analytics_data.start_year
		start_month = self.analytics_data.start_month
		end_year = self.analytics_data.end_year
		end_month = self.analytics_data.end_month
		num_urls = len(self.analytics_data.urls)

		self.analytics_label.config(text=f'SensorID: {sensor_id}\nZeitraum: {start_month}/{start_year} - {end_month}/{end_year}\nAnzahl URLs: {num_urls}')
	
	def download_data(self):
		# Startet den Download der Daten
		if self.analytics_data is None:
			messagebox.showerror('Fehler', 'Erstellen Sie zuerst ein Analyseobjekt.')
			return
		
		try:
			self.status_label.config(text='Download läuft...', foreground='orange')
			self.download_button.config(state='disabled')
			self.validate_button.config(state='disabled')
			self.import_button.config(state='disabled')

			# Download in separatem Thread
			self.download_thread = threading.Thread(target=self.analytics_data.download_csv)
			self.download_thread.start()

			# Prüfen, ob der Thread noch läuft
			self.check_download_thread()
			
		except Exception as e:
			messagebox.showerror('Fehler', f'Fehler beim Download: {str(e)}')
			self.status_label.config(text='Download fehlgeschlagen', foreground='red')
			self.download_button.config(state='normal')
			self.validate_button.config(state='normal')
			self.import_button.config(state='disabled')

	def check_download_thread(self):
		if self.download_thread.is_alive():
			self.root.after(500, self.check_download_thread)
		else:
			self.status_label.config(text='Download abgeschlossen!', foreground='green')
			self.download_button.config(state='normal')
			self.validate_button.config(state='normal')
			self.import_button.config(state='normal')
			if self.analytics_data.downloads > 0:
				messagebox.showinfo('Download', f'{self.analytics_data.downloads} Dateien wurden erfolgreich heruntergeladen!')
			if self.analytics_data.downloads == 0:
				messagebox.showinfo('Download', f'Es wurden keine neuen Dateien heruntergeladen.')

	def import_data(self):
		# Startet den Import der CSV-Dateien in die Datenbank
		if self.analytics_data is None:
			messagebox.showerror('Fehler', 'Erstellen Sie zuerst ein Analyseobjekt.')
			return
		
		try:
			self.status_label.config(text='Import läuft...', foreground='orange')
			self.download_button.config(state='disabled')
			self.validate_button.config(state='disabled')
			self.import_button.config(state='disabled')

			# Import in separatem Thread
			self.import_thread = threading.Thread(target=self.run_import)
			self.import_thread.start()

			# Prüfen, ob der Thread noch läuft
			self.check_import_thread()
			
		except Exception as e:
			messagebox.showerror('Fehler', f'Fehler beim Import: {str(e)}')
			self.status_label.config(text='Import fehlgeschlagen', foreground='red')
			self.download_button.config(state='normal')
			self.validate_button.config(state='normal')
			self.import_button.config(state='normal')

	def run_import(self):
		# Führt den tatsächlichen Import aus (wird in separatem Thread ausgeführt)
		self.import_results = self.analytics_data.import_all_csv_files()

	def check_import_thread(self):
		if self.import_thread.is_alive():
			self.root.after(500, self.check_import_thread)
		else:
			self.status_label.config(text='Import abgeschlossen!', foreground='green')
			self.download_button.config(state='normal')
			self.validate_button.config(state='normal')
			self.import_button.config(state='normal')
			
			imported, skipped = self.import_results
			messagebox.showinfo('Import', f'Import abgeschlossen!\n{imported} neue Datensätze importiert\n{skipped} Datensätze übersprungen (bereits vorhanden)')

	def open_analysis_window(self):
		# Öffnet das Analysefenster
		if self.analytics_data is None:
			messagebox.showerror('Fehler', 'Erstellen Sie zuerst ein Analyseobjekt.')
			return
		
		# Prüfen ob Datenbank existiert
		if not os.path.exists(self.analytics_data.database_path):
			messagebox.showerror('Fehler', 'Datenbank nicht gefunden. Bitte erst Daten importieren.')
			return
		
		try:
			AnalysisWindow(self.root, self.analytics_data)
		except Exception as e:
			messagebox.showerror('Fehler', f'Fehler beim Öffnen des Analysefensters:\n{str(e)}')

GUI().root.mainloop()