import pandas as pd
import numpy as np
import joblib

# Dictionnaire pour les chemins des fichiers et des modèles
capteur_config = {
    1: {"data_file": "data_capteur1_filtered.csv", "model": "sensor_model_s1.pkl"},
    2: {"data_file": "data_capteur2_filtered.csv", "model": "sensor_model_s2.pkl"},
    3: {"data_file": "data_capteur3_filtered.csv", "model": "sensor_model_s3.pkl"},
    4: {"data_file": "data_capteur4_filtered.csv", "model": "sensor_model_s4.pkl"},
    5: {"data_file": "data_capteur5_filtered.csv", "model": "sensor_model_s5.pkl"},
}

# Résultat final pour le nombre de saisies
saisies_count = {}

# Traitement pour chaque capteur
for capteur_id, config in capteur_config.items():
    try:
        # Charger les données
        df = pd.read_csv(config["data_file"])
        print(f"Traitement des données pour le capteur {capteur_id}...")

        # Charger le modèle associé
        model = joblib.load(config["model"])

        # Vérifier que les colonnes nécessaires sont présentes
        if "Timestamp" not in df.columns or "Resistance" not in df.columns:
            raise ValueError("Le fichier doit contenir deux colonnes : 'Timestamp' et 'Resistance'.")

        # S'assurer que les colonnes sont bien de type numérique
        df['Resistance'] = pd.to_numeric(df['Resistance'], errors='coerce')
        df['Timestamp'] = pd.to_numeric(df['Timestamp'], errors='coerce')
        df = df.dropna(subset=['Resistance', 'Timestamp'])  # Supprimer les lignes avec des valeurs non numériques

        # Calcul des features
        # Calcul des dérivées temporelles (dR/dt)
        dR_dt = []
        timestamps = df['Timestamp'].values
        resistances = df['Resistance'].values

        for i in range(1, len(resistances)):
            delta_t = timestamps[i] - timestamps[i - 1]
            if delta_t != 0:  # Vérifier que le delta temps n'est pas zéro
                dR_dt.append((resistances[i] - resistances[i - 1]) / delta_t)
            else:
                dR_dt.append(0)  # Ajouter une valeur nulle si delta_t est zéro

        # Ajouter la dérivée au DataFrame, avec un décalage pour correspondre aux indices
        df['ResistanceDiff'] = [0] + dR_dt  # Ajouter un zéro au début pour conserver la taille

        # Énergie cumulative (somme des carrés des différences)
        df['Energy'] = df['ResistanceDiff'].pow(2).cumsum()

        # Moyenne et écart-type sur une fenêtre de 5 points
        df['ResistanceRollingMean'] = df['Resistance'].rolling(window=5).mean().fillna(0)
        df['ResistanceRollingStd'] = df['Resistance'].rolling(window=5).std().fillna(0)

        # Sélectionner les features utilisées pour la prédiction
        features = ['Resistance', 'ResistanceRollingMean', 'ResistanceRollingStd', 'ResistanceDiff', 'Energy']
        if not all(feature in df.columns for feature in features):
            raise ValueError("Certaines features nécessaires ne sont pas calculées correctement.")

        X = df[features]

        # Effectuer les prédictions
        df['Prediction'] = model.predict(X)

        # Ajouter une colonne interprétée pour indiquer le type (exemple : Saisie ou null)
        df['PredictionLabel'] = df['Prediction'].apply(lambda x: "Saisie" if x == 1 else "null")

        # Compter le nombre de saisies
        saisies_count[capteur_id] = (df['PredictionLabel'] == "Saisie").sum()

        # Sauvegarder les résultats
        output_file = f"data_capteur{capteur_id}_predictions.csv"
        df[['Timestamp', 'Resistance', 'PredictionLabel']].to_csv(output_file, index=False)
        print(f"Les prédictions pour le capteur {capteur_id} ont été enregistrées dans : {output_file}")

    except Exception as e:
        print(f"Erreur lors du traitement des données pour le capteur {capteur_id} : {e}")

# Afficher le nombre de saisies pour chaque capteur
print("\nNombre total de saisies détectées :")
for capteur_id, count in saisies_count.items():
    print(f"Capteur {capteur_id} : {count} saisies")
