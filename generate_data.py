import wave
import math
import struct
import os
import random
import json

def create_wav(filename, freq=440.0, duration=1.0, is_noise=False):
    sample_rate = 44100
    obj = wave.open(filename, 'w')
    obj.setnchannels(1)
    obj.setsampwidth(2)
    obj.setframerate(sample_rate)

    for i in range(int(sample_rate * duration)):
        if is_noise:
            value = random.randint(-32767, 32767)
        else:
            # simple sine wave, simulate differing frequencies just for file headers
            value = int(32767.0 * math.sin(2.0 * math.pi * freq * (i / float(sample_rate))))
        
        data = struct.pack('<h', value)
        obj.writeframesraw(data)
    
    obj.close()

def generate_gps_telemetry(filename, num_records=50, anomaly=False):
    base_lat, base_lon = 44.5, -110.5  # Somewhere in Yellowstone
    records = []
    
    for i in range(num_records):
        lat = base_lat + random.uniform(-0.05, 0.05)
        lon = base_lon + random.uniform(-0.05, 0.05)
        
        if anomaly and i > num_records // 2:
            # Animal scattering! Rapid burst in one direction
            lat += 0.05 * (i - num_records//2)
            lon -= 0.05 * (i - num_records//2)
            
        records.append({
            "animal_id": f"COL-{random.randint(100, 999)}",
            "timestamp": f"2026-04-16T12:00:{i:02d}Z",
            "lat": lat,
            "lon": lon,
            "heart_rate_bpm": random.randint(60, 90) if not anomaly else random.randint(120, 180)
        })
        
    with open(filename, 'w') as f:
        json.dump(records, f, indent=2)

if __name__ == "__main__":
    test_dir = os.path.join(os.path.dirname(__file__), "test_data")
    os.makedirs(test_dir, exist_ok=True)
    
    print(f"Generating synthetic audio and telemetry in {test_dir}...")
    
    create_wav(os.path.join(test_dir, "gunshot_01.wav"), freq=150.0, duration=0.5, is_noise=True)
    create_wav(os.path.join(test_dir, "chainsaw_loop.wav"), freq=80.0, duration=2.0)
    create_wav(os.path.join(test_dir, "wildlife_birds.wav"), freq=1200.0, duration=3.0)
    
    generate_gps_telemetry(os.path.join(test_dir, "gps_normal.json"), num_records=20, anomaly=False)
    generate_gps_telemetry(os.path.join(test_dir, "gps_anomaly_distress.json"), num_records=20, anomaly=True)
    
    print("Done generated test files.")
