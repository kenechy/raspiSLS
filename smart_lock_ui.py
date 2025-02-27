import sqlite3
import pytz
import customtkinter as ctk
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

def update_datetime():
    ph_time = datetime.now(pytz.timezone("Asia/Manila"))  # Get PH time
    time_str = ph_time.strftime("%I:%M:%S %p")  # Convert to AM/PM format
    time_label.configure(text=time_str)
    root.after(1000, update_datetime)

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

    query += " ORDER BY timestamp DESC"  # ✅ Ensure newest logs appear first

    cursor.execute(query, params)
    logs = cursor.fetchall()
    conn.close()
    return logs

# Clear Logs
def clear_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admin_logs")
    conn.commit()
    conn.close()
    show_logs_screen()

# Show Login Screen
def show_login_screen():
    for widget in root.winfo_children():
        widget.destroy()

    global username_entry, password_entry, status_label, time_label

    # Time Label (Upper Right Corner)
    time_label = ctk.CTkLabel(root, text="", font=("Arial", 14))
    time_label.place(x=360, y=10)  # Adjusted for upper-right positioning

    update_datetime()  # Start updating time

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


# Show Logs Screen (Now Scrollable)
def show_logs_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # Back Button (Upper-Left Corner)
    back_button = ctk.CTkButton(root, text="⬅ Back", command=show_login_screen)
    back_button.place(x=10, y=10)  

    title_label = ctk.CTkLabel(root, text="Admin Logs", font=("Arial", 20))
    title_label.pack(pady=(40, 10))  

    filter_var = ctk.StringVar(value="All")
    filter_options = ctk.CTkOptionMenu(root, variable=filter_var, values=["All", "Today", "Past Week"], command=lambda _: show_logs_screen())
    filter_options.pack(pady=5)

    logs = fetch_logs(filter_var.get())  # Fetch logs in descending order

    # Frame to hold success & failed logs side by side
    logs_container = ctk.CTkFrame(root)
    logs_container.pack(fill="both", expand=True, padx=10, pady=5)

    # ✅ Scrollable Frame for Successful Attempts (LEFT)
    success_frame = ctk.CTkScrollableFrame(logs_container, width=220, height=200)
    success_frame.pack(side="left", fill="both", expand=True, padx=5)

    # ✅ Scrollable Frame for Failed Attempts (RIGHT)
    failed_frame = ctk.CTkScrollableFrame(logs_container, width=220, height=200)
    failed_frame.pack(side="right", fill="both", expand=True, padx=5)

    ctk.CTkLabel(success_frame, text="✅ Successful Attempts").pack(pady=5)
    ctk.CTkLabel(failed_frame, text="❌ Failed Attempts").pack(pady=5)

    for log in logs:
        timestamp, status, input_type = log
        formatted_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%b %d, %Y %I:%M %p")  # Convert to readable format

        log_entry = f"{formatted_time} - {input_type}"

        if status == "Success":
            ctk.CTkLabel(success_frame, text=log_entry).pack(anchor="w", padx=10, pady=2)
        else:
            ctk.CTkLabel(failed_frame, text=log_entry).pack(anchor="w", padx=10, pady=2)
  
# Show PIN Screen
def show_pin_screen():
    for widget in root.winfo_children():
        widget.destroy()

    global time_label
    time_label = ctk.CTkLabel(root, text="", font=("Arial", 14))
    time_label.place(x=360, y=10)

    update_datetime()

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