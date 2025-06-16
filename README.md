# Hacking for Defense (H4D) Assistant

This project provides an interactive, AI-powered assistant designed to be a companion for the "Hacking for Defense" book. Users can ask questions in natural language to query the book's content, get summaries of key concepts, and receive detailed explanations of methodologies presented within the text.

The application is designed for a production environment, running as a persistent background service that starts automatically on system boot.

## Core Features

-   **Instructions & Chat Pages**: A dedicated instructions page with important usage guidelines and a clean, responsive chat interface.
-   **Shared Password Protection**: A simple, single-password layer to restrict public access and allow for team use.
-   **Optimized React Frontend**: A fast and modern user interface built for production.
-   **Unified Python Backend**: A single Flask server handles API requests and serves the static frontend files.
-   **Automated Production Setup**: Includes scripts to automate installation and a `systemd` service for autostarting on boot.

---

## 🚀 Production Setup on a New Machine

These steps will guide you through installing all necessary dependencies and preparing the application to run on a new Ubuntu-based system.

### 1. Prerequisites

Ensure the following are installed on your server:
-   **Git**: `sudo apt update && sudo apt install git`
-   **Python 3.10+** & `venv`: `sudo apt install python3.10-venv`
-   **Node.js (v18+)** & `npm`: Use `nvm` (Node Version Manager) for best results.
  ```bash
  curl -o- [https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh](https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh) | bash
  source ~/.bashrc
  nvm install --lts
-   **loclx**: The LocalXpose client, installed and authenticated on your system.

### 2. Get the Project
Clone the repository from GitHub:

```bash
# Replace <your-github-repository-url> with the actual URL
git clone <your-github-repository-url> H4Dassistant
cd H4Dassistant
```

### 3. Run the Setup Script
This master script will install all dependencies (Python & Node.js) and create the production build of the frontend.

```bash
# Make production scripts executable
chmod +x production/*.sh

# Run the setup
./production/setup_production.sh
```

### 4. Configure Environment Variables
Your API key and application password are stored in an environment file. This file must be created manually and will be ignored by Git.

```bash
# Navigate into the api directory
cd api

# Create the .env file
nano .env
```
Paste the following lines into the file, replacing the placeholder values with your actual credentials.

```
OPENAI_API_KEY=sk-YourSecretOpenAIKey
H4D_APP_PASSWORD=YourSuperSecretPasswordForYourTeam
```
Save the file (Ctrl+X, Y, Enter) and return to the root directory (cd ..).

### ▶️ Running the Application
#### Manual Start (for testing)
You can run the application stack directly from the project root:

```bash
./production/autostart_production.sh
```
The application will be live at: `http://h4dassistant.com`

#### Autostart on System Boot (systemd) - Recommended
This is the standard method for a production server.

**Create the Service File:**

```bash
sudo nano /etc/systemd/system/h4dassistant.service
```

**Paste the Configuration:** Copy the text below into the editor. Remember to replace `your_username` with your actual Linux username (e.g., `jadericdawson`).

```ini
[Unit]
Description=H4D Assistant Application Stack
After=network-online.target

[Service]
User=your_username
Type=forking
WorkingDirectory=/home/your_username/Documents/AI/H4Dassistant
ExecStart=/home/your_username/Documents/AI/H4Dassistant/production/autostart_production.sh
ExecStop=/home/your_username/Documents/AI/H4Dassistant/production/stop_production.sh
Restart=on-failure
TimeoutSec=300

[Install]
WantedBy=multi-user.target
```

**Enable and Start the Service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable h4dassistant.service
sudo systemctl start h4dassistant.service
```

**Check the Status:**

```bash
systemctl status h4dassistant.service
