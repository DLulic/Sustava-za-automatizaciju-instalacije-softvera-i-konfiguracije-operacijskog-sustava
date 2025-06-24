import json
import os
import subprocess
import threading

def _uninstall_all_programs_worker(page_instance, tasks_to_uninstall, initial_load=False):
    """
    Worker function to uninstall all designated programs in a separate thread.
    """
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "Functions",
        "UninstallPrograms.json"
    )
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)

        for index, task_name in enumerate(tasks_to_uninstall):
            def schedule_ui_update(color):
                page_instance.after(0, lambda name=task_name, i=index, c=color: page_instance.set_task_status(name, i, c))

            schedule_ui_update('yellow')
            
            target_task = next((task for task in tasks_data if task.get("name") == task_name), None)
            
            task_successful = True
            if not target_task or not target_task.get("name_program"):
                print(f"No valid program name found for '{task_name}'.")
                task_successful = False
            else:
                program_name = target_task.get("name_program")
                source = target_task.get("Source", "AppxPackage")
                print(f"Uninstalling {program_name} using {source}...")
                if source == "Winget":
                    try:
                        result = subprocess.run(
                            ["winget", "uninstall", "--id", program_name, "--accept-source-agreements", "--accept-package-agreements"],
                            capture_output=True, text=True, shell=True
                        )
                        # Winget success codes: 0 (success), 0x8A15002B (already uninstalled), etc.
                        success_codes = {0, -1978335148, -1978335189, -1978334963, -1978334962, -1978335189, 0x8A150054, 0x8A15010D, 0x8A15010E, 0x8a15002b}
                        if result.returncode not in success_codes:
                            raise subprocess.CalledProcessError(
                                returncode=result.returncode, cmd=result.args, output=result.stdout, stderr=result.stderr
                            )
                        print(f"Successfully uninstalled or already absent: {program_name}.")
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to uninstall {program_name} (winget).\n--- Winget Output ---\nSTDOUT: {e.output}\nSTDERR: {e.stderr}\n---------------------")
                        task_successful = False
                else:
                    command = f"Get-AppxPackage *{program_name}* | Remove-AppxPackage"
                    try:
                        result = subprocess.run(
                            ["powershell.exe", "-Command", command],
                            capture_output=True, text=True, shell=True
                        )
                        if result.returncode != 0:
                            # If the command fails, it might be because the app is already uninstalled, which we treat as success.
                            # We check stderr to be more specific.
                            if "is not recognized" not in result.stderr and "Cannot find path" not in result.stderr and "No object found" not in result.stderr:
                                 raise subprocess.CalledProcessError(
                                    returncode=result.returncode, cmd=command, output=result.stdout, stderr=result.stderr
                                )
                        print(f"Successfully uninstalled or already absent: {program_name}.")
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to uninstall {program_name} (AppxPackage).\n--- PowerShell Output ---\nSTDOUT: {e.output}\nSTDERR: {e.stderr}\n---------------------")
                        task_successful = False
            
            final_color = '#2E7D32' if task_successful else '#C62828'
            schedule_ui_update(final_color)

    except Exception as e:
        print(f"An error occurred during program uninstallation: {e}")
    finally:
        if initial_load:
            page_instance.after(1200, lambda: page_instance.change_tab(3, initial_load=True))

def update_uninstall_programs_tasks(page_instance, initial_load=False, auto_install=False):
    """Load tasks from UninstallPrograms.json and optionally auto-uninstall them."""
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "Functions",
        "UninstallPrograms.json"
    )
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)
            task_names = [task.get("name", "Nepoznat zadatak") for task in tasks_data]
            page_instance.update_tasks(task_names)
            
            if auto_install:
                threading.Thread(
                    target=_uninstall_all_programs_worker,
                    args=(page_instance, task_names, initial_load),
                    daemon=True
                ).start()
    except Exception as e:
        print(f"Error loading uninstall tasks: {e}")
        page_instance.update_tasks([f"Greška pri učitavanju: {e}"])
