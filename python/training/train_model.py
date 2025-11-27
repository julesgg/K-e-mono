import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
from sklearn.model_selection import train_test_split


# Charger les données
df = pd.read_csv("data_sensor3.csv")
print(df.head())
print(df.info())
print(df.describe())

# Vérifier que les colonnes nécessaires sont présentes
if 'Resistance' not in df.columns or 'Timestamp' not in df.columns:
    raise ValueError("Le fichier doit contenir les colonnes 'Resistance' et 'Timestamp'.")

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

# Calcul de l'énergie (somme cumulée des carrés des variations)
df['Energy'] = df['ResistanceDiff'].pow(2).cumsum()

# Calcul de la fonction de Lagrange : L = 1/2 mv^2 - U (ici, mv^2 = ResistanceDiff^2 et U = Resistance)
df['Lagrange'] = (0.5 * df['ResistanceDiff'].pow(2)) - df['Resistance']

# # Moyenne et écart-type sur une fenêtre de 5 points
df['ResistanceRollingMean'] = df['Resistance'].rolling(window=5).mean().fillna(0)
df['ResistanceRollingStd'] = df['Resistance'].rolling(window=5).std().fillna(0)

saisie_data = df[df['ButtonState'] == 1]
mouvement_data = df[df['ButtonState'] == 0]

df['Label'] = df['ButtonState']

features = [ 'Resistance', 'ResistanceRollingMean', 'ResistanceRollingStd', 'ResistanceDiff', 'Energy']
            #  'ResistanceDiff', 'ResistanceRollingMean', 'ResistanceRollingStd', 'Lagrange']
X = df[features]
y = df['Label']

# Diviser les données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialiser le modèle
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Entraîner le modèle
model.fit(X_train.values, y_train)

# Évaluer le modèle
accuracy = model.score(X_test, y_test)
print(f"Précision du modèle : {accuracy*100:.2f}%")

# Sauvegarder le modèle entraîné
joblib.dump(model, 'sensor3_model.pkl')
print("Modèle sauvegardé dans 'sensor3_model.pkl'")
