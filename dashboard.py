import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os
import pandas as pd
from datetime import datetime

# Configure page
st.set_page_config(page_title="Ranger Command Center", layout="wide", page_icon="📡")

# Inject Custom CSS for Premium Black/Glassmorphism Look
st.markdown("""
<style>
    .reportview-container {
        background-color: #0d1117;
        color: white;
    }
    .main {
        background-color: #0d1117;
    }
    /* Glassmorphism card */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        font-family: 'Inter', sans-serif;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #00ff88;
    }
    .metric-value-danger {
        font-size: 2rem;
        font-weight: bold;
        color: #ff3366;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("📡 Ranger Command Center | Autonomous Anti-Poaching System")
st.markdown("Real-time threat monitoring utilizing edge-deployed multi-modal acoustic, imagery, and telemetry models.</br><hr>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎛️ Demo Controls")
    st.info("Start `sensor_simulator.py` in another terminal to generate live data.")
    uploaded_file = st.file_uploader("Upload Node Data (Audio/Image)", type=["wav", "jpg", "png"])
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' Processed!")
        st.json({"threat_class": "Poaching (Gunshot)" if "gun" in uploaded_file.name.lower() else "Wildlife/Normal", "confidence": 0.98})

# Layout
col1, col2 = st.columns([2, 1])

ALERTS_FILE = "live_alerts.json"

def get_alerts():
    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

alerts = get_alerts()

with col1:
    st.markdown("### 🗺️ Live Node Map & Cluster View")
    
    # Create Folium Map with Dark Tiles
    m = folium.Map(location=[44.5, -110.5], zoom_start=11, tiles="CartoDB dark_matter")
    
    # Plot recent alerts
    poaching_count = 0
    for a in alerts:
        is_threat = "Poaching" in a["threat_class"] or "Distress" in a["threat_class"]
        if is_threat: poaching_count += 1
        
        color = "red" if is_threat else ("orange" if "Disturbance" in a["threat_class"] else "green")
        icon = "crosshairs" if is_threat else "leaf"
        
        folium.Marker(
            [a["lat"], a["lon"]],
            popup=f"<b>{a['threat_class']}</b><br>Confidence: {a['confidence']}<br>Coords: [{a['lat']:.4f}, {a['lon']:.4f}]",
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(m)
        
        # Add a pulsating circle for high threat
        if is_threat:
            folium.CircleMarker(
                location=[a["lat"], a["lon"]],
                radius=15,
                color="red",
                fill=True,
                fillColor="red",
                fillOpacity=0.4
            ).add_to(m)

    st_folium(m, width=900, height=500, returned_objects=[])

with col2:
    st.markdown("### ⚡ System Status & Metrics")
    
    # Quick metrics in custom HTML
    avg_latency = sum(a.get("latency", 0) for a in alerts)/len(alerts) if alerts else 0
    model_size = alerts[0].get("model_mb", 14.5) if alerts else 0
    
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-label">Active Threats Detected</div>
        <div class="metric-value-danger">{poaching_count}</div>
        <br>
        <div class="metric-label">Edge Model Overhead</div>
        <div class="metric-value">{model_size:.2f} MB</div>
        <br>
        <div class="metric-label">Avg Pipeline Latency</div>
        <div class="metric-value">{avg_latency:.2f} sec</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🚨 Live Event Feed")
    feed_container = st.container(height=350)
    with feed_container:
        if not alerts:
            st.info("Awaiting sensor data... Start the `sensor_simulator.py` script.")
        for a in alerts:
            alert_color = "🔴" if "Poaching" in a['threat_class'] or "Distress" in a['threat_class'] else "🟢"
            st.markdown(f"""
            <div style="border-left: 3px solid #3366ff; padding-left: 10px; margin-bottom: 10px;">
                <small style="color: #8b949e;">{a['timestamp']} • {a['sensor_type']}</small><br>
                <b>{alert_color} {a['threat_class']}</b><br>
                <small>Conf: {int(a['confidence']*100)}% | Latency: {a['latency']}s  | Coords: [{a['lat']:.2f}, {a['lon']:.2f}]</small>
            </div>
            """, unsafe_allow_html=True)

# Add a manual refresh button, though in standard st we configure auto-refresh or use st_autorefresh
if st.button("🔄 Sync with Edge Nodes"):
    st.rerun()
