#!/bin/bash
set -e

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script with sudo (e.g., sudo ./install.sh)"
  exit 1
fi

REPO_URL="https://github.com/debdattamandalin/test.git"
APP_NAME="xndcy-dashboard"
APP_DIR="/opt/$APP_NAME"
VENV_DIR="$APP_DIR/venv"

# Determine the non-root user who ran sudo
if [ -n "$SUDO_USER" ]; then
    APP_USER="$SUDO_USER"
else
    APP_USER=$(whoami)
fi

echo "Updating system packages..."
apt-get update

echo "Installing Git, Python and necessary system dependencies..."
apt-get install -y git python3 python3-venv python3-pip python3-dev build-essential curl sqlite3 nginx certbot python3-certbot-nginx

echo "Setting up application in directory: $APP_DIR"

if [ -d "$APP_DIR" ]; then
    echo "Directory $APP_DIR already exists. Pulling latest changes..."
    cd "$APP_DIR"
    sudo -u "$APP_USER" git pull
else
    echo "Cloning repository..."
    git clone "$REPO_URL" "$APP_DIR"
    chown -R "$APP_USER":"$APP_USER" "$APP_DIR"
    cd "$APP_DIR"
fi

echo "Setting up virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    sudo -u "$APP_USER" python3 -m venv "$VENV_DIR"
fi

# Activate venv and install dependencies
echo "Installing Python dependencies..."
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install -r requirements.txt
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install gunicorn

echo "Setting up the database..."
sudo -u "$APP_USER" "$VENV_DIR/bin/python" setup_db.py

echo "Creating systemd service..."
cat > /etc/systemd/system/$APP_NAME.service << EOF
[Unit]
Description=Gunicorn instance to serve $APP_NAME
After=network.target

[Service]
User=$APP_USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind 127.0.0.1:5005 app:app

[Install]
WantedBy=multi-user.target
EOF

echo "Starting and enabling the service..."
systemctl daemon-reload
systemctl enable $APP_NAME
systemctl restart $APP_NAME

echo "Configuring firewall..."
if command -v ufw > /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
fi

PUBLIC_IP=$(curl -s --max-time 3 ifconfig.me)
if [ -z "$PUBLIC_IP" ]; then
    PUBLIC_IP=$(curl -s --max-time 3 api.ipify.org)
fi
if [ -z "$PUBLIC_IP" ]; then
    PUBLIC_IP="_"
fi

echo "Cleaning up old Nginx configurations..."
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-enabled/xndcy-setup
rm -f /etc/nginx/sites-enabled/xndcy-prod
rm -f /etc/nginx/sites-enabled/default-drop
rm -f /etc/nginx/sites-available/xndcy-setup
rm -f /etc/nginx/sites-available/xndcy-prod
rm -f /etc/nginx/sites-available/default-drop

echo "Setting up initial Nginx configuration..."
cat > /etc/nginx/sites-available/xndcy-setup << EOF
server {
    listen 80 default_server;
    server_name _;
    return 444;
}

server {
    listen 80;
    server_name $PUBLIC_IP;
    location / {
        proxy_pass http://127.0.0.1:5005;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/xndcy-setup /etc/nginx/sites-enabled/xndcy-setup
systemctl restart nginx

echo "Creating SSL auto-provisioning script..."
cat > $APP_DIR/enable_ssl.sh << 'EOF'
#!/bin/bash
DOMAIN=$1
EMAIL=$2
LOGFILE="/var/log/xndcy_ssl_setup.log"

{
echo "Starting SSL provisioning for $DOMAIN at $(date)"

# Create new nginx site for the domain
cat > /etc/nginx/sites-available/xndcy-prod << NGINX_EOF
server {
    listen 80;
    server_name $DOMAIN;
    location / {
        proxy_pass http://127.0.0.1:5005;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX_EOF
ln -sf /etc/nginx/sites-available/xndcy-prod /etc/nginx/sites-enabled/xndcy-prod

# Remove the setup default site
rm -f /etc/nginx/sites-enabled/xndcy-setup

# Create a drop-all default site to reject direct IP access
cat > /etc/nginx/sites-available/default-drop << NGINX_EOF
server {
    listen 80 default_server;
    server_name _;
    return 444;
}
NGINX_EOF
ln -sf /etc/nginx/sites-available/default-drop /etc/nginx/sites-enabled/default-drop

systemctl restart nginx

# Run certbot to get SSL and configure it
if [ -z "$EMAIL" ] || [ "$EMAIL" = "null" ]; then
    CERTBOT_EMAIL_ARG="--register-unsafely-without-email"
else
    CERTBOT_EMAIL_ARG="-m $EMAIL"
fi

echo "Running certbot..."
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos $CERTBOT_EMAIL_ARG --redirect
echo "Certbot finished."
} >> "$LOGFILE" 2>&1
EOF
chmod +x $APP_DIR/enable_ssl.sh
chown root:root $APP_DIR/enable_ssl.sh

echo "Configuring sudoers for automatic SSL provisioning..."
echo "$APP_USER ALL=(root) NOPASSWD: $APP_DIR/enable_ssl.sh" > /etc/sudoers.d/xndcy-ssl
chmod 0440 /etc/sudoers.d/xndcy-ssl

echo "================================================================"
echo "Installation Complete!"
echo "Your application has been cloned from GitHub and is running via systemd."
echo "You can view its status with: sudo systemctl status $APP_NAME"
echo "You can view the logs with: sudo journalctl -u $APP_NAME -f"
echo ""
echo "You can access your dashboard right now at:"
echo "http://$PUBLIC_IP"
echo "================================================================"
