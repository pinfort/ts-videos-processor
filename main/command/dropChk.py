from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip

from main.dto.executedFileDto import ExecutedFileDto
from main.component.database import Database
from main.component.executer import executeCommand
from main.repository.executedFileRepository import ExecutedFileRepository
from main.component.fileName import FileName
from main.dto.converter.executedFileDtoConverter import ExecutedFileDtoConverter

class DropChk():
    APPLICATION_PATH: str = str(Path(__file__).parent.parent.parent.joinpath("libraries\\tsDropChk\\tsDropChkx64.exe").absolute())
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

        executedFile: ExecutedFileDto = ExecutedFileDtoConverter.convert(filePath=path, drops=drops)

        print(f"""
            File executed.
            file={executedFile.file},
            drops={executedFile.drops},
            size={executedFile.size},
            recorded_at={executedFile.recorded_at},
            channel={executedFile.channel},
            channelName={executedFile.channelName},
            duration={executedFile.duration},
            title={executedFile.title}
        """)
        self.executedFileRepository.insert(executedFile)
        self.database.commit()
