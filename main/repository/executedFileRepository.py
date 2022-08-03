from __future__ import with_statement
from datetime import datetime
from pathlib import Path
from typing import Union

import pymysql

from main.component.database import Database
from main.component.dependencyInjector import getInstance
from main.dto.executedFileDto import ExecutedFileDto
from main.enum.executedFileStatus import ExecutedFileStatus

class ExecutedFileRepository:
    database: Database = getInstance(Database, None)

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
                    title,
                    status
                ) VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                str(executedFile.file),
                executedFile.drops,
                executedFile.size,
                executedFile.recorded_at,
                executedFile.channel,
                executedFile.channelName,
                executedFile.duration,
                executedFile.title,
                executedFile.status.name
            ))
            self.database.commit()
        self.database.reConnect()

    def find(self, id: int) -> Union[ExecutedFileDto, None]:
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
                    title,
                    status
                FROM
                    executed_file
                WHERE
                    id = {id}
            """)
            result: pymysql.connections.MySQLResult = cursor.fetchone()
        if result is None:
            return None
        dto = ExecutedFileDto(
            id=result["id"],
            file=Path(result["file"]),
            drops=result["drops"],
            size=result["size"],
            recorded_at=result["recorded_at"],
            channel=result["channel"],
            channelName=result["channelName"],
            duration=result["duration"],
            title=result["title"],
            status=ExecutedFileStatus[result["status"]],
        )
        self.database.reConnect()
        return dto

    def findByFile(self, file:Path) -> Union[ExecutedFileDto, None]:
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
                    title,
                    status
                FROM
                    executed_file
                WHERE
                    file = %s
            """, (
                str(file),
            ))
            result: pymysql.connections.MySQLResult = cursor.fetchone()
        if result is None:
            return None
        dto = ExecutedFileDto(
            id=result["id"],
            file=Path(result["file"]),
            drops=result["drops"],
            size=result["size"],
            recorded_at=result["recorded_at"],
            channel=result["channel"],
            channelName=result["channelName"],
            duration=result["duration"],
            title=result["title"],
            status=ExecutedFileStatus[result["status"]],
        )
        self.database.reConnect()
        return dto

    def findByTitle(self, title:str) -> Union[ExecutedFileDto, None]:
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
                    title,
                    status
                FROM
                    executed_file
                WHERE
                    title = %s
            """, (
                title,
            ))
            result: pymysql.connections.MySQLResult = cursor.fetchone()
        if result is None:
            return None
        dto = ExecutedFileDto(
            id=result["id"],
            file=Path(result["file"]),
            drops=result["drops"],
            size=result["size"],
            recorded_at=result["recorded_at"],
            channel=result["channel"],
            channelName=result["channelName"],
            duration=result["duration"],
            title=result["title"],
            status=ExecutedFileStatus[result["status"]],
        )
        self.database.reConnect()
        return dto

    def deleteByFile(self, file:Path) -> None:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                DELETE
                FROM
                    executed_file
                WHERE
                    file = %s
            """, (
                str(file),
            ))
            self.database.commit()
        self.database.reConnect()

    def updateStatus(self, id: int, status: ExecutedFileStatus) -> None:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE
                    executed_file
                SET
                    status = %s
                WHERE
                    id = %s
            """, (
                status.name,
                id,
            ))
            self.database.commit()
        self.database.reConnect()

    def findByBroadCastInfo(self, recordedAt: datetime, channel: str, channelName: str) -> Union[ExecutedFileDto, None]:
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
                    title,
                    status
                FROM
                    executed_file
                WHERE
                    recorded_at = %s
                AND
                    channel = %s
                AND
                    channelName = %s
            """, (
                recordedAt,
                channel,
                channelName
            ))
            result: pymysql.connections.MySQLResult = cursor.fetchone()
        if result is None:
            return None
        dto = ExecutedFileDto(
            id=result["id"],
            file=Path(result["file"]),
            drops=result["drops"],
            size=result["size"],
            recorded_at=result["recorded_at"],
            channel=result["channel"],
            channelName=result["channelName"],
            duration=result["duration"],
            title=result["title"],
            status=ExecutedFileStatus[result["status"]],
        )
        self.database.reConnect()
        return dto
