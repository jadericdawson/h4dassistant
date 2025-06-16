#!/usr/bin/env bash
# autostart_production.sh - Launches the unified server and loclx tunnel.

set -e
# The script is now inside the 'production' folder, so the project root is one level up.
PROJECT_DIR=$(dirname "$(realpath "$0")")/..
cd "$PROJECT_DIR" || exit

echo "🚀 Launching H4D Assistant Production Stack..."

# --- Start Unified Server (Backend + Frontend) ---
# This single Python server runs on port 5055 and serves both the API
# and the React production build files.
echo "[1/2] Starting Python production server..."
# The python command needs to be run from the 'api' directory, and the venv is in the project root.
(cd api && source ../.venv/bin/activate && python server_production.py) &
SERVER_PID=$!
echo "   ↳ Server PID: $SERVER_PID"
sleep 5

# --- Start Loclx Tunnel ---
# This points your public domain to the unified server.
echo "[2/2] Starting loclx tunnel for h4dassistant.com..."
loclx tunnel http --to localhost:5055 --reserved-domain h4dassistant.com &
TUNNEL_PID=$!
echo "   ↳ Tunnel PID: $TUNNEL_PID"

echo ""
echo "🎉 Production services launched!"
echo "   - Your application is now live at: http://h4dassistant.com"
