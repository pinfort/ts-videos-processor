from __future__ import with_statement
from pathlib import Path
from typing import Union

import pymysql

from main.component.database import Database
from main.component.dependencyInjector import getInstance
from main.dto.programDto import ProgramDto
from main.enum.programStatus import ProgramStatus

class ProgramRepository:
    database: Database = getInstance(Database)

    def insert(self, program: ProgramDto):
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO program(
                    name,
                    executed_file_id,
                    status
                ) VALUES (
                    %s,
                    %s,
                    %s
                )
            """, (
                program.name,
                program.executedFileId,
                program.status.name,
            ))
            self.database.commit()
        self.database.reConnect()

    def updateStatusByexecutedFileId(self, executedFileId: int, status: ProgramStatus) -> None:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE
                    program
                SET
                    status = %s
                WHERE
                    executed_file_id = %s
            """, (
                status.name,
                executedFileId,
            ))
            self.database.commit()
        self.database.reConnect()

    def findByName(self, name: str) -> Union[ProgramDto, None]:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    id,
                    name,
                    executed_file_id,
                    status
                FROM
                    program
                WHERE
                    name = %s
            """, (
                name,
            ))
            result: pymysql.connections.MySQLResult = cursor.fetchone()
        if result is None:
            return None
        dto = ProgramDto(
            id=result["id"],
            name=result["name"],
            executedFileId=result["executed_file_id"],
            status=ProgramStatus[result["status"]],
        )
        self.database.reConnect()
        return dto

    def findByExecutedFileId(self, executedFileId: int) -> Union[ProgramDto, None]:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    id,
                    name,
                    executed_file_id,
                    status
                FROM
                    program
                WHERE
                    executed_file_id = %s
            """, (
                executedFileId,
            ))
            result: pymysql.connections.MySQLResult = cursor.fetchone()
        if result is None:
            return None
        dto = ProgramDto(
            id=result["id"],
            name=result["name"],
            executedFileId=result["executed_file_id"],
            status=ProgramStatus[result["status"]],
        )
        self.database.reConnect()
        return dto

    def find(self, id: int) -> Union[ProgramDto, None]:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    id,
                    name,
                    executed_file_id,
                    status
                FROM
                    program
                WHERE
                    id = %s
            """, (
                id,
            ))
            result: pymysql.connections.MySQLResult = cursor.fetchone()
        if result is None:
            return None
        dto = ProgramDto(
            id=result["id"],
            name=result["name"],
            executedFileId=result["executed_file_id"],
            status=ProgramStatus[result["status"]],
        )
        self.database.reConnect()
        return dto

    def deleteByexecutedFileId(self, executedFileId: int) -> None:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                DELETE
                FROM
                    program
                WHERE
                    executed_file_id = %s
            """, (
                executedFileId,
            ))
            self.database.commit()
        self.database.reConnect()

    def selectByStatus(self, status: ProgramStatus, offset:int, limit: int) -> list[ProgramDto]:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    id,
                    name,
                    executed_file_id,
                    status
                FROM
                    program
                WHERE
                    status = %s
                LIMIT
                    %s, %s
            """, (
                status.name,
                offset,
                limit,
            ))
            results: list[pymysql.connections.MySQLResult] = cursor.fetchall()
        dtoList = [
            ProgramDto(
                id=result["id"],
                name=result["name"],
                executedFileId=result["executed_file_id"],
                status=ProgramStatus[result["status"]],
            )
            for result in results
        ]
        self.database.reConnect()
        return dtoList
