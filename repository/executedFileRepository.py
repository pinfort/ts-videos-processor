import sqlite3
from pathlib import Path

from component.database import Database
from dto.executedFileDto import ExecutedFileDto

class ExecutedFileRepository:
    database: Database

    def __init__(self, database: Database):
        self.database = database

    def insert(self, executedFile: ExecutedFileDto):
        self.database.cursor.execute(f"""
            INSERT INTO executed_file(
                file,
                drops,
                size,
                recorded_at,
                channel,
                title
            ) VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
        """, (
            str(executedFile.file),
            executedFile.drops,
            executedFile.size,
            executedFile.recorded_at,
            executedFile.channel,
            executedFile.title
        ))
        self.database.commit()

    def find(self, id: int) -> ExecutedFileDto:
        self.database.cursor.execute(f"""
            SELECT
                id,
                file,
                drops,
                size,
                recorded_at as "rec_at [timestamp]",
                channel,
                title
            FROM
                executed_file
            WHERE
                id = {id}
        """)
        result: sqlite3.Row = self.database.cursor.fetchone()
        return ExecutedFileDto(
            id=result[0],
            file=Path(result[1]),
            drops=result[2],
            size=result[3],
            recorded_at=result[4],
            channel=result[5],
            title=result[6]
        )
    
    def findByFile(self, file:Path) -> ExecutedFileDto:
        self.database.cursor.execute(f"""
            SELECT
                id,
                file,
                drops,
                size,
                recorded_at as "rec_at [timestamp]",
                channel,
                title
            FROM
                executed_file
            WHERE
                file = ?
        """, (
            str(file),
        ))
        result: sqlite3.Row = self.database.cursor.fetchone()
        return ExecutedFileDto(
            id=result[0],
            file=Path(result[1]),
            drops=result[2],
            size=result[3],
            recorded_at=result[4],
            channel=result[5],
            title=result[6]
        )
