import sqlite3
import customtkinter as ctk
from datetime import datetime

# Initialize CustomTkinter
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

# Database Functions
def authenticate_admin(username, password):
    conn = sqlite3.connect("smart_lock.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM admin WHERE username = ? AND password = ?", (username, password))
    admin = cursor.fetchone()

    if admin:
        log_admin_login(admin[0])
        show_logs_screen()  # Switch to logs screen
    else:
        status_label.configure(text="Invalid credentials", text_color="red")

    conn.close()

def log_admin_login(admin_id):
    conn = sqlite3.connect("smart_lock.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO login_logs (admin_id) VALUES (?)", (admin_id,))
    conn.commit()
    conn.close()

def fetch_logs():
    conn = sqlite3.connect("smart_lock.db")
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM login_logs ORDER BY id DESC")
    logs = cursor.fetchall()
    conn.close()
    return logs

# UI Functions
def login():
    username = username_entry.get()
    password = password_entry.get()
    authenticate_admin(username, password)

def show_logs_screen():
    for widget in root.winfo_children():
        widget.destroy()

    title_label = ctk.CTkLabel(root, text="Login Logs", font=("Arial", 20))
    title_label.pack(pady=10)

    logs = fetch_logs()
    
    log_textbox = ctk.CTkTextbox(root, width=300, height=200)
    log_textbox.pack(pady=10)
    
    for log in logs:
        log_textbox.insert("end", f"{log[0]}\n")
    
    back_button = ctk.CTkButton(root, text="Back to Login", command=show_login_screen)
    back_button.pack(pady=10)

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

    keyboard_button = ctk.CTkButton(root, text="Open Keyboard", command=lambda: show_keyboard(username_entry))
    keyboard_button.pack(pady=5)

    login_button = ctk.CTkButton(root, text="Login", command=login)
    login_button.pack(pady=10)

    status_label = ctk.CTkLabel(root, text="")
    status_label.pack(pady=5)

    # PIN Unlock Button
    pin_unlock_button = ctk.CTkButton(root, text="Enter PIN to Unlock", command=show_pin_screen)
    pin_unlock_button.pack(pady=10)

# Virtual Keyboard
def show_keyboard(entry_widget):
    keyboard = ctk.CTkToplevel(root)
    keyboard.geometry("400x250")
    keyboard.title("Virtual Keyboard")

    keys = [
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
        "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P",
        "A", "S", "D", "F", "G", "H", "J", "K", "L",
        "Z", "X", "C", "V", "B", "N", "M"
    ]

    def insert_key(key):
        entry_widget.insert("end", key)

    def backspace():
        entry_widget.delete(len(entry_widget.get()) - 1)

    row = 0
    col = 0
    for key in keys:
        btn = ctk.CTkButton(keyboard, text=key, width=35, height=30, command=lambda k=key: insert_key(k))
        btn.grid(row=row, column=col, padx=2, pady=2)
        col += 1
        if col > 9:
            col = 0
            row += 1

    backspace_btn = ctk.CTkButton(keyboard, text="⌫", width=60, height=30, command=backspace)
    backspace_btn.grid(row=row + 1, column=0, columnspan=3, padx=2, pady=2)

    close_btn = ctk.CTkButton(keyboard, text="Close", width=60, height=30, command=keyboard.destroy)
    close_btn.grid(row=row + 1, column=3, columnspan=3, padx=2, pady=2)

# PIN Unlock UI
def show_pin_screen():
    for widget in root.winfo_children():
        widget.destroy()

    title_label = ctk.CTkLabel(root, text="Enter PIN to Unlock", font=("Arial", 20))
    title_label.pack(pady=10)

    global pin_entry, pin_result_label
    pin_entry = ctk.CTkEntry(root, show="*")
    pin_entry.pack(pady=5)

    unlock_button = ctk.CTkButton(root, text="Unlock Door", command=unlock_with_pin)
    unlock_button.pack(pady=10)

    pin_result_label = ctk.CTkLabel(root, text="")
    pin_result_label.pack(pady=5)

    back_button = ctk.CTkButton(root, text="Back to Login", command=show_login_screen)
    back_button.pack(pady=10)

# PIN Authentication sd
def unlock_with_pin():
    try:
        pin = int(pin_entry.get())  # Convert input to integer
    except ValueError:
        pin_result_label.configure(text="Invalid PIN format!", text_color="red")
        return

    conn = sqlite3.connect("smart_lock.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM admin WHERE pin = ?", ((int.pin),))
    admin = cursor.fetchone()

    if admin:
        pin_result_label.configure(text=f"Door Unlocked! Welcome {admin[0]}", text_color="green")
    else:
        pin_result_label.configure(text="Invalid PIN!", text_color="red")

    conn.close()


# Initialize Main Window
root = ctk.CTk()
root.geometry("480x320")  # Adjusted for 3.5-inch LCD screen
root.title("Smart Lock System")

# Show Login Screen First
show_login_screen()

# Run App
root.mainloop()
