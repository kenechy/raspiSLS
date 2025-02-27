import sqlite3
from datetime import datetime

# Database initialization
def init_db():
    conn = sqlite3.connect("smart_lock.db")
    cursor = conn.cursor()

    # Create admin table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # Create login logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (admin_id) REFERENCES admin(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

# Function to add an admin (Run once to set up the admin)
def add_admin(username, password):
    conn = sqlite3.connect("smart_lock.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print("Admin account created successfully.")
    except sqlite3.IntegrityError:
        print("Error: Admin username already exists.")

    conn.close()

# Function to log admin login
def log_admin_login(admin_id):
    conn = sqlite3.connect("smart_lock.db")
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO login_logs (admin_id) VALUES (?)", (admin_id,))
    conn.commit()
    conn.close()

# Function to authenticate admin
def authenticate_admin(username, password):
    conn = sqlite3.connect("smart_lock.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM admin WHERE username = ? AND password = ?", (username, password))
    admin = cursor.fetchone()

    if admin:
        print("Login successful.")
        log_admin_login(admin[0])
        return True
    else:
        print("Invalid username or password.")
        return False

    conn.close()

# Initialize database (Run this once)
init_db()

# Example usage:
# Run this once to add an admin (change credentials as needed)
# add_admin("admin", "password123")

# Authenticate admin (for login)
# authenticate_admin("admin", "password123")
