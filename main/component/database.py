from __future__ import annotations
from pathlib import Path
import pymysql

from main.config import database

# スレッドセーフではない
class Database:
    DATABASE_PATH = Path(__file__).parent.parent.parent.joinpath("database/database.sqlite")
    connection: pymysql.Connection

    def __init__(self):
        self.connection = pymysql.connect(
            host=database.DATABASE_HOST,
            user=database.DATABASE_USER,
            password=database.DATABASE_PASSWORD,
            db=database.DATABASE_DATABASE,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )

    def rollback(self):
        self.connection.rollback()

    def commit(self):
        self.connection.commit()

    def disConnect(self):
        self.connection.close()

    def __del__(self):
        self.disConnect()
