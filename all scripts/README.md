# H4D Assistant Chatbot (Production Deployment)

# H4D Assistant Chatbot (Production Deployment)

This project provides an interactive, AI-powered assistant designed to be a companion for the book "Hacking for Defense." Users can ask questions in natural language to query the book's content, get summaries of key concepts, and receive detailed explanations of methodologies presented within the text. The application's goal is to make the principles of Hacking for Defense more accessible and easier to understand for students, entrepreneurs, and defense professionals.

## Core Features

-   **Optimized React Frontend**: A fast, responsive chat interface built for production (`npm run build`).
-   **Unified Python Backend**: A single Flask server handles API requests, serves the static frontend files, and manages user authentication.
-   **Secure User Accounts**: Includes user registration, login, and password reset functionality to protect API key usage.
-   **Persistent & Automated**: Designed for permanent hosting with scripts to automate setup and a `systemd` service for autostarting on system boot.

---

## ☁️ Pushing to GitHub (First-Time Setup)

Follow these steps from the root `H4Dassistant` directory on your current machine to publish your project to a new GitHub repository.

1.  **Initialize Git**
    This turns your project folder into a Git repository.
    ```bash
    git init -b main
    ```

2.  **Add all files for tracking**
    This stages all files (except those listed in `.gitignore`) for your first commit.
    ```bash
    git add .
    ```

3.  **Make your first commit**
    This saves the project's current state to your local Git history.
    ```bash
    git commit -m "Initial commit: Setup complete production application"
    ```

4.  **Connect to your GitHub Repository**
    Go to [GitHub](https://github.com/new) and create a new, empty repository. GitHub will give you an HTTPS URL. Use it in the command below.
    ```bash
    # Replace <your-github-repository-url> with the HTTPS URL you just copied
    git remote add origin <your-github-repository-url>
    ```

5.  **Push your code to GitHub**
    This uploads your code to the GitHub repository.
    ```bash
    git push -u origin main
    ```

---

## 🚀 One-Time Setup on `powerjad` (Home Computer)

These steps will guide you through cloning the repository and installing all necessary dependencies on your new Ubuntu machine.

1.  **Prerequisites**
    Ensure the following are installed on your `powerjad` Ubuntu desktop:
    -   **Git**: `sudo apt update && sudo apt install git`
    -   **Python 3.10+** & `venv`: `sudo apt install python3 python3-venv`
    -   **Node.js 18+** & `npm`: Follow official installation guides for Node.js.
    -   **`loclx`**: The LocalXpose client, installed and authenticated.

2.  **Clone the Repository**
    Open a terminal and clone your project from GitHub.
    ```bash
    # Replace <your-github-repository-url> with the actual URL
    git clone <your-github-repository-url>
    cd H4Dassistant
    ```

3.  **Make Scripts Executable**
    This one-time step gives you permission to run the setup and control scripts.
    ```bash
    chmod +x setup_production.sh
    chmod +x autostart_production.sh
    chmod +x stop_production.sh
    ```

4.  **Run the Setup Script**
    This master script will install all Python/Node.js dependencies and create the production build of the frontend.
    ```bash
    ./setup_production.sh
    ```

5.  **Configure Environment Variables**
    Your API keys are stored in an environment file that is never committed to GitHub.
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

From the project's root directory (`H4Dassistant`), you can control the entire application stack.

-   **To Start Everything (Server + Tunnel):**
    ```bash
    ./autostart_production.sh
    ```
-   **To Stop Everything:**
    ```bash
    ./stop_production.sh
    ```

Your application will be live at: **`http://h4dassistant.com`**

---

## 🔄 Autostart on System Boot (`systemd` Service)

This will make your application start automatically every time your `powerjad` computer boots up.

1.  **Create the Service File**
    Use a text editor like `nano` to create a new service definition file:
    ```bash
    sudo nano /etc/systemd/system/h4d-assistant.service
    ```

2.  **Paste the Service Configuration**
    Copy and paste the following configuration. It is already configured for your username `powerjad`.

    ```ini
    [Unit]
    Description=H4D Assistant Application Stack (Server + Tunnel)
    After=network-online.target

    [Service]
    User=powerjad
    Type=forking
    WorkingDirectory=/home/powerjad/Documents/AI/H4Dassistant
    ExecStart=/home/powerjad/Documents/AI/H4Dassistant/autostart_production.sh
    ExecStop=/home/powerjad/Documents/AI/H4Dassistant/stop_production.sh
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
