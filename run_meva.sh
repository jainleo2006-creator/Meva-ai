#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# run_meva.sh  —  Launch MEVA with 5 workers (handles 10 concurrent users)
#
# Usage:
#   chmod +x run_meva.sh
#   ./run_meva.sh
#
# Requirements:
#   pip install streamlit requests python-dotenv markdown
#   GROQ_API_KEY must be in your .env file or exported as an env var
# ─────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT="meva_v6_0.py"
PORTS=(8501 8502 8503 8504 8505)
LOGDIR="logs"

# ── Sanity checks ─────────────────────────────────────────────────────────────
if [ ! -f "$SCRIPT" ]; then
  echo "❌  $SCRIPT not found. Run this script from the same folder as the app."
  exit 1
fi

if ! command -v streamlit &>/dev/null; then
  echo "❌  streamlit not found. Run: pip install streamlit"
  exit 1
fi

# ── Clean up any old instances ────────────────────────────────────────────────
echo "🛑  Stopping any running MEVA instances..."
pkill -f "streamlit run meva_v" 2>/dev/null || true
sleep 1

# ── Create log directory ──────────────────────────────────────────────────────
mkdir -p "$LOGDIR"

# ── Start workers ─────────────────────────────────────────────────────────────
echo ""
echo "🏍️  Starting MEVA workers..."
echo "─────────────────────────────────────"

for PORT in "${PORTS[@]}"; do
  streamlit run "$SCRIPT" \
    --server.port="$PORT" \
    --server.headless=true \
    --server.enableCORS=false \
    > "$LOGDIR/meva_$PORT.log" 2>&1 &

  PID=$!
  echo "  ✅  Worker on port $PORT  (PID $PID)"
  echo "$PID" >> "$LOGDIR/pids.txt"
done

echo "─────────────────────────────────────"
echo ""
echo "📋  Logs: $LOGDIR/meva_<port>.log"
echo "🌐  Next step: configure nginx to load-balance ports 8501–8505"
echo "    (see nginx.conf in this folder)"
echo ""
echo "To stop all workers:  pkill -f 'streamlit run meva_v'"
