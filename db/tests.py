from db_api.provider import create_connect
from db.user import User

if name == "main":
    create_connect()

    new_user = User()
    new_user.login = "test3"
    new_user.password = "test3"
    new_user.save()

    new_user_id = new_user.user_id
    print(new_user_id)

    user = User.load(new_user_id)
    user.delete()

    users = User.load_by({"password": "dddd"})
    for user in users:
        print(dict(user))

    try:
        new_user = User()
        new_user.login = "zxczxc"
        new_user.save()
    except Exception as e:
        print(e)

    try:
        new_user = User.load(2)
        new_user.user_id = 666
        new_user.user_id = 222

        print(new_user.get_modified_properties())
        new_user.save()
    except Exception as e:
        print(e)

    user = User.load(2)
    user.update({
        'login': 'new_login',
        'password': 'new_password',
    })
    print(user.get_modified_properties())