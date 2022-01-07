from pathlib import Path
from typing import Union

import pymysql

from main.component.database import Database
from main.dto.createdFileDto import CreatedFileDto

class CreatedFileRepository:
    database: Database

    def __init__(self, database: Database):
        self.database = database

    def insert(self, createdFile: CreatedFileDto):
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO created_file (
                    splitted_file_id,
                    file,
                    size,
                    mime,
                    encoding
                ) VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                createdFile.splittedFileId,
                str(createdFile.file),
                createdFile.size,
                createdFile.mime,
                createdFile.encoding
            ))
            self.database.commit()
        self.database.reConnect()

    def find(self, id) -> Union[CreatedFileDto, None]:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    id,
                    splitted_file_id,
                    file,
                    size,
                    mime,
                    encoding
                FROM
                    created_file
                WHERE
                    id = {id}
            """)
            result: pymysql.connections.MySQLResult = cursor.fetchone()
        if result is None:
            return None
        dto = CreatedFileDto(
            id=result["id"],
            splittedFileId=result["splitted_file_id"],
            file=Path(result["file"]),
            size=result["size"],
            mime=result["mime"],
            encoding=result["encoding"],
        )
        self.database.reConnect()
        return dto

    def selectBySplittedFileId(self, splittedFileId: int) -> list[CreatedFileDto]:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    id,
                    splitted_file_id,
                    file,
                    size,
                    mime,
                    encoding
                FROM
                    splitted_file
                WHERE
                    splitted_file_id = {splittedFileId}
            """)
            results: list[pymysql.connections.MySQLResult] = cursor.fetchall()
        dtoList = [
            CreatedFileDto(
                id=result["id"],
                splittedFileId=result["splitted_file_id"],
                file=Path(result["file"]),
                size=result["size"],
                mime=result["mime"],
                encoding=result["encoding"],
            )
            for result in results
        ]
        self.database.reConnect()
        return dtoList
