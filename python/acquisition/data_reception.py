import serial
import csv
import numpy as np
import math
import time
import os  # Pour gérer le fichier d'arrêt

# Paramètres de connexion série
port = "COM5"  # Remplace par le port de ton Arduino
baudrate = 9600
timeout = 1

# Fichiers CSV pour chaque capteur
sensor_files = {
    1: 'data_capteur1_filtered.csv',
    2: 'data_capteur2_filtered.csv',
    3: 'data_capteur3_filtered.csv',
    4: 'data_capteur4_filtered.csv',
    5: 'data_capteur5_filtered.csv'
}

# Nom du fichier signal d'arrêt
stop_signal_file = "stop_signal.txt"

def remove_duplicates_by_time(rows):
    unique_rows = []
    seen_timestamps = set()
    for row in rows:
        timestamp = row[0]
        if timestamp not in seen_timestamps:
            unique_rows.append(row)
            seen_timestamps.add(timestamp)
    return unique_rows

def filter_by_std_dev(rows):
    resistances = [row[1] for row in rows]
    mean_resistance = np.mean(resistances)
    std_resistance = np.std(resistances)
    return [
        row for row in rows
        if abs(row[1] - mean_resistance) <= 3 * std_resistance
    ]

try:
    # Ouvrir la connexion série
    ser = serial.Serial(port, baudrate, timeout=timeout)
    time.sleep(2)  # Attendre que la connexion s'établisse

    print("Début de la réception des données...")

    # Fichiers pour écrire les données
    file_handlers = {key: open(filename, mode='w', newline='') for key, filename in sensor_files.items()}
    csv_writers = {key: csv.writer(fh) for key, fh in file_handlers.items()}

    # Écrire les en-têtes pour chaque fichier
    for writer in csv_writers.values():
        writer.writerow(["Timestamp", "Resistance"])

    # Dictionnaire pour stocker temporairement les données par capteur
    data_buffer = {key: [] for key in sensor_files.keys()}

    while True:
        # Vérifier si le fichier d'arrêt existe
        if os.path.exists(stop_signal_file):
            print("Signal d'arrêt détecté. Arrêt de la réception des données.")
            break

        line = ser.readline().decode('utf-8').strip()
        if line:
            print(line)  # Afficher les données reçues pour le débogage
            try:
                # Extraire les données : Capteur, Temps, Résistance
                sensor_id, timestamp, resistance = line.split(',')
                sensor_id = int(sensor_id)
                timestamp = float(timestamp)
                resistance = float(resistance)

                # Filtrer les valeurs infinies ou non finies
                if not math.isfinite(resistance):
                    print(f"Valeur infinie ou non valide ignorée : {line}")
                    continue

                # Ajouter la donnée au buffer du capteur correspondant
                if sensor_id in data_buffer:
                    data_buffer[sensor_id].append([timestamp, resistance])

            except ValueError:
                print("Erreur de format dans les données reçues :", line)

        # Traiter les données tous les 100 lignes
        for sensor_id, rows in data_buffer.items():
            if len(rows) >= 100:
                # Supprimer les doublons
                rows = remove_duplicates_by_time(rows)

                # Supprimer les valeurs incohérentes par rapport à l'écart-type
                rows = filter_by_std_dev(rows)

                # Convertir les timestamps et résistances en entiers (après vérification)
                rows = [[int(ts), int(r)] for ts, r in rows if math.isfinite(r)]

                # Écrire les données filtrées dans le fichier CSV correspondant
                csv_writers[sensor_id].writerows(rows)

                # Vider le buffer pour ce capteur
                data_buffer[sensor_id] = []

except KeyboardInterrupt:
    print("Arrêt par l'utilisateur.")

finally:
    # Traiter les données restantes dans le buffer
    for sensor_id, rows in data_buffer.items():
        if rows:
            rows = remove_duplicates_by_time(rows)
            rows = filter_by_std_dev(rows)
            rows = [[int(ts), int(r)] for ts, r in rows if math.isfinite(r)]
            csv_writers[sensor_id].writerows(rows)

    # Fermer les fichiers et la connexion série
    for fh in file_handlers.values():
        fh.close()
    ser.close()
    print("Fin de la réception des données.")

    # Supprimer le fichier d'arrêt
    if os.path.exists(stop_signal_file):
        os.remove(stop_signal_file)
        print(f"Fichier signal '{stop_signal_file}' supprimé.")
