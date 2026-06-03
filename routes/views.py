from flask import Blueprint, render_template, session, redirect
from utils.db import get_db_connection
import sqlite3
from datetime import datetime, timezone
import zoneinfo

views_bp = Blueprint('views_bp', __name__)

def format_actual_time(dt_str, tz_name):
    try:
        dt_utc = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        try:
            dt_local = dt_utc.astimezone(zoneinfo.ZoneInfo(tz_name))
        except:
            dt_local = dt_utc
        return dt_local.strftime('%b %d, %I:%M %p')
    except Exception as e:
        return dt_str

@views_bp.context_processor
def inject_global_data():
    """Injects organization and user data into all templates rendered by this blueprint."""
    conn = get_db_connection()
    try:
        # Fetch organization info
        org_name = conn.execute('SELECT value FROM settings WHERE key = ?', ('org_name',)).fetchone()
        org_logo = conn.execute('SELECT value FROM settings WHERE key = ?', ('org_logo',)).fetchone()
        org_tz = conn.execute('SELECT value FROM settings WHERE key = ?', ('timezone',)).fetchone()
        
        org_name = org_name[0] if org_name else 'Xndcy Dashboard'
        org_logo = org_logo[0] if org_logo else None
        org_tz = org_tz[0] if org_tz else 'UTC'
        
        user_name = 'Admin User'
        user_pic = None
        if 'user_id' in session:
            user = conn.execute('SELECT full_name, profile_pic FROM users WHERE id = ?', (session['user_id'],)).fetchone()
            if user:
                user_name = user['full_name']
                user_pic = user['profile_pic']
                
        return {
            'org_name': org_name,
            'org_logo': org_logo,
            'org_tz': org_tz,
            'user_name': user_name,
            'user_pic': user_pic
        }
    except sqlite3.OperationalError:
        return {
            'org_name': 'Xndcy Dashboard',
            'org_logo': None,
            'org_tz': 'UTC',
            'user_name': 'Admin User',
            'user_pic': None
        }
    finally:
        conn.close()

@views_bp.route('/')
def index():
    conn = get_db_connection()
    try:
        user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    except sqlite3.OperationalError:
        user_count = 0
    conn.close()
    
    if user_count == 0:
        import shutil
        total, used, free = shutil.disk_usage('/')
        free_gb = free // (2**30)
        max_storage = max(1, free_gb - 8)
        return render_template('onboarding.html', max_storage=max_storage)
    else:
        if 'user_id' in session:
            return redirect('/dashboard')
        return redirect('/login')

@views_bp.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@views_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
        
    conn = get_db_connection()
    try:
        user_count_row = conn.execute('SELECT COUNT(*) FROM users').fetchone()
        total_users = user_count_row[0] if user_count_row else 0
        
        storage_row = conn.execute('SELECT SUM(storage) FROM users').fetchone()
        allocated_storage = storage_row[0] if storage_row and storage_row[0] else 0
        
        limit_row = conn.execute("SELECT value FROM settings WHERE key = 'allocated_storage'").fetchone()
        if limit_row and limit_row[0]:
            total_storage = int(limit_row[0])
        else:
            total_storage = 500
        
        activities = conn.execute('SELECT * FROM activities ORDER BY id DESC LIMIT 12').fetchall()
        activities = [dict(a) for a in activities]
        
        # We need org_tz for formatting, fetch it just for formatting
        org_tz_row = conn.execute('SELECT value FROM settings WHERE key = ?', ('timezone',)).fetchone()
        org_tz = org_tz_row[0] if org_tz_row else 'UTC'
        
        for a in activities:
            a['time_formatted'] = format_actual_time(a['timestamp'], org_tz)
            
    except sqlite3.OperationalError:
        total_users = 0
        allocated_storage = 0
        total_storage = 500
        activities = []
    finally:
        conn.close()
        
    return render_template('dashboard.html', total_users=total_users, allocated_storage=allocated_storage, total_storage=total_storage, activities=activities)

@views_bp.route('/users')
def users_page():
    if 'user_id' not in session:
        return redirect('/login')
        
    conn = get_db_connection()
    try:
        all_users = conn.execute('''
            SELECT u.id, u.user_code, u.job_title, u.full_name, u.email, u.first_name, u.last_name, u.profile_pic, u.storage, r.name as role_name, r.color as role_color 
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            ORDER BY u.id DESC
        ''').fetchall()
    except sqlite3.OperationalError:
        all_users = []
    finally:
        conn.close()
        
    return render_template('users.html', all_users=all_users)

@views_bp.route('/roles')
def roles_page():
    if 'user_id' not in session:
        return redirect('/login')
        
    conn = get_db_connection()
    try:
        db_roles = conn.execute('''
            SELECT r.*, COUNT(u.id) as user_count 
            FROM roles r 
            LEFT JOIN users u ON r.id = u.role_id 
            GROUP BY r.id 
            ORDER BY r.id DESC
        ''').fetchall()
        
        all_roles = []
        for r in db_roles:
            all_roles.append({
                'id': r['id'],
                'name': r['name'],
                'icon': r['icon'],
                'color': r['color'],
                'default_storage': r['default_storage'],
                'user_count': r['user_count'],
                'permissions': 'All Permissions', # Placeholder
                'description': f"Default storage: {r['default_storage']}GB"
            })
    except sqlite3.OperationalError:
        all_roles = []
    finally:
        conn.close()
        
    return render_template('roles.html', all_roles=all_roles)

@views_bp.route('/roles/add')
def roles_add_page():
    if 'user_id' not in session:
        return redirect('/login')
        
    return render_template('roles_add.html')

@views_bp.route('/onboarding')
def onboarding():
    return redirect('/')

@views_bp.route('/users/add')
def users_add_page():
    if 'user_id' not in session:
        return redirect('/login')
        
    conn = get_db_connection()
    try:
        roles = conn.execute('SELECT id, name, icon, color, default_storage FROM roles ORDER BY name ASC').fetchall()
    except sqlite3.OperationalError:
        roles = []
    finally:
        conn.close()
        
    return render_template('users_add.html', roles=roles)

@views_bp.route('/users/edit/<int:id>')
def users_edit_page(id):
    if 'user_id' not in session:
        return redirect('/login')
        
    conn = get_db_connection()
    try:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
        roles = conn.execute('SELECT id, name, default_storage FROM roles').fetchall()
    except sqlite3.OperationalError:
        user = None
        roles = []
    finally:
        conn.close()
        
    if not user:
        return redirect('/users')
        
    return render_template('users_edit.html', user=dict(user), roles=roles)

@views_bp.route('/roles/edit/<int:id>')
def roles_edit_page(id):
    if 'user_id' not in session:
        return redirect('/login')
        
    conn = get_db_connection()
    try:
        role = conn.execute('SELECT * FROM roles WHERE id = ?', (id,)).fetchone()
    except sqlite3.OperationalError:
        role = None
    finally:
        conn.close()
        
    if not role:
        return redirect('/roles')
        
    return render_template('roles_edit.html', role=dict(role))
