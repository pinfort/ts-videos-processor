import sys
import json
from os.path import join, dirname
from dotenv import load_dotenv

from logging import Logger, config, getLogger
from pathlib import Path

from main.component.database import Database
from main.dto.createdFileDto import CreatedFileDto
from main.dto.executedFileDto import ExecutedFileDto
from main.dto.splittedFileDto import SplittedFileDto
from main.repository.executedFileRepository import ExecutedFileRepository
from main.repository.splittedFileRepository import SplittedFileRepository
from main.repository.createdFileRepository import CreatedFileRepository
from main.repository.programRepository import ProgramRepository
from main.component.nas import Nas


class Reset:
    database: Database
    executedFileRepository: ExecutedFileRepository
    splittedFileRepository: SplittedFileRepository
    createdFileRepository: CreatedFileRepository
    programRepository: ProgramRepository
    logger: Logger
    nas: Nas

    def __init__(self) -> None:
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        with open("log_config.json", 'r') as f:
            config.dictConfig(json.load(f))
        self.logger = getLogger(__name__)
        self.database = Database()
        self.executedFileRepository = ExecutedFileRepository(self.database)
        self.createdFileRepository = CreatedFileRepository(self.database)
        self.splittedFileRepository = SplittedFileRepository(self.database)
        self.programRepository = ProgramRepository(self.database)
        self.nas = Nas()

    def reset(self, path:Path) -> None:
        self.logger.info(f"reset processing. path:{path}")
        executedFile: ExecutedFileDto = self.executedFileRepository.findByFile(path)
        splittedFiles: list[SplittedFileDto] = self.splittedFileRepository.selectByExecutedFileId(executedFile.id)
        for f in splittedFiles:
            createdFiles: list[CreatedFileDto] = self.createdFileRepository.selectBySplittedFileId(f.id)
            for c in createdFiles:
                self.logger.info(f"created file found. path:{c.file}")
                # TODO delete NAS files
            self.createdFileRepository.deleteBySplittedFileId(f.id)

            self.logger.info(f"splitted file found. path:{f.file}")
            if f.file.exists():
                self.logger.info(f"splitted file will be deleted. path:{f.file}")
                f.file.unlink()

        self.splittedFileRepository.deleteByExecutedFileId(executedFile.id)
        self.logger.info(f"splitted file deleted. executedFileId:{executedFile.id}")

        self.programRepository.deleteByexecutedFileId(executedFile.id)
        self.logger.info(f"program deleted. executedFileId:{executedFile.id}")
        # 元ファイルは削除しない!!!
        # if executedFile.file.exists():
        #     self.logger.info(f"executed file will be deleted. executedFile:{executedFile.file}")
        #     executedFile.file.unlink()

        self.executedFileRepository.deleteByFile(path)

def main():
    """
    処理をリセットする。生成されたファイルは軒並み削除される。一部削除されないことがある。
    """
    reset = Reset()
    reset.reset(sys.argv[1])

if __name__ == "__main__":
    main()
