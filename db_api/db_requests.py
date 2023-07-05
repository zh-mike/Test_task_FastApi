import sqlite3


class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path

    def execute(self, sql: str, parameters: tuple = tuple(),
                fetchone=False, fetchall=False, commit=False):
        with sqlite3.connect(self.db_path) as con:
            cursor = con.cursor()
            data = None
            cursor.execute(sql, parameters)
            if commit == True:
                con.commit()
            if fetchone == True:
                data = cursor.fetchone()
            if fetchall == True:
                data = cursor.fetchall()
            return data

    def create_users_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE,
        password TEXT
        );
        """
        self.execute(sql, commit=True)

    def create_posts_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        body TEXT,
        user_id INTAGRE
        );
        """
        self.execute(sql, commit=True)

    def add_user(self, user_login, user_password):
        sql = "INSERT INTO Users(login, password) VALUES (?, ?)"
        parameters = (user_login, user_password)
        self.execute(sql, parameters=parameters, commit=True)

    def search_user(self, user_logit, search_to='login'):
        sql = f"SELECT * FROM Users WHERE {search_to}=?"
        return self.execute(sql, parameters=(user_logit,), fetchone=True)


