from logging import Logger, getLogger

from main.component.database import Database
from main.dto.executedFileDto import ExecutedFileDto
from main.dto.splittedFileDto import SplittedFileDto
from main.repository.splittedFileRepository import SplittedFileRepository

class MainSplittedFileFinder:
    splittedFileRepository: SplittedFileRepository = SplittedFileRepository()
    logger: Logger = getLogger(__name__)

    def splittedFileFromExecutedFile(self, executedFile: ExecutedFileDto) -> SplittedFileDto:
        """
            処理ファイルデータから分割済みファイルを取得

            分割された複数のファイルから、メインとなるファイルを取得する
        """
        splittedFiles: list[SplittedFileDto] = self.splittedFileRepository.selectByExecutedFileId(executedFile.id)
        splittedFileCount: int = len(splittedFiles)
        self.logger.info(f"{splittedFileCount} splitted files found. starting validation")
        mainFile: SplittedFileDto

        # TSSplitterの結果のファイル数に応じてファイルの確認処理を分岐
        if splittedFileCount == 1:
            mainFile = self.splittedFileCountIsOne(executedFile, splittedFiles)
        elif splittedFileCount == 2:
            mainFile = self.splittedFileCountIsTwo(executedFile, splittedFiles)
        else:
            raise Exception(f"unexpected splitted file count! file_count:{splittedFileCount} executed_file_id:{executedFile.id}")

        if not self.validateMainFile(mainFile, executedFile):
            raise Exception(f"main file not found. executedFile:{executedFile.file}, executedFileId:{executedFile.id}")

        self.logger.info(f"""
        main file found.
        id={mainFile.id},
        executeFileId={mainFile.executedFileId},
        file={mainFile.file},
        size={mainFile.size},
        duration={mainFile.duration}
        """)
        return mainFile

    def splittedFileCountIsTwo(self, executedFile: ExecutedFileDto, splittedFiles: list[SplittedFileDto]) -> SplittedFileDto:
        # TSSplitterの結果は２ファイルを期待
        if(len(splittedFiles) != 2):
            raise Exception(f"splitted file counts not 2! executedFile:{executedFile.file}, executedFileId:{executedFile.id}")
        mainFile: SplittedFileDto
        gabageFile: SplittedFileDto

        # ファイルサイズの大きいほうをメインファイルと推測
        if(splittedFiles[0].size >= splittedFiles[1].size):
            mainFile = splittedFiles[0]
            gabageFile = splittedFiles[1]
        else:
            mainFile = splittedFiles[1]
            gabageFile = splittedFiles[0]

        # ゴミファイルの長さが長いと、何らかの異常がある場合がある
        if(gabageFile.duration > 20.0):
            raise Exception(f"main file not found. gabage file duration is grater than 20.0! executedFile:{executedFile.file}, executedFileId:{executedFile.id}")

        # ゴミファイルのファイルサイズはメインファイルの10%以下
        if gabageFile.size > (mainFile.size * 0.1):
            raise Exception(f"main file not found. gabage file size is grater than 10%% of mainfile. executedFile:{executedFile.file}, executedFileId:{executedFile.id}")

        return mainFile

    def splittedFileCountIsOne(self, executedFile: ExecutedFileDto, splittedFiles: list[SplittedFileDto]) -> SplittedFileDto:
        if len(splittedFiles) != 1:
            raise Exception(f"splitted file counts not 1! executed_file_id:{executedFile.id}")
        splittedFile: SplittedFileDto = splittedFiles[0]

        return splittedFile

    def validateMainFile(self, splittedFile: SplittedFileDto, executedFile: ExecutedFileDto) -> bool:
        if splittedFile is None:
            self.logger.warn("splitted file is None")
            raise Exception(f"main file not found. splitted file is None executedFile:{executedFile.file}, executedFileId:{executedFile.id}")

        if splittedFile.duration < 1:
            self.logger.warn("length of file is too short")
            raise Exception(f"main file not found. length of file is too short executedFile:{executedFile.file}, executedFileId:{executedFile.id}")

        if executedFile.drops > 1000:
            self.logger.warn(f"too many drops in executedFile. id:{executedFile.id} drops:{executedFile.drops}")
            raise Exception(f"main file not found. too many drops in executedFile. id:{executedFile.id} drops:{executedFile.drops}, executedFile:{executedFile.file}")

        # 分割されたファイルの再生時間とオリジナルファイルの再生時間の差は20秒以下-5秒以上。
        # 分割ファイルの時間が元ファイルより伸びる事象があったため、5秒まで分割ファイルのほうが長いことを許可
        durationDifference: int = int(executedFile.duration) - int(splittedFile.duration)
        if durationDifference < -5 or durationDifference > 20:
            self.logger.warn(f"duration between original and splitted is too different! executed_file_id:{executedFile.id}, executedFileDuration:{executedFile.duration}, splittedFileDuration:{splittedFile.duration}")
            raise Exception(f"main file not found. duration between original and splitted is too different! executed_file_id:{executedFile.id}, executedFile:{executedFile.file}, executedFileDuration:{executedFile.duration}, splittedFileDuration:{splittedFile.duration}")
        return True
