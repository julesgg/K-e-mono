// Définir les broches
const int sensorPin = A3;    // Broche du capteur de pression
const float R_fixed = 9100.0; // Résistance fixe du pont diviseur (9.1kΩ)
const float V_in = 3.3;      // Tension d'alimentation (3.3V)

// Variables
unsigned long startTime;     // Temps de démarrage
float resistance = 0.0;      // Résistance calculée
int buttonState = 0;         // État simulé par la touche du clavier

void setup() {
  // Initialisation de la communication série
  Serial.begin(9600);

  // Configurer les broches
  pinMode(sensorPin, INPUT);

  // Enregistrer l'heure de démarrage
  startTime = millis();

  Serial.println("Prêt. Appuyez sur 'p' pour indiquer une saisie, 'r' pour relâcher.");
}

void loop() {
  // Lire la valeur analogique du capteur
  int sensorValue = analogRead(sensorPin);

  // Convertir la valeur analogique en tension (0 à 3.3V)
  float V_out = sensorValue * (V_in / 1023.0);

  // Calculer la résistance du FSR
  if (V_out > 0) { // Éviter la division par zéro
    resistance = R_fixed * (V_in - V_out) / V_out;
  } else {
    resistance = 0; // Résistance indéfinie si V_out est 0
  }

  // Vérifier les données reçues via la connexion série
  if (Serial.available() > 0) {
    char input = Serial.read(); // Lire le caractère envoyé
    if (input == '1') {
      buttonState = 1; // Touche 'p' appuyée, bouton simulé en "pressé"
    } else if (input == '0') {
      buttonState = 0; // Touche 'r' appuyée, bouton simulé en "relâché"
    }
  }

  // Calculer le temps écoulé depuis le début
  unsigned long currentTime = millis();
  float elapsedTime = (currentTime - startTime) / 1000.0; // Convertir en secondes

  // Afficher les données dans le moniteur série
  Serial.print(elapsedTime, 2); // Temps écoulé avec 2 décimales
  Serial.print(", ");
  Serial.print(resistance, 2); // Résistance avec 2 décimales
  Serial.print(", ");
  Serial.println(buttonState); // État simulé par la touche

  delay(100); // Délai de 100 ms entre les mesures
}
