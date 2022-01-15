from os import name
from pathlib import Path
from logging import Logger, getLogger
from typing import Union
from moviepy.video.io.VideoFileClip import VideoFileClip

from main.dto.executedFileDto import ExecutedFileDto
from main.component.database import Database
from main.component.executer import executeCommand
from main.dto.programDto import ProgramDto
from main.enum.programStatus import ProgramStatus
from main.repository.executedFileRepository import ExecutedFileRepository
from main.component.fileName import FileName
from main.dto.converter.executedFileDtoConverter import ExecutedFileDtoConverter
from main.repository.programRepository import ProgramRepository

class DropChk():
    APPLICATION_PATH: str = str(Path(__file__).parent.parent.parent.joinpath("libraries\\tsDropChk\\tsDropChkx64.exe").absolute())
    OPTIONS = "-nolog -srcpath"
    executedFileRepository: ExecutedFileRepository
    programRepository: ProgramRepository
    database: Database
    logger: Logger

    def __init__(self) -> None:
        self.database = Database()
        self.executedFileRepository = ExecutedFileRepository(self.database)
        self.programRepository = ProgramRepository(self.database)
        self.logger = getLogger(__name__)

    def dropChk(self, path: Path) -> bool:
        if(not path.exists()):
            raise Exception(f"file not found path:{path}")

        programExistanceCheck: Union[ProgramDto, None] = self.programRepository.findByName(path.name)
        self.logger.info(f"program existance check. name:{path.name}")
        if not (programExistanceCheck is None):
            self.logger.warn(f"provided file path already processed. ingoring. path:{path}")
            if programExistanceCheck.status is not ProgramStatus.COMPLETED:
                self.logger.warn(f"provided already processed but not completed. if you want retry, remove all files and DB records and restart again. path:{path}")
            return False

        command = DropChk.APPLICATION_PATH + " " + DropChk.OPTIONS + " \"" + str(path) + "\""
        self.logger.info(f"dropchk starting with command:{command} path:{path}")
        drops: int = executeCommand(command)
        self.logger.info(f"dropchk finished. path:{path}, drops:{drops}")

        executedFile: ExecutedFileDto = ExecutedFileDtoConverter.convert(filePath=path, drops=drops)

        self.logger.info(f"""
            File executed.
            file={executedFile.file},
            drops={executedFile.drops},
            size={executedFile.size},
            recorded_at={executedFile.recorded_at},
            channel={executedFile.channel},
            channelName={executedFile.channelName},
            duration={executedFile.duration},
            title={executedFile.title},
            status={executedFile.status.name}
        """)
        self.executedFileRepository.insert(executedFile)

        executedFileCreated: ExecutedFileDto = self.executedFileRepository.findByFile(executedFile.file)
        program: ProgramDto = ProgramDto(
            id=1,
            name=executedFile.file.name,
            executedFileId=executedFileCreated.id,
            status=ProgramStatus.REGISTERED
        )
        self.programRepository.insert(program)
        self.database.commit()
        return True

    def rollback(self, path:Path) -> None:
        """
        処理を巻き戻す。いまのところはDB登録処理だけ
        """
        self.logger.warn(f"dropChkTask. rollbacking and deleteing DB records. path:{path}")
        executedFile: ExecutedFileDto = self.executedFileRepository.findByFile(path)
        self.programRepository.deleteByexecutedFileId(executedFile.id)
        self.executedFileRepository.deleteByFile(path)

        self.logger.warn(f"dropChk rollback task completed. path:{path}")
