import json
import os
import subprocess
import threading
from typing import Dict, Any
from Controller.mysql import insert_report
from Controller.config import config_manager
from utils.logger import logger
from pathlib import Path

def _apply_group_policy_worker(page_instance, tasks_to_apply, initial_load=False):
    json_path = config_manager.get_functions_path() / "GroupPolicy.json"
    # Load computer_name using config manager
    try:
        computer_name = config_manager.get_computer_name()
    except Exception as e:
        logger.error(f"Error loading computer name: {e}", file=Path(__file__).name)
        computer_name = ''
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)

        for index, task_name in enumerate(tasks_to_apply):
            def schedule_ui_update(color):
                page_instance.after(0, lambda name=task_name, i=index, c=color: page_instance.set_task_status(name, i, c))

            schedule_ui_update('yellow')
            target_task = next((task for task in tasks_data if task.get("name") == task_name), None)
            task_successful = True
            if not target_task or not target_task.get("enable", True):
                logger.info(f"Skipping '{task_name}' (not enabled or not found).", file=Path(__file__).name)
                task_successful = False
            else:
                reg_path = target_task.get("regPath")
                reg_name = target_task.get("regName")
                reg_value = target_task.get("regValue")
                reg_type = target_task.get("type", "DWORD")
                if not reg_path or not reg_name:
                    logger.error(f"Missing registry path or name for '{task_name}'.", file=Path(__file__).name)
                    task_successful = False
                else:
                    # Check if the key exists
                    check_key_cmd = f"Test-Path -Path \"{reg_path}\""
                    result_check = subprocess.run(
                        ["powershell.exe", "-Command", check_key_cmd],
                        capture_output=True, text=True, shell=True
                    )
                    if "True" not in result_check.stdout:
                        # Only create if it does not exist
                        create_key_cmd = f"New-Item -Path \"{reg_path}\" -Force"
                        try:
                            result_create = subprocess.run(
                                ["powershell.exe", "-Command", create_key_cmd],
                                capture_output=True, text=True, shell=True
                            )
                            if result_create.returncode != 0:
                                raise subprocess.CalledProcessError(
                                    returncode=result_create.returncode, cmd=create_key_cmd, output=result_create.stdout, stderr=result_create.stderr
                                )
                        except subprocess.CalledProcessError as e:
                            logger.error(f"Failed to create registry key {reg_path}.\n--- PowerShell Output ---\nSTDOUT: {e.output}\nSTDERR: {e.stderr}\n---------------------", file=Path(__file__).name)
                            task_successful = False
                    # Use the raw reg_value from JSON
                    value_str = str(reg_value)
                    type_flag = "-Type DWord" if reg_type.upper() == "DWORD" else "-Type String"
                    # Wrap reg_path in double quotes for Set-ItemProperty
                    command = f"Set-ItemProperty -Path \"{reg_path}\" -Name '{reg_name}' -Value {value_str} {type_flag} -Force"
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
                        logger.info(f"Successfully set {reg_name} in {reg_path} to {reg_value}.", file=Path(__file__).name)
                    except subprocess.TimeoutExpired:
                        logger.error(f"Task '{task_name}' timed out after 5 minutes", file=Path(__file__).name)
                        task_successful = False
                    except subprocess.CalledProcessError as e:
                        logger.error(f"Failed to set {reg_name} in {reg_path}.\n--- PowerShell Output ---\nSTDOUT: {e.output}\nSTDERR: {e.stderr}\n---------------------", file=Path(__file__).name)
                        task_successful = False
            final_color = '#2E7D32' if task_successful else '#C62828'
            schedule_ui_update(final_color)
            status = 'success' if task_successful else 'failure'
            logger.info(f"Task '{task_name}' completed with status: {status}", file=Path(__file__).name)
            insert_report(computer_name, 'group policy', task_name, status)
        # Run gpupdate /force at the end
        try:
            logger.info("Running gpupdate /force ...", file=Path(__file__).name)
            result_gpupdate = subprocess.run(
                ["gpupdate", "/force"],
                capture_output=True, text=True, shell=True,
                timeout=300  # 5 minute timeout
            )
            logger.info(f"gpupdate /force output:\nSTDOUT: {result_gpupdate.stdout}\nSTDERR: {result_gpupdate.stderr}", file=Path(__file__).name)
        except subprocess.TimeoutExpired:
            logger.error("gpupdate /force timed out after 5 minutes", file=Path(__file__).name)
        except Exception as e:
            logger.error(f"Failed to run gpupdate /force: {e}", file=Path(__file__).name)
    except Exception as e:
        logger.error(f"Error applying group policy tasks: {e}", file=Path(__file__).name)
    finally:
        if initial_load:
            page_instance.after(1200, lambda: page_instance.change_tab(2, initial_load=True))

def update_group_policy_tasks(page_instance, initial_load=False, auto_install=True):
    """Load tasks from GroupPolicy.json and optionally apply them."""
    json_path = config_manager.get_functions_path() / "GroupPolicy.json"
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)
            # Only show tasks where enable is true (default to true if missing)
            task_names = [task.get("name", "Nepoznat zadatak") for task in tasks_data if task.get("enable", True)]
            page_instance.update_tasks(task_names)
            if auto_install:
                threading.Thread(
                    target=_apply_group_policy_worker,
                    args=(page_instance, task_names, initial_load),
                    daemon=True
                ).start()
    except Exception as e:
        logger.error(f"Error loading group policy tasks: {e}", file=Path(__file__).name)
        page_instance.update_tasks([f"Greška pri učitavanju: {e}"])
