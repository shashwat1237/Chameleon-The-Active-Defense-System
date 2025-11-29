#!/bin/bash
set -e

echo "🚀 Booting Chameleon Defense System..."

#############################################
# 1. CLEAN SHUTDOWN (Safe for Render)
#############################################
cleanup() {
    echo "🛑 Shutting down Chameleon Defense System..."
    pkill -P $$ || true
}
trap cleanup SIGINT SIGTERM

#############################################
# 2. STREAMLIT CONFIG
#############################################
mkdir -p .streamlit
cat <<EOF > .streamlit/credentials.toml
[general]
email = ""
EOF

#############################################
# 3. PRE-FLIGHT: Generate mutation
#############################################
echo "🛠️ Generating initial mutation state..."
python core/mutator.py

#############################################
# 4. START SERVERS (NO RELOAD IN PRODUCTION)
#############################################
echo "⚙️ Starting Server Node A..."
uvicorn target_app.active_server:app --port 8001 --host 0.0.0.0 > nodeA.log 2>&1 &

echo "⚙️ Starting Server Node B..."
uvicorn target_app.active_server:app --port 8002 --host 0.0.0.0 > nodeB.log 2>&1 &

echo "⚙️ Starting Proxy..."
python core/proxy.py > proxy.log 2>&1 &

#############################################
# 5. INITIALIZE BOT
#############################################
echo "⏳ Waiting for subsystems to initialize..."
sleep 5

echo "🤖 Launching Hacker Bot..."
python demo_scripts/hacker_bot.py > bot.log 2>&1 &

#############################################
# 6. START STREAMLIT DASHBOARD (FOREGROUND)
#############################################
echo "✅ Starting Dashboard on Port $PORT"

exec streamlit run dashboard.py \
    --server.port $PORT \
    --server.enableCORS false \
    --server.address 0.0.0.0 \
    --server.headless true \
    --theme.base "dark"
