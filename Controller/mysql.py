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
    """
    Returns all rows from the USER table as a list of dictionaries.
    """
    if _mysql_conn is None:
        raise RuntimeError("MySQL connection is not open.")
    cursor = _mysql_conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM USER")
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
