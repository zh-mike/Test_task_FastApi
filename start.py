from db_api import provider as db

if __name__ == '__main__':
    db.create_users_table()
    db.create_posts_table()