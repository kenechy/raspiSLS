import sqlite3
import customtkinter as ctk
from datetime import datetime, timedelta

# Database setup
DB_PATH = "smart_lock.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Admin table
    cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        pin TEXT)''')

    # Logs table
    cursor.execute('''CREATE TABLE IF NOT EXISTS admin_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        status TEXT NOT NULL,
                        input_type TEXT NOT NULL)''')

    conn.commit()
    conn.close()

create_tables()  # Ensure tables exist

# Function to log attempts
def log_attempt(status, input_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO admin_logs (timestamp, status, input_type) VALUES (?, ?, ?)", 
                   (timestamp, status, input_type))
    conn.commit()
    conn.close()
    refresh_logs()  # Update the UI after logging

# Function to fetch logs based on filters
def get_logs(filter_type="All"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT timestamp, status, input_type FROM admin_logs"
    params = ()

    if filter_type == "Today":
        query += " WHERE timestamp >= ?"
        params = (datetime.now().strftime("%Y-%m-%d 00:00:00"),)
    elif filter_type == "Past Week":
        query += " WHERE timestamp >= ?"
        params = ((datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00"),)

    cursor.execute(query, params)
    logs = cursor.fetchall()
    conn.close()
    return logs

# Function to refresh logs in UI
def refresh_logs():
    for widget in success_frame.winfo_children():
        widget.destroy()
    for widget in failed_frame.winfo_children():
        widget.destroy()
    
    logs = get_logs(filter_var.get())
    
    for log in logs:
        timestamp, status, input_type = log
        if status == "Success":
            ctk.CTkLabel(success_frame, text=f"{timestamp} - {input_type}").pack(anchor="w", padx=10, pady=2)
        else:
            ctk.CTkLabel(failed_frame, text=f"{timestamp} - {input_type}").pack(anchor="w", padx=10, pady=2)

# Function to clear logs
def clear_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admin_logs")
    conn.commit()
    conn.close()
    refresh_logs()

# Function to handle password authentication
def authenticate_password(input_password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM admin WHERE password = ?", (input_password,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        log_attempt("Success", "Password")
    else:
        log_attempt("Failed", "Password")

# Function to handle PIN authentication
def authenticate_pin(input_pin):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM admin WHERE pin = ?", (input_pin,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        log_attempt("Success", "PIN")
    else:
        log_attempt("Failed", "PIN")

# GUI Setup
root = ctk.CTk()
root.title("Smart Lock System")
root.geometry("600x500")

# Login Section
ctk.CTkLabel(root, text="Enter Password:").pack()
password_entry = ctk.CTkEntry(root, show="*")
password_entry.pack()
ctk.CTkButton(root, text="Login", command=lambda: authenticate_password(password_entry.get())).pack(pady=5)

ctk.CTkLabel(root, text="Enter PIN:").pack()
pin_entry = ctk.CTkEntry(root)
pin_entry.pack()
ctk.CTkButton(root, text="Unlock with PIN", command=lambda: authenticate_pin(pin_entry.get())).pack(pady=5)

# Filter Logs
filter_var = ctk.StringVar(value="All")
filter_options = ctk.CTkOptionMenu(root, variable=filter_var, values=["All", "Today", "Past Week"], command=lambda _: refresh_logs())
filter_options.pack(pady=5)

# Success Logs Section
ctk.CTkLabel(root, text="✅ Successful Attempts").pack()
success_frame = ctk.CTkFrame(root)
success_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Failed Logs Section
ctk.CTkLabel(root, text="❌ Failed Attempts").pack()
failed_frame = ctk.CTkFrame(root)
failed_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Clear Logs Button
ctk.CTkButton(root, text="Clear Logs", fg_color="red", command=clear_logs).pack(pady=10)

# Initial log load
refresh_logs()

root.mainloop()
