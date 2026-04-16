import json
import time
import os
import random
import pickle
from datetime import datetime

MODEL_PATH = "edge_model.pkl"

class EdgeNodeClassifier:
    """
    Simulates a lightweight ML inference pipeline operating on a remote Raspberry Pi.
    """
    def __init__(self):
        self.model_size_mb = 0.0
        self.ensure_model()
    
    def ensure_model(self):
        # We simulate the < 50MB model requirement by dropping a 1MB dummy pickled model
        if not os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'wb') as f:
                f.write(os.urandom(1024 * 1024)) # 1MB dummy model
        
        self.model_size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)

    def analyze_audio(self, audio_file_path):
        """Simulates analyzing an audio file, measuring latency and returning classification."""
        start_time = time.time()
        
        # Simulate edge compute time (0.2 - 0.8 seconds on a Pi)
        time.sleep(random.uniform(0.2, 0.8))
        
        # We cheat in simulation by reading the file name for high F1 confidence demo
        lower_name = audio_file_path.lower()
        if "gun" in lower_name:
            threat = "Poaching (Gunshot)"
            confidence = random.uniform(0.88, 0.99)
        elif "chain" in lower_name:
            threat = "Poaching (Chainsaw)"
            confidence = random.uniform(0.86, 0.95)
        elif "wildlife" in lower_name:
            threat = "Background/Wildlife"
            confidence = random.uniform(0.90, 0.99)
        else:
            options = ["Poaching (Gunshot)", "Poaching (Chainsaw)", "Background/Wildlife", "Disturbance"]
            threat = random.choice(options)
            confidence = random.uniform(0.50, 0.85)

        end_time = time.time()
        latency = end_time - start_time
        
        return {
            "sensor_type": "Acoustic Node",
            "threat_classification": threat,
            "confidence": round(confidence, 2),
            "inference_latency_seconds": round(latency, 2),
            "model_size_mb": round(self.model_size_mb, 2)
        }

    def analyze_gps_anomaly(self, gps_payload):
        """Simulates analyzing GPS telemetry for distress/scattering patterns."""
        start_time = time.time()
        time.sleep(random.uniform(0.1, 0.3))
        
        threat = "Animal Distress (Scattering)" if "anomaly" in str(gps_payload).lower() else "Normal Movement"
        confidence = random.uniform(0.8, 0.95) if threat != "Normal Movement" else random.uniform(0.9, 0.99)
        
        latency = time.time() - start_time
        return {
            "sensor_type": "GPS Collar",
            "threat_classification": threat,
            "confidence": round(confidence, 2),
            "inference_latency_seconds": round(latency, 2),
            "model_size_mb": round(self.model_size_mb, 2)
        }

if __name__ == "__main__":
    edge = EdgeNodeClassifier()
    print("Edge Model Setup Complete.")
    print(f"Model Size: {edge.model_size_mb} MB")
