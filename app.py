import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

# --- Constants ---
DATA_FILE = "mood_data.json"
CREDENTIALS_FILE = "credentials.json"
REMINDER_INTERVAL = 86400  # 24 hours

# --- Ensure mood file exists ---
if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# --- Ensure credentials exist ---
def ensure_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump({"username": "admin", "password": "admin"}, f)

# --- Authenticate User ---
def login_screen():
    login = tk.Tk()
    login.title("🔐 Login")
    login.geometry("300x200")
    login.configure(bg="#2C2C2C")

    tk.Label(login, text="Username", bg="#2C2C2C", fg="white").pack(pady=5)
    user_entry = tk.Entry(login)
    user_entry.pack()

    tk.Label(login, text="Password", bg="#2C2C2C", fg="white").pack(pady=5)
    pass_entry = tk.Entry(login, show="*")
    pass_entry.pack()

    def verify():
        with open(CREDENTIALS_FILE, "r") as f:
            creds = json.load(f)
        if user_entry.get() == creds['username'] and pass_entry.get() == creds['password']:
            login.destroy()
            start_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    tk.Button(login, text="Login", command=verify, bg="#4CAF50", fg="white").pack(pady=10)
    login.mainloop()

# --- Save Entry ---
def save_entry():
    mood = mood_var.get()
    note = journal_text.get("1.0", tk.END).strip()
    if not mood or not note:
        messagebox.showwarning("Missing Info", "Please select a mood and write something.")
        return

    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mood": mood,
        "note": note
    }

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = []

    data.append(entry)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    messagebox.showinfo("Saved", "✅ Your mood has been logged.")
    journal_text.delete("1.0", tk.END)
    mood_var.set("")

# --- View Entries ---
def view_entries():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    
    viewer = tk.Toplevel(root)
    viewer.title("📜 Past Entries")
    viewer.geometry("500x400")
    text = tk.Text(viewer)
    text.pack(expand=True, fill='both')

    for e in data:
        text.insert(tk.END, f"{e['date']} | {e['mood']}\n{e['note']}\n{'-'*50}\n")

# --- Filter Entries ---
def filter_entries():
    mood_filter = filter_var.get()
    date_filter = date_entry.get()

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    result = []
    for e in data:
        if (not mood_filter or mood_filter in e['mood']) and (not date_filter or date_filter in e['date']):
            result.append(e)

    result_win = tk.Toplevel(root)
    result_win.title("🔍 Filtered Entries")
    result_win.geometry("500x400")
    text = tk.Text(result_win)
    text.pack(expand=True, fill='both')

    for e in result:
        text.insert(tk.END, f"{e['date']} | {e['mood']}\n{e['note']}\n{'-'*50}\n")

# --- Export ---
def export_entries():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if file_path:
        with open(file_path, "w") as f:
            for e in data:
                f.write(f"{e['date']} | {e['mood']}\n{e['note']}\n{'-'*50}\n")
        messagebox.showinfo("Exported", "Entries exported successfully!")

# --- Chart ---
def mood_chart():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    mood_count = {}
    for e in data:
        mood_count[e['mood']] = mood_count.get(e['mood'], 0) + 1

    chart_win = tk.Toplevel(root)
    chart_win.title("📊 Mood Distribution")
    fig, ax = plt.subplots()
    ax.bar(mood_count.keys(), mood_count.values())
    ax.set_title("Mood Frequency")
    ax.set_ylabel("Count")

    canvas = FigureCanvasTkAgg(fig, master=chart_win)
    canvas.draw()
    canvas.get_tk_widget().pack()

# --- Reminder ---
def reminder_loop():
    def loop():
        while True:
            time.sleep(REMINDER_INTERVAL)
            messagebox.showinfo("Reminder", "🧠 Time to log your mood!")
    threading.Thread(target=loop, daemon=True).start()

# --- Start Main App ---
def start_app():
    global root, mood_var, journal_text, filter_var, date_entry
    root = tk.Tk()
    root.title("🧠 Mood Journal")
    root.geometry("600x600")
    root.config(bg="#2E2E2E")

    tk.Label(root, text="How are you feeling today?", bg="#2E2E2E", fg="white", font=("Segoe UI", 12)).pack(pady=10)
    mood_var = tk.StringVar()
    tk.OptionMenu(root, mood_var, "😊 Happy", "😢 Sad", "😐 Neutral", "😡 Angry", "😴 Tired", "😌 Grateful").pack()

    tk.Label(root, text="Write your thoughts below:", bg="#2E2E2E", fg="white", font=("Segoe UI", 10)).pack(pady=10)
    journal_text = tk.Text(root, height=10, width=60)
    journal_text.pack(pady=5)

    tk.Button(root, text="💾 Save Entry", command=save_entry, bg="#4CAF50", fg="white").pack(pady=10)
    tk.Button(root, text="📜 View Past Entries", command=view_entries).pack(pady=5)
    tk.Button(root, text="🔍 Filter Entries", command=filter_entries).pack(pady=5)
    tk.Button(root, text="📈 Mood Chart", command=mood_chart).pack(pady=5)
    tk.Button(root, text="📤 Export to File", command=export_entries).pack(pady=5)

    filter_var = tk.StringVar()
    tk.Label(root, text="Mood to Filter (Optional):", bg="#2E2E2E", fg="white").pack()
    tk.Entry(root, textvariable=filter_var).pack()
    date_entry = tk.Entry(root)
    tk.Label(root, text="Date to Filter (Optional YYYY-MM-DD):", bg="#2E2E2E", fg="white").pack()
    date_entry.pack()

    reminder_loop()
    root.mainloop()

# --- Launch App ---
ensure_credentials()
login_screen()
