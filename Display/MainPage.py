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
        self.auto_install_triggered = set()
        self.active_tab_index = 0
        self.task_colors = {}
        self.tour_in_progress = True

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
            lbl.bind("<Button-1>", lambda event, index=i: self.on_tab_click(index))
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

    def on_tab_click(self, tab_index):
        """Handles a manual tab click, respecting the guided tour status."""
        if not self.tour_in_progress:
            self.change_tab(tab_index, initial_load=False)
        else:
            print("Automated setup in progress. Please wait.")

    def end_guided_tour(self):
        """Marks the end of the guided tour, enabling manual navigation."""
        print("Automated setup complete. You can now navigate freely.")
        self.tour_in_progress = False

    def set_task_status(self, task_name, task_index, color):
        """Updates the color of a task in the list and stores it."""
        if self.active_tab_index not in self.task_colors:
            self.task_colors[self.active_tab_index] = {}
        
        # Check if the task is still visible at the given index
        if self.tasks_list.size() > task_index and self.tasks_list.get(task_index) == task_name:
            self.task_colors[self.active_tab_index][task_name] = color
            self.tasks_list.itemconfig(task_index, {'bg': color})

    def change_tab(self, tab_index, initial_load=False):
        """Change the active tab and update the task list."""
        self.active_tab_index = tab_index
        self.set_active_tab(tab_index)
        
        # Decide if auto-install should run for this tab
        should_auto_install = (tab_index in [2, 3, 4]) and (tab_index not in self.auto_install_triggered)

        if tab_index == 0:
            update_main_tasks(self, initial_load)
        elif tab_index == 1:
            update_group_policy_tasks(self, initial_load)
        elif tab_index == 2:
            update_dependencies_tasks(self, initial_load, auto_install=should_auto_install)
        elif tab_index == 3:
            update_python_dependencies_tasks(self, initial_load, auto_install=should_auto_install)
        elif tab_index == 4:
            completion_callback = self.end_guided_tour if initial_load else None
            update_programs_tasks(self, initial_load, auto_install=should_auto_install, tour_completion_callback=completion_callback)
        else:
            self.update_tasks([])

        if should_auto_install:
            self.auto_install_triggered.add(tab_index)

    def update_tasks(self, tasks):
        """Update the tasks list with a new list of task names."""
        self.tasks_list.delete(0, tk.END)
        task_colors_for_tab = self.task_colors.get(self.active_tab_index, {})
        for i, task in enumerate(tasks):
            self.tasks_list.insert(tk.END, task)
            if task in task_colors_for_tab:
                self.tasks_list.itemconfig(i, {'bg': task_colors_for_tab[task]})

    def set_active_tab(self, tab_index):
        """Sets the active tab by highlighting it."""
        for i, lbl in enumerate(self.tab_labels):
            lbl.config(bg="#444" if i == tab_index else "#222")