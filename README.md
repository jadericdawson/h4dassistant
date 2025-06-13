# H4D Assistant Chatbot (Production Deployment)

This repository contains the source code for the H4D Assistant, a chatbot application powered by the OpenAI API. It features a Python Flask backend that provides a REST API and serves an optimized React frontend for the user interface.

The application is designed to be hosted permanently on a server and start automatically on boot using `systemd`.

## Core Features

-   **Optimized React Frontend**: A fast, responsive chat interface built for production using `npm run build`.
-   **Unified Python Backend**: A single Flask server handles API requests and serves the static frontend files.
-   **Persistent & Automated**: Designed for permanent hosting with scripts to automate setup and a `systemd` service for autostarting on system boot.

---

## 🚀 One-Time Setup on a New Machine

These steps will guide you through installing all necessary dependencies and preparing the application to run.

1.  **Prerequisites**
    Ensure the following are installed on your Ubuntu machine:
    -   **Git**: `sudo apt update && sudo apt install git`
    -   **Python 3.10+** & `venv`: `sudo apt install python3 python3-venv`
    -   **Node.js 18+** & `npm`: Follow official installation guides for Node.js.
    -   **`loclx`**: The LocalXpose client, installed and authenticated.

2.  **Get the Project Files**
    Transfer the `H4Dassistant` project folder to your new machine (e.g., via a USB drive or by cloning from your GitHub repository). Place it in your desired location, for example: `~/Documents/AI/`.

3.  **Make Scripts Executable**
    From the project's root `H4Dassistant` directory, run this one-time command to grant execute permissions.
    ```bash
    chmod +x production/setup_production.sh
    chmod +x production/autostart_production.sh
    chmod +x production/stop_production.sh
    ```

4.  **Run the Setup Script**
    This master script will install all dependencies and create the production build of the frontend.
    ```bash
    ./production/setup_production.sh
    ```

5.  **Configure Environment Variables**
    Your API keys are stored in an environment file. This file must be created manually.
    ```bash
    # Navigate into the api directory
    cd api

    # Copy the example file to create your own .env file
    cp .env.example .env

    # Edit the file with your secret key
    nano .env
    ```
    Paste your `OPENAI_API_KEY` into the file and save it (`Ctrl+X`, then `Y`, then `Enter`).

---

## ▶️ Running the Application Manually

From the project's root directory (`H4Dassistant`), you can control the entire application stack using the scripts located in the `production` folder.

-   **To Start Everything (Server + Tunnel):**
    ```bash
    ./production/autostart_production.sh
    ```
-   **To Stop Everything:**
    ```bash
    ./production/stop_production.sh
    ```

Your application will be live at: **`http://h4dassistant.com`**

---

## 🔄 Autostart on System Boot (`systemd` Service)

This will make your application start automatically every time the computer boots up.

1.  **Create the Service File**
    Use a text editor like `nano` to create a new service definition file:
    ```bash
    sudo nano /etc/systemd/system/h4d-assistant.service
    ```

2.  **Paste the Service Configuration**
    Copy and paste the following configuration. Replace `your_username` with your actual Ubuntu username (e.g., `powerjad`).

    ```ini
    [Unit]
    Description=H4D Assistant Application Stack (Server + Tunnel)
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

3.  **Enable and Start the Service**
    -   **Reload `systemd`** to make it aware of your new service:
        ```bash
        sudo systemctl daemon-reload
        ```
    -   **Enable the service** so it starts automatically on every boot:
        ```bash
        sudo systemctl enable h4d-assistant.service
        ```
    -   **Start the service now** to test it without rebooting:
        ```bash
        sudo systemctl start h4d-assistant.service
        ```
    -   **Check its status** to ensure everything is running correctly:
        ```bash
        systemctl status h4d-assistant.service
        ```
