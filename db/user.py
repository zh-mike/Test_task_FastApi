from db.model import Model


class User(Model):
    _pk = "user_id"
    _table_name = "Users"
    _parameters = {
        "user_id": {"pseudo": "Идентификатор пользователя", "validators": ["ReadOnly"]},
        "login": {"pseudo": "Логин", "validators": ["Required"]},
        "password": {"pseudo": "Пароль", "validators": ["Required"]},
    }