from pathlib import Path

from dto.executedFileDto import ExecutedFileDto
from component.database import Database
from component.executer import executeCommand
from repository.executedFileRepository import ExecutedFileRepository
from component.fileName import FileName

class DropChk():
    APPLICATION_PATH: str = str(Path(__file__).parent.parent.joinpath("libraries\\tsDropChk\\tsDropChkx64.exe").absolute())
    OPTIONS = "-nolog -srcpath"
    executedFileRepository: ExecutedFileRepository
    database: Database

    def __init__(self) -> None:
        self.database = Database()
        self.executedFileRepository = ExecutedFileRepository(self.database)

    def dropChk(self, path: Path):
        if(not path.exists()):
            raise Exception(f"file not found path:{path}")
        command = DropChk.APPLICATION_PATH + " " + DropChk.OPTIONS + " \"" + str(path) + "\""
        print(f"dropchk starting with command:{command} path:{path}")
        drops: int = executeCommand(command)
        fileSize: int = path.stat().st_size
        fileName: FileName = FileName(path.name)

        executedFile: ExecutedFileDto = ExecutedFileDto(
            id=1,
            file=path,
            drops=drops,
            size=fileSize,
            recorded_at=fileName.recorded_at,
            channel=fileName.channel,
            title=fileName.title
        )
        print(f"""
            File executed.
            file={executedFile.file},
            drops={executedFile.drops},
            size={executedFile.size},
            recorded_at={executedFile.recorded_at},
            channel={executedFile.channel},
            title={executedFile.title}
        """)
        self.executedFileRepository.insert(executedFile)
        self.database.commit()
