from os import unlink
from pathlib import Path
import glob
from logging import Logger, getLogger
from moviepy.video.io.VideoFileClip import VideoFileClip

from main.dto.splittedFileDto import SplittedFileDto
from main.dto.executedFileDto import ExecutedFileDto
from main.dto.converter.splittedFileDtoConverter import SplittedFileDtoConverter
from main.component.database import Database
from main.component.executer import executeCommand
from main.enum.executedFileStatus import ExecutedFileStatus
from main.repository.splittedFileRepository import SplittedFileRepository
from main.repository.executedFileRepository import ExecutedFileRepository
from main.component.mainSplittedFileFinder import MainSplittedFileFinder

class TsSplitter():
    APPLICATION_PATH: str = str(Path(__file__).parent.parent.parent.joinpath("libraries\\TsSplitter128\\TsSplitter.exe").absolute())
    OPTIONS = "-SD -EIT -1SEG"
    WORK_DIRECTORY = "tssplitter"
    splittedFileRepository: SplittedFileRepository
    executedFileRepository: ExecutedFileRepository
    database: Database
    logger: Logger

    def __init__(self):
        self.database = Database()
        self.splittedFileRepository = SplittedFileRepository(self.database)
        self.executedFileRepository = ExecutedFileRepository(self.database)
        self.mainSplittedFileFinder = MainSplittedFileFinder(self.database)
        self.logger = getLogger(__name__)

    def tsSplitter(self, path: Path) -> SplittedFileDto:
        self.__validate(path)

        originalFile: ExecutedFileDto = self.executedFileRepository.findByFile(path)

        outputPath = path.parent.joinpath(TsSplitter.WORK_DIRECTORY)
        if(not outputPath.exists()):
            outputPath.mkdir()

        self.__executeCommand(path, outputPath)

        files = self.findFiles(originalFile)
        if(len(files) == 0):
            raise Exception(f"splitted file not found. original:{originalFile}")

        for file in files:
            self.logger.info(f"found splitted file. path:{file}")
            self.splittedFileRepository.insert(file)
            self.logger.info(f"""
            File Splitting executed.
            id={file.id},
            executeFileId={file.executedFileId},
            file={file.file},
            size={file.size},
            duration={file.duration},
            status={file.status}
            """)

        executedFile: ExecutedFileDto = self.executedFileRepository.findByFile(path)
        self.executedFileRepository.updateStatus(executedFile.id, ExecutedFileStatus.SPLITTED)
        splittedFile: SplittedFileDto = self.mainSplittedFileFinder.splittedFileFromExecutedFile(executedFile)
        # メインファイルのオブジェクトを返す
        return splittedFile

    def findFiles(self, originalFile:ExecutedFileDto) -> list[SplittedFileDto]:
        files: list[SplittedFileDto] = list()
        directory = originalFile.file.parent.joinpath(TsSplitter.WORK_DIRECTORY)
        pattern = glob.escape(originalFile.file.stem) + "*.m2ts"
        self.logger.debug(f"search pattern {pattern}")
        for file in directory.glob(pattern):
            self.logger.debug(f"file found {file}")
            files.append(
                SplittedFileDtoConverter.convert(
                    filePath=file,
                    originalFile=originalFile
                )
            )
        return files
    
    def __validate(self, path: Path) -> None:
        # 対象パスの存在チェック
        if(not path.exists()):
            raise Exception(f"file not found path:{path}")
        
        # すでに存在しているときは、意図しない上書きを防ぐためエラーにする
        originalFile: ExecutedFileDto = self.executedFileRepository.findByFile(path)
        existingFiles = self.findFiles(originalFile)
        if(len(existingFiles) > 0):
            self.logger.error(f"ERROR: splitted file already exist! original:{originalFile}")
            for file in existingFiles:
                self.logger.error(file)
            raise Exception(f"splitted file already exist! original:{originalFile}")
    
    def __executeCommand(self, inputPath: Path, outPutPath: Path) -> None:
        command = TsSplitter.APPLICATION_PATH + " " + TsSplitter.OPTIONS + " -OUT \"" + str(outPutPath.absolute()) + "\" -SEP \"" + str(inputPath.absolute()) + "\""
        self.logger.info(f"tsSpliter starting with command:{command}")
        exitCode: int = 0
        try:
            exitCode = executeCommand(command)
        except:
            pass
        if(exitCode != 0):
            self.logger.error("splitting file become error!")
            raise Exception("splitting file become error!")

    def rollback(self, path: Path) -> None:
        originalFile: ExecutedFileDto = self.executedFileRepository.findByFile(path)
        self.logger.warn(f"tsSplitterTask. rollbacking and deleting files and DB records. executedFile:{originalFile.file}, executedFileId:{originalFile.id}")

        # 実ファイル削除
        directory = originalFile.file.parent.joinpath(TsSplitter.WORK_DIRECTORY)
        pattern = glob.escape(originalFile.file.stem) + "*.m2ts"
        self.logger.debug(f"search pattern {pattern}")
        for file in directory.glob(pattern):
            self.logger.warn(f"tsSplitter rollback task. deleting file. file:{file}")
            if(file.exists()):
                file.unlink()

        # DB削除
        self.splittedFileRepository.deleteByExecutedFileId(originalFile.id)

        self.logger.warn(f"tsSplitter rollback task completed. executedFile:{originalFile.file}, executedFileId:{originalFile.id}")
