from model import Model

class Users(Model):
    _table_name = 'Users'
    _fields = {
        'id': None,
        'login': None,
        'password': None,
    }


class Posts(Model):
    _table_name = 'Posts'
    _fields = {
        'id': None,
        'title': None,
        'body': None,
        'user_id': None,
        'likes': '',
        'sum_likes': 0,
    }


if __name__ == '__main__':



    # us1 = Posts()
    post = Posts()
    print(post._properties)

    # us1.title = '23333'
    # us1.body = '33333'
    # us1.user_id = '1'
    # us1.login = 1
    # us1.save()