import tkinter as tk
from tkinter import ttk
import json
import os
from .WindowsSettingsPage import update_main_tasks
from .GroupPolicy import update_group_policy_tasks
from .InstallDependencies import update_dependencies_tasks
from .InstallPythonDependenciesPage import update_python_dependencies_tasks
from .InstallProgramsPage import update_programs_tasks

class MainPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Main layout: left for tabs, right for tasks
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Vertical tabs on the left (non-interactive)
        tab_names = ["Postavljanje Windowsa", "Group Policy", "Instalacija dodataka", "Instalacija python dodataka", "Instalacija programa"]
        tabs_frame = tk.Frame(self, bg="#222")
        tabs_frame.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)
        self.tab_labels = []
        for i, name in enumerate(tab_names):
            lbl = tk.Label(
                tabs_frame,
                text=name,
                anchor="w",
                width=16,
                padx=10,
                pady=10,
                bg="#444" if i == 0 else "#222",  # Highlight first tab as active
                fg="#fff"
            )
            lbl.pack(fill="x", pady=2)
            lbl.bind("<Button-1>", lambda event, index=i: self.change_tab(index, initial_load=False))
            self.tab_labels.append(lbl)

        # Tasks on the right with scrollbar
        tasks_frame = ttk.Frame(self)
        tasks_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        tasks_frame.columnconfigure(0, weight=1)
        tasks_frame.rowconfigure(1, weight=1)

        tasks_label = ttk.Label(tasks_frame, text="Popis zadataka")
        tasks_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.tasks_list = tk.Listbox(tasks_frame, height=10)
        self.tasks_list.grid(row=1, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(tasks_frame, orient=tk.VERTICAL, command=self.tasks_list.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tasks_list.config(yscrollcommand=scrollbar.set)

        self.change_tab(0, initial_load=True)

    def change_tab(self, tab_index, initial_load=False):
        """Change the active tab and update the task list."""
        self.set_active_tab(tab_index)
        if tab_index == 0:
            update_main_tasks(self, initial_load)
        elif tab_index == 1:
            update_group_policy_tasks(self, initial_load)
        elif tab_index == 2:
            update_dependencies_tasks(self, initial_load)
        elif tab_index == 3:
            update_python_dependencies_tasks(self, initial_load)
        elif tab_index == 4:
            update_programs_tasks(self, initial_load)
        else:
            # Clear tasks for other tabs for now
            self.update_tasks([])

    def update_tasks(self, tasks):
        """Update the tasks list with a new list of task names."""
        self.tasks_list.delete(0, tk.END)
        for task in tasks:
            self.tasks_list.insert(tk.END, task)
        
    def set_active_tab(self, tab_index):
        """Sets the active tab by highlighting it."""
        for i, lbl in enumerate(self.tab_labels):
            lbl.config(bg="#444" if i == tab_index else "#222")