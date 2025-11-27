import csv
import numpy as np

input_file_path = 'data_porte.csv'
output_file_path = 'data_porte_filtered_1dec2.csv'

def remove_duplicates_by_time(rows):
    """
    Supprime les doublons basés uniquement sur le timestamp (Time).
    Si plusieurs lignes ont le même timestamp, la première est conservée.
    """
    unique_rows = []
    seen_timestamps = set()  # Pour enregistrer les timestamps déjà rencontrés
    for row in rows:
        timestamp = float(row[0])  # Récupérer uniquement le timestamp
        if timestamp not in seen_timestamps:
            unique_rows.append(row)
            seen_timestamps.add(timestamp)  # Marquer ce timestamp comme traité
    return unique_rows

try:
    with open(input_file_path, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        headers = next(reader)  # Lire les en-têtes
        rows = []

        # Collecter les données pour le traitement
        for row in reader:
            if row:
                # Formater les timestamps et résistances
                timestamp = float(row[0]) - 1734023691
                resistance = float(row[1])
                state = int(float(row[2]))

                # Supprimer les doublons exacts
                rows = remove_duplicates_by_time(rows)

                # Arrondir à un chiffre après la virgule
                timestamp = round(timestamp, 1)
                resistance = round(resistance, 1)

                rows.append([timestamp, resistance, state])


        # Supprimer les valeurs incohérentes par écart-type
        resistances = [row[1] for row in rows]
        mean_resistance = np.mean(resistances)
        std_resistance = np.std(resistances)
        filtered_rows = [
            row for row in rows
            if abs(row[1] - mean_resistance) <= 3 * std_resistance
        ]

        # Gérer les transitions incohérentes entre séries
        cleaned_rows = []
        for i in range(len(filtered_rows) - 1):
            current_row = filtered_rows[i]
            next_row = filtered_rows[i + 1]

            # Si une transition d'état est détectée
            if current_row[2] != next_row[2]:
                # Vérifier si la transition est incohérente
                if abs(current_row[1] - next_row[1]) <= 3:
                    # Identifier la ligne incohérente
                    if abs(next_row[1] - mean_resistance) > abs(current_row[1] - mean_resistance):
                        continue  # Supprimer la ligne suivante
                    elif abs(current_row[1] - mean_resistance) > abs(next_row[1] - mean_resistance):
                        continue  # Supprimer la ligne actuelle

            # Ajouter la ligne si elle est valide
            cleaned_rows.append(current_row)

        # Ajouter la dernière ligne si elle n'est pas supprimée
        if len(filtered_rows) > 0:
            cleaned_rows.append(filtered_rows[-1])

    # Sauvegarder les données nettoyées
    with open(output_file_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(headers)  # Réécrire les en-têtes
        writer.writerows(cleaned_rows)  # Écrire les lignes nettoyées

    print(f"Le fichier filtré et nettoyé a été enregistré sous : {output_file_path}")

except FileNotFoundError:
    print(f"Le fichier '{input_file_path}' est introuvable.")
except ValueError:
    print("Erreur de conversion : vérifiez que les colonnes contiennent des nombres.")
except Exception as e:
    print(f"Une erreur est survenue : {e}")
