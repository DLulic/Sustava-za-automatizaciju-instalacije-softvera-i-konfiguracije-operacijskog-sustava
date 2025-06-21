import json
import os

def update_dependencies_tasks(page_instance, initial_load=False):
    """Load tasks from DependenciesWinget.json for 'Instalacija dodataka' and update the task list."""
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "Functions",
        "DependenciesWinget.json"
    )
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)
            task_names = [
                task.get("Name", "Nepoznat zadatak")
                for task in tasks_data.values()
                if task.get("category") == "Instalacija dodataka"
            ]
            page_instance.update_tasks(task_names)
            if initial_load:
                page_instance.after(1200, lambda: page_instance.change_tab(3, initial_load=True))
    except Exception as e:
        print(f"Error loading dependency tasks: {e}")
        page_instance.update_tasks([f"Greška pri učitavanju: {e}"])
