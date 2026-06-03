import sqlite3

def fix():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("UPDATE roles SET default_storage = 5 WHERE name = 'Administrator'")
    cursor.execute("UPDATE users SET storage = 5 WHERE job_title = 'Administrator'")
    
    conn.commit()
    conn.close()
    print("Fixed!")

if __name__ == '__main__':
    fix()
