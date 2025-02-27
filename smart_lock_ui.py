import sqlite3
import customtkinter as ctk
import time
from datetime import datetime, timedelta

# Initialize CustomTkinter
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

DB_PATH = "smart_lock.db"

# Database Setup
def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        pin TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS admin_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        status TEXT NOT NULL,
                        input_type TEXT NOT NULL)''')

    conn.commit()
    conn.close()

create_tables()



# Log Admin Login Attempt
def log_attempt(status, input_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO admin_logs (timestamp, status, input_type) VALUES (?, ?, ?)", 
                   (timestamp, status, input_type))
    conn.commit()
    conn.close()

# Authenticate Admin
def authenticate_admin(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM admin WHERE username = ? AND password = ?", (username, password))
    admin = cursor.fetchone()
    
    if admin:
        log_attempt("Success", "Password")
        show_logs_screen()
    else:
        log_attempt("Failed", "Password")
        status_label.configure(text="Invalid credentials", text_color="red")
    
    conn.close()

# Authenticate PIN
def authenticate_pin(pin):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM admin WHERE pin = ?", (pin,))
    admin = cursor.fetchone()

    if admin:
        log_attempt("Success", "PIN")
        pin_result_label.configure(text=f"Door Unlocked! Welcome {admin[0]}", text_color="green")
    else:
        log_attempt("Failed", "PIN")
        pin_result_label.configure(text="Invalid PIN!", text_color="red")

    conn.close()

# Fetch Logs
def fetch_logs(filter_type="All"):
    """Fetch logs from database in descending order (newest first)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    base_query = "SELECT timestamp, status, input_type FROM admin_logs"
    order_by = " ORDER BY timestamp DESC"
    params = ()

    if filter_type == "Today":
        base_query += " WHERE timestamp >= ?"
        params = (datetime.now().strftime("%Y-%m-%d 00:00:00"),)
    elif filter_type == "Past Week":
        base_query += " WHERE timestamp >= ?"
        params = ((datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00"),)

    full_query = base_query + order_by
    cursor.execute(full_query, params)
    logs = cursor.fetchall()
    conn.close()
    return logs




# Show Login Screen
def show_login_screen():
    for widget in root.winfo_children():
        widget.destroy()

    global username_entry, password_entry, status_label

    title_label = ctk.CTkLabel(root, text="Admin Login", font=("Arial", 20))
    title_label.pack(pady=10)

    username_entry = ctk.CTkEntry(root, placeholder_text="Username")
    username_entry.pack(pady=5)

    password_entry = ctk.CTkEntry(root, placeholder_text="Password", show="*")
    password_entry.pack(pady=5)

    login_button = ctk.CTkButton(root, text="Login", command=lambda: authenticate_admin(username_entry.get(), password_entry.get()))
    login_button.pack(pady=10)

    status_label = ctk.CTkLabel(root, text="")
    status_label.pack(pady=5)

    pin_unlock_button = ctk.CTkButton(root, text="Enter PIN to Unlock", command=show_pin_screen)
    pin_unlock_button.pack(pady=10)


def show_logs_screen():
    for widget in root.winfo_children():
        widget.destroy()

    back_button = ctk.CTkButton(root, text="⬅", width=40, height=30, font=("Arial", 14), command=show_login_screen)
    back_button.place(x=10, y=10)

    global datetime_label
    datetime_label = ctk.CTkLabel(root, text="", font=("Arial", 14))
    datetime_label.place(x=320, y=10)
    

    title_label = ctk.CTkLabel(root, text="Admin Logs", font=("Arial", 20))
    title_label.pack(pady=(40, 10))

    filter_var = ctk.StringVar(value="All")
    filter_options = ctk.CTkOptionMenu(root, variable=filter_var, values=["All", "Today", "Past Week"], command=lambda _: show_logs_screen())
    filter_options.pack(pady=5)

    logs = fetch_logs(filter_var.get())

    scrollable_frame = ctk.CTkScrollableFrame(root, width=450, height=200)
    scrollable_frame.pack(padx=10, pady=5, fill="both", expand=True)

    success_frame = ctk.CTkFrame(scrollable_frame)
    success_frame.pack(fill="both", expand=True, padx=10, pady=5)

    failed_frame = ctk.CTkFrame(scrollable_frame)
    failed_frame.pack(fill="both", expand=True, padx=10, pady=5)

    ctk.CTkLabel(success_frame, text="✅ Successful Attempts").pack()
    ctk.CTkLabel(failed_frame, text="❌ Failed Attempts").pack()

    for log in logs:
        timestamp, status, input_type = log
        log_entry = f"{timestamp} - {input_type}"
        if status == "Success":
            ctk.CTkLabel(success_frame, text=log_entry).pack(anchor="w", padx=10, pady=2)
        else:
            ctk.CTkLabel(failed_frame, text=log_entry).pack(anchor="w", padx=10, pady=2)

    clear_logs_button = ctk.CTkButton(root, text="Clear Logs", fg_color="red", command=clear_logs)
    clear_logs_button.pack(pady=10)
# Show PIN Screen
def show_pin_screen():
    for widget in root.winfo_children():
        widget.destroy()

    title_label = ctk.CTkLabel(root, text="Enter PIN to Unlock", font=("Arial", 20))
    title_label.pack(pady=10)

    global pin_entry, pin_result_label
    pin_entry = ctk.CTkEntry(root, show="*")
    pin_entry.pack(pady=5)

    unlock_button = ctk.CTkButton(root, text="Unlock Door", command=lambda: authenticate_pin(pin_entry.get()))
    unlock_button.pack(pady=10)

    pin_result_label = ctk.CTkLabel(root, text="")
    pin_result_label.pack(pady=5)

    back_button = ctk.CTkButton(root, text="Back to Login", command=show_login_screen)
    back_button.pack(pady=10)

# Initialize Main Window
root = ctk.CTk()
root.geometry("480x320")  # Adjusted for 3.5-inch LCD screen
root.title("Smart Lock System")

show_login_screen()

root.mainloop()
