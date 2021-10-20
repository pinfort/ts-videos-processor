from __future__ import with_statement
from pathlib import Path

import pymysql

from main.component.database import Database
from main.dto.executedFileDto import ExecutedFileDto

class ExecutedFileRepository:
    database: Database

    def __init__(self, database: Database):
        self.database = database

    def insert(self, executedFile: ExecutedFileDto):
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO executed_file(
                    file,
                    drops,
                    size,
                    recorded_at,
                    channel,
                    channelName,
                    duration,
                    title
                ) VALUES (
                    ?,
                    ?,
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
                executedFile.channelName,
                executedFile.duration,
                executedFile.title
            ))
        self.database.commit()

    def find(self, id: int) -> ExecutedFileDto:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    id,
                    file,
                    drops,
                    size,
                    recorded_at,
                    channel,
                    channelName,
                    duration,
                    title
                FROM
                    executed_file
                WHERE
                    id = {id}
            """)
            result: pymysql.connections.MySQLResult = cursor.fetchone()
        return ExecutedFileDto(
            id=result["id"],
            file=Path(result["file"]),
            drops=result["drops"],
            size=result["size"],
            recorded_at=result["recorded_at"],
            channel=result["channel"],
            channelName=result["channelName"],
            duration=result["duration"],
            title=result["title"]
        )

    def findByFile(self, file:Path) -> ExecutedFileDto:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    id,
                    file,
                    drops,
                    size,
                    recorded_at,
                    channel,
                    channelName,
                    duration,
                    title
                FROM
                    executed_file
                WHERE
                    file = ?
            """, (
                str(file),
            ))
            result: pymysql.connections.MySQLResult = cursor.fetchone()
        return ExecutedFileDto(
            id=result["id"],
            file=Path(result["file"]),
            drops=result["drops"],
            size=result["size"],
            recorded_at=result["recorded_at"],
            channel=result["channel"],
            channelName=result["channelName"],
            duration=result["duration"],
            title=result["title"]
        )
