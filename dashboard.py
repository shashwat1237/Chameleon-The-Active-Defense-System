import streamlit as st
import graphviz
import time
import requests
import os
MUTATION_INTERVAL=30
st.set_page_config(page_title="CHAMELEON: Cloud Defense", layout="wide", page_icon="🦎")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #00ff41; font-family: 'Courier New'; }
    h1, h2, h3, .stMetricLabel { color: #00ff41 !important; }
    div.stMetric { border: 1px solid #333; padding: 10px; border-radius: 5px; background-color: #161b22; }
    .status-box { padding: 10px; border-radius: 5px; margin-bottom: 20px; font-weight: bold; }
    .success { background-color: #0f3d0f; border: 1px solid #00ff41; color: #00ff41; }
    .error { background-color: #3d0f0f; border: 1px solid #ff4b4b; color: #ff4b4b; }
</style>
""", unsafe_allow_html=True)

st.title("🦎 CHAMELEON: ACTIVE DECEPTION SYSTEM")

# Heartbeat Check
try:
    r = requests.get("http://127.0.0.1:8000/", timeout=2)
    status_html = f'<div class="status-box success">CLOUD STATUS: 🟢 OPERATIONAL | BACKEND: ONLINE</div>'
except:
    status_html = f'<div class="status-box error">CLOUD STATUS: 🔴 BOOTING DEFENSE ENGINE...</div>'
st.markdown(status_html, unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Runtime Topology")
    # [VERIFIED] Relies on 'apt-get install graphviz' in Dockerfile
    graph = graphviz.Digraph()
    graph.attr(bgcolor='#0e1117', rankdir='LR')
    graph.attr('node', style='filled', fontcolor='black', fontname='Courier')
    graph.attr('edge', color='white')

    timestamp = time.time()
    seconds = int(timestamp)
    cycle = (seconds // MUTATION_INTERVAL) % 2
    time_left = MUTATION_INTERVAL - (seconds % MUTATION_INTERVAL)
    
    graph.node('H', 'BOTNET\n(Internal)', fillcolor='#ff4b4b', fontcolor='white')
    graph.node('P', 'PROXY\n(Gateway)', fillcolor='#0078ff', fontcolor='white')

    if cycle == 0:
        graph.node('A', 'NODE A (8001)\n[ACTIVE]', fillcolor='#00ff41')
        graph.node('B', 'NODE B (8002)\n[MUTATING...]', fillcolor='#555555', fontcolor='white')
        graph.edge('P', 'A', color='#00ff41', penwidth='3')
        graph.edge('P', 'B', style='dashed', color='#555555')
    else:
        graph.node('A', 'NODE A (8001)\n[MUTATING...]', fillcolor='#555555', fontcolor='white')
        graph.node('B', 'NODE B (8002)\n[ACTIVE]', fillcolor='#00ff41')
        graph.edge('P', 'A', style='dashed', color='#555555')
        graph.edge('P', 'B', color='#00ff41', penwidth='3')

    if time_left < 6: 
        graph.edge('H', 'P', label='Replay Attack\n(Stale Token)', color='#ff4b4b', penwidth='2')
    else:
        graph.edge('H', 'P', label='Scanning...', color='white', style='dotted')
    
    st.graphviz_chart(graph, width="stretch")

with col2:
    st.subheader("Defense Telemetry")
    st.metric("NEXT MUTATION IN", f"{time_left} seconds")
    
    current_hash = hex(int(timestamp // MUTATION_INTERVAL))[2:8]
    st.text("CURRENT ROUTE MAP:")
    st.code(f"""
/admin/login  -> /admin/login_{current_hash}
/api/balance  -> /api/balance_{current_hash}
    """, language="bash")
    
    st.markdown("---")

    if time_left < 6:
        st.error("🚨 THREAT DETECTED: REPLAY ATTACK")
        st.warning("⚠️ HONEYPOT ACTIVATED")
        st.code("""
{
  "status": "TRAP_DOOR_ACTIVATED",
  "action": "LOGGING_IP_ADDRESS",
  "payload": "POISON_PILL_v9"
}
        """, language="json")
    else:
        st.success("✅ SYSTEM SECURE")
        st.write("Waiting for attack signature...")

time.sleep(1)
st.rerun()