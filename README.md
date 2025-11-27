# 🥋 K’e-mono — Smart kimono with e-textile Pressure Sensors & ML Grip Detection

K’e-mono is a smart judo kimono integrating resistive e-textile pressure sensors and a machine-learning pipeline able to detect kumi-kata (grips) in real time.  
The system was developed as part of a research project on performance enhancement through smart textiles, embedded electronics, and signal processing.

---

## 🔧 System Overview

### 1. Textile Sensors
Custom-made textile pressure sensors built with:
- EeonTex piezoresistive fabric  
- Madeira HC40 conductive thread  
- Denim textile support  
- Interdigitated electrode stitched pattern  
- Pressure measured through resistance variation  

### 2. Electronic Module
- **Arduino Nano 33 BLE**
- Simultaneous reading of **5 resistive sensors** (voltage divider)
- Sampling rate: **10 Hz**
- Bluetooth Low Energy streaming to a Python interface

### 3. Machine Learning Pipeline
Each sensor has its own dedicated ML model:
- 5-minute dataset per sensor with manual button annotation (1 = grip, 0 = no grip)
- Preprocessing and filtering
- Feature extraction (variance, derivative, slope, etc.)
- Individual Random Forest model for each sensor
- Real-time inference during judo training

---

## 📁 Repository Structure
```
K-e-mono/
│
├── firmware/
│   ├── training_mode/          # One-sensor dataset recording + button label
│   └── real_use/               # Five-sensor BLE streaming during real training
│
├── python/
│   ├── acquisition/            # BLE data reception
│   ├── training/               # Data formatting, filtering, and ML training
│   ├── inference/              # Real-time grip detection + visualization
│   └── utils/                  # Optional mathematical and plotting utilities
│
└── data/
    ├── raw/                    # Example raw datasets
    ├── processed/              # Filtered / windowed datasets
    └── models/                 # Trained Random Forest models (sensor_model_sX.pkl)

```

🚀 How to Use

**Training Mode (dataset creation)**

Flash:
firmware/training_mode/kemono_training.ino

Record data:
python python/training/collecte_train.py

Preprocess:
python python/training/format_data.py

Train ML models:
python python/training/train_model.py

Trained models are stored in the data/models folder.

**Real-Use Mode (live grip detection)**

Flash:
firmware/real_use/kemono_realtime.ino

Launch the interface:
python python/inference/app.py

Displays:
Grip detection
Grip repartition

👤 Author
Developed by Jules Gueguen (2024-2025).
Smart textiles • Embedded electronics • Machine learning • Sports performance analysis.
