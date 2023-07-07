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


class Posts(BaseModel):
    title: str
    body: str


JWT_SECRET = 'nvuesbfiwu;bf34ubfcwkebjro;'
JWT_ALG = 'HS256'

app = FastAPI(
    title="Test app"
)


def check_post(current_user, post_id):
    if 'success' in current_user:  # Проверяем верный ли jwt
        return current_user
    founded_post = db.search_post(post_id, search_to='post_id')
    if founded_post == None:
        return {'success': False, 'message': "Post not found"}
    if founded_post[0]['user_id'] != current_user['user_id']:
        return {'success': False, 'message': "This is not your post"}
    return {'success': True}


async def get_current_user(jwt_token: str = Header()):
    try:
        decoded_jwt = jwt.decode(jwt_token, JWT_SECRET, algorithms=JWT_ALG)
        current_user = db.search_user(decoded_jwt['user_id'], search_to='user_id')
        return current_user[0]
    except jwt.exceptions.DecodeError:
        return {'success': False, 'message': 'Invalid jwt-token'}


@app.post('/register')
def registration(user: Users):
    db.create_users_table()
    if db.search_user(user.login) is not None:
        return {'success': False, 'message': "User login is exists", 'user': user.login}
    db.add_user(user.login, user.password)
    curr_user = db.search_user(user.login)
    return {'success': True, 'message': 'User registered', 'user': curr_user}


@app.get('/user')
def authorization(login: str, password: str):
    founded_user = db.search_user(login)[0]
    print(founded_user)
    if founded_user is None:
        return {'success': False, 'message': "User not found"}
    if founded_user['login'] == login and founded_user['password'] == password:
        encoded_jwt = jwt.encode({'user_id': founded_user['user_id']}, JWT_SECRET, algorithm=JWT_ALG)
        return {'success': True, 'jwt-token': encoded_jwt}
    return {'success': False, 'message': "Invalid password"}


@app.post('/user/posts')
def add_post(post: Posts, current_user: Dict = Depends(get_current_user)):
    db.create_posts_table()
    curr_id = db.add_post(post.title, post.body, current_user['user_id'])
    curr_post = db.search_post(curr_id)
    return {'success': True, 'message': "Post added", 'post': curr_post}


@app.get('/posts')
def get_all_posts(current_user: Dict = Depends(get_current_user)):
    if 'success' in current_user:
        return current_user
    all_posts = db.search_all_posts()
    for el in all_posts:
        el['likes'] = len(el['likes'].split())
    return {'success': True, 'message': "All posts", 'posts': all_posts}


@app.get('/user/posts')
def get_user_posts(current_user: Dict = Depends(get_current_user)):
    if 'success' in current_user:
        return current_user
    user_posts = db.search_user_posts(current_user['user_id'])
    if user_posts == []:
        return {'success': False, 'message': "You don't have posts"}
    for el in user_posts:
        el['likes'] = len(el['likes'].split())
    return {'success': True, 'message': "All your posts", 'posts': user_posts}


@app.get('/user/post')
def get_post(post_id, current_user: Dict = Depends(get_current_user)):
    if 'success' in current_user:
        return current_user
    user_post = db.search_post(post_id, search_to='post_id')
    if user_post is None:
        return {'success': False, 'message': "Post not found"}
    user_post[0]['likes'] = len(user_post[0]['likes'].split())
    return {'success': True, 'posts': user_post}


@app.delete('/user/post')
def delete_post(post_id, current_user: Dict = Depends(get_current_user)):
    answer = check_post(current_user, post_id)
    if answer['success'] is True:
        db.del_post(post_id, current_user['user_id'])
        return {'success': True, 'message': "Post deleted"}
    return answer


@app.put('/user/post')
def update_post(post: Posts, post_id, current_user: Dict = Depends(get_current_user)):
    answer = check_post(current_user, post_id)
    if answer['success'] is True:
        db.update_post(new_post=post, post_id=post_id, user_id=current_user['user_id'])
        return {'success': True, 'message': "Post update"}
    return answer

@app.post('/likes')
def like_post(post_id, current_user: Dict = Depends(get_current_user)):
    if 'success' in current_user:
        return current_user
    founded_post = db.search_post(post_id, search_to='post_id')
    if founded_post is None:
        return {'success': False, 'message': "Post not found"}
    if founded_post[0]['user_id'] == current_user['user_id']:
        return {'success': False, 'message': "This is your post"}
    likes_lst = []
    if founded_post[0]['likes'] is not None:
        likes_lst = founded_post[0]['likes'].split()
        print(likes_lst)
        if str(current_user['user_id']) in likes_lst:
            return {'success': False, 'message': "You can liked post only once"}
    likes_lst.append(str(current_user['user_id']))
    likes = " ".join(likes_lst)
    print(likes)
    db.liked(post_id,  likes)
    return {'success': True, 'message': "You liked this post"}
