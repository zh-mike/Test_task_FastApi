# Создайте простой RESTful API с помощью FastAPI для приложения социальной сети
# Функциональные требования:
# Должна быть какая-то форма аутентификации и регистрации (JWT, Oauth, Oauth 2.0 и т.д.)
# Как пользователь, я должен иметь возможность зарегистрироваться и войти в систему
# Как пользователь, я должен иметь возможность создавать, редактировать, удалять и просматривать записи
# Как пользователь, я могу лайкать или не лайкать посты других пользователей, но не свои собственные
# API нуждается в документации по пользовательскому интерфейсу (Swagger/ReDoc)


from fastapi import FastAPI, Header, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict
import jwt
from classes import Users, Posts


class User(BaseModel):
    login: str
    password: str


class Post(BaseModel):
    title: str
    body: str


JWT_SECRET = 'nvuesbfiwu;bf34ubfcwkebjro;'
JWT_ALG = 'HS256'

app = FastAPI(
    title="Test app"
)


async def get_current_user(jwt_token: str = Header()):
    try:
        decoded_jwt = jwt.decode(jwt_token, JWT_SECRET, algorithms=JWT_ALG)
        current_user = Users.load({'id': decoded_jwt['user_id']})

        if current_user is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        return current_user, decoded_jwt['user_id']

    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post('/register')
def registration(user: User):

    if Users.load({'login': user.login}) is not None:

        raise HTTPException(status_code=403, detail="User login is exists")

    current_user = Users()
    current_user.login = user.login
    current_user.password = user.password
    current_user.save()

    return {'success': True, 'message': 'User registered',
            'user': Users.load({'login': current_user.login})}


@app.get('/user')
def authorization(login: str, password: str):
    founded_user = Users.load({'login': login})

    if founded_user is None:

        raise HTTPException(status_code=404, detail="User not found")


    if founded_user.login == login and founded_user.password == password:
        encoded_jwt = jwt.encode({'user_id': founded_user.id}, JWT_SECRET, algorithm=JWT_ALG)

        return {'success': True, 'jwt-token': encoded_jwt}

    raise HTTPException(status_code=401, detail="Invalid password")


@app.post('/user/posts')
def add_post(post: Post, current_user: Dict = Depends(get_current_user)):
    new_post = Posts()
    new_post.title = post.title
    new_post.body = post.body
    new_post.user_id = current_user[1]
    new_post.save()

    return {'success': True, 'message': "Post added", 'post': new_post}


@app.get('/posts')
def get_all_posts(current_user: Dict = Depends(get_current_user)):
    all_posts = Posts.load_by()

    return {'success': True, 'message': "All posts", 'posts': all_posts}


@app.get('/user/posts')
def get_user_posts(current_user: Dict = Depends(get_current_user)):
    user_posts = Posts.load_by({'user_id': current_user[0].user_id})

    if user_posts == []:

        raise HTTPException(status_code=404, detail="Post not found")

    return {'success': True, 'message': "All your posts", 'posts': user_posts}


@app.get('/user/post')
def get_post(post_id, current_user: Dict = Depends(get_current_user)):
    found_post = Posts.load({'id': post_id})

    if found_post is None:

        raise HTTPException(status_code=404, detail="Post not found")

    found_post.hide_likes()

    return {'success': True, 'posts': found_post}


@app.delete('/user/post')
def delete_post(post_id, current_user: Dict = Depends(get_current_user)):
    current_post = Posts.load({'id': post_id})

    if current_post.user_id != current_user[1]:

        raise HTTPException(status_code=403, detail="This is not your post")

    Posts.delete(post_id)

    return {'success': True, 'message': "Post deleted"}


@app.put('/user/post')
def update_post(post: Post, post_id, current_user: Dict = Depends(get_current_user)):
    current_post = Posts.load({'id': post_id})

    if current_post.user_id != current_user[1]:

        raise HTTPException(status_code=403, detail="This is not your post")

    current_post.title = post.title
    current_post.body = post.body
    current_post.update()

    return {'success': True, 'message': "Post update"}


@app.post('/likes')
def like_post(post_id, current_user: Dict = Depends(get_current_user)):
    current_post = Posts.load({'id': post_id})

    if current_post is None:

        raise HTTPException(status_code=404, detail="Post not found")

    if current_post.user_id == current_user[1]:

        raise HTTPException(status_code=403, detail="This is your post")

    print(current_post.likes)
    likes_lst = []

    if current_post.likes != ' ':
        likes_lst = current_post.likes.split()

        if str(current_user[1]) in likes_lst:

            raise HTTPException(status_code=403, detail="You can liked post only once")

    likes_lst.append(str(current_user[1]))
    likes = " ".join(likes_lst)
    current_post.likes = likes
    current_post.sum_likes = int(current_post.sum_likes) + 1
    current_post.update()

    return {'success': True, 'message': "You liked this post"}
