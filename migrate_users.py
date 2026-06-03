import sqlite3
import random
import string

def generate_user_code(cursor):
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        count = cursor.execute('SELECT COUNT(*) FROM users WHERE user_code = ?', (code,)).fetchone()[0]
        if count == 0:
            return code

def migrate():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 1. Add columns
    columns = [
        "first_name TEXT",
        "last_name TEXT",
        "job_title TEXT",
        "storage INTEGER",
        "user_code TEXT"
    ]
    
    for col in columns:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass
        
    # 2. Update existing users
    users = cursor.execute("SELECT id, full_name FROM users").fetchall()
    
    for user_id, full_name in users:
        code = generate_user_code(cursor)
        
        parts = full_name.split(' ', 1)
        first_name = parts[0] if parts else ""
        last_name = parts[1] if len(parts) > 1 else ""
        
        cursor.execute("""
            UPDATE users 
            SET first_name = ?, last_name = ?, job_title = ?, storage = ?, user_code = ?
            WHERE id = ?
        """, (first_name, last_name, "Administrator", 50, code, user_id))
        
    conn.commit()
    conn.close()
    print("Migration successful.")

if __name__ == '__main__':
    migrate()
