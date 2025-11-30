#!/usr/bin/env bash
# start.sh - upgraded to be Render-safe while preserving original messages and ordering
set -euo pipefail

echo "🚀 Booting Chameleon Defense System..."

cleanup() {
    echo "🛑 Shutting down Chameleon Defense System..."
    # Try to gracefully kill known processes
    pkill -f "uvicorn dynamic_server:app" || true
    pkill -f "python -m core.proxy" || true
    pkill -f "python -m demo_scripts.hacker_bot" || true
    # fallback: kill children of this shell
    pkill -P $$ || true
    # give processes a moment
    sleep 0.3
}
trap cleanup SIGINT SIGTERM

export PYTHONUNBUFFERED=1

# Streamlit config directory
mkdir -p .streamlit
cat <<EOF > .streamlit/credentials.toml
[general]
email = ""
EOF

echo "🛠️ Generating initial mutation state..."
python -m core.mutator || true

RUNTIME_MUTATED="/tmp/active_server.py"
MUTATION_STATE="/tmp/mutation_state.json"

WAIT_SECONDS=0
MAX_WAIT=10
echo "[startup] Waiting for runtime mutated server at ${RUNTIME_MUTATED} ..."
while [ ! -f "$RUNTIME_MUTATED" ] && [ $WAIT_SECONDS -lt $MAX_WAIT ]; do
    sleep 0.5
    WAIT_SECONDS=$((WAIT_SECONDS+1))
done

if [ -f "$RUNTIME_MUTATED" ]; then
    echo "[startup] Found mutated runtime server after ${WAIT_SECONDS} checks."
else
    echo "[startup][warning] Mutated runtime server not found at ${RUNTIME_MUTATED}. Proceeding (nodes will retry load)."
fi

echo "⚙️ Starting Server Node A..."
python -m uvicorn dynamic_server:app --port 8001 --host 0.0.0.0 > /tmp/nodeA.log 2>&1 &

echo "⚙️ Starting Server Node B..."
python -m uvicorn dynamic_server:app --port 8002 --host 0.0.0.0 > /tmp/nodeB.log 2>&1 &

echo "⚙️ Starting Proxy..."
python -m core.proxy > /tmp/proxy.log 2>&1 &

echo "⏳ Waiting for subsystems to initialize..."
sleep 2

echo "🤖 Launching Hacker Bot..."
python -m demo_scripts.hacker_bot > /tmp/bot.log 2>&1 &
sleep 0.5

# tail logs to stdout so Render log viewer and container stdout show them
tail -F /tmp/nodeA.log /tmp/nodeB.log /tmp/proxy.log /tmp/bot.log > /tmp/combined_logs.log 2>&1 &
TAIL_PID=$!

# Start Streamlit in foreground but don't exec (so trap remains active). Wait for it.
PORT=${PORT:-10000}
echo "✅ Starting Dashboard on Port $PORT"

python -m streamlit run dashboard.py \
  --server.port $PORT \
  --server.enableCORS false \
  --server.address 0.0.0.0 \
  --server.headless true \
  --theme.base "dark" &

STREAMLIT_PID=$!

# Wait for streamlit; if it exits, cleanup will run via trap when the script terminates
wait "$STREAMLIT_PID"

# If streamlit stops, clean up tails and backgrounded processes
kill "$TAIL_PID" || true
cleanup
