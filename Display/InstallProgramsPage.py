import json
import os

def update_programs_tasks(page_instance, initial_load=False):
    """Load tasks from DependenciesWinget.json for 'Instalacija programa' and update the task list."""
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
                if task.get("category") == "Instalacija programa"
            ]
            page_instance.update_tasks(task_names)
    except Exception as e:
        print(f"Error loading program tasks: {e}")
        page_instance.update_tasks([f"Greška pri učitavanju: {e}"])
