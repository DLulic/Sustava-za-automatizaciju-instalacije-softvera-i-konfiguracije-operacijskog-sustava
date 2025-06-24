import tkinter as tk
from tkinter import messagebox
import ctypes
import sys
import os
import datetime
import json
from Display.MainPage import MainPage

# Redirect all output to a log file, creating it if it doesn't exist
log_path = os.path.join(os.path.dirname(__file__), 'app.log')
if not os.path.exists(log_path):
    with open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"\n--- App started at {datetime.datetime.now()} ---\n")
else:
    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"\n--- App started at {datetime.datetime.now()} ---\n")
sys.stdout = open(log_path, 'a', encoding='utf-8')
sys.stderr = open(log_path, 'a', encoding='utf-8')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def open_start_page(root, content_frame):
    # Remove current widgets from the content frame
    for widget in content_frame.winfo_children():
        widget.destroy()
    # Add MainPage to the content frame
    page = MainPage(content_frame)
    page.pack(fill="both", expand=True)

def main():
    if not is_admin():
        # Use pythonw.exe for no console
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", pythonw, params, os.getcwd(), 1
            )
        except Exception as e:
            tk.Tk().withdraw()
            messagebox.showerror(
                "Administrator Privileges Required",
                f"Failed to elevate privileges: {e}"
            )
        sys.exit(0)

    root = tk.Tk()
    dark_mode = True  # Set to True for dark mode, False for light mode
    if dark_mode:
        root.tk_setPalette(background='#2E2E2E', foreground='#FFFFFF')
        root.option_add('*TButton*highlightBackground', '#2E2E2E')
        root.option_add('*TButton*highlightColor', '#2E2E2E')
    else:
        root.tk_setPalette(background='#FFFFFF', foreground='#000000')
    root.title("Sustav za automatizaciju instalacije softvera")
    root.geometry("400x200")

    content_frame = tk.Frame(root)
    content_frame.pack(fill="both", expand=True)

    # Center the window on the screen
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 800
    window_height = 600
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Dvorana input field
    naziv_racunala_var = tk.StringVar()
    naziv_racunala_label = tk.Label(content_frame, text="Naziv računala:")
    naziv_racunala_label.pack(pady=(10, 0))
    naziv_racunala_entry = tk.Entry(content_frame, textvariable=naziv_racunala_var, width=30)
    naziv_racunala_entry.pack(pady=(0, 10))

    label = tk.Label(content_frame, text="Sustav za automatizaciju instalacije softvera", wraplength=350)
    label.pack(pady=20)

    def start_main_page():
        # Save dvorana_var to Storage/dvorana.json
        storage_dir = os.path.join(os.path.dirname(__file__), 'Storage')
        os.makedirs(storage_dir, exist_ok=True)
        data_path = os.path.join(storage_dir, 'data.json')
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump({"Naziv računala": naziv_racunala_var.get()}, f, ensure_ascii=False, indent=2)
        # Continue to main page
        for widget in content_frame.winfo_children():
            widget.destroy()
        page = MainPage(content_frame)
        page.pack(fill="both", expand=True)

    btn = tk.Button(content_frame, text="Pokreni", command=start_main_page)
    btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()