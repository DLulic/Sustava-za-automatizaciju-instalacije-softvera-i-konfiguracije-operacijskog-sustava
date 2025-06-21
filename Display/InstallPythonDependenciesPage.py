import json
import os
import subprocess
import threading
import sys

def _install_all_python_deps_worker(page_instance, tasks_to_install, initial_load=False):
    """
    Worker function to install all python dependencies in a separate thread.
    """
    python_executable = sys.executable

    for index, task_name in enumerate(tasks_to_install):
        def schedule_ui_update(color):
            page_instance.after(0, lambda name=task_name, i=index, c=color: page_instance.set_task_status(name, i, c))

        schedule_ui_update('yellow')
        task_successful = True
        try:
            print(f"Installing {task_name}...")
            subprocess.run(
                [python_executable, "-m", "pip", "install", task_name],
                check=True, capture_output=True, text=True
            )
            print(f"Successfully installed {task_name}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {task_name}. Stderr: {e.stderr}")
            task_successful = False
        except Exception as e:
            print(f"An error occurred installing {task_name}: {e}")
            task_successful = False
            
        final_color = '#2E7D32' if task_successful else '#C62828'
        schedule_ui_update(final_color)
    
    if initial_load:
        page_instance.after(1200, lambda: page_instance.change_tab(4, initial_load=True))

def update_python_dependencies_tasks(page_instance, initial_load=False, auto_install=False):
    """Load tasks from PythonDependencies.json and optionally auto-install them."""
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
            
            if auto_install:
                threading.Thread(
                    target=_install_all_python_deps_worker,
                    args=(page_instance, task_names, initial_load),
                    daemon=True
                ).start()

    except Exception as e:
        print(f"Error loading python dependency tasks: {e}")
        page_instance.update_tasks([f"Greška pri učitavanju: {e}"])
