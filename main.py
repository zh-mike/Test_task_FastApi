# Создайте простой RESTful API с помощью FastAPI для приложения социальной сети
# Функциональные требования:
# Должна быть какая-то форма аутентификации и регистрации (JWT, Oauth, Oauth 2.0 и т.д.)
# Как пользователь, я должен иметь возможность зарегистрироваться и войти в систему
# Как пользователь, я должен иметь возможность создавать, редактировать, удалять и просматривать записи
# Как пользователь, я могу лайкать или не лайкать посты других пользователей, но не свои собственные
# API нуждается в документации по пользовательскому интерфейсу (Swagger/ReDoc)

from fastapi import FastAPI, Header, Depends
from pydantic import BaseModel
from typing import Dict
import jwt
from loader import db


class Users(BaseModel):
    login: str
    password: str


# Класс для удобной работы с ответом от бд
class Current_user:
    def __init__(self, id, login, password):
        self.id = id
        self.login = login
        self.password = password


JWT_SECRET = 'nvuesbfiwu;bf34ubfcwkebjro;'
JWT_ALG = 'HS256'

app = FastAPI(
    title="Test app"
)


async def get_current_user(jwt_token: str = Header()):
    try:
        decoded_jwt = jwt.decode(jwt_token, JWT_SECRET, algorithms=JWT_ALG)
        curr_user = Current_user(*db.search_user(decoded_jwt['user_id'], search_to='id'))
        return curr_user
    except jwt.exceptions.DecodeError:
        return {'success': False, 'message': 'Invalid x-token'}


@app.post('/register')
def registration(user: Users):
    db.create_users_table()
    if db.search_user(user.login) is not None:
        return {'success': False, 'message': "User login is exists", 'user': user.login}
    db.add_user(user.login, user.password)
    curr_user = Current_user(*db.search_user(user.login))
    return {'success': True, 'message': 'User registered', 'user': curr_user}


@app.get('/user')
def authorization(login: str, password: str):
    founded_user = db.search_user(login)
    if founded_user is None:
        return {'success': False, 'message': "User not found"}
    current_user = Current_user(*founded_user)  # Привожу данные из бд к классу для удобства
    if current_user.login == login and current_user.password == password:
        encoded_jwt = jwt.encode({'user_id': current_user.id}, JWT_SECRET, algorithm=JWT_ALG)
        return {'success': True, 'jwt-token': encoded_jwt}
    return {'success': False, 'message': "Invalid password"}


@app.get('/test_jwt')
def back(current_user: Dict = Depends(get_current_user)):
    return current_user
