import json
import os
import subprocess
import threading
from Controller.mysql import insert_report

def _run_windows_settings_worker(page_instance, tasks_to_run, initial_load=False):
    # Load config and data
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Storage', 'config.json')
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Storage', 'data.json')
    windows_key = ''
    computer_name = ''
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                windows_key = config.get('windows_key', '')
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                computer_name = data.get('Naziv računala', '')
    except Exception as e:
        print(f"Error loading config/data: {e}")

    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "Functions",
        "WindowsSetting.json"
    )
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)

        for index, task in enumerate(tasks_to_run):
            def schedule_ui_update(color):
                page_instance.after(0, lambda name=task['name'], i=index, c=color: page_instance.set_task_status(name, i, c))

            schedule_ui_update('yellow')
            command = task.get('command', '')
            if not command:
                print(f"No command for task '{task['name']}'")
                schedule_ui_update('#C62828')
                # Log failure
                insert_report(computer_name, 'windows_setting', task['name'], 'failure')
                continue
            # Replace placeholders
            command = command.replace('<Your-Product-Key>', windows_key)
            command = command.replace('<NewComputerName>', computer_name)
            print(f"Running command for '{task['name']}': {command}")
            status = 'success'
            try:
                result = subprocess.run(
                    ["powershell.exe", "-Command", command],
                    capture_output=True, text=True, shell=True
                )
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(
                        returncode=result.returncode, cmd=command, output=result.stdout, stderr=result.stderr
                    )
                print(f"Successfully ran: {command}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to run command for {task['name']}.\n--- Output ---\nSTDOUT: {e.output}\nSTDERR: {e.stderr}\n---------------------")
                schedule_ui_update('#C62828')
                status = 'failure'
                insert_report(computer_name, 'windows settings', task['name'], status)
                continue
            schedule_ui_update('#2E7D32')
            insert_report(computer_name, 'windows settings', task['name'], status)
            print(computer_name, 'windows settings', task['name'], status)
    except Exception as e:
        print(f"Error running windows settings tasks: {e}")
    finally:
        if initial_load:
            page_instance.after(1200, lambda: page_instance.change_tab(1, initial_load=True))

def update_main_tasks(page_instance, initial_load=False, auto_install=True):
    """Load tasks from WindowsSetting.json and optionally run them."""
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "Functions",
        "WindowsSetting.json"
    )
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
        print(f"Error loading windows settings tasks: {e}")
        page_instance.update_tasks([f"Greška pri učitavanju: {e}"])