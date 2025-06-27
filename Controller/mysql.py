import os
import json
import mysql.connector

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Storage', 'config.json')

_mysql_conn = None  # Private global connection

def open_mysql_connection():
    global _mysql_conn
    if _mysql_conn is not None:
        return _mysql_conn
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(json.dumps(config, indent=2))
    required_fields = ["mysql_host", "mysql_port", "mysql_user", "mysql_password", "mysql_database"]
    for field in required_fields:
        if not config.get(field):
            raise ValueError(f"Missing MySQL config field: {field}")
    _mysql_conn = mysql.connector.connect(
        host=config["mysql_host"],
        port=config["mysql_port"],
        user=config["mysql_user"],
        password=config["mysql_password"],
        database=config["mysql_database"]
    )
    return _mysql_conn

def get_connection():
    return _mysql_conn

def close_mysql_connection():
    global _mysql_conn
    if _mysql_conn is not None:
        try:
            _mysql_conn.close()
            print("MySQL connection closed.")
        except Exception as e:
            print(f"Error closing MySQL connection: {e}")
        _mysql_conn = None

def select_all_users():
    if _mysql_conn is None:
        raise RuntimeError("MySQL connection is not open.")
    cursor = _mysql_conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM USER")
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Error: {e}")

def select_all_programs():
    if _mysql_conn is None:
        raise RuntimeError("MySQL connection is not open.")
    cursor = _mysql_conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM PROGRAMS")
        results = cursor.fetchall()

        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Functions', 'DependenciesWinget.json')
        programs_dict = {}
        for prog in results:
            # Map fields according to the required mapping
            name = prog.get("program_name")
            if not name:
                continue
            mapped = {
                "id": prog.get("program_id"),
                "category": prog.get("program_category"),
                "Name": name,
                "Desc": prog.get("program_desc"),
                "winget": prog.get("program_package"),
                "enable": bool(prog.get("program_enabled"))
            }
            programs_dict[name] = mapped
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(programs_dict, f, ensure_ascii=False, indent=4)

        return results
    except Exception as e:
        print(f"Error: {e}")

def select_all_group_policy():
    if _mysql_conn is None:
        raise RuntimeError("MySQL connection is not open.")
    cursor = _mysql_conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM POLICIES")
        results = cursor.fetchall()

        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Functions', 'GroupPolicy.json')
        policies_list = []
        for prog in results:
            mapped = {
                "id": prog.get("policies_id"),
                "name": prog.get("policies_name"),
                "regPath": prog.get("policies_regPath"),
                "regName": prog.get("policies_regName"),
                "regValue": prog.get("policies_regVaule"),
                "regValueRevert": prog.get("policies_regVauleRevert"),
                "type": prog.get("policies_type"),
                "enable": bool(prog.get("policies_enable")),
            }
            policies_list.append(mapped)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(policies_list, f, ensure_ascii=False, indent=4)

        return results
    except Exception as e:
        print(f"Error: {e}")

def select_all_python_dependencies():
    if _mysql_conn is None:
        raise RuntimeError("MySQL connection is not open.")
    cursor = _mysql_conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT python_name FROM PYTHON")
        results = cursor.fetchall()

        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Functions', 'PythonDependencies.json')
        dependencies = [prog.get("python_name") for prog in results if prog.get("python_name")]
        out_dict = {"dependencies": dependencies}
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(out_dict, f, ensure_ascii=False, indent=4)

        return results
    except Exception as e:
        print(f"Error: {e}")

def select_all_uninstall_programs():
    if _mysql_conn is None:
        raise RuntimeError("MySQL connection is not open.")
    cursor = _mysql_conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM UNINSTALL_PROGRAMS")
        results = cursor.fetchall()

        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Functions', 'UninstallPrograms.json')
        policies_list = []
        for prog in results:
            mapped = {
                "id": prog.get("uninstall_id"),
                "name": prog.get("uninstall_name"),
                "name_program": prog.get("uninstall_name_program"),
                "Source": prog.get("uninstall_source")
            }
            policies_list.append(mapped)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(policies_list, f, ensure_ascii=False, indent=4)

        return results
    except Exception as e:
        print(f"Error: {e}")

def select_all_windows_settings():
    if _mysql_conn is None:
        raise RuntimeError("MySQL connection is not open.")
    cursor = _mysql_conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM WIN_SETTINGS")
        results = cursor.fetchall()

        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Functions', 'WindowsSetting.json')
        policies_list = []
        for prog in results:
            mapped = {
                "id": prog.get("settings_id"),
                "name": prog.get("settings_name"),
                "command": prog.get("settings_command"),
                "enable": bool(prog.get("settings_enable"))
            }
            policies_list.append(mapped)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(policies_list, f, ensure_ascii=False, indent=4)

        return results
    except Exception as e:
        print(f"Error: {e}")

def insert_report(computer_name, task_type, task_name, status):
    if _mysql_conn is None:
        raise RuntimeError("MySQL connection is not open.")
    cursor = _mysql_conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO REPORT (report_computer_name, report_task_type, report_task_name, report_status, report_timestamp) "
            "VALUES (%s, %s, %s, %s, NOW())",
            (computer_name, task_type, task_name, status)
        )
        _mysql_conn.commit()
    except Exception as e:
        print(f"Error inserting report: {e}")