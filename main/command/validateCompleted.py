from cmath import inf
import itertools
from logging import Logger, getLogger

from main.component.database import Database
from main.component.dependencyInjector import getInstance
from main.dto.createdFileDto import CreatedFileDto
from main.repository.createdFileRepository import CreatedFileRepository
from main.repository.splittedFileRepository import SplittedFileRepository
from main.repository.programRepository import ProgramRepository
from main.component.nas import Nas

class ValidateCompleted():
    database: Database
    createdFileRepository: CreatedFileRepository = CreatedFileRepository()
    splittedFileRepository: SplittedFileRepository = SplittedFileRepository()
    programRepository: ProgramRepository = ProgramRepository()
    logger: Logger = getLogger(__name__)
    nas: Nas = getInstance(Nas)

    def validate(self, programId: int) -> bool:
        self.logger.info(f"validating program id:{programId}")
        program = self.programRepository.find(programId)
        if program is None:
            self.logger.info(f"program provided id is not found id:{programId}")
            return False

        splittedFiles = self.splittedFileRepository.selectByExecutedFileId(program.executedFileId)
        if len(splittedFiles) == 0:
            self.logger.info(f"splittedFile is not found executedFileId:{program.executedFileId}, programId:{program.id}")
            return False

        createdFiles: list[CreatedFileDto] = list(itertools.chain.from_iterable([self.createdFileRepository.selectBySplittedFileId(splittedFile.id) for splittedFile in splittedFiles]))
        self.logger.info(f"found created files:{createdFiles}")
        existCreatedFiles: list[CreatedFileDto] = [createdFile for createdFile in createdFiles if self.nas.fileOrDirectoryExists(createdFile.file)]
        self.logger.info(f"exist createdFiles:{existCreatedFiles}")

        gzipFileExist: bool = False
        movieFileExist: bool = False

        for createdFile in existCreatedFiles:
            if createdFile.encoding == "gzip" and createdFile.mime == "video/vnd.dlna.mpeg-tts":
                self.logger.debug(f"gzip file found! path:{createdFile.file}, id:{createdFile.id}")
                gzipFileExist = True
            elif createdFile.mime == "video/mp4":
                self.logger.debug(f"video file found! path:{createdFile.file}, id:{createdFile.id}")
                movieFileExist = True

        if gzipFileExist and movieFileExist:
            self.logger.info(f"program valid. programId:{program.id}")
            return True
        self.logger.info(f"program invalid. programId:{program.id}, name:{program.name}, gzipFileExist:{gzipFileExist}, movieFileExist:{movieFileExist}")
        return False
