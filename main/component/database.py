from __future__ import annotations
from pathlib import Path
import pymysql
from main.component.dependencyInjector import register

from main.config import database

# スレッドセーフではない
class Database:
    DATABASE_PATH = Path(__file__).parent.parent.parent.joinpath("database/database.sqlite")
    connection: pymysql.Connection

    def __init__(self):
        self.connect()

    def connect(self):
        self.connection = pymysql.connect(
            host=database.DATABASE_HOST,
            user=database.DATABASE_USER,
            password=database.DATABASE_PASSWORD,
            db=database.DATABASE_DATABASE,
            port=int(database.DATABASE_PORT),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )

    def rollback(self):
        self.connection.rollback()

    def commit(self):
        self.connection.commit()

    def disConnect(self):
        self.connection.close()

    def reConnect(self):
        self.disConnect()
        self.connect()

    def __del__(self):
        self.disConnect()

@register
def registerDatabase() -> Database:
    return Database()

registerDatabase()
