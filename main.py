import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import sys
import os
import datetime
import json
from Display.MainPage import MainPage
from Display.mysqlPage import MysqlConfigFrame
from Controller.mysql import open_mysql_connection, close_mysql_connection, select_all_users, select_all_programs, select_all_group_policy, select_all_python_dependencies, select_all_uninstall_programs, select_all_windows_settings

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

def cleanup_and_exit():
    close_mysql_connection()
    root.destroy()

def main():
    if not is_admin():
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

    global root
    root = tk.Tk()
    dark_mode = True  # Set to True for dark mode, False for light mode
    if dark_mode:
        root.tk_setPalette(background='#2E2E2E', foreground='#FFFFFF')
        root.option_add('*TButton*highlightBackground', '#2E2E2E')
        root.option_add('*TButton*highlightColor', '#2E2E2E')
        style = ttk.Style()
        style.theme_use('default')
        style.configure('.', background='#2E2E2E', foreground='#FFFFFF')
        style.configure('TNotebook', background='#222222', foreground='#FFFFFF')
        style.configure('TNotebook.Tab', background='#444444', foreground='#FFFFFF')
        style.map('TNotebook.Tab', background=[('selected', '#2E2E2E')], foreground=[('selected', '#FFFFFF')])
        style.configure('TLabel', background='#2E2E2E', foreground='#FFFFFF')
        style.configure('TEntry', fieldbackground='#444444', foreground='#FFFFFF')
        style.configure('TFrame', background='#2E2E2E')
    else:
        root.tk_setPalette(background='#FFFFFF', foreground='#000000')
    root.title("Sustav za automatizaciju instalacije softvera")
    root.geometry("800x600")

    def show_main_app():
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        # First tab: main screen
        main_frame = tk.Frame(notebook)
        notebook.add(main_frame, text="Početna")

        # Second tab: automation workflow (add later)
        automation_frame = tk.Frame(notebook)
        automation_tab_added = [False]  # Use a list for mutability in closure

        # --- Main tab content ---
        naziv_racunala_var = tk.StringVar()
        naziv_racunala_label = tk.Label(main_frame, text="Naziv računala:")
        naziv_racunala_label.pack(pady=(10, 0))
        naziv_racunala_entry = tk.Entry(main_frame, textvariable=naziv_racunala_var, width=30)
        naziv_racunala_entry.pack(pady=(0, 10))

        label = tk.Label(main_frame, text="Sustav za automatizaciju instalacije softvera", wraplength=350)
        label.pack(pady=20)

        def on_automation_finished():
            btn.config(state='normal')
            naziv_racunala_entry.config(state='normal')

        def start_main_page():
            # Save to Storage/data.json
            storage_dir = os.path.join(os.path.dirname(__file__), 'Storage')
            os.makedirs(storage_dir, exist_ok=True)
            data_path = os.path.join(storage_dir, 'data.json')
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump({"Naziv računala": naziv_racunala_var.get()}, f, ensure_ascii=False, indent=2)
            # Add automation tab if not already present
            if not automation_tab_added[0]:
                notebook.add(automation_frame, text="Automatizacija")
                automation_tab_added[0] = True
            # Switch to automation tab
            notebook.select(1)
            # Re-initialize MainPage each time
            for widget in automation_frame.winfo_children():
                widget.destroy()
            btn.config(state='disabled')
            naziv_racunala_entry.config(state='disabled')
            page = MainPage(automation_frame, on_automation_finished=on_automation_finished)
            page.pack(fill="both", expand=True)

            # Try to open MySQL connection and fetch users (now only after config is valid)
            try:
                open_mysql_connection()
                print("MySQL connection opened.")
            except Exception as e:
                print(f"Could not connect to MySQL or fetch users: {e}")

        btn = tk.Button(main_frame, text="Pokreni", command=start_main_page)
        btn.pack(pady=10)

    # MySQL config logic
    config_path = os.path.join(os.path.dirname(__file__), 'Storage', 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            open_mysql_connection()
            select_all_programs()
            select_all_group_policy()
            select_all_python_dependencies()
            select_all_uninstall_programs()
            select_all_windows_settings()
    else:
        config = {}
    mysql_fields = ["mysql_host", "mysql_user", "mysql_password", "mysql_database"]
    if any(not config.get(f) for f in mysql_fields):
        def after_mysql():
            mysql_frame.destroy()
            try:
                open_mysql_connection()
                print("MySQL connection opened.")
                select_all_programs()
                select_all_group_policy()
                select_all_python_dependencies()
                select_all_uninstall_programs()
                select_all_windows_settings()
            except Exception as e:
                import traceback
                print(f"Could not connect to MySQL or fetch users: {e}")
                traceback.print_exc()
            show_main_app()
        mysql_frame = MysqlConfigFrame(root, config_path, config, on_save=after_mysql)
        mysql_frame.pack(fill="both", expand=True)
    else:
        show_main_app()

    root.protocol("WM_DELETE_WINDOW", cleanup_and_exit)
    root.mainloop()

if __name__ == "__main__":
    main()