import sqlite3
from loader import db_path
connector = None


def create_connect(db_path=db_path):
    global connector
    connector = sqlite3.connect(db_path)
    connector.row_factory = sqlite3.Row


def execute(sql: str, parameters: tuple = tuple(),
            fetchone=False, fetchall=False, commit=False, lastrowid=False):

    with sqlite3.connect(db_path) as connector:

        connector.row_factory = sqlite3.Row

        create_connect()
        cursor = connector.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connector.commit()

        if fetchone:
            data = cursor.fetchone()

            if data is None:
                return None

            data = dict(data)

        if fetchall:
            data = cursor.fetchall()

            if data is None:
                return []

            if type(data) != list:
                data = [data]

            for i, el in enumerate(data):
                data[i] = dict(el)

        if lastrowid:
            data = cursor.lastrowid

        return data


def select_str(table_name: str, field_names: list = [], where: dict = {}):
    if len(field_names):
        fields = ','.join(field_names)
    else:
        fields = '*'

    w_str = where_str(where)

    return f"SELECT {fields} FROM {table_name}{w_str}"


def insert_str(table_name: str, values: dict):
    fields = ', '.join(values.keys())
    values = ', '.join(['?'] * len(values.keys()))

    return f"INSERT INTO {table_name} ({fields}) VALUES ({values})"


def update_str(table_name: str, values: dict, where: dict = {}):
    lst = []
    for k in values.keys():
        lst.append(f"{k} = ?")

    values_str = ", ".join(lst)
    w_str = where_str(where)
    return f"UPDATE {table_name} SET {values_str}{w_str}"


def delete_str(table_name: str, where: dict = {}):
    w_str = where_str(where)
    return f"DELETE FROM {table_name}{w_str}"


def where_str(conditions: dict = {}):
    if not conditions:
        return ""

    lst = []
    for k in conditions.keys():
        lst.append(f"{k} = ?")

    conditions_str = " AND ".join(lst)
    return f" WHERE {conditions_str}"


def create_users_table():
    sql = """
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT UNIQUE,
    password TEXT
    );
    """
    data = execute(sql, commit=False)



def create_posts_table():
    sql = """
    CREATE TABLE IF NOT EXISTS Posts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    body TEXT,
    user_id INTEGER,
    likes TEXT DEFAULT ' ',
    sum_likes INTEGER DEFAULT 0
    );
    """
    data = execute(sql, commit=False)



