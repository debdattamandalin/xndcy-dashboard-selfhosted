from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import get_db_connection
import sqlite3
import hashlib
import requests
import subprocess

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/api/setup', methods=['POST'])
def setup_api():
    conn = get_db_connection()
    try:
        user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    except sqlite3.OperationalError:
        user_count = 0
        
    if user_count > 0:
        conn.close()
        return jsonify({'success': False, 'message': 'Setup already completed.'}), 400
        
    data = request.json
    org_name = data.get('orgName')
    first_name = data.get('firstName', '')
    last_name = data.get('lastName', '')
    full_name = f"{first_name} {last_name}".strip()
    email = data.get('email')
    password = data.get('password')
    logo_base64 = data.get('logo')
    profile_pic_base64 = data.get('profilePic')
    domain = data.get('domain', 'Unknown Domain')
    auth_method = data.get('authMethod', 'Unknown Auth')
    timezone = data.get('timezone', 'UTC')
    
    if not email or not password or not org_name or not first_name or not last_name:
        conn.close()
        return jsonify({'success': False, 'message': 'Missing required fields.'}), 400
        
    password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    # Process profile picture if provided
    db_profile_pic_path = None
    if profile_pic_base64:
        try:
            import base64
            import os
            header, encoded = profile_pic_base64.split(",", 1)
            ext = '.png' if 'png' in header.lower() else '.jpg'
            
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()[:8]
            profile_pic_filename = f'user_profile_{email_hash}{ext}'
            profile_pic_path = os.path.join(upload_dir, profile_pic_filename)
            
            with open(profile_pic_path, 'wb') as f:
                f.write(base64.b64decode(encoded))
                
            db_profile_pic_path = f'/static/uploads/{profile_pic_filename}'
        except Exception as e:
            print("Failed to save profile pic:", e)

    import random, string
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        count = conn.execute('SELECT COUNT(*) FROM users WHERE user_code = ?', (code,)).fetchone()[0]
        if count == 0:
            break
    conn.execute('INSERT INTO roles (name, icon, color, default_storage) VALUES (?, ?, ?, ?)', ('Administrator', 'shield', '#448aff', 5))
    role_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            
    conn.execute('INSERT INTO users (email, full_name, first_name, last_name, password_hash, profile_pic, user_code, role_id, storage, job_title) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (email, full_name, first_name, last_name, password_hash, db_profile_pic_path, code, role_id, 5, 'Administrator'))
    user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('org_name', org_name))
    conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('timezone', timezone))
    
    allocated_storage = data.get('allocatedStorage')
    if allocated_storage:
        conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('allocated_storage', allocated_storage))

    
    # Process logo if provided
    if logo_base64:
        try:
            import base64
            import os
            header, encoded = logo_base64.split(",", 1)
            ext = '.png' if 'png' in header.lower() else '.jpg'
            
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            logo_filename = f'org_logo{ext}'
            logo_path = os.path.join(upload_dir, logo_filename)
            
            with open(logo_path, 'wb') as f:
                f.write(base64.b64decode(encoded))
                
            db_path = f'/static/uploads/{logo_filename}'
            conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('org_logo', db_path))
        except Exception as e:
            print("Failed to save logo:", e)
            
    # Insert activities sequentially
    conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                 (f"Organization '{org_name}' Configured", 'System-Auto', 'Success', 'domain'))
                 
    if logo_base64:
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                     (f"Organization Logo Added", 'System-Auto', 'Success', 'image'))

    conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                 ("Role 'Administrator' Created", 'System-Auto', 'Success', 'shield'))

    conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                 ("Admin Account Created", 'System-Auto', 'Success', 'person_add'))
                 
    if allocated_storage:
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                     (f"Allocated Storage Set: {allocated_storage}GB", 'System-Auto', 'Success', 'storage'))

    conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                 (f"Domain Connected: {domain}", auth_method, 'Success', 'language'))
    conn.commit()
    conn.close()
    
    session.clear()
    
    le_email = data.get('leEmail', email)
    
    if domain and domain != 'Unknown Domain' and domain != 'Cloudflare Managed':
        try:
            subprocess.Popen(
                ['/usr/bin/sudo', '/opt/xndcy-dashboard/enable_ssl.sh', domain, le_email],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
                start_new_session=True
            )
        except Exception as e:
            print(f"Failed to start SSL provisioning: {e}")
            
    return jsonify({'success': True})

