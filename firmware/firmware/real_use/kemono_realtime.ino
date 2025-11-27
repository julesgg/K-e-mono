// Définition des broches analogiques pour les capteurs
const int sensorPins[] = {A1, A2, A3, A4, A5}; // Capteurs connectés aux broches A1 à A5
const int numSensors = 5; // Nombre de capteurs
const float R_fixed = 9100.0; // Résistance fixe du pont diviseur (9.1kΩ)
const float V_in = 3.3; // Tension d'alimentation (3.3V)

// Tableau pour stocker les résistances calculées
float sensorResistances[numSensors];
unsigned long startTime;

void setup() {
  Serial.begin(9100); // Initialisation de la communication série
  while (!Serial) {
    ; // Attendre que le port série soit prêt
  }
  startTime = millis(); // Temps de départ pour l'horodatage
  Serial.println("Début de la collecte de données...");
}

void loop() {
  for (int i = 0; i < numSensors; i++) {
    // Lire la valeur analogique du capteur
    int sensorValue = analogRead(sensorPins[i]);

    // Convertir la valeur analogique en tension
    float V_out = sensorValue * (V_in / 1023.0);

    // Calculer la résistance du capteur
    float R_FSR = R_fixed * (V_in - V_out) / V_out;

    // Temps écoulé depuis le début de la collecte
    unsigned long currentTime = millis() - startTime;

    // Transmettre les données au format CSV
    // Format : "Capteur, Temps, Résistance"
    Serial.print(i + 1); // Numéro du capteur
    Serial.print(",");
    Serial.print(currentTime); // Temps en millisecondes
    Serial.print(",");
    Serial.println(R_FSR); // Résistance calculée en Ohms
  }

  delay(100); // Pause de 100 ms avant la prochaine lecture
}
