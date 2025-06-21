import json
import os

def update_group_policy_tasks(page_instance, initial_load=False):
    """Load tasks from GroupPolicy.json and update the main task list."""
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "Functions",
        "GroupPolicy.json"
    )
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)
            task_names = [task.get("name", "Nepoznat zadatak") for task in tasks_data]
            page_instance.update_tasks(task_names)
            if initial_load:
                page_instance.after(1200, lambda: page_instance.change_tab(2, initial_load=True))
                
    except Exception as e:
        print(f"Error loading group policy tasks: {e}")
        page_instance.update_tasks([f"Greška pri učitavanju: {e}"])
