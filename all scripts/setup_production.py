#!/usr/bin/env bash
# setup_production.sh - Installs dependencies and creates a production build.

set -e
echo "--- Starting H4D Assistant Production Setup ---"

# 1. Set up Python Backend in /api
echo "[1/2] Setting up Python backend..."
cd api
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..
echo "✅ Python setup complete."

# 2. Set up and Build Frontend in /modern-chatbot
echo "[2/2] Setting up and building React frontend..."
cd modern-chatbot
npm install
echo "Creating production build..."
npm run build
cd ..
echo "✅ Frontend build complete."

echo "--- ✅ Full Production Setup Complete ---"
echo "Next steps:"
echo "1. Ensure your .env file is configured in the 'api' folder."
echo "2. Run './autostart_production.sh' to start the application."
