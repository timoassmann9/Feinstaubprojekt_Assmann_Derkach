from generate_urls import GenerateUrls
import requests
import gzip
import shutil
import os

url_list = GenerateUrls('sds011', 140, 2023, 2023, 1, 1)

# Download
for url in url_list:
    response = requests.get(url)
    url_end = url.rfind('/')
    file_name = url[url_end:]
    file_Path = 'Feinstaubprojekt_Assmann_Derkach' + file_name
    print(file_Path)

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
