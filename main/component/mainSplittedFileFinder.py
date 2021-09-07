from main.component.database import Database
from main.dto.executedFileDto import ExecutedFileDto
from main.dto.splittedFileDto import SplittedFileDto
from main.repository.splittedFileRepository import SplittedFileRepository

class MainSplittedFileFinder:
    splittedFileRepository: SplittedFileRepository

    def __init__(self, database: Database) -> None:
        self.splittedFileRepository = SplittedFileRepository(database)

    def splittedFileFromExecutedFile(self, executedFile: ExecutedFileDto) -> SplittedFileDto:
        """
            処理ファイルデータから分割済みファイルを取得

            分割された複数のファイルから、メインとなるファイルを取得する
        """
        splittedFiles: list[SplittedFileDto] = self.splittedFileRepository.selectByExecutedFileId(executedFile.id)
        # TSSplitterの結果は２ファイルを期待
        if(len(splittedFiles) != 2):
            raise Exception(f"splitted file counts not 2! id:{executedFile.id}")
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
        if(gabageFile.duration > 5.0):
            raise Exception("gabage file duration id grater than 5.0!")

        print(f"""
        main file found.
        id={mainFile.id},
        executeFileId={mainFile.executedFileId},
        file={mainFile.file},
        size={mainFile.size},
        duration={mainFile.duration}
        """)
        return mainFile
