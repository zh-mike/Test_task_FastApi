import sqlite3


class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path

    def execute(self, sql: str, parameters: tuple = tuple(),
                fetchone=False, fetchall=False, commit=False, lastrowid=False):
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
            if lastrowid == True:
                data = cursor.lastrowid
            return data

    def create_users_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE,
        password TEXT
        );
        """
        self.execute(sql, commit=True)


    def add_user(self, user_login, user_password):
        sql = "INSERT INTO Users(login, password) VALUES (?, ?)"
        parameters = (user_login, user_password)
        self.execute(sql, parameters=parameters, commit=True)

    def search_user(self, user_logit, search_to='login'):
        sql = f"SELECT * FROM Users WHERE {search_to}=?"
        current_user = self.execute(sql, parameters=(user_logit,), fetchone=True)
        if current_user == None:
            return None
        return self.in_dict(current_user, model_user=True)

    def create_posts_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Posts(
        post_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        body TEXT,
        user_id INTEGER,
        likes TEXT
        );
        """
        self.execute(sql, commit=True)

    def add_post(self, title, body, user_id):
        sql = "INSERT INTO Posts(title, body, user_id) VALUES (?, ?, ?)"
        parameters = (title, body, user_id)
        return self.execute(sql, parameters=parameters, commit=True, lastrowid=True)

    def search_post(self, id, search_to='rowid'):
        sql = f"SELECT * FROM Posts WHERE {search_to}=?"
        user_posts = self.execute(sql, parameters=(id,), fetchone=True)
        if user_posts == None:
            return None
        return self.in_dict(user_posts)

    def search_user_posts(self, user_id):
        sql = "SELECT * FROM Posts WHERE user_id=?"
        user_posts = self.execute(sql, parameters=(user_id,), fetchall=True)
        return self.in_dict(user_posts)


    def search_all_posts(self):
        sql = "SELECT * FROM Posts"
        all_posts = self.execute(sql, fetchall=True)
        return self.in_dict(all_posts)

    def del_post(self, post_id, user_id):
        sql = f"DELETE FROM Posts WHERE post_id={post_id} AND user_id={user_id}"
        self.execute(sql, commit=True)


    def update_post(self, new_post, post_id, user_id):

        sql = f"UPDATE Posts SET title='{new_post.title}', body='{new_post.body}' WHERE post_id={post_id}"
        self.execute(sql, commit=True)

    @staticmethod
    def in_dict(db_answer, model_user=False):
        """
        Функция для преобразования полученной от бд информации в dict
        для удобства дальнейшей работы.
        """
        result_lst = []
        model = ['post_id', 'title', 'body', 'user_id', 'likes']
        mod_user = ['user_id', 'login', 'password']
        if isinstance(db_answer, tuple):
            db_answer = [db_answer]
        if model_user == True:
            model = mod_user
        for el in db_answer:
            result_lst.append(dict(zip(model, el)))
        return result_lst