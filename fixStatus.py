import sys
import json
from os.path import join, dirname
from dotenv import load_dotenv

from logging import Logger, config, getLogger
from pathlib import Path

from main.component.database import Database
from main.component.dependencyInjector import getInstance
from main.dto.createdFileDto import CreatedFileDto
from main.dto.executedFileDto import ExecutedFileDto
from main.dto.programDto import ProgramDto
from main.dto.splittedFileDto import SplittedFileDto
from main.enum.programStatus import ProgramStatus
from main.repository.executedFileRepository import ExecutedFileRepository
from main.repository.splittedFileRepository import SplittedFileRepository
from main.repository.createdFileRepository import CreatedFileRepository
from main.repository.programRepository import ProgramRepository
from main.component.nas import Nas


class FixStatus:
    executedFileRepository: ExecutedFileRepository = ExecutedFileRepository()
    splittedFileRepository: SplittedFileRepository = SplittedFileRepository()
    createdFileRepository: CreatedFileRepository = CreatedFileRepository()
    programRepository: ProgramRepository = ProgramRepository()
    logger: Logger
    nas: Nas = getInstance(Nas)

    def __init__(self) -> None:
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        with open("log_config.json", 'r') as f:
            config.dictConfig(json.load(f))
        self.logger = getLogger(__name__)

    def fix(self) -> None:
        self.logger.info(f"fixStatus processing.")
        selected: int = 1000
        offset = 0

        while selected >= 1000:
            programs = self.programRepository.selectByStatus(ProgramStatus.ERROR, offset, 1000)
            offset = offset + 1000
            selected = len(programs)
            self.logger.info(f"{selected} programs selected.")

            for program in programs:
                if self.isProgramCompleted(program):
                    self.logger.info(f"program completed! programId:{program.id}")
                    self.programRepository.updateStatusByexecutedFileId(program.executedFileId, ProgramStatus.COMPLETED)
                else:
                    self.logger.info(f"program not completed. programId:{program.id}")

    def isProgramCompleted(self, program: ProgramDto) -> bool:
        gzipExist: bool = False
        movieExist: bool = False
        splittedFiles = self.splittedFileRepository.selectByExecutedFileId(program.executedFileId)
        for splittedFile in splittedFiles:
            createdFiles = self.createdFileRepository.selectBySplittedFileId(splittedFile.id)
            for createdFile in createdFiles:
                if createdFile.encoding == "gzip" and createdFile.mime == "video/vnd.dlna.mpeg-tts":
                    gzipExist = True
                elif createdFile.mime == "video/mp4":
                    movieExist = True
                if not self.nas.fileOrDirectoryExists(createdFile.file):
                    return False
        if not gzipExist or not movieExist:
            return False
        return True

def main():
    """
    programテーブルのstatusを修正する。
    programのstatusがERRORとなっている行に対して、createdFileのファイルが実際にあるか確認し、
    m2ts.gzとmp4のファイルが最低１ファイルずつ実際に存在すれば、COMPLETEDにstatusを更新する。
    """
    fixStatus = FixStatus()
    fixStatus.fix()

if __name__ == "__main__":
    main()
