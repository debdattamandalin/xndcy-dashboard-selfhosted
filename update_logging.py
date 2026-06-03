import re

with open('routes/api.py', 'r') as f:
    content = f.read()

# Fix setup() admin user creation
setup_orig = """    conn.execute('INSERT INTO users (email, full_name, password_hash, profile_pic) VALUES (?, ?, ?, ?)', (email, full_name, password_hash, db_profile_pic_path))"""
setup_new = """    import random, string
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        count = conn.execute('SELECT COUNT(*) FROM users WHERE user_code = ?', (code,)).fetchone()[0]
        if count == 0:
            break
            
    conn.execute('INSERT INTO users (email, full_name, password_hash, profile_pic, user_code) VALUES (?, ?, ?, ?, ?)', (email, full_name, password_hash, db_profile_pic_path, code))"""
content = content.replace(setup_orig, setup_new)

# Fix login()
login_orig = """            try:
                conn_log.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                             (f"User Logged In", user['full_name'], 'Logged', 'login'))"""
login_new = """            try:
                conn_log.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                             (f"User Logged In", user['user_code'], 'Logged', 'login'))"""
content = content.replace(login_orig, login_new)

# Fix logout()
logout_orig = """            user = conn_log.execute('SELECT full_name FROM users WHERE id = ?', (user_id,)).fetchone()
            if user:
                conn_log.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                             (f"User Logged Out", user['full_name'], 'Logged', 'logout'))"""
logout_new = """            user = conn_log.execute('SELECT user_code FROM users WHERE id = ?', (user_id,)).fetchone()
            if user:
                conn_log.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)', 
                             (f"User Logged Out", user['user_code'], 'Logged', 'logout'))"""
content = content.replace(logout_orig, logout_new)

# Fix Role Created
role_created_orig = """        user = conn.execute('SELECT full_name FROM users WHERE id = ?', (user_id,)).fetchone()
        user_name = user['full_name'] if user else 'System'
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)',
                     (f"Role Created: {name}", user_name, 'Success', icon))"""
role_created_new = """        user = conn.execute('SELECT user_code FROM users WHERE id = ?', (user_id,)).fetchone()
        user_code = user['user_code'] if user else 'System'
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)',
                     (f"Role Created: {name}", user_code, 'Success', icon))"""
content = content.replace(role_created_orig, role_created_new)

# Fix Role Deleted
role_deleted_orig = """        user = conn.execute('SELECT full_name FROM users WHERE id = ?', (user_id,)).fetchone()
        user_name = user['full_name'] if user else 'System'
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)',
                     (f"Role Deleted: {role_name}", user_name, 'Success', 'delete'))"""
role_deleted_new = """        user = conn.execute('SELECT user_code FROM users WHERE id = ?', (user_id,)).fetchone()
        user_code = user['user_code'] if user else 'System'
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)',
                     (f"Role Deleted: {role_name}", user_code, 'Success', 'delete'))"""
content = content.replace(role_deleted_orig, role_deleted_new)

# Fix User Provisioned
user_prov_orig = """        user = conn.execute('SELECT full_name FROM users WHERE id = ?', (user_id,)).fetchone()
        user_name = user['full_name'] if user else 'System'
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)',
                     (f"User Provisioned: {full_name}", user_name, 'Success', 'person_add'))"""
user_prov_new = """        user = conn.execute('SELECT user_code FROM users WHERE id = ?', (user_id,)).fetchone()
        user_code = user['user_code'] if user else 'System'
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)',
                     (f"User Provisioned: {full_name}", user_code, 'Success', 'person_add'))"""
content = content.replace(user_prov_orig, user_prov_new)

# Fix User Deleted
user_del_orig = """        current_user = conn.execute('SELECT full_name FROM users WHERE id = ?', (current_user_id,)).fetchone()
        current_name = current_user['full_name'] if current_user else 'System'
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)',
                     (f"User Deleted: {target_name}", current_name, 'Success', 'person_remove'))"""
user_del_new = """        current_user = conn.execute('SELECT user_code FROM users WHERE id = ?', (current_user_id,)).fetchone()
        current_code = current_user['user_code'] if current_user else 'System'
        
        conn.execute('INSERT INTO activities (event_name, source, status, icon) VALUES (?, ?, ?, ?)',
                     (f"User Deleted: {target_name}", current_code, 'Success', 'person_remove'))"""
content = content.replace(user_del_orig, user_del_new)

with open('routes/api.py', 'w') as f:
    f.write(content)
print("Updated api.py successfully.")
