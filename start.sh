#!/bin/bash
set -e

echo "🚀 Booting Chameleon Defense System..."

# Handles graceful shutdowns so the platform (Render/Docker/etc.) doesn’t leave orphan processes behind.
cleanup() {
    echo "🛑 Shutting down Chameleon Defense System..."
    pkill -P $$ || true
}
trap cleanup SIGINT SIGTERM

# Streamlit needs a credentials file even in headless mode.
# We create the directory manually to avoid permission issues inside containers.
mkdir -p .streamlit
cat <<EOF > .streamlit/credentials.toml
[general]
email = ""
EOF

# Before launching anything, generate the first mutation cycle so both nodes
# start with a consistent route map. Without this, the system would boot
# with stale or mismatched endpoints.
echo "🛠️ Generating initial mutation state..."
python core/mutator.py

# Start the two backend nodes. These run the same app but are intentionally
# started on different ports so the proxy can switch between them as the
# MTD cycle progresses.
echo "⚙️ Starting Server Node A..."
uvicorn target_app.active_server:app --port 8001 --host 0.0.0.0 > nodeA.log 2>&1 &

echo "⚙️ Starting Server Node B..."
uvicorn target_app.active_server:app --port 8002 --host 0.0.0.0 > nodeB.log 2>&1 &

# Launch the proxy that routes traffic to the correct node based on
# the mutation window. This is effectively the brains of the active switching logic.
echo "⚙️ Starting Proxy..."
python core/proxy.py > proxy.log 2>&1 &

# Give all subsystems a moment to warm up—Uvicorn, the proxy, and mutation state.
echo "⏳ Waiting for subsystems to initialize..."
sleep 5

# Launch the simulated attacker to continuously probe the system.
# It drives the telemetry panel and shows how attackers interact with mutated routes.
echo "🤖 Launching Hacker Bot..."
python demo_scripts/hacker_bot.py > bot.log 2>&1 &

# Start the Streamlit dashboard in the foreground so logs remain attached
# and the container behaves correctly on most hosting providers.
echo "✅ Starting Dashboard on Port $PORT"

exec streamlit run dashboard.py \
    --server.port $PORT \
    --server.enableCORS false \
    --server.address 0.0.0.0 \
    --server.headless true \
    --theme.base "dark"
