import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import ctypes
import sys
import os
from typing import Optional
from Display.MainPage import MainPage
from Display.mysqlPage import MysqlConfigFrame
from Controller.mysql import open_mysql_connection, close_mysql_connection, select_all_users, select_all_programs, select_all_group_policy, select_all_python_dependencies, select_all_uninstall_programs, select_all_windows_settings
from Controller.config import config_manager
from utils.logger import logger
from pathlib import Path

# Initialize logging
logger.log_startup()

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
    root = ttk.Window(themename="darkly")
    root.title("Sustav za automatizaciju instalacije softvera")
    root.geometry("800x600")

    def show_main_app():
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        # First tab: main screen
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Početna")

        # Second tab: automation workflow (add later)
        automation_frame = ttk.Frame(notebook)
        automation_tab_added = [False]  # Use a list for mutability in closure

        # --- Main tab content ---
        naziv_racunala_var = tk.StringVar()
        naziv_racunala_label = ttk.Label(main_frame, text="Naziv računala:")
        naziv_racunala_label.pack(pady=(10, 0))
        naziv_racunala_entry = ttk.Entry(main_frame, textvariable=naziv_racunala_var, width=30)
        naziv_racunala_entry.pack(pady=(0, 10))
        
        windows_key_var = tk.StringVar()
        windows_key_label = ttk.Label(main_frame, text="Windows ključ:")
        windows_key_label.pack(pady=(10, 0))
        windows_key_entry = ttk.Entry(main_frame, textvariable=windows_key_var, width=30)
        windows_key_entry.pack(pady=(0, 10))
        # Load existing key
        try:
            windows_key_var.set(config_manager.get_windows_key())
        except Exception as e:
            logger.warning(f"Could not load Windows key: {e}", file=Path(__file__).name)

        label = ttk.Label(main_frame, text="Sustav za automatizaciju instalacije softvera", wraplength=350)
        label.pack(pady=20)

        def on_automation_finished():
            btn.config(state='normal')
            naziv_racunala_entry.config(state='normal')
            windows_key_entry.config(state='normal')

        def start_main_page():
            try:
                # Save configuration using config manager
                config_manager.update_data({"Naziv računala": naziv_racunala_var.get()})
                config_manager.update_config({"windows_key": windows_key_var.get()})
            except Exception as e:
                logger.error(f"Failed to save configuration: {e}", file=Path(__file__).name)
                messagebox.showerror("Error", f"Failed to save configuration: {e}")
                return

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
            windows_key_entry.config(state='disabled')
            page = MainPage(automation_frame, on_automation_finished=on_automation_finished)
            page.pack(fill="both", expand=True)

            # Try to open MySQL connection and fetch users (now only after config is valid)
            try:
                open_mysql_connection()
                print("MySQL connection opened.")
            except Exception as e:
                logger.error(f"Could not connect to MySQL or fetch users: {e}", file=Path(__file__).name)

        btn = ttk.Button(main_frame, text="Pokreni", command=start_main_page, bootstyle=SUCCESS)
        btn.pack(pady=10)

    # MySQL config logic
    try:
        config = config_manager.get_config()
        # Try to initialize MySQL if config is complete
        mysql_fields = ["mysql_host", "mysql_port", "mysql_user", "mysql_password", "mysql_database"]
        if all(config.get(f) for f in mysql_fields):
            try:
                open_mysql_connection()
                select_all_programs()
                select_all_group_policy()
                select_all_python_dependencies()
                select_all_uninstall_programs()
                select_all_windows_settings()
                logger.info("MySQL initialization completed successfully", file=Path(__file__).name)
            except Exception as e:
                logger.error(f"MySQL initialization failed: {e}", file=Path(__file__).name)
    except Exception as e:
        config = {}
        logger.error(f"Error loading config: {e}", file=Path(__file__).name)
    mysql_fields = ["mysql_host", "mysql_user", "mysql_password", "mysql_database"]
    if any(not config.get(f) for f in mysql_fields):
        def after_mysql():
            mysql_frame.destroy()
            try:
                open_mysql_connection()
                # Clear MySQL config cache and reinitialize
                config_manager.clear_cache()
                select_all_programs()
                select_all_group_policy()
                select_all_python_dependencies()
                select_all_uninstall_programs()
                select_all_windows_settings()
                logger.info("MySQL connection opened.", file=Path(__file__).name)
            except Exception as e:
                logger.error(f"Could not connect to MySQL or fetch users: {e}", file=Path(__file__).name)
            show_main_app()
        mysql_frame = MysqlConfigFrame(root, str(config_manager.config_file), config, on_save=after_mysql)
        mysql_frame.pack(fill="both", expand=True)
    else:
        show_main_app()

    root.protocol("WM_DELETE_WINDOW", cleanup_and_exit)
    root.mainloop()

if __name__ == "__main__":
    main()