from logging import Logger, getLogger

from main.component.database import Database
from main.dto.executedFileDto import ExecutedFileDto
from main.dto.splittedFileDto import SplittedFileDto
from main.repository.splittedFileRepository import SplittedFileRepository

class MainSplittedFileFinder:
    splittedFileRepository: SplittedFileRepository
    logger: Logger

    def __init__(self, database: Database) -> None:
        self.splittedFileRepository = SplittedFileRepository(database)
        self.logger = getLogger(__name__)

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

        self.validateMainFile(mainFile, executedFile)

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
            raise Exception(f"splitted file counts not 2! executed_file_id:{executedFile.id}")
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
            raise Exception("gabage file duration id grater than 20.0!")

        # ゴミファイルのファイルサイズはメインファイルの10%以下
        if gabageFile.size > (mainFile.size * 0.1):
            raise Exception("gabage file size is grater than 10%% of mainfile.")

        return mainFile

    def splittedFileCountIsOne(self, executedFile: ExecutedFileDto, splittedFiles: list[SplittedFileDto]) -> SplittedFileDto:
        if len(splittedFiles) != 1:
            raise Exception(f"splitted file counts not 1! executed_file_id:{executedFile.id}")
        splittedFile: SplittedFileDto = splittedFiles[0]

        return splittedFile

    def validateMainFile(self, splittedFile: SplittedFileDto, executedFile: ExecutedFileDto) -> None:
        if splittedFile is None:
            raise Exception("splitted file is None")

        if splittedFile.duration < 1:
            raise Exception("length of file is too short")

        if executedFile.drops > 1000:
            raise Exception(f"too many drops in executedFile. id:{executedFile.id} drops:{executedFile.drops}")

        # 分割されたファイルの再生時間とオリジナルファイルの再生時間の差は20秒以下0秒以上。
        durationDifference: int = int(executedFile.duration) - int(splittedFile.duration)
        if durationDifference < 0 or durationDifference > 20:
            raise Exception(f"duration between original and splitted is too different! executed_file_id:{executedFile.id}")
