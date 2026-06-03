import sqlite3
import random
import string

def fix():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 1. Create Administrator role if it doesn't exist
    role = cursor.execute("SELECT id FROM roles WHERE name = 'Administrator'").fetchone()
    if not role:
        cursor.execute("INSERT INTO roles (name, icon, color, default_storage) VALUES (?, ?, ?, ?)", ('Administrator', 'shield', '#448aff', 50))
        role_id = cursor.lastrowid
    else:
        role_id = role[0]
        
    # 2. Update user to have the role and storage
    users = cursor.execute("SELECT id FROM users").fetchall()
    for user in users:
        user_id = user[0]
        cursor.execute("UPDATE users SET role_id = ?, storage = 50, job_title = 'Administrator' WHERE id = ?", (role_id, user_id))
        
    # 3. Delete the false "Storage Allocated: 500GB" activity
    cursor.execute("DELETE FROM activities WHERE event_name = 'Storage Allocated: 500GB'")
    
    conn.commit()
    conn.close()
    print("Fixed!")

if __name__ == '__main__':
    fix()
