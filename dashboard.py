import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os
import pandas as pd
from datetime import datetime
import time
import streamlit.components.v1 as components

# Configure page
st.set_page_config(page_title="Ranger Command Center", layout="wide")

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

st.title("Ranger Command Center")



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

# OUTSIDE LOOP - STATIC MAP ALERTS
alerts_for_map = get_alerts()

with col1:
    header_col1, header_col2 = st.columns([2.5, 1.5])
    with header_col1:
        st.markdown("### Live Node Map & Cluster View")
    with header_col2:
        # Dynamic Map Filter (Dropdown Selectbox)
        unique_threats = ["All"] + sorted(list(set(a["threat_class"] for a in alerts_for_map)))
        selected_filter = st.selectbox("Filter Map", unique_threats, label_visibility="collapsed")

        has_focus = False
        try:
            if hasattr(st, "query_params") and "focus_lat" in st.query_params: has_focus = True
            elif hasattr(st, "experimental_get_query_params") and "focus_lat" in st.experimental_get_query_params(): has_focus = True
        except: pass
        
        if has_focus:
            st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
            if st.button("Reset Map View", use_container_width=True):
                try:
                    if hasattr(st, "query_params"): st.query_params.clear()
                    else: st.experimental_set_query_params()
                except: pass
                st.session_state.is_dispatched = False
                st.rerun()

    # Handle Map Focus State
    # Secure iframe Sandbox Bridge (Pierces the Folium execution container for reporting) 
    components.html("""
    <script>
    const parentWin = window.parent;
    const parentDoc = parentWin.document;
    
    // Create the navigation relay button in the exact root Streamlit DOM to bypass the top-level navigation CSP rules completely
    let relayBtn = parentDoc.getElementById('sandbox-relay-btn');
    if (!relayBtn) {
        relayBtn = parentDoc.createElement('button');
        relayBtn.id = 'sandbox-relay-btn';
        relayBtn.style.display = 'none';
        parentDoc.body.appendChild(relayBtn);
    }

    if (!parentWin._dispatch_listener_added) {
        parentWin.addEventListener('message', function(event) {
            try {
                if (event.data && event.data.type === 'dispatch_report') {
                    // Assign the navigation command onto a raw HTML string. Native HTML attributes bypass CSP evaluation rules!
                    let command = "window.location.search = '?focus_lat=" + event.data.lat + "&focus_lon=" + event.data.lon + "&action=dispatch';";
                    relayBtn.setAttribute("onclick", command);
                    // Force a click on the root document level, entirely breaking the iframe sandbox jail!!
                    relayBtn.click();
                }
            } catch(e) {}
        });
        parentWin._dispatch_listener_added = true;
    }
    </script>
    """, height=0, width=0)

    center_lat, center_lon = 44.5, -110.5
    zoom_level = 11
    
    if has_focus:
        # Check for Native Streamlit Dispatch reporting action
        is_dispatch = False
        try:
            if hasattr(st, "query_params") and st.query_params.get("action") == "dispatch": is_dispatch = True
            elif hasattr(st, "experimental_get_query_params") and "dispatch" in st.experimental_get_query_params().get("action", []): is_dispatch = True
        except: pass

        if is_dispatch:
            # Native JS-injected Banner for precise absolute positioning and auto-close
            components.html("""
            <script>
            const doc = window.parent.document;
            const bannerId = "dispatch-success-banner";
            
            // Remove if already exists to prevent stacking
            if (doc.getElementById(bannerId)) {
                doc.getElementById(bannerId).remove();
            }
            
            const popup = doc.createElement('div');
            popup.id = bannerId;
            popup.style.cssText = "position: fixed; top: 100px; right: 30px; z-index: 99999; background: #161b22; padding: 15px 20px; border-radius: 10px; border: 1px solid #00ff88; box-shadow: 0px 4px 15px rgba(0, 255, 136, 0.2); display: flex; align-items: flex-start; gap: 15px; font-family: 'Inter', sans-serif; min-width: 250px; animation: slideInRight 0.4s ease-out;";
            
            popup.innerHTML = `
                <div style="flex-grow: 1;">
                    <div style="font-weight: bold; font-size: 14px; margin-bottom: 2px; color: white;">Threat Reported</div>
                    <div style="color: #c9d1d9; font-size: 12px;">Nearby officers alerted</div>
                </div>
                <button id="close-dispatch" style="background: none; border: none; color: #8b949e; cursor: pointer; font-size: 20px; padding: 0; line-height: 1; transition: color 0.2s;">&times;</button>
                <style>
                @keyframes slideInRight {
                    from { transform: translateX(120%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                </style>
            `;
            doc.body.appendChild(popup);
            
            // Allow manual close
            const closeBtn = doc.getElementById('close-dispatch');
            closeBtn.onmouseover = () => closeBtn.style.color = '#00ff88';
            closeBtn.onmouseout = () => closeBtn.style.color = '#8b949e';
            closeBtn.onclick = () => popup.remove();
            
            // Auto-close after 3 seconds
            setTimeout(() => {
                if (doc.getElementById(bannerId)) doc.getElementById(bannerId).remove();
            }, 3000);
            </script>
            """, height=0, width=0)

        try:
            if hasattr(st, "query_params"):
                center_lat = float(st.query_params["focus_lat"])
                center_lon = float(st.query_params["focus_lon"])
            else:
                center_lat = float(st.experimental_get_query_params()["focus_lat"][0])
                center_lon = float(st.experimental_get_query_params()["focus_lon"][0])
            zoom_level = 14  # Reduced zoom from 18 to 14 for better geographic context
        except Exception:
            has_focus = False

    # Create Folium Map with Default Tiles (Fixes black screen in remote areas)
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)
    
    # Infallible Sandbox JavaScript Bridge
    # This script resides directly within the Folium iframe. It uses a MutationObserver to 
    # bypass Leaflet's strict 'disableClickPropagation' layer which normally blocks document globals.
    bridge_script = """
    <script>
    const observer = new MutationObserver((mutations) => {
        const btn = document.getElementById('dispatch_report_btn');
        if (btn && !btn.hasAttribute('listener-added')) {
            btn.setAttribute('listener-added', 'true');
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                window.parent.postMessage({
                    type: 'dispatch_report',
                    lat: btn.getAttribute('data-lat'),
                    lon: btn.getAttribute('data-lon')
                }, '*');
            });
        }
    });
    observer.observe(document.body, {childList: true, subtree: true});
    </script>
    """
    m.get_root().html.add_child(folium.Element(bridge_script))
    
    # Plot recent alerts
    poaching_count_map = 0
    for a in alerts_for_map:
        is_threat = "Poaching" in a["threat_class"] or "Distress" in a["threat_class"]
        if is_threat: poaching_count_map += 1
        
        # If the map is zoomed into a specific focus, hide all generic markers
        if has_focus:
            continue
            
        # Apply the explicit user layout filter
        if selected_filter != "All" and a["threat_class"] != selected_filter:
            continue
        color = "red" if is_threat else ("orange" if "Disturbance" in a["threat_class"] else "green")
        icon = "crosshairs" if is_threat else "leaf"
        
        popup_content = f"<b>{a['threat_class']}</b><br>Confidence: {a['confidence']}<br>Coords: [{a['lat']:.4f}, {a['lon']:.4f}]"
        if is_threat:
            popup_content += f'<br><br><button id="dispatch_report_btn" data-lat="{a["lat"]}" data-lon="{a["lon"]}" onclick="window.parent.postMessage({{type:\'dispatch_report\', lat:{a["lat"]}, lon:{a["lon"]}}}, \'*\'); return false;" style="display:inline-block; padding: 5px 10px; background: #ff3366; color: white; border: none; border-radius: 4px; font-weight: bold; width: 100%; text-align: center; cursor: pointer;">Report</button>'
        
        folium.Marker(
            [a["lat"], a["lon"]],
            popup=popup_content,
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

    # Add massive highlight ring for the specific focused threat
    if has_focus:
        # Match the focused location with memory to retrieve its exact metadata
        focused_alert = next((a for a in alerts_for_map if abs(a["lat"] - center_lat) < 0.0001 and abs(a["lon"] - center_lon) < 0.0001), None)
        
        popup_html = "FOCUSED THREAT"
        if focused_alert:
            popup_html = f"<b>{focused_alert['threat_class']}</b><br>Conf: {focused_alert['confidence']}<br>[{focused_alert['lat']:.4f}, {focused_alert['lon']:.4f}]"
            popup_html += f'<br><br><button id="dispatch_report_btn" data-lat="{center_lat}" data-lon="{center_lon}" onclick="window.parent.postMessage({{type:\'dispatch_report\', lat:{center_lat}, lon:{center_lon}}}, \'*\'); return false;" style="display:inline-block; padding: 5px 10px; background: #ff3366; color: white; border: none; border-radius: 4px; font-weight: bold; width: 100%; text-align: center; cursor: pointer;">Report</button>'

        folium.CircleMarker(
            location=[center_lat, center_lon],
            radius=45,
            color="#00e5ff", # Bright cyan for contrast
            weight=5,
            fill=True,
            fillOpacity=0.2,
            popup=popup_html
        ).add_to(m)
        folium.Marker(
            [center_lat, center_lon],
            popup=popup_html,
            icon=folium.Icon(color="cyan", icon="info-sign")
        ).add_to(m)

    st_folium(m, width=900, height=500, returned_objects=[])

with col2:
    if 'auto_refresh_enabled' not in st.session_state:
        st.session_state.auto_refresh_enabled = True

    @st.fragment(run_every=3 if st.session_state.auto_refresh_enabled else None)
    def live_feed_panel():
        alerts = get_alerts()
        
        # Initialize session state for tracking new alerts
        if "last_alert_id" not in st.session_state:
            st.session_state.last_alert_id = None
        if "last_alert_timestamp" not in st.session_state:
            st.session_state.last_alert_timestamp = 0
            
        if alerts:
            latest_alert = alerts[0]
            current_alert_id = f"{latest_alert['timestamp']}_{latest_alert['lat']}_{latest_alert['lon']}"
            is_threat = "Poaching" in latest_alert["threat_class"] or "Distress" in latest_alert["threat_class"]
            
            if is_threat:
                # Check if it's a completely new threat
                if current_alert_id != st.session_state.last_alert_id:
                    st.session_state.last_alert_id = current_alert_id
                    st.session_state.last_alert_timestamp = time.time()
                    
                # Render the custom popup for up to 10 seconds using robust JS components injection
                time_elapsed = time.time() - st.session_state.last_alert_timestamp
                if time_elapsed <= 10:
                    components.html(
                        f"""
                        <script>
                        const doc = window.parent.document;
                        const alertId = "popup-{current_alert_id}";
                        
                        // Remove older custom popups if they exist
                        doc.querySelectorAll('.custom-st-popup').forEach(el => {{
                            if (el.id !== alertId) el.remove();
                        }});
                        
                        if (!sessionStorage.getItem('dismissed-{current_alert_id}') && !doc.getElementById(alertId)) {{
                            const popup = doc.createElement('div');
                            popup.id = alertId;
                            popup.className = 'custom-st-popup';
                            popup.style.cssText = "position: fixed; bottom: 30px; right: 30px; z-index: 99999; background: #161b22; padding: 15px 20px; border-radius: 10px; border: 1px solid #ff3366; box-shadow: 0px 4px 15px rgba(255, 51, 102, 0.4); display: flex; align-items: flex-start; gap: 15px; font-family: 'Inter', sans-serif; width: 330px; cursor: pointer; transition: transform 0.2s; animation: slideIn 0.4s ease-out;";
                            
                            popup.onmouseover = () => popup.style.transform = 'scale(1.02)';
                            popup.onmouseout = () => popup.style.transform = 'scale(1)';
                            
                            popup.innerHTML = `
                                <div style="flex-grow: 1;">
                                    <div style="color: #ff3366; font-weight: bold; font-size: 13px; margin-bottom: 5px;">THREAT DETECTED</div>
                                    <div style="color: #c9d1d9; font-size: 13px; line-height: 1.4;">
                                        <b style="color: white; font-size: 15px;">{latest_alert['threat_class']}</b><br>
                                        Conf: {latest_alert['confidence']*100:.1f}% | [{latest_alert['lat']:.2f}, {latest_alert['lon']:.2f}]<br>
                                        <span style="color: #44b5ff; font-size: 11px; margin-top:5px; display:inline-block;">Click to view</span>
                                    </div>
                                </div>
                                <button id="close-btn-{current_alert_id}" style="background: none; border: none; color: #8b949e; cursor: pointer; font-size: 22px; padding: 0; line-height: 1; transition: color 0.2s;">&times;</button>
                                <style>
                                @keyframes slideIn {{
                                  from {{ transform: translateX(120%); opacity: 0; }}
                                  to {{ transform: translateX(0); opacity: 1; }}
                                }}
                                </style>
                            `;
                            
                            // The redirection logic mapped safely onto the parent DOM avoiding Streamlit sandbox closures
                            popup.setAttribute("onclick", "if(event.target.tagName !== 'BUTTON') {{ window.scrollTo({{top: 0, behavior: 'smooth'}}); setTimeout(() => {{ window.location.assign('?focus_lat={latest_alert['lat']}&focus_lon={latest_alert['lon']}'); }}, 150); }}");
                            
                            doc.body.appendChild(popup);
                            
                            // Close button logic executing cleanly in parent origin context
                            const closeBtn = doc.getElementById('close-btn-{current_alert_id}');
                            closeBtn.onmouseover = () => closeBtn.style.color = '#ff3366';
                            closeBtn.onmouseout = () => closeBtn.style.color = '#8b949e';
                            closeBtn.setAttribute("onclick", "event.stopPropagation(); sessionStorage.setItem('dismissed-{current_alert_id}', 'true'); this.parentElement.remove();");
                        }}
                        
                        // Always assure it is removed when time's up
                        const msRemaining = {int(10000)};
                        setTimeout(() => {{
                            if (doc.getElementById(alertId)) doc.getElementById(alertId).remove();
                        }}, msRemaining);
                        </script>
                        """,
                        height=0,
                        width=0
                    )

        st.markdown("### System Status & Metrics")
        
        poaching_count = sum(1 for a in alerts if "Poaching" in a["threat_class"] or "Distress" in a["threat_class"])
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
        
        st.markdown("### Live Event Feed")
        feed_container = st.container(height=350)
        with feed_container:
            if not alerts:
                st.info("Awaiting sensor data... Start the `sensor_simulator.py` script.")
            for a in alerts:
                alert_color = "Critical:" if "Poaching" in a['threat_class'] or "Distress" in a['threat_class'] else "Normal:"
                st.markdown(f"""
                <a href="?focus_lat={a['lat']}&focus_lon={a['lon']}" target="_parent" style="text-decoration: none; color: inherit; display: block;">
                    <div style="border-left: 3px solid #3366ff; padding-left: 10px; padding-bottom: 5px; padding-top: 5px; margin-bottom: 10px; border-radius: 4px; transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='transparent'">
                        <small style="color: #8b949e;">{a['timestamp']} • {a['sensor_type']}</small><br>
                        <b>{alert_color} {a['threat_class']}</b><br>
                        <small>Conf: {int(a['confidence']*100)}% | Latency: {a['latency']}s  | Coords: [{a['lat']:.2f}, {a['lon']:.2f}]</small>
                    </div>
                </a>
                """, unsafe_allow_html=True)

        # Auto-refresh is gracefully handled by st.fragment(run_every=3) now preventing ghost elements

    live_feed_panel()

# Sync Controls
st.markdown("---")
cols = st.columns([1, 1, 2])
with cols[0]:
    if st.button("Sync Map Manually"):
        st.rerun()
with cols[1]:
    st.checkbox("Enable Live Auto-Sync for Feed", value=True, key="auto_refresh_enabled", help="Automatically refreshes the feed and metrics WITHOUT resetting the map view!")
