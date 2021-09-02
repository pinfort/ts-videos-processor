import sqlite3
from pathlib import Path
from main.component.fileName import FileName
from main.component.database import Database
from main.dto.executedFileDto import ExecutedFileDto


database = Database()

database.cursor.execute("""
    SELECT
        id,
        file,
        drops,
        size,
        recorded_at as "rec_at [timestamp]",
        channel,
        channelName,
        title
    FROM
        executed_file
""")
result: list[sqlite3.Row] = database.cursor.fetchall()

for item in result:
    dto = ExecutedFileDto(
        id=item[0],
        file=Path(item[1]),
        drops=item[2],
        size=item[3],
        recorded_at=item[4],
        channel=item[5],
        channelName=FileName(Path(item[1]).name).channelName,
        title=item[7]
    )
    database.cursor.execute("""
        UPDATE
            executed_file
        SET
            channelName=?
        WHERE
            id=?
    """,
    (
        dto.channelName,
        dto.id
    ))
database.commit()
