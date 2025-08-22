import os
import json
import mysql.connector
from mysql.connector import pooling
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from pathlib import Path

from Controller.config import config_manager
from utils.logger import logger

_mysql_conn = None  # Private global connection
_mysql_pool = None  # Connection pool<

def open_mysql_connection():
    global _mysql_conn, _mysql_pool
    if _mysql_conn is not None:
        return _mysql_conn
    
    try:
        mysql_config = config_manager.get_mysql_config()
        logger.info(f"MySQL config loaded: {mysql_config}", file=Path(__file__).name)
        
        # Create connection pool for better performance
        pool_config = {
            'pool_name': 'automation_pool',
            'pool_size': 5,
            'host': mysql_config['mysql_host'],
            'port': mysql_config['mysql_port'],
            'user': mysql_config['mysql_user'],
            'password': mysql_config['mysql_password'],
            'database': mysql_config['mysql_database'],
            'autocommit': True,
            'charset': 'utf8mb4',
            'use_unicode': True,
            'get_warnings': True
        }
        
        _mysql_pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
        _mysql_conn = _mysql_pool.get_connection()
        logger.log_mysql_connection("opened", file=Path(__file__).name)
        return _mysql_conn
        
    except Exception as e:
        logger.error(f"Failed to open MySQL connection: {e}", file=Path(__file__).name)
        raise

def get_connection():
    return _mysql_conn

def close_mysql_connection():
    global _mysql_conn, _mysql_pool
    if _mysql_conn is not None:
        try:
            _mysql_conn.close()
            _mysql_conn = None
            logger.log_mysql_connection("closed", file=Path(__file__).name)
        except Exception as e:
            logger.error(f"Error closing MySQL connection: {e}", file=Path(__file__).name)
    
    if _mysql_pool is not None:
        try:
            _mysql_pool.close()
            _mysql_pool = None
            logger.log_mysql_connection("pool closed", file=Path(__file__).name)
        except Exception as e:
            logger.error(f"Error closing MySQL connection pool: {e}", file=Path(__file__).name)

def select_all_users():
    if _mysql_conn is None:
        raise RuntimeError("MySQL connection is not open.")
    cursor = _mysql_conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM USER")
        results = cursor.fetchall()
        logger.info(f"Retrieved {len(results)} users from database", file=Path(__file__).name)
        return results
    except Exception as e:
        logger.error(f"Error selecting users: {e}", file=Path(__file__).name)
        return []

def select_all_programs():
    if _mysql_conn is None:
        raise RuntimeError("MySQL connection is not open.")
    cursor = _mysql_conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM PROGRAMS")
        results = cursor.fetchall()

        json_path = config_manager.get_functions_path() / "DependenciesWinget.json"
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

        logger.info(f"Updated programs JSON with {len(programs_dict)} programs", file=Path(__file__).name)
        return results
    except Exception as e:
        logger.error(f"Error selecting programs: {e}", file=Path(__file__).name)
        return []

def select_all_group_policy():
    if _mysql_conn is None:
        raise RuntimeError("MySQL connection is not open.")
    cursor = _mysql_conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM POLICIES")
        results = cursor.fetchall()

        json_path = config_manager.get_functions_path() / 'GroupPolicy.json'
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

        json_path = config_manager.get_functions_path() / 'PythonDependencies.json'
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

        json_path = config_manager.get_functions_path() / 'UninstallPrograms.json'
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

        json_path = config_manager.get_functions_path() / 'WindowsSetting.json'
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