import sqlite3
from pathlib import Path
from typing import Union

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
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                splittedFile.executedFileId,
                str(splittedFile.file),
                splittedFile.size,
                splittedFile.duration
            ))
            self.database.commit()
        self.database.reConnect()

    def find(self, id) -> Union[SplittedFileDto, None]:
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
        if result is None:
            return None
        dto = SplittedFileDto(
            id=result["id"],
            executedFileId=result["executed_file_id"],
            file=Path(result["file"]),
            size=result["size"],
            duration=result["duration"]
        )
        self.database.reConnect()
        return dto

    def selectByExecutedFileId(self, executedFileId: int) -> list[SplittedFileDto]:
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
                    executed_file_id = {executedFileId}
            """)
            results: list[pymysql.connections.MySQLResult] = cursor.fetchall()
        dtoList = [
            SplittedFileDto(
                id=result["id"],
                executedFileId=result["executed_file_id"],
                file=Path(result["file"]),
                size=result["size"],
                duration=result["duration"]
            )
            for result in results
        ]
        self.database.reConnect()
        return dtoList

    def findByFile(self, file: Path):
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
                    file = %s
            """, (
                str(file),
            ))
            result: pymysql.connections.MySQLResult = cursor.fetchone()
        if result is None:
            return None
        dto = SplittedFileDto(
            id=result["id"],
            executedFileId=result["executed_file_id"],
            file=Path(result["file"]),
            size=result["size"],
            duration=result["duration"]
        )
        self.database.reConnect()
        return dto
