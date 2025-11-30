#!/usr/bin/env bash
# start.sh - Path fix applied
set -euo pipefail

echo "🚀 Booting Chameleon Defense System..."

cleanup() {
    echo "🛑 Shutting down Chameleon Defense System..."
    pkill -f "uvicorn dynamic_server:app" |

| true
    pkill -f "python -m core.proxy" |

| true
    pkill -f "python -m demo_scripts.hacker_bot" |

| true
    pkill -P $$ |

| true
    sleep 0.3
}
trap cleanup SIGINT SIGTERM

export PYTHONUNBUFFERED=1

# Streamlit config
mkdir -p.streamlit
cat <<EOF >.streamlit/credentials.toml
[general]
email = ""
EOF

echo "🛠️ Generating initial mutation state..."
python -m core.mutator |

| true

# --- BUG FIX START ---
# mutator.py writes to target_app/active_server.py relative to WORKDIR /app
RUNTIME_MUTATED="target_app/active_server.py"
# --- BUG FIX END ---

WAIT_SECONDS=0
MAX_WAIT=10
echo "[startup] Waiting for runtime mutated server at ${RUNTIME_MUTATED}..."

while &&; do
    sleep 0.5
    WAIT_SECONDS=$((WAIT_SECONDS+1))
done

if; then
    echo "[startup] Found mutated runtime server after ${WAIT_SECONDS} checks."
else
    echo "[startup][warning] Mutated runtime server not found at ${RUNTIME_MUTATED}. Proceeding..."
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

# Tail logs for Render dashboard visibility
tail -F /tmp/nodeA.log /tmp/nodeB.log /tmp/proxy.log /tmp/bot.log > /tmp/combined_logs.log 2>&1 &
TAIL_PID=$!

PORT=${PORT:-10000}
echo "✅ Starting Dashboard on Port $PORT"

python -m streamlit run dashboard.py \
  --server.port $PORT \
  --server.enableCORS false \
  --server.address 0.0.0.0 \
  --server.headless true \
  --theme.base "dark" &

STREAMLIT_PID=$!
wait "$STREAMLIT_PID"

kill "$TAIL_PID" |

| true
cleanup
