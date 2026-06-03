<div align="center">
  <img src="https://raw.githubusercontent.com/debdattamandalin/xndcy-dashboard/main/static/img/logo.png" alt="Xndcy Logo" width="120" onerror="this.src='https://ui-avatars.com/api/?name=Xndcy&background=1e1e1e&color=fff&size=120&rounded=true'"/>
  
  # Xndcy Dashboard
  
  **A sleek, high-performance administrative dashboard built with Flask, SQLite, and Tailwind CSS.**
  
  ---
</div>

## ✨ Overview

Xndcy Dashboard is a modern, responsive administrative interface designed for speed and beautiful aesthetics. Built on a lightweight **Flask + SQLite** backend, it uses **Tailwind CSS** to deliver a stunning "glassmorphism" dark-mode UI with smooth micro-animations.

## 🚀 Features

### 1. Zero-Config Setup & Onboarding
- **Smart Initialization**: The app automatically detects if it's running for the first time and locks the setup flow once the initial admin is created.
- **Organization Branding**: Upload custom organization logos and admin profile pictures (stored efficiently via Base64).
- **Intelligent Timezones**: Features a custom-built, OS-agnostic timezone selector that automatically detects and defaults to the user's local browser timezone.

### 2. Secure Authentication
- **Robust Hashing**: Passwords are securely hashed using `pbkdf2:sha256`.
- **Session Management**: Lightweight session-based authentication protects all administrative routes.
- **Dynamic Login**: The login portal dynamically greets users with the organization's custom branding configured during setup.

### 3. Dynamic Dashboard
- **Real-time Metrics**: 
  - **User Tracking**: Live database queries keep the "Total Users" widget perfectly in sync.
  - **Storage Allocation**: Dynamically calculates storage limits (e.g., 5GB allocated per registered user out of a 500GB pool) complete with an animated progress bar.
- **Live Activity Feed**: 
  - A beautiful, custom-scrollable table displaying recent system and user events.
  - **Expandable Details**: Click any row to seamlessly reveal extended event details (like exact timestamps and event triggers).
  - **Instant Filtering**: Client-side JavaScript filtering allows instant switching between `All`, `System`, and `User` events without page reloads.
- **Global Clock**: A real-time header clock that ticks accurately in the organization's chosen timezone.

### 4. Premium UI/UX Design
- **Tailwind CSS**: Fully custom utility-class styling with tailored components.
- **Typography**: Powered by the beautiful **Geist** font family for high legibility and a modern feel.
- **Iconography**: Integrated **Google Material Symbols (Outlined)** for crisp, scalable icons.
- **Custom Components**: Avoids ugly native OS HTML elements (like default `<select>` dropdowns and scrollbars) in favor of custom-built, styled alternatives.

## 🛠️ Technology Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite3
- **Frontend**: HTML5, Vanilla JavaScript
- **Styling**: Tailwind CSS (via CDN) + Custom CSS Variables
- **Fonts/Icons**: Google Fonts (Geist, Material Symbols)

## 📦 Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/debdattamandalin/xndcy-dashboard.git
   cd xndcy-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install flask werkzeug
   ```

3. **Run the application**
   ```bash
   python3 app.py
   ```
   *The app will automatically start at `http://127.0.0.1:5000`.*

4. **Resetting the Database**
   If you ever need to wipe the dashboard and trigger the onboarding flow again, simply delete the SQLite database and run the setup script:
   ```bash
   rm database.db
   python3 setup_db.py
   ```

## 💖 Credits

This project was built with the assistance of **[Antigravity](https://deepmind.google/)**, an agentic coding assistant, and beautifully designed with the help of **[Stitch](https://stitch.withgoogle.com)**.

---
*Crafted with ❤️ by Xenodochy Team*