@api_bp.route('/api/cloudflare/zones', methods=['POST'])
def cloudflare_zones():
    data = request.json
    token = data.get('token')
    if not token:
        return jsonify({'success': False, 'error': 'Token is required'})
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    try:
        response = requests.get('https://api.cloudflare.com/client/v4/zones', headers=headers)
        if response.status_code != 200:
            return jsonify({'success': False, 'error': 'Invalid token or Cloudflare API error'})
        
        zones_data = response.json().get('result', [])
        zones = [{'id': z['id'], 'name': z['name']} for z in zones_data]
        return jsonify({'success': True, 'zones': zones})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/api/cloudflare/provision', methods=['POST'])
def cloudflare_provision():
    data = request.json
    token = data.get('token')
    zone_id = data.get('zone_id')
    domain = data.get('domain')
    
    if not all([token, zone_id, domain]):
        return jsonify({'success': False, 'error': 'Missing required fields'})
        
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    try:
        # Get public IPv4 and IPv6
        ipv4, ipv6 = None, None
        try:
            r4 = requests.get('https://ipv4.icanhazip.com', timeout=3)
            if r4.status_code == 200: ipv4 = r4.text.strip()
        except: pass
        
        try:
            r6 = requests.get('https://ipv6.icanhazip.com', timeout=3)
            if r6.status_code == 200: ipv6 = r6.text.strip()
        except: pass

        if not ipv4 and not ipv6:
            return jsonify({'success': False, 'error': 'Could not determine public IPv4 or IPv6 address. Ensure the server has internet access.'})

        # Fetch existing records for the domain
        rec_url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={domain}'
        rec_response = requests.get(rec_url, headers=headers)
        
        if rec_response.status_code == 200:
            existing = rec_response.json().get('result', [])
            for record in existing:
                if record['type'] in ['A', 'CNAME', 'AAAA']:
                    return jsonify({'success': False, 'error': f"DNS record for '{domain}' already exists! Please delete it manually in Cloudflare, or choose a different subdomain."})
        
        # Create records
        created_any = False
        errors = []
        
        if ipv4:
            payload = {'type': 'A', 'name': domain, 'content': ipv4, 'ttl': 1, 'proxied': False}
            res = requests.post(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', headers=headers, json=payload)
            if res.status_code == 200:
                created_any = True
            else:
                err = 'Failed to create A record'
                try: err = res.json().get('errors', [{}])[0].get('message', err)
                except: pass
                errors.append(f"A Record: {err}")
                
        if ipv6:
            payload = {'type': 'AAAA', 'name': domain, 'content': ipv6, 'ttl': 1, 'proxied': False}
            res = requests.post(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', headers=headers, json=payload)
            if res.status_code == 200:
                created_any = True
            else:
                err = 'Failed to create AAAA record'
                try: err = res.json().get('errors', [{}])[0].get('message', err)
                except: pass
                errors.append(f"AAAA Record: {err}")
                
        if created_any:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': f'Cloudflare API Error: {"; ".join(errors)}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/api/check_session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({'logged_in': True})
    return jsonify({'logged_in': False})

@api_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', False)
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        session.clear()
        session['user_id'] = user['id']
        if remember:
            session.permanent = True
        else:
            session.permanent = False
            
        # Log login activity
        try:
            conn_log = get_db_connection()
            conn_log.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                             (f"User Logged In", user['user_code'], 'Logged', 'login'))
            conn_log.commit()
            conn_log.close()
        except Exception as e:
            print("Failed to log login activity:", e)
            
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

@api_bp.route('/api/logout', methods=['POST'])
def logout():
    user_id = session.get('user_id')
    if user_id:
        try:
            conn_log = get_db_connection()
            user = conn_log.execute('SELECT user_code FROM users WHERE id = ?', (user_id,)).fetchone()
            if user:
                conn_log.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                                 (f"User Logged Out", user['user_code'], 'Logged', 'logout'))
                conn_log.commit()
            conn_log.close()
        except Exception as e:
            print("Failed to log logout activity:", e)
            
    session.clear()
    return jsonify({'success': True})


# ---------------------------------------------------------
# DNS Verification Endpoints
# ---------------------------------------------------------

DNS_SECRET = b"XNDCY_SECRET"

def generate_dns_token(domain):
    if not domain:
        return ""
    h = hashlib.sha256(domain.lower().encode('utf-8') + DNS_SECRET).hexdigest()
    return f"xndcy-verification=v1_{h[:12]}"

def get_public_ip():
    try:
        return requests.get("https://ifconfig.me", timeout=3).text.strip()
    except:
        return "YOUR_SERVER_IP"

