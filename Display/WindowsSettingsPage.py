import json
import subprocess
import threading
from Controller.mysql import insert_report
from Controller.config import config_manager
from utils.logger import logger
from pathlib import Path

def _run_windows_settings_worker(page_instance, tasks_to_run, initial_load=False):
    # Load config and data using config manager
    try:
        windows_key = config_manager.get_windows_key()
        computer_name = config_manager.get_computer_name()
    except Exception as e:
        logger.error(f"Error loading config/data: {e}", file=Path(__file__).name)
        windows_key = ''
        computer_name = ''

    json_path = config_manager.get_functions_path() / "WindowsSetting.json"
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)

        for index, task in enumerate(tasks_to_run):
            def schedule_ui_update(color):
                page_instance.after(0, lambda name=task['name'], i=index, c=color: page_instance.set_task_status(name, i, c))

            schedule_ui_update('yellow')
            command = task.get('command', '')
            if not command:
                logger.error(f"No command for task '{task['name']}'", file=Path(__file__).name)
                schedule_ui_update('#C62828')
                # Log failure
                insert_report(computer_name, 'windows_setting', task['name'], 'failure')
                continue
            # Replace placeholders
            command = command.replace('<Your-Product-Key>', windows_key)
            command = command.replace('<NewComputerName>', computer_name)
            logger.info(f"Running command for '{task['name']}': {command}", file=Path(__file__).name)
            status = 'success'
            try:
                result = subprocess.run(
                    ["powershell.exe", "-Command", command],
                    capture_output=True, text=True, shell=True,
                    timeout=300  # 5 minute timeout
                )
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(
                        returncode=result.returncode, cmd=command, output=result.stdout, stderr=result.stderr
                    )
                logger.info(f"Successfully ran: {command}", file=Path(__file__).name)
            except subprocess.TimeoutExpired:
                logger.error(f"Task '{task['name']}' timed out after 5 minutes", file=Path(__file__).name)
                schedule_ui_update('#C62828')
                status = 'failure'
                insert_report(computer_name, 'windows settings', task['name'], status)
                continue
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to run command for {task['name']}.\n--- Output ---\nSTDOUT: {e.output}\nSTDERR: {e.stderr}\n---------------------", file=Path(__file__).name)
                schedule_ui_update('#C62828')
                status = 'failure'
                insert_report(computer_name, 'windows settings', task['name'], status)
                continue
            schedule_ui_update('#2E7D32')
            insert_report(computer_name, 'windows settings', task['name'], status)
            logger.info(f"{computer_name} windows settings {task['name']} {status}", file=Path(__file__).name)
    except Exception as e:
        logger.error(f"Error running windows settings tasks: {e}", file=Path(__file__).name)
    finally:
        if initial_load:
            page_instance.after(1200, lambda: page_instance.change_tab(1, initial_load=True))

def update_main_tasks(page_instance, initial_load=False, auto_install=True):
    """Load tasks from WindowsSetting.json and optionally run them."""
    json_path = config_manager.get_functions_path() / "WindowsSetting.json"
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)
            # Only show enabled tasks
            enabled_tasks = [task for task in tasks_data if task.get('enable', True)]
            task_names = [task.get("name", "Nepoznat zadatak") for task in enabled_tasks]
            page_instance.update_tasks(task_names)
            if auto_install:
                threading.Thread(
                    target=_run_windows_settings_worker,
                    args=(page_instance, enabled_tasks, initial_load),
                    daemon=True
                ).start()
    except Exception as e:
        logger.error(f"Error loading windows settings tasks: {e}", file=Path(__file__).name)
        page_instance.update_tasks([f"Greška pri učitavanju: {e}"])