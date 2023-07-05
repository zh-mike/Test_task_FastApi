from db_api import Database

from pathlib import Path

db_path = Path('db_api', "database.db")
db = Database(db_path=db_path)