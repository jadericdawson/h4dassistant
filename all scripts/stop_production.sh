#!/usr/bin/env bash
# stop_production.sh - Finds and stops all processes related to the H4D Assistant.

echo "--- Shutting down H4D Assistant services ---"

# --- Stop the Python Flask Server (on port 5055) ---
# Find the PID of the process using TCP port 5055
SERVER_PID=$(lsof -t -i:5055)

if [ -n "$SERVER_PID" ]; then
    echo "[1/2] Found Python server running on port 5055 (PID: $SERVER_PID)."
    kill -9 "$SERVER_PID"
    echo "   ↳ Server stopped."
else
    echo "[1/2] No Python server found on port 5055."
fi

# --- Stop all Loclx Tunnels ---
# Find any running process with 'loclx' in its name
LOCLX_PIDS=$(pgrep -f "loclx")

if [ -n "$LOCLX_PIDS" ]; then
    echo "[2/2] Found loclx tunnel processes (PIDs: $LOCLX_PIDS)."
    # Kill all found loclx processes
    kill -9 $LOCLX_PIDS
    echo "   ↳ Tunnels stopped."
else
    echo "[2/2] No loclx tunnels found running."
fi

echo ""
echo "✅ Shutdown complete. All services should be stopped."

