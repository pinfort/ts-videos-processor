from ctypes import Union
from logging import Logger, getLogger

from main.component.database import Database
from main.component.dependencyInjector import getInstance
from main.dto.createdFileDto import CreatedFileDto
from main.dto.executedFileDto import ExecutedFileDto
from main.dto.programDto import ProgramDto
from main.dto.splittedFileDto import SplittedFileDto
from main.repository.createdFileRepository import CreatedFileRepository
from main.repository.executedFileRepository import ExecutedFileRepository
from main.repository.programRepository import ProgramRepository
from main.repository.splittedFileRepository import SplittedFileRepository
from main.component.nas import Nas

class RemoveProgram():
    executedFileRepository: ExecutedFileRepository = ExecutedFileRepository()
    splittedFileRepository: SplittedFileRepository = SplittedFileRepository()
    createdFileRepository: CreatedFileRepository = CreatedFileRepository()
    programRepository: ProgramRepository = ProgramRepository()
    logger: Logger = getLogger(__name__)
    nas: Nas = getInstance(Nas, None)

    def remove(self, programId: int) -> None:
        self.logger.info(f"reset processing. programId:{programId}")
        program: Union[ProgramDto, None] = self.programRepository.find(programId)
        if program is None:
            self.logger.error(f"program not found. aborting. id:{programId}")
            return
        self.logger.info(f"program will be deleted: {program.name}")
        response = input("is it OK? [y/N]>")
        if response.lower() != "y":
            self.logger.error(f"cancelled. aborting. id:{programId}")
            return
        executedFile: Union[ExecutedFileDto, None] = self.executedFileRepository.find(program.executedFileId)
        if executedFile is None:
            self.logger.error(f"executedFile not found. aborting. executedfileId:{program.executedFileId}")
            return
        splittedFiles: list[SplittedFileDto] = self.splittedFileRepository.selectByExecutedFileId(executedFile.id)
        for f in splittedFiles:
            createdFiles: list[CreatedFileDto] = self.createdFileRepository.selectBySplittedFileId(f.id)
            for c in createdFiles:
                self.logger.info(f"created file found. path:{c.file}")
                if self.nas.fileOrDirectoryExists(c.file):
                    self.logger.info(f"file deleted. file:{c.file}")
                    self.nas.removeFile(c.file)
            self.createdFileRepository.deleteBySplittedFileId(f.id)

            self.logger.info(f"splitted file found. path:{f.file}")
            if f.file.exists():
                self.logger.info(f"splitted file will be deleted. path:{f.file}")
                f.file.unlink()
            if f.file.parent.joinpath("succeeded").joinpath(f.file.name).exists():
                self.logger.info(f"splitted file will be deleted. path:{f.file.parent.joinpath('succeeded').joinpath(f.file.name)}")
                f.file.parent.joinpath("succeeded").joinpath(f.file.name).unlink()

        self.splittedFileRepository.deleteByExecutedFileId(executedFile.id)
        self.logger.info(f"splitted file deleted. executedFileId:{executedFile.id}")

        self.programRepository.deleteByexecutedFileId(executedFile.id)
        self.logger.info(f"program deleted. executedFileId:{executedFile.id}")
        # 元ファイルは削除しない!!!
        # if executedFile.file.exists():
        #     self.logger.info(f"executed file will be deleted. executedFile:{executedFile.file}")
        #     executedFile.file.unlink()

        self.executedFileRepository.deleteByFile(executedFile.file)
