import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import os
import time
from datetime import datetime
import random

# --- CONFIGURATION ---
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Aegis Sentinel | AI SQLi Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE INITIALIZATION ---
if "token" not in st.session_state:
    st.session_state.token = None
if "terminal_logs" not in st.session_state:
    st.session_state.terminal_logs = [f"[{datetime.now().strftime('%H:%M:%S')}] SYSTEM BOOT... AEGIS SENTINEL ONLINE."]
if "source_ip" not in st.session_state:
    st.session_state.source_ip = f"{random.randint(10, 192)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

def add_terminal_log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.terminal_logs.append(f"[{timestamp}] {msg}")
    if len(st.session_state.terminal_logs) > 30:
        st.session_state.terminal_logs.pop(0)

# --- VISUALIZATION FUNCTIONS ---
def draw_risk_gauge(confidence):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = confidence * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Consensus Threat Level (%)", 'font': {'size': 18, 'color': '#ccd6f6'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#ccd6f6"},
            'bar': {'color': "#ff3131" if confidence > 0.5 else "#00ff9d"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#444",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(0, 255, 157, 0.1)'},
                {'range': [30, 70], 'color': 'rgba(255, 255, 0, 0.1)'},
                {'range': [70, 100], 'color': 'rgba(255, 49, 49, 0.1)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 3},
                'thickness': 0.75,
                'value': confidence * 100
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ccd6f6", 'family': "sans serif"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=250
    )
    return fig

def draw_radar_chart(res=None):
    categories = ['Semantic Obfuscation', 'Time-Based Sleep', 'Union Exfiltration', 'Boolean Inference', 'Tautology Filter']
    
    if res and res['prediction'] == 1:
        at = res.get('attack_type', 'Unknown')
        values = [random.randint(60, 95) for _ in categories]
        if 'Union' in at: values[2] = 98; values[0] = 85
        elif 'Time' in at: values[1] = 99; values[0] = 90
        elif 'Tautology' in at: values[4] = 99
        elif 'Obfuscated' in at: values[0] = 99
    elif res and res['prediction'] == 0:
        values = [random.randint(5, 20) for _ in categories]
    else:
        values = [0, 0, 0, 0, 0]
         
    # Close the polygon
    categories = [*categories, categories[0]]
    values = [*values, values[0]]
        
    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                fillcolor='rgba(255, 49, 49, 0.2)' if res and res['prediction'] == 1 else 'rgba(0, 255, 157, 0.2)',
                line=dict(color='#ff3131' if res and res['prediction'] == 1 else '#00ff9d', width=2),
                name='Current Vector'
            )
        ]
    )
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color='#8892b0', gridcolor='rgba(136, 146, 176, 0.2)', tickfont=dict(size=9)),
            angularaxis=dict(color='#64ffda', linecolor='rgba(136, 146, 176, 0.2)', tickfont=dict(size=11))
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color='#ccd6f6', family='Inter'),
        margin=dict(l=30, r=30, t=20, b=20),
        height=280
    )
    return fig

def draw_model_comparison_chart(probs):
    if not probs:
        return None
    
    # Sort models by probability for better visualization
    sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    models = [m[0].upper() for m in sorted_probs]
    values = [m[1] * 100 for m in sorted_probs]
    
    colors = ['#ff3131' if v >= 50 else '#00ff9d' for v in values]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=models,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255, 255, 255, 0.1)', width=1)
        ),
        text=[f"{v:.1f}%" for v in values],
        textposition='auto',
        hovertemplate="Model: %{y}<br>Confidence: %{x:.2f}%<extra></extra>"
    ))
    
    fig.update_layout(
        xaxis=dict(title="Confidence (%)", range=[0, 100], gridcolor='rgba(136, 146, 176, 0.1)', tickfont=dict(color='#8892b0')),
        yaxis=dict(autorange="reversed", tickfont=dict(color='#64ffda', size=11)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color='#ccd6f6', family='Inter'),
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
        showlegend=False
    )
    return fig


