import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
import os
from tkinter import messagebox
import time
from Controller.mysql import open_mysql_connection


class MysqlConfigFrame(ttk.Frame):
    def __init__(self, parent, config_path, config, on_save=None):
        super().__init__(parent)
        self.config_path = config_path
        self.config = config
        self.on_save = on_save
        self.entries = {}
        fields = [
            ("mysql_host", "Host"),
            ("mysql_user", "Korisnik"),
            ("mysql_port", "Port"),
            ("mysql_password", "Lozinka"),
            ("mysql_database", "Baza")
        ]
        for i, (key, label) in enumerate(fields):
            ttk.Label(self, text=label+":").grid(row=i, column=0, sticky="e", padx=10, pady=5)
            ent = ttk.Entry(self, width=25, show="*" if key=="mysql_password" else None)
            ent.grid(row=i, column=1, padx=10, pady=5)
            if config.get(key):
                ent.insert(0, str(config[key]))
            self.entries[key] = ent

        btn = ttk.Button(self, text="Spremi", command=self.save_and_continue, bootstyle=SUCCESS)
        btn.grid(row=len(fields), column=0, columnspan=2, pady=15)

    def save_and_continue(self):
        for key, ent in self.entries.items():
            val = ent.get().strip()
            if key == "mysql_port":
                try:
                    val = int(val)
                except Exception:
                    val = 3306
            self.config[key] = val
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

        # Try to connect to MySQL
        try:
            time.sleep(0.5)
            open_mysql_connection()
        except Exception as e:
            messagebox.showerror("MySQL Connection Error", f"Could not connect to MySQL:\n{e}")
            return  # Do not proceed, let user correct info
        if self.on_save:
            self.on_save()
