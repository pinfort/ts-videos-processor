import sqlite3
from pathlib import Path

import pymysql

from main.component.database import Database
from main.dto.splittedFileDto import SplittedFileDto

class SplittedFileRepository:
    database: Database

    def __init__(self, database: Database):
        self.database = database

    def insert(self, splittedFile: SplittedFileDto):
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO splitted_file (
                    executed_file_id,
                    file,
                    size,
                    duration
                ) VALUES (
                    ?,
                    ?,
                    ?,
                    ?
                )
            """, (
                splittedFile.executedFileId,
                str(splittedFile.file),
                splittedFile.size,
                splittedFile.duration
            ))
        self.database.commit()

    def find(self, id) -> SplittedFileDto:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    id,
                    executed_file_id,
                    file,
                    size,
                    duration
                FROM
                    splitted_file
                WHERE
                    id = {id}
            """)
            result: pymysql.connections.MySQLResult = cursor.fetchone()
        return SplittedFileDto(
            id=result["id"],
            executedFileId=result["executed_file_id"],
            file=Path(result["file"]),
            size=result["size"],
            duration=result["duration"]
        )

    def selectByExecutedFileId(self, executedFileId: int) -> list[SplittedFileDto]:
        self.database.cursor.execute(f"""
            SELECT
                id,
                executed_file_id,
                file,
                size,
                duration
            FROM
                splitted_file
            WHERE
                executed_file_id = {executedFileId}
        """)
        results: list[sqlite3.Row] = self.database.cursor.fetchall()
        return [
            SplittedFileDto(
                id=result[0],
                executedFileId=result[1],
                file=Path(result[2]),
                size=result[3],
                duration=result[4]
            )
            for result in results
        ]
