#!/bin/bash
set -e

# [VERIFIED] Cleanup function uses 'kill 0' to terminate the entire process group
cleanup() {
    echo "🛑 Shutting down Chameleon Defense System..."
    kill 0
    wait
}

trap cleanup SIGINT SIGTERM EXIT

echo "🚀 Booting Chameleon Defense System..."

# 0. PRE-FLIGHT: Configure Streamlit
mkdir -p .streamlit
echo '[general]
email = ""
' > .streamlit/credentials.toml

# [VERIFIED] CRITICAL STEP: Generate the server code BEFORE starting servers
echo "🛠️  Generating initial mutation state..."
python core/mutator.py

# 1. Start Server Node A (Background)
# [VERIFIED] --reload is enabled so the server updates when mutator.py runs
uvicorn target_app.active_server:app --port 8001 --host 0.0.0.0 --reload --reload-dir target_app &

# 2. Start Server Node B (Background)
uvicorn target_app.active_server:app --port 8002 --host 0.0.0.0 --reload --reload-dir target_app &

# 3. Start The Proxy (Background)
python core/proxy.py > proxy.log 2>&1 &

# 4. Stabilization Wait
echo "⏳ Waiting for subsystems to initialize..."
sleep 5

# 5. Start the Hacker Bot (Background)
python demo_scripts/hacker_bot.py > bot.log 2>&1 &

# 6. Start the Dashboard (Foreground)
# [VERIFIED] Runs in headless mode and binds to the correct Cloud Port
echo "✅ Starting Dashboard on Port $PORT"
streamlit run dashboard.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --theme.base "dark"