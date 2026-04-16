import json
import time
import os
import random
from edge_inference import EdgeNodeClassifier

ALERTS_FILE = "live_alerts.json"
GPS_FILE = "live_gps.json"

edge_node = EdgeNodeClassifier()

base_lat, base_lon = 44.5, -110.5

def random_coordinate():
    return [base_lat + random.uniform(-0.02, 0.02), base_lon + random.uniform(-0.02, 0.02)]

def reset_files():
    with open(ALERTS_FILE, 'w') as f:
        json.dump([], f)
    
    # Initialize some random starting GPS locations for animals
    initial_gps = []
    for i in range(15):
        coord = random_coordinate()
        initial_gps.append({
            "id": f"Zebra-{i}",
            "lat": coord[0],
            "lon": coord[1],
            "status": "normal"
        })
    with open(GPS_FILE, 'w') as f:
        json.dump(initial_gps, f)

def simulate_event():
    event_type = random.choice(["audio", "gps", "audio", "audio", "gps"])
    
    if event_type == "audio":
        audio_choice = random.choice(["gun", "chainsaw", "wildlife", "wind"])
        print(f"Node detected audio: {audio_choice}.wav")
        # Send through inference
        result = edge_node.analyze_audio(f"virtual_fs/{audio_choice}.wav")
        coord = random_coordinate()
    else:
        print(f"Node detected GPS telemetry update.")
        result = edge_node.analyze_gps_anomaly({"status": "anomaly_movement"})
        # We make it anomalous a fraction of the time
        coord = random_coordinate()

    # Create Alert
    alert = {
        "timestamp": time.strftime('%H:%M:%S'),
        "lat": coord[0],
        "lon": coord[1],
        "sensor_type": result["sensor_type"],
        "threat_class": result["threat_classification"],
        "confidence": result["confidence"],
        "latency": result["inference_latency_seconds"],
        "model_mb": result["model_size_mb"]
    }
    
    # Read existing
    try:
        with open(ALERTS_FILE, 'r') as f:
            alerts = json.load(f)
    except:
        alerts = []
        
    alerts.insert(0, alert)  # Add to top
    alerts = alerts[:20]     # Keep last 20
    
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)

    return alert

if __name__ == "__main__":
    print("Starting Sensor Simulator...")
    reset_files()
    while True:
        # Random interval between events (3 to 10 seconds)
        sleep_time = random.uniform(3.0, 10.0)
        time.sleep(sleep_time)
        alert = simulate_event()
        print(f"Generated Alert -> {alert['threat_class']} @ {alert['confidence']*100}%")
