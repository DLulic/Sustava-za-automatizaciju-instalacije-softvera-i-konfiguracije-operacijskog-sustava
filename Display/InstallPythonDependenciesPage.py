import json
import os
import subprocess
import threading
import sys
from typing import Dict, Any
from Controller.mysql import insert_report
from Controller.config import config_manager
from utils.logger import logger
from pathlib import Path

def _install_all_python_deps_worker(page_instance, tasks_to_install, initial_load=False):
    """
    Worker function to install all python dependencies in a separate thread.
    """
    python_executable = sys.executable
    # Load computer_name using config manager
    try:
        computer_name = config_manager.get_computer_name()
    except Exception as e:
        logger.error(f"Error loading computer name: {e}", file=Path(__file__).name)
        computer_name = ''

    for index, task_name in enumerate(tasks_to_install):
        def schedule_ui_update(color):
            page_instance.after(0, lambda name=task_name, i=index, c=color: page_instance.set_task_status(name, i, c))

        schedule_ui_update('yellow')
        task_successful = True
        try:
            logger.info(f"Installing {task_name}...", file=Path(__file__).name)
            subprocess.run(
                [python_executable, "-m", "pip", "install", task_name],
                check=True, capture_output=True, text=True,
                timeout=300  # 5 minute timeout
            )
            logger.info(f"Successfully installed {task_name}.", file=Path(__file__).name)
        except subprocess.TimeoutExpired:
            logger.error(f"Installation of {task_name} timed out after 5 minutes", file=Path(__file__).name)
            task_successful = False
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {task_name}. Stderr: {e.stderr}", file=Path(__file__).name)
            task_successful = False
        except Exception as e:
            logger.error(f"An error occurred installing {task_name}: {e}", file=Path(__file__).name)
            task_successful = False
        final_color = '#2E7D32' if task_successful else '#C62828'
        schedule_ui_update(final_color)
        status = 'success' if task_successful else 'failure'
        logger.info(f"Task '{task_name}' completed with status: {status}", file=Path(__file__).name)
        insert_report(computer_name, 'python dodaci', task_name, status)
    if initial_load:
        page_instance.after(1200, lambda: page_instance.change_tab(5, initial_load=True))

def update_python_dependencies_tasks(page_instance, initial_load=False, auto_install=False):
    """Load tasks from PythonDependencies.json and optionally auto-install them."""
    json_path = config_manager.get_functions_path() / "PythonDependencies.json"
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
        logger.error(f"Error loading python dependency tasks: {e}", file=Path(__file__).name)
        page_instance.update_tasks([f"Greška pri učitavanju: {e}"])
