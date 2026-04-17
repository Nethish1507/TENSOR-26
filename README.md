# Ranger Command Center - TENSOR Project

An AI-powered wildlife conservation dashboard for detecting poaching and animal distress at the edge.

## 🚀 Deployment to Streamlit Community Cloud

This project is optimized for a zero-configuration deployment on Streamlit Cloud.

### Steps to Deploy:

1.  **GitHub:** Push this entire project to a public repository on GitHub.
2.  **Streamlit Cloud:** 
    - Sign in to [share.streamlit.io](https://share.streamlit.io/).
    - Click **"New app"**.
    - Select your repository, the main branch, and set the **Main file path** to `app.py`.
3.  **Launch:** Once deployed, the app will automatically start its internal sensor simulator, and you will see live alerts on the map instantly.

### Why app.py?
Streamlit Cloud requires the entry point to be in the root directory. `app.py` serves as the bridge to the dashboard logic located in the `frontend/` folder.

## 🛠️ Local Development

To run the dashboard locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 🧠 AI Simulation
The project includes an **Edge Inference Simulator** that mimics a Raspberry Pi running an XGBoost model. It processes acoustic data (gunshots/chainsaws) and GPS anomalies (scattering patterns) to alert rangers in real-time.
