from flask import Flask, request, redirect
import sqlite3
import secrets
from datetime import timedelta
from routes.views import views_bp
from routes.api import api_bp
from utils.db import get_db_connection

app = Flask(__name__)
# Use a persistent secret key for session signing
import os
secret_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret.key')
if os.path.exists(secret_file):
    with open(secret_file, 'r') as f:
        app.secret_key = f.read().strip()
else:
    app.secret_key = secrets.token_hex(16)
    with open(secret_file, 'w') as f:
        f.write(app.secret_key)
app.permanent_session_lifetime = timedelta(days=30)

# Register Blueprints
app.register_blueprint(views_bp)
app.register_blueprint(api_bp)

@app.before_request
def check_setup():
    if request.path.startswith('/static/') or request.path.startswith('/api/'):
        return
        
    conn = get_db_connection()
    try:
        user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    except sqlite3.OperationalError:
        user_count = 0
    conn.close()
    
    is_setup = user_count > 0
    
    if not is_setup and request.path != '/':
        return redirect('/')
        
    if is_setup and request.path == '/onboarding':
        return redirect('/login')

@app.after_request
def add_header(response):
    if not request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    is_debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=5005, debug=is_debug)
