import serial
import csv
import threading
import time
import keyboard  # pip install keyboard

# Paramètres de connexion série
port = "COM5"  # Remplace par le port de ton Arduino
baudrate = 9600
timeout = 1

# Fichier CSV de sortie
output_file = "data_sensor.csv"

# Variable pour l'état du bouton
button_state = 0

def listen_for_keyboard():
    """
    Fonction exécutée dans un thread séparé pour écouter les pressions de touche.
    La touche '1' est utilisée pour indiquer que le bouton est pressé.
    """
    global button_state
    while True:
        if keyboard.is_pressed("1"):
            button_state = 1
        else:
            button_state = 0


# Démarrer un thread pour écouter les pressions de touches
keyboard_thread = threading.Thread(target=listen_for_keyboard, daemon=True)
keyboard_thread.start()

try:
    # Ouvrir la connexion série
    ser = serial.Serial(port, baudrate, timeout=timeout)
    time.sleep(2)  # Attendre que la connexion série soit établie

    print("Début de la réception des données...")
    print("Appuie sur 'b' pour indiquer que le bouton est pressé.")

    # Ouvrir le fichier CSV pour écrire les données
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Écrire l'en-tête
        writer.writerow(["Timestamp", "Resistance", "ButtonState"])

        while True:
            line = ser.readline().decode("utf-8").strip()
            if line:
                print(line)  # Afficher les données reçues pour le débogage
                try:
                    # Extraire les données du capteur (timestamp et résistance)
                    timestamp, resistance = line.split(",")
                    timestamp = float(timestamp)
                    resistance = float(resistance)

                    # Écrire les données dans le fichier CSV avec l'état du bouton
                    writer.writerow([timestamp, resistance, button_state])

                except ValueError:
                    print("Erreur de format dans les données reçues :", line)

except KeyboardInterrupt:
    print("Arrêt par l'utilisateur.")

finally:
    if ser.is_open:
        ser.close()
    print(f"Les données ont été enregistrées dans : {output_file}")
