import unittest
from pathlib import Path
from component.database import Database
from repository.splittedFileRepository import SplittedFileRepository
from dto.splittedFileDto import SplittedFileDto

class SplittedFileRepositoryTest(unittest.TestCase):
    def test_insert(self):
        database: Database = Database(':memory:')

        database.cursor.executescript("""

            PRAGMA foreign_keys=true;

            CREATE TABLE "executed_file" (
                "id"	INTEGER NOT NULL,
                "file"	TEXT NOT NULL,
                "drops"	INTEGER NOT NULL,
                "size"	INTEGER NOT NULL,
                "recorded_at"	NUMERIC NOT NULL,
                "channel"	TEXT NOT NULL,
                "title"	TEXT NOT NULL,
                PRIMARY KEY("id")
            );

            CREATE TABLE "splitted_file" (
                "id"	INTEGER NOT NULL,
                "executed_file_id"	INTEGER NOT NULL,
                "file"	TEXT NOT NULL,
                "size"	INTEGER NOT NULL,
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
                "title"
            ) VALUES (
                "1",
                "test",
                "1",
                "1",
                "1",
                "a",
                "a"
            )
        """)
        database.commit()

        repository: SplittedFileRepository = SplittedFileRepository(database)
        dto = SplittedFileDto(
            1,
            1,
            Path("test"),
            1
        )
        repository.insert(dto)

        find = repository.find(1)
        self.assertEqual(find.id, 1)
        self.assertEqual(find.executedFileId, 1)
        self.assertEqual(find.file, Path("test"))
        self.assertEqual(find.size, 1)

if __name__  == '__main__':
    unittest.main()
