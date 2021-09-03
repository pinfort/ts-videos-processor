from pathlib import Path
from main.component.database import Database
from main.repository.splittedFileRepository import SplittedFileRepository
from main.dto.splittedFileDto import SplittedFileDto

def test_insert():
    database: Database = Database(':memory:')

    database.cursor.executescript("""

        PRAGMA foreign_keys=true;

        CREATE TABLE "executed_file" (
            "id"	INTEGER NOT NULL,
            "file"	TEXT NOT NULL UNIQUE,
            "drops"	INTEGER NOT NULL,
            "size"	INTEGER NOT NULL,
            "recorded_at"	NUMERIC NOT NULL,
            "channel"	TEXT NOT NULL,
            "title"	TEXT NOT NULL,
            "channelName"	TEXT NOT NULL,
            "duration"	REAL NOT NULL,
            PRIMARY KEY("id")
        );

        CREATE TABLE "splitted_file" (
            "id"	INTEGER NOT NULL,
            "executed_file_id"	INTEGER NOT NULL,
            "file"	TEXT NOT NULL,
            "size"	INTEGER NOT NULL,
            "duration"	REAL NOT NULL,
            FOREIGN KEY("executed_file_id") REFERENCES "executed_file"("id"),
            PRIMARY KEY("id")
        );

        INSERT INTO "executed_file"(
            "id",
            "file",
            "drops",
            "size",
            "recorded_at",
            "channel",
            "channelName",
            "duration",
            "title"
        ) VALUES (
            "1",
            "test",
            "1",
            "1",
            "1",
            "a",
            "a",
            "1",
            "a"
        )
    """)
    database.commit()

    repository: SplittedFileRepository = SplittedFileRepository(database)
    dto = SplittedFileDto(
        1,
        1,
        Path("test"),
        1,
        1
    )
    repository.insert(dto)

    find = repository.find(1)
    assert find.id == 1
    assert find.executedFileId == 1
    assert find.file == Path("test")
    assert find.size == 1
    assert find.duration == 1
