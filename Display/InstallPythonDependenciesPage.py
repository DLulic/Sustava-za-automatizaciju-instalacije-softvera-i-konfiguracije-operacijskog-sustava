import json
import os

def update_python_dependencies_tasks(page_instance, initial_load=False):
    """Load tasks from PythonDependencies.json and update the main task list."""
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "Functions",
        "PythonDependencies.json"
    )
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)
            task_names = tasks_data.get("dependencies", [])
            page_instance.update_tasks(task_names)
            if initial_load:
                page_instance.after(1200, lambda: page_instance.change_tab(4, initial_load=True))
    except Exception as e:
        print(f"Error loading python dependency tasks: {e}")
        page_instance.update_tasks([f"Greška pri učitavanju: {e}"])
