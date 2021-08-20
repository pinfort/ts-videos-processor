import sqlite3
from pathlib import Path

from component.database import Database
from dto.splittedFileDto import SplittedFileDto

class SplittedFileRepository:
    database: Database

    def __init__(self, database: Database):
        self.database = database

    def insert(self, splittedFile: SplittedFileDto):
        self.database.cursor.execute(f"""
            INSERT INTO splitted_file (
                executed_file_id,
                file,
                size
            ) VALUES (
                ?,
                ?,
                ?
            )
        """, (
            splittedFile.executedFileId,
            str(splittedFile.file),
            splittedFile.size
        ))
        self.database.commit()

    def find(self, id) -> SplittedFileDto:
        self.database.cursor.execute(f"""
            SELECT
                id,
                executed_file_id,
                file,
                size
            FROM
                splitted_file
            WHERE
                id = {id}
        """)
        result: sqlite3.Row = self.database.cursor.fetchone()
        return SplittedFileDto(
            id=result[0],
            executedFileId=result[1],
            file=Path(result[2]),
            size=result[3]
        )