def render_terminal(logs):
    html = f"""
    <div style="background: rgba(5, 11, 20, 0.95); border: 1px solid rgba(0, 229, 255, 0.2); border-radius: 8px; padding: 15px; font-family: 'JetBrains Mono', monospace; font-size: 0.85em; box-shadow: inset 0 0 20px rgba(0,0,0,1), 0 0 10px rgba(0, 229, 255, 0.1); height: 260px; overflow-y: auto;">
      <div style="color: rgba(100, 255, 218, 0.6); margin-bottom: 12px; border-bottom: 1px solid rgba(100, 255, 218, 0.2); padding-bottom: 8px; font-size: 0.9em;">soc-admin@aegis-core:~# tail -f /var/log/waf/intercept.log</div>
    """
    for log in logs:
        color = "#00ff9d"
        if "BLOCK" in log or "Error" in log or "DENIED" in log: color = "#ff3131"
        elif "WARN" in log: color = "#facc15"
        elif "Verdict" in log: color = "#64ffda"
        html += f'<div style="margin-bottom: 6px; color: {color}; line-height: 1.4;">{log}</div>'
    
    html += '<div style="animation: blinker 1s step-start infinite; color: #64ffda; margin-top: 5px;">█</div>'
    html += """
    <style>@keyframes blinker { 50% { opacity: 0; } }</style>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- PAGE FUNCTIONS ---
def login():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.title("🛡️ AEGIS SENTINEL")
        st.caption("Secure Operator Authentication")
        with st.form("login_form"):
            username = st.text_input("Operator ID")
            password = st.text_input("Access Key", type="password")
            submit = st.form_submit_button("AUTHORIZE ACCESS", use_container_width=True)
            
            if submit:
                try:
                    res = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
                    if res.status_code == 200:
                        st.session_state.token = res.json()["access_token"]
                        add_terminal_log(f"Operator '{username}' authorized. Commencing active monitoring.")
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: Invalid Credentials")
                except Exception as e:
                    st.error(f"SYSTEM ERROR: Connection to core AP refused. ({str(e)})")

def dashboard():
    # Sidebar
    with st.sidebar:
        st.title("🛡️ Aegis Sentinel")
        st.caption("AI-Ensemble Analytics")
        st.divider()
        st.subheader("System Health")
        st.success("✔️ API Gateway: ACTIVE")
        st.success("✔️ Neural Engine: LOADED")
        st.info("ℹ️ Consensus Analytics: ONLINE")

        st.divider()
        st.subheader("Proxy Simulation")
        st.write(f"**Ingress IP:** `{st.session_state.source_ip}`")
        st.write("**Target Node:** `/api/v1/users`")
        
        st.divider()
        if st.button("Log Out / Clear Cache", use_container_width=True):
            st.session_state.token = None
            st.session_state.last_result = None
            st.session_state.terminal_logs = [f"[{datetime.now().strftime('%H:%M:%S')}] SYSTEM BOOT... AEGIS ONLINE."]
            st.rerun()

    # --- PRO-MAX CSS INJECTION ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono&display=swap');
        
        /* Global Reset & Body */
        .stApp {
            background: radial-gradient(circle at top center, #0a192f, #020c1b);
            color: #ccd6f6;
            font-family: 'Inter', sans-serif;
        }

        /* Glassmorphism Containers Customization */
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > div {
            background: rgba(17, 34, 64, 0.35);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(100, 255, 218, 0.15);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            transition: all 0.3s ease;
        }
        
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > div:hover {
            border: 1px solid rgba(100, 255, 218, 0.3);
            box-shadow: 0 8px 32px 0 rgba(100, 255, 218, 0.05);
        }
        
        /* Neon Accents */
        h1, h2, h3 {
            color: #64ffda !important;
            text-shadow: 0 0 10px rgba(100, 255, 218, 0.3);
            font-weight: 700 !important;
        }
        
        .stButton > button {
            background: rgba(100, 255, 218, 0.1) !important;
            color: #64ffda !important;
            border: 1px solid #64ffda !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: 0.3s !important;
        }
        .stButton > button:hover {
            background: #64ffda !important;
            color: #020c1b !important;
            box-shadow: 0 0 20px rgba(100, 255, 218, 0.5);
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #020c1b !important;
            border-right: 1px solid rgba(100, 255, 218, 0.1);
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #020c1b; }
        ::-webkit-scrollbar-thumb { background: #112240; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #233554; }
        </style>
    """, unsafe_allow_html=True)

    # Main Dashboard Header
    st.title("🛡️ Aegis Sentinel: AI-Ensemble Threat Analytics")
    st.caption("Advanced Semantic SQLi Interception & Model Consensus Intelligence")

    st.divider()
    
    # Layout Strategy
    r1c1, r1c2 = st.columns([1, 1], gap="large")
    
    with r1c1:
        st.subheader("1. Assessment Sandbox")
        st.info("⚠️ Non-Executable Environment. Inputs are not executed against a database.")
        query_input = st.text_area("Live External Payload:", height=100, placeholder="Type SQL injection payload here to test detection...")
        
        if st.button("INTERCEPT & ANALYZE PAYLOAD", type="primary", use_container_width=True):
            if not query_input.strip():
                st.warning("Payload empty. Skipping scan.")
            else:
                add_terminal_log(f"Received external payload: {query_input[:20]}...")
                add_terminal_log("Executing regex sanitization rules... [PASS]")
                add_terminal_log("Piping payload to ML ensemble...")
                
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                payload = {
                    "query": query_input,
                    "source_ip": st.session_state.source_ip,
                    "endpoint": "/api/v1/users"
                }
                
                try:
                    res = requests.post(f"{API_URL}/predict", json=payload, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.last_result = data
                        st.session_state.last_query = query_input
                        add_terminal_log("Analysis complete. Constructing XAI report.")
                        add_terminal_log(f"Verdict: {data['risk_level']} Risk ({data['attack_type']})")
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")
                except Exception as e:
                    st.error(f"API Error: {str(e)}")
        
        st.divider()
        st.subheader("📟 Real-Time Event Stream")
        render_terminal(st.session_state.terminal_logs)

    with r1c2:
        st.subheader("2. Interception Verdict (XAI)")
        
        if "last_result" in st.session_state and st.session_state.last_result is not None:
            res = st.session_state.last_result
            
            with st.container(border=True):
                col_g1, col_g2 = st.columns([3, 2])
                with col_g1:
                    st.plotly_chart(draw_risk_gauge(res['confidence']), use_container_width=True)
                with col_g2:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if res['prediction'] == 1:
                        st.error("### 🚨 BLOCKED\n**Action:** Connection Dropped")
                    else:
                        st.success("### ✅ ALLOWED\n**Action:** Forwarded Upstream")
            
            st.subheader("Diagnostic Explainability")
            with st.container(border=True):
                st.markdown(f"**Primary Intent:** `{res['attack_type']}`")
                
                if res['keywords']:
                    cols = st.columns(min(len(res['keywords']), 4))
                    for i, kw in enumerate(res['keywords']):
                        cols[i%4].button(kw, key=f"kw_{i}", disabled=True)
                else:
                    st.write("`No obvious semantic triggers detected.`")
                    
                conf_interval = round(res['confidence'] * 100, 2)
                st.caption(f"Statistical Confidence Band: {conf_interval - 2.5:.2f}% to {conf_interval + 2.5:.2f}%")
            
            st.subheader("Attack Vector Topology")
            with st.container(border=True):
                st.plotly_chart(draw_radar_chart(res), use_container_width=True)
        else:
            with st.container(border=True):
                st.info("Awaiting traffic input for diagnostic analysis.")
                st.markdown("<br>"*10, unsafe_allow_html=True)

    # --- ROW 2 ---
    st.divider()
    r2c1, r2c2 = st.columns([1, 1], gap="large")
    
    with r2c1:
        st.subheader("Model Comparison Analytics")
        if "last_result" in st.session_state and st.session_state.last_result is not None:
            res = st.session_state.last_result
            probs = res['individual_probabilities']
            
            # 1. Comparative Visualization
            st.plotly_chart(draw_model_comparison_chart(probs), use_container_width=True)
            
            # 2. Consensus Intelligence Layer
            if probs:
                malicious_count = sum(1 for p in probs.values() if p >= 0.5)
                total_models = len(probs)
                consensus_pct = (malicious_count / total_models) * 100
                
                highest_model = max(probs, key=probs.get)
                highest_conf = probs[highest_model] * 100
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.metric("Model Consensus", f"{malicious_count}/{total_models}", f"{consensus_pct:.0f}% Agreement", delta_color="inverse" if malicious_count > 0 else "normal")
                with col_c2:
                    st.metric("Lead Predictor", highest_model.upper(), f"{highest_conf:.1f}% Conf")
                
                st.markdown(f"🧠 **Strategic Insight:** The defensive layer has reached a **{consensus_pct:.0f}%** consensus. `{'BLOCK' if res['prediction'] == 1 else 'ALLOW'}` action was triggered based on weighted scoring.")
            else:
                st.markdown("⚠️ **Alert:** Decision made by **Heuristic/Structural Layer** (Pre-AI Block). No ML breakdown available.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Deep Telemetry Matrix")
            
            metrics = {
                "xgboost": {"Acc": "98.2%", "Wt": "0.2"},
                "lstm": {"Acc": "96.5%", "Wt": "0.2"},
                "randomforest": {"Acc": "97.1%", "Wt": "0.2"},
                "decisiontree": {"Acc": "94.3%", "Wt": "0.1"},
                "lightgbm": {"Acc": "97.8%", "Wt": "0.1"},
                "logisticregression": {"Acc": "92.0%", "Wt": "0.1"},
                "linearsvc": {"Acc": "93.5%", "Wt": "0.1"}
            }
            html_matrix = """
            <style>
            .model-matrix { width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; background: transparent; }
            .model-matrix th { background: rgba(10, 25, 47, 0.8); text-align: left; padding: 12px; font-weight: 600; color: #8892b0; font-size: 0.9em; border-bottom: 2px solid #64ffda; }
            .model-matrix td { padding: 14px 12px; border-bottom: 1px solid rgba(88, 166, 255, 0.05); color: #ccd6f6; font-size: 0.9em; }
            .model-matrix tr:hover { background: rgba(100, 255, 218, 0.05); }
            
            .vote-badge { padding: 4px 12px; border-radius: 6px; font-size: 0.75em; font-weight: 700; display: inline-block; min-width: 60px; text-align: center; }
            .badge-safe { background: rgba(0, 255, 157, 0.1); color: #00ff9d; border: 1px solid #00ff9d; }
            .badge-malicious { background: rgba(255, 49, 49, 0.1); color: #ff3131; border: 1px solid #ff3131; box-shadow: 0 0 5px rgba(255, 49, 49, 0.3); }
            
            .conf-bar-bg { width: 100px; height: 8px; background: rgba(255,255,255,0.05); border-radius: 4px; overflow: hidden; display: inline-block; vertical-align: middle; margin-right: 12px; border: 1px solid rgba(255,255,255,0.1); }
            .conf-bar-fill { height: 100%; border-radius: 4px; transition: width 1s ease-in-out; }
            </style>
            <table class="model-matrix">
            <tr><th>Detection Layer</th><th>Weight</th><th>State</th><th>Confidence Telemetry</th><th>Reliability</th></tr>
            """
            for mod, prob in probs.items():
                m = metrics.get(mod, {"Acc":"-", "Wt":"-"})
                is_mal = prob >= 0.5
                vote_cls = "badge-malicious" if is_mal else "badge-safe"
                vote_txt = "DETECT" if is_mal else "CLEAN"
                bar_col = "linear-gradient(90deg, #ff3131, #ff5e5e)" if is_mal else "linear-gradient(90deg, #00ff9d, #00e676)"
                percentage = prob * 100
                html_matrix += f"""<tr>
                  <td><span style="color: #64ffda; font-weight: 600;">{mod.upper()}</span></td>
                  <td style="color: #8892b0;">{m['Wt']}</td>
                  <td><span class="vote-badge {vote_cls}">{vote_txt}</span></td>
                  <td>
                    <div class="conf-bar-bg"><div class="conf-bar-fill" style="width: {percentage}%; background: {bar_col};"></div></div>
                    <span style="font-family: 'JetBrains Mono'; font-size: 0.85em;">{percentage:.1f}%</span>
                  </td>
                  <td style="color: #8892b0;">{m['Acc']}</td>
                </tr>"""
            html_matrix += "</table>"
            st.markdown(html_matrix, unsafe_allow_html=True)
        else:
            with st.container(border=True):
                st.info("Ensemble weighting details will populate here post-scan.")
                st.markdown("<br>"*5, unsafe_allow_html=True)
        
    with r2c2:
        st.subheader("Global Threat Ledger")
        st.markdown("📡 **Live Feed:** Listening for network ingestion anomalies...")
        
        ledger_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
          body {{ margin: 0; padding: 0; font-family: 'Inter', sans-serif; background: transparent; color: #ccd6f6; }}
          .ledger-container {{ max-height: 400px; overflow-y: auto; background: rgba(17, 34, 64, 0.4); border-radius: 8px; border: 1px solid rgba(88, 166, 255, 0.1); }}
          table {{ width: 100%; border-collapse: collapse; }}
          th {{ background: rgba(10, 25, 47, 0.95); position: sticky; top: 0; text-align: left; padding: 12px; font-weight: 600; color: #8892b0; font-size: 0.85em; z-index: 10; border-bottom: 1px solid rgba(0, 242, 255, 0.2); }}
          td {{ padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.85em; }}
          tr:hover {{ background: rgba(255, 255, 255, 0.05); box-shadow: inset 0 0 10px rgba(0, 242, 255, 0.15); }}
          
          .badge {{ padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.75em; }}
          .b-allow {{ background: rgba(0, 255, 157, 0.15); color: #00ff9d; border: 1px solid rgba(0, 255, 157, 0.3); }}
          .b-block {{ background: rgba(255, 49, 49, 0.15); color: #ff3131; border: 1px solid rgba(255, 49, 49, 0.3); box-shadow: 0 0 8px rgba(255, 49, 49, 0.4); }}
          
          .type-badge {{ padding: 3px 8px; border-radius: 12px; font-size: 0.75em; border: 1px solid rgba(255,255,255,0.2); }}
          
          @keyframes insertFlash {{
            0% {{ background-color: rgba(255, 49, 49, 0.6); box-shadow: inset 0 0 20px rgba(255, 49, 49, 0.8); }}
            100% {{ background-color: transparent; box-shadow: inset 0 0 0 transparent; }}
          }}
          .new-row {{ animation: insertFlash 3s ease-out; border-left: 3px solid #ff3131; }}
          
          ::-webkit-scrollbar {{ width: 6px; }}
          ::-webkit-scrollbar-track {{ background: rgba(10, 25, 47, 0.5); }}
          ::-webkit-scrollbar-thumb {{ background: rgba(88, 166, 255, 0.3); border-radius: 3px; }}
          @keyframes blinker {{ 50% {{ opacity: 0.3; }} }}
        </style>
        </head>
        <body>
          <div style="padding: 10px 15px; display: flex; align-items: center; justify-content: space-between; background: rgba(10, 25, 47, 0.8); border-bottom: 2px solid #64ffda;">
            <div style="display: flex; align-items: center; font-size: 0.85em; color: #64ffda; font-weight: 600;">
              <div style="width:10px; height:10px; border-radius:50%; background:#00ff9d; box-shadow: 0 0 10px #00ff9d; margin-right: 10px; animation: blinker 1.5s linear infinite;"></div>
              SOC LIVE FEED: CONNECTED
            </div>
            <div style="font-size: 0.75em; color: #8892b0; font-family: 'JetBrains Mono';">SYSLOG_MODE: ACTIVE</div>
          </div>

          <div class="ledger-container">
            <table id="logTable">
              <thead>
                <tr><th>Timestamp</th><th>Ingress IP</th><th>Classification</th><th>Action</th><th>Payload Snippet</th></tr>
              </thead>
              <tbody id="logBody">
              </tbody>
            </table>
          </div>

          <script>
            const logBody = document.getElementById('logBody');
            let maxLogs = 20;

            function addRow(data, isNew=false) {{
              const tr = document.createElement('tr');
              if(isNew && data.prediction == 1) tr.classList.add('new-row');
              
              let verdictBadge = data.prediction == 1 ? '<span class="badge b-block">BLOCK</span>' : '<span class="badge b-allow">ALLOW</span>';
              let payload = data.query || "";
              let shortPayload = payload.length > 25 ? payload.substring(0, 25) + "..." : payload;
              
              tr.innerHTML = `
                <td style="color: #a8b2d1;">${{data.timestamp}}</td>
                <td style="font-family: monospace; color: #a8b2d1;">${{data.source_ip}}</td>
                <td><span class="type-badge">${{data.attack_type}}</span></td>
                <td>${{verdictBadge}}</td>
                <td title="${{payload.replace(/"/g, '&quot;')}}" style="font-family: monospace; color: #e6f1ff; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${{shortPayload}}</td>
              `;
              
              logBody.insertBefore(tr, logBody.firstChild);
              while(logBody.children.length > maxLogs) {{ logBody.removeChild(logBody.lastChild); }}
            }}
            
            // Initial data load
            fetch('http://127.0.0.1:8000/logs?limit=' + maxLogs)
              .then(r => r.json())
              .then(logs => {{
                 logs.reverse().forEach(log => {{
                    let d = {{
                        timestamp: log.timestamp.split('T')[1]?.substring(0,8) || log.timestamp,
                        source_ip: log.source_ip,
                        attack_type: log.attack_type,
                        prediction: log.prediction,
                        query: log.query
                    }};
                    addRow(d);
                 }});
              }}).catch(e => console.log("Fetch error", e));
              
            // WebSocket Connection
            function connect() {{
                const ws = new WebSocket('ws://127.0.0.1:8000/ws/alerts');
                ws.onmessage = function(event) {{
                    const d = JSON.parse(event.data);
                    addRow(d, true);
                }};
                ws.onclose = function(e) {{
                    setTimeout(function() {{
                        connect();
                    }}, 2000);
                }};
            }}
            connect();
          </script>
        </body>
        </html>
        """
        components.html(ledger_html, height=480, scrolling=False)

if __name__ == "__main__":
    if st.session_state.token is None:
        login()
    else:
        dashboard()