@api_bp.route('/api/dns-info', methods=['GET'])
def dns_info():
    domain = request.args.get('domain', '').strip()
    if not domain:
        return jsonify({'error': 'Domain required'}), 400
        
    expected_token = generate_dns_token(domain)
    public_ip = get_public_ip()
    return jsonify({
        'domain': domain,
        'txt_name': f"_xndcy-dashboard.{domain}",
        'a_name': domain,
        'expected_token': expected_token,
        'expected_a_record': public_ip
    })

@api_bp.route('/api/verify-dns', methods=['POST'])
def verify_dns():
    data = request.json or {}
    domain = data.get('domain', '').strip()
    if not domain:
        return jsonify({'success': False, 'message': 'Domain required'}), 400
        
    expected_token = generate_dns_token(domain)
    public_ip = get_public_ip()
    txt_verified = False
    a_verified = False
    
    txt_url = f"https://dns.google/resolve?name=_xndcy-dashboard.{domain}&type=TXT"
    try:
        r = requests.get(txt_url, timeout=5).json()
        if 'Answer' in r:
            for answer in r['Answer']:
                value = answer.get('data', '').strip('"')
                if value == expected_token:
                    txt_verified = True
                    break
    except Exception as e:
        print(f"TXT verification error: {e}")
        
    a_url = f"https://dns.google/resolve?name={domain}&type=A"
    try:
        r = requests.get(a_url, timeout=5).json()
        if 'Answer' in r:
            for answer in r['Answer']:
                val = answer.get('data', '')
                if val == public_ip:
                    a_verified = True
                    break
    except Exception as e:
        print(f"A verification error: {e}")
        
    return jsonify({
        'success': True,
        'txt_verified': txt_verified,
        'a_verified': a_verified
    })

# ---------------------------------------------------------
# Roles Endpoints
# ---------------------------------------------------------

@api_bp.route('/api/roles', methods=['POST'])
def create_role():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    data = request.json
    name = data.get('name')
    icon = data.get('icon')
    color = data.get('color')
    default_storage = data.get('default_storage')
    
    if not name or not icon or not color or default_storage is None:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
    try:
        default_storage = int(default_storage)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid storage value'}), 400
        
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO roles (name, icon, color, default_storage) VALUES (?, ?, ?, ?)',
                     (name, icon, color, default_storage))
        
        # Log activity
        user_id = session.get('user_id')
        user = conn.execute('SELECT user_code FROM users WHERE id = ?', (user_id,)).fetchone()
        user_code = user['user_code'] if user else 'System'
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)',
                     (f"Role Created: {name}", user_code, 'Success', icon))
        
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500
        
    conn.close()
    return jsonify({'success': True})

@api_bp.route('/api/roles/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    try:
        # Check if users are assigned to this role
        user_count = conn.execute('SELECT COUNT(*) FROM users WHERE role_id = ?', (role_id,)).fetchone()[0]
        if user_count > 0:
            conn.close()
            return jsonify({'success': False, 'message': f'Cannot delete role: {user_count} user(s) are currently assigned to it.'}), 400
            
        # Get role name for logging
        role = conn.execute('SELECT name FROM roles WHERE id = ?', (role_id,)).fetchone()
        if not role:
            conn.close()
            return jsonify({'success': False, 'message': 'Role not found.'}), 404
            
        role_name = role['name']
        
        # Delete the role
        conn.execute('DELETE FROM roles WHERE id = ?', (role_id,))
        
        # Log activity
        user_id = session.get('user_id')
        user = conn.execute('SELECT user_code FROM users WHERE id = ?', (user_id,)).fetchone()
        user_code = user['user_code'] if user else 'System'
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)',
                     (f"Role Deleted: {role_name}", user_code, 'Success', 'delete'))
                     
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500
        
    conn.close()
    return jsonify({'success': True})

