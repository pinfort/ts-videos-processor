from __future__ import annotations
from pathlib import Path
import sqlite3
from sqlite3.dbapi2 import Cursor

# スレッドセーフではない
class Database:
    DATABASE_PATH = Path(__file__).parent.parent.joinpath("database/database.sqlite")
    connection: sqlite3.Connection
    cursor: Cursor

    def __init__(self, path: str | None = None):
        if(path is None):
            self.connection = sqlite3.connect(Database.DATABASE_PATH)
        else:
            self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

    def rollback(self):
        self.connection.rollback()

    def commit(self):
        self.connection.commit()

    def disConnect(self):
        self.connection.close()
    
    def __del__(self):
        self.disConnect()
