<div align="center">
  <img src="https://raw.githubusercontent.com/debdattamandalin/xndcy-dashboard-selfhosted/main/static/img/logo.png" alt="Xndcy Logo" width="120" onerror="this.src='https://ui-avatars.com/api/?name=Xndcy&background=1e1e1e&color=fff&size=120&rounded=true'"/>
  
  # Xndcy Dashboard Self-Hosted
  
  **A sleek, high-performance administrative dashboard built with Flask, SQLite, and Tailwind CSS.**
  
  ---
</div>

## ✨ Overview

Xndcy Dashboard is a modern, self-hosted administrative interface designed for speed and beautiful aesthetics. Built on a lightweight **Flask + SQLite** backend, it uses **Tailwind CSS** and **GSAP** to deliver a stunning "glassmorphism" dark-mode UI with highly responsive micro-animations. 

## 🚀 Key Features

### 1. Zero-Config Setup & Onboarding
- **Smart Initialization**: The app automatically detects if it's running for the first time and walks you through a gorgeous setup flow before locking it down.
- **Organization Branding**: Upload custom organization logos and admin profile pictures (stored efficiently via Base64).
- **Intelligent Timezones**: Features a custom-built, OS-agnostic timezone selector that automatically detects and defaults to the user's local browser timezone.

### 2. Advanced Role Management (New!)
- **Dynamic Roles**: Create custom roles with highly granular permissions.
- **Custom Color Pickers**: Assign unique, brand-aligned colors to every role using an entirely custom-built HTML5 canvas HSV color picker.
- **Integrated Iconography**: Choose from dozens of Material Symbols for your roles using a seamless dropdown popover.
- **Storage Allocation Defaults**: Define default storage quotas (e.g. 5GB) for users assigned to specific roles.

### 3. Comprehensive User Management (New!)
- **Full CRUD Capabilities**: Add, edit, and manage users dynamically.
- **Form Protection Logic**: Intelligent "dirty-state" tracking takes snapshots of your form on load, showing a beautiful Discard UI only when actual unsaved changes are detected.
- **Auto-Allocation**: Assigning a role to a user automatically grants them the base storage limit specified by the role configuration.

### 4. Dynamic Dashboard & Live Analytics
- **Storage Progress Visualization**: Dynamically aggregates total storage limits allocated to users against the global organizational pool, visualizing it via an animated progress bar.
- **Live Activity Feed**: A beautiful, custom-scrollable table displaying recent system and user events. Click any row to expand detailed logs.
- **Instant Filtering**: Client-side JavaScript filtering allows instant switching between `All`, `System`, and `User` events without page reloads.

### 5. Premium UI/UX Design
- **GSAP Animations**: Every page features buttery-smooth staggered entrance animations (`gsap-stagger-item`).
- **Complex UI Stacking contexts**: Fully custom-built `<select>` dropdowns and popovers that intelligently escape animation stacking contexts to float perfectly over UI elements.
- **Tailwind CSS**: Fully custom utility-class styling with tailored components.
- **Typography**: Powered by the beautiful **Geist** font family.

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite3
- **Frontend**: HTML5, Vanilla JavaScript, GSAP
- **Styling**: Tailwind CSS (via CDN) + Custom CSS Variables
- **Fonts/Icons**: Google Fonts (Geist, Material Symbols Outlined)

---

## 📦 Automated Production Installation (Ubuntu/Debian)

If you are deploying this dashboard to a live Linux server (Ubuntu/Debian), we have provided a fully automated installation script. 

This script will automatically:
- Install system dependencies (Git, Python, Nginx, Certbot, Gunicorn, SQLite).
- Clone the repository into `/opt/xndcy-dashboard`.
- Create a Python virtual environment and install requirements.
- Configure and start a `systemd` background service to keep the app running.
- Set up an Nginx reverse proxy to expose the dashboard on port 80.
- Provide a helper script (`sudo /opt/xndcy-dashboard/enable_ssl.sh`) to instantly generate free SSL certificates via Let's Encrypt.

To use the automated installer, simply run:
```bash
sudo chmod +x install.sh
sudo ./install.sh
```

---

## 💻 Local Development

### Prerequisites
Make sure you have Python 3.8+ installed on your system.

### 1. Clone the repository
```bash
git clone https://github.com/debdattamandalin/xndcy-dashboard-selfhosted.git
cd xndcy-dashboard-selfhosted
```

### 2. Set up a virtual environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
*(If `requirements.txt` is missing, just run `pip install flask werkzeug`)*

### 4. Initialize and Run the application
```bash
python3 app.py
```
*The app will automatically start at `http://127.0.0.1:5000`. If no database exists, it will automatically prompt you with the setup wizard.*

### 5. Resetting the Database
If you ever need to completely wipe the dashboard and trigger the onboarding flow again, simply delete the SQLite database and run the setup script manually:
```bash
rm database.db
python3 setup_db.py
```

---

## 💖 Credits

This project was built with the assistance of **[Antigravity](https://deepmind.google/)**, an agentic coding assistant, and beautifully designed with the help of **[Stitch](https://stitch.withgoogle.com)**.

---
*Crafted with ❤️ by Xenodochy Team*