@api_bp.route('/api/users', methods=['POST'])
def create_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    data = request.json
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    personal_email = data.get('personalEmail')
    job_title = data.get('jobTitle')
    role_id = data.get('roleId')
    storage = data.get('storage')
    
    if not first_name or not last_name or not email or not personal_email or not job_title or not role_id or storage is None:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
    try:
        storage = int(storage)
        role_id = int(role_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid storage or role ID value'}), 400
        
    full_name = f"{first_name} {last_name}"
    
    import random, string
    conn = get_db_connection()
    try:
        # Check storage limit
        current_storage_row = conn.execute('SELECT SUM(storage) FROM users').fetchone()
        current_storage = current_storage_row[0] if current_storage_row and current_storage_row[0] else 0
        
        if current_storage + storage > 500:
            conn.close()
            return jsonify({'success': False, 'message': f'Storage overallocation. Cannot allocate {storage}GB. Only {500 - current_storage}GB remaining.'}), 400
            
        # Generate unique user code
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            count = conn.execute('SELECT COUNT(*) FROM users WHERE user_code = ?', (code,)).fetchone()[0]
            if count == 0:
                break
                
        # Password not required for provisioning in this iteration, set a dummy hash
        password_hash = "dummy_hash" 
        
        conn.execute('''
            INSERT INTO users (email, personal_email, full_name, password_hash, first_name, last_name, job_title, role_id, storage, user_code) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, personal_email, full_name, password_hash, first_name, last_name, job_title, role_id, storage, code))
        
        # Log activity
        user_id = session.get('user_id')
        user = conn.execute('SELECT user_code FROM users WHERE id = ?', (user_id,)).fetchone()
        user_code = user['user_code'] if user else 'System'
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)',
                     (f"User Provisioned: {full_name}", user_code, 'Success', 'person_add'))
                     
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'User with this email already exists.'}), 400
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500
        
    conn.close()
    return jsonify({'success': True})

@api_bp.route('/api/users/<int:target_user_id>', methods=['DELETE'])
def delete_user(target_user_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    current_user_id = session.get('user_id')
    
    # Prevent users from deleting themselves
    if current_user_id == target_user_id:
        return jsonify({'success': False, 'message': 'You cannot delete your own account.'}), 400
        
    conn = get_db_connection()
    try:
        # Check if target user exists
        target_user = conn.execute('SELECT full_name FROM users WHERE id = ?', (target_user_id,)).fetchone()
        if not target_user:
            conn.close()
            return jsonify({'success': False, 'message': 'User not found.'}), 404
            
        target_name = target_user['full_name']
        
        # Delete the user
        conn.execute('DELETE FROM users WHERE id = ?', (target_user_id,))
        
        # Log activity
        current_user = conn.execute('SELECT user_code FROM users WHERE id = ?', (current_user_id,)).fetchone()
        current_code = current_user['user_code'] if current_user else 'System'
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)',
                     (f"User Deleted: {target_name}", current_code, 'Success', 'person_remove'))
                     
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500
        
    conn.close()
    return jsonify({'success': True})


@api_bp.route('/api/users/<int:id>', methods=['PUT'])
def edit_user(id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    data = request.json
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    personal_email = data.get('personalEmail')
    job_title = data.get('jobTitle')
    role_id = data.get('roleId')
    storage = data.get('storage')
    
    if not all([first_name, last_name, email, personal_email, job_title, role_id, storage]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
    full_name = f"{first_name} {last_name}"
    
    conn = get_db_connection()
    try:
        # Check if email is used by someone else
        existing = conn.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email, id)).fetchone()
        if existing:
            return jsonify({'success': False, 'message': 'Email is already in use by another user.'}), 400
            
        current_user = conn.execute('SELECT user_code FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        executor_code = current_user['user_code'] if current_user else 'Unknown'
        
        target_user = conn.execute('SELECT user_code FROM users WHERE id = ?', (id,)).fetchone()
        target_code = target_user['user_code'] if target_user else 'Unknown'
        
        conn.execute('''
            UPDATE users 
            SET first_name = ?, last_name = ?, full_name = ?, email = ?, personal_email = ?, job_title = ?, role_id = ?, storage = ?
            WHERE id = ?
        ''', (first_name, last_name, full_name, email, personal_email, job_title, role_id, storage, id))
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                     (f"User {target_code} updated", executor_code, 'Success', 'edit'))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()
        
    return jsonify({'success': True})


@api_bp.route('/api/roles/<int:id>', methods=['PUT'])
def edit_role(id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    data = request.json
    name = data.get('name')
    icon = data.get('icon')
    color = data.get('color')
    default_storage = data.get('default_storage')
    
    if not all([name, icon, color, default_storage]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
    conn = get_db_connection()
    try:
        current_user = conn.execute('SELECT user_code FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        executor_code = current_user['user_code'] if current_user else 'Unknown'
        
        conn.execute('''
            UPDATE roles 
            SET name = ?, icon = ?, color = ?, default_storage = ?
            WHERE id = ?
        ''', (name, icon, color, default_storage, id))
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                     (f"Role '{name}' updated", executor_code, 'Success', 'edit'))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()
        
    return jsonify({'success': True})
