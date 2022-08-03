import pymysql
from main.component.database import Database
from main.component.dependencyInjector import getInstance
from main.dto.programWithExecuted import ProgramWithExecuted
from main.enum.programStatus import ProgramStatus


class ProgramWithExecutedRepository:
    database: Database = getInstance(Database, None)

    def selectByNameAndStatus(self, keyword: str, status: ProgramStatus) -> list[ProgramWithExecuted]:
        with self.database.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    pg.id,
                    pg.name,
                    pg.executed_file_id,
                    pg.status,
                    ex.drops,
                    ex.size,
                    ex.recorded_at,
                    ex.channel,
                    ex.channelName,
                    ex.title,
                    ex.duration
                FROM
                    program pg
                INNER JOIN executed_file ex
                ON pg.executed_file_id = ex.id
                WHERE
                    pg.name LIKE %s
                AND pg.status = %s
                ORDER BY recorded_at
            """, (
                f"%{keyword}%",
                status.name,
            ))
            results: list[pymysql.connections.MySQLResult] = cursor.fetchall()
        dtoList = [
            ProgramWithExecuted(
                id=result["id"],
                name=result["name"],
                executedFileId=result["executed_file_id"],
                status=ProgramStatus[result["status"]],
                drops=result["drops"],
                size=result["size"],
                recorded_at=result["recorded_at"],
                channel=result["channel"],
                channelName=result["channelName"],
                title=result["title"],
                duration=result["duration"]
            )
            for result in results
        ]
        self.database.reConnect()
        return dtoList
