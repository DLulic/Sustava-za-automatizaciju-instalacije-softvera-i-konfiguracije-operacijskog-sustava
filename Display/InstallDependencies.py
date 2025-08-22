import json
import subprocess
import threading
from Controller.mysql import insert_report
from Controller.config import config_manager
from utils.logger import logger
from pathlib import Path

def _install_all_dependencies_worker(page_instance, tasks_to_install, initial_load=False):
    """
    Worker function to install all dependencies in a separate thread.
    Updates the UI via page_instance.after().
    """
    json_path = config_manager.get_functions_path() / "DependenciesWinget.json"
    # Load computer_name using config manager
    try:
        computer_name = config_manager.get_computer_name()
    except Exception as e:
        logger.error(f"Error loading computer name: {e}", file=Path(__file__).name)
        computer_name = ''
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)

        for index, task_name in enumerate(tasks_to_install):
            def schedule_ui_update(color):
                page_instance.after(0, lambda name=task_name, i=index, c=color: page_instance.set_task_status(name, i, c))

            schedule_ui_update('yellow')

            target_task = next((task for task in tasks_data.values() if task.get("Name") == task_name), None)
            
            task_successful = True
            if not target_task or not target_task.get("winget"):
                logger.error(f"No valid winget task found for '{task_name}'.", file=Path(__file__).name)
                task_successful = False
            else:
                winget_ids = [id.strip() for id in target_task.get("winget").split(',')]
                for winget_id in winget_ids:
                    logger.info(f"Installing {winget_id}...", file=Path(__file__).name)
                    try:
                        result = subprocess.run(
                            ["winget", "install", "--id", winget_id, "--accept-source-agreements", "--accept-package-agreements"],
                            capture_output=True, text=True, shell=True,
                            timeout=600  # 10 minute timeout for installations
                        )
                        success_codes = {0, -1978335148, -1978335189, -1978334963, -1978334962, -1978335189, 0x8A150054, 0x8A15010D, 0x8A15010E, 0x8a15002b}
                        if result.returncode not in success_codes:
                            raise subprocess.CalledProcessError(
                                returncode=result.returncode, cmd=result.args, output=result.stdout, stderr=result.stderr
                            )
                        logger.info(f"Successfully installed or already present: {winget_id}.", file=Path(__file__).name)
                    except subprocess.TimeoutExpired:
                        logger.error(f"Installation of {winget_id} timed out after 10 minutes", file=Path(__file__).name)
                        task_successful = False
                        break
                    except subprocess.CalledProcessError as e:
                        logger.error(f"Failed to install {winget_id}.\n--- Winget Output ---\nSTDOUT: {e.output}\nSTDERR: {e.stderr}\n---------------------", file=Path(__file__).name)
                        task_successful = False
                        break
            
            final_color = '#2E7D32' if task_successful else '#C62828'
            schedule_ui_update(final_color)
            status = 'success' if task_successful else 'failure'
            logger.info(f"Task '{task_name}' completed with status: {status}", file=Path(__file__).name)
            insert_report(computer_name, 'instalacija dodataka', task_name, status)

    except Exception as e:
        logger.error(f"An error occurred during installation: {e}", file=Path(__file__).name)
    finally:
        if initial_load:
            page_instance.after(1200, lambda: page_instance.change_tab(4, initial_load=True))

def update_dependencies_tasks(page_instance, initial_load=False, auto_install=False):
    """Load tasks from DependenciesWinget.json and optionally auto-install them."""
    json_path = config_manager.get_functions_path() / "DependenciesWinget.json"
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)
            task_names = [
                task.get("Name", "Nepoznat zadatak")
                for task in tasks_data.values()
                if task.get("category") == "Instalacija dodataka"
            ]
            page_instance.update_tasks(task_names)

            if auto_install:
                threading.Thread(
                    target=_install_all_dependencies_worker,
                    args=(page_instance, task_names, initial_load),
                    daemon=True
                ).start()
    except Exception as e:
        logger.error(f"Error loading dependency tasks: {e}", file=Path(__file__).name)
        page_instance.update_tasks([f"Greška pri učitavanju: {e}"])