from typing import Union
import json
import sys
import traceback
import mimetypes

from logging import Logger, config, getLogger
from pathlib import Path
from os.path import join, dirname
from typing import Iterable
from dotenv import load_dotenv
from smb.base import SharedFile
from main.component.dependencyInjector import getInstance

from main.component.nas import Nas
from main.component.database import Database
from main.dto.createdFileDto import CreatedFileDto
from main.dto.executedFileDto import ExecutedFileDto
from main.dto.splittedFileDto import SplittedFileDto
from main.dto.programDto import ProgramDto
from main.enum.createdFileStatus import CreatedFileStatus
from main.enum.executedFileStatus import ExecutedFileStatus
from main.enum.programStatus import ProgramStatus
from main.enum.splittedFileStatus import SplittedFileStatus
from main.repository.createdFileRepository import CreatedFileRepository
from main.repository.splittedFileRepository import SplittedFileRepository
from main.repository.executedFileRepository import ExecutedFileRepository
from main.repository.programRepository import ProgramRepository
from main.component.normalize import Normalize
from main.component.fileName import FileName
from main.config.nas import NAS_ROOT_DIR

class MoveOldFiles():
    """
    旧仕様(V1, V2)のファイルを新仕様(V3)に合わせてDB登録、ファイル移動を行います。
    V1: DB登録なし、ファイルは一番組につき動画ファイルひとつのみ。
    V2: DB登録あるが、executedfileとsplittedFileのみ。ファイルは動画ファイルのほかログファイルもあり。
    V3: 新仕様。executedFile, splittedFile, createdFile, program登録あり。ファイルは動画ファイルのほかログファイルもあり。
    """
    logger: Logger
    createdFileRepository: CreatedFileRepository = CreatedFileRepository()
    splittedFileRespository: SplittedFileRepository = SplittedFileRepository()
    executedFileRepository: ExecutedFileRepository = ExecutedFileRepository()
    programRepository: ProgramRepository = ProgramRepository()
    nas: Nas = getInstance(Nas)
    normalize: Normalize = Normalize()

    def __init__(self) -> None:
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        with open("log_config.json", 'r') as f:
            config.dictConfig(json.load(f))
        self.logger = getLogger(__name__)

    def processPath(self, path: Path) -> None:
        self.logger.info(f"processing path started. path:{path}")

        if(not self.nas.fileOrDirectoryExists(path)):
            self.logger.error(f"""path not exist path:{str(path)}""")
            return

        if not self.nas.getFile(path).isDirectory:
            self.logger.error("please give directory. file is not supported now.")
            return
        files: list[SharedFile] = self.nas.getList(path)

        for file in files:
            if file.isDirectory:
                continue
            if not self.nas.fileOrDirectoryExists(path.joinpath(file.filename)):
                self.logger.info(f"file already processed. skipping. file:{file.filename}")
                # ループ中に、同じファイル群のファイルが処理された場合、そのファイル群に含まれるファイルはすべて移動される。
                # そのため、ループが回ってきたときには既に存在しないファイルである場合があるので、その場合はスキップ
                continue
            self.logger.info(f"processing file. file:{file.filename}")
            try:
                self.processFile(path, file, files)
            except Exception as e:
                stackTrace: str = traceback.format_exc()
                self.logger.error(f"processing file failed. file:{file} reason:{e} stackTrace:{stackTrace}")
        self.logger.info("processing path finished.")

    def selectTargetFileFromFileList(self, pattern: str, files: list[SharedFile]) -> Iterable[SharedFile]:
        """
        そのディレクトリにあるファイル群から、今回処理するファイル群を選択する。
        メイン動画ファイル、ログファイルなど。
        """
        self.logger.info(f"selecting... pattern:{pattern}")
        for file in files:
            filename: str = file.filename
            if filename.startswith(pattern):
                yield file

    def processFile(self, directory: Path, file: SharedFile, files: list[SharedFile]) -> None:
        """
        DB導入後、executedFileとsplittedFileのみ存在する旧仕様ファイルを処理。
        DB導入前仕様ファイルが見つかれば、processNotRegisteredFileに流す。
        """
        self.logger.info(f"process file started. file:{file.filename}")
        if file.filename.endswith(".log"):
            self.logger.info("it is log. skipping.")
            return
        executedFile: Union[ExecutedFileDto, None] = self.getExecutedFile(file)
        if executedFile is None:
            """
            DB導入前の旧仕様ファイル。処理を流す。
            """
            self.logger.info(f"executed file not registered. going to V1 function. file:{file.filename}")
            return self.processNotRegisteredFile(directory, file, files)
        self.logger.info(f"executed file found. dto:{executedFile}")
        splittedFiles: list[SplittedFileDto] = self.splittedFileRespository.selectByExecutedFileId(executedFile.id)
        if len(splittedFiles) == 0:
            self.logger.info(f"splitted file not found. skipping. file:{file.filename}")
            return

        mainSplittedFile: Union[SplittedFileDto, None] = self.getMailSplittedFile(splittedFiles)

        targetFiles: list[SharedFile] = list(self.selectTargetFileFromFileList(executedFile.file.stem, files))
        targetDirectory = self.moveFiles(directory, targetFiles)
        self.createCreatedFileRecords(targetDirectory, targetFiles, mainSplittedFile)
        self.createProgramRecord(targetFiles, executedFile)
        self.executedFileRepository.updateStatus(executedFile.id, ExecutedFileStatus.SPLITTED)
        for splittedFile in splittedFiles:
            self.splittedFileRespository.updateStatus(splittedFile.id, SplittedFileStatus.COMPRESS_SAVED)
        self.logger.info(f"process file finished. file:{file.filename}")

    def getMailSplittedFile(self, splittedFiles: list[SplittedFileDto]) -> Union[SplittedFileDto, None]:
        # 最も大きいファイルをメインとする
        mainSplittedFile: Union[SplittedFileDto, None] = None
        for splittedFile in splittedFiles:
            if mainSplittedFile is None or mainSplittedFile.size < splittedFile.size:
                mainSplittedFile = splittedFile
        self.logger.info(f"splitted file found. dto:{mainSplittedFile}")
        return mainSplittedFile

    def processNotRegisteredFile(self, directory: Path, file: SharedFile, files: list[SharedFile]) -> None:
        """
        DB導入前の旧仕様ファイルを処理。
        """
        self.logger.info(f"processing V1 file. file:{file.filename}, directory:{directory}")
        targetFiles = list(self.selectTargetFileFromFileList(Path(file.filename).stem, files))
        executedFile = self.createExecutedFileRecord(directory, file)
        splittedFile = self.createSplittedFileRecord(executedFile)
        targetDirectory = self.moveFiles(directory, targetFiles)
        self.createCreatedFileRecords(targetDirectory, targetFiles, splittedFile)
        self.createProgramRecord(targetFiles, executedFile)
        self.logger.info(f"process file finished. file:{file.filename}")

    def createExecutedFileRecord(self, directory: Path, file: SharedFile) -> ExecutedFileDto:
        filename = FileName(file.filename)
        executedFile = ExecutedFileDto(
            id=0,
            file=directory.joinpath(file.filename),
            drops=0,
            size=file.file_size,
            recorded_at=filename.recorded_at,
            channel=filename.channel,
            channelName=filename.channelName,
            title=filename.title,
            duration=0,
            status=ExecutedFileStatus.SPLITTED,
        )
        self.logger.info(f"creating executedFile. dto:{executedFile}")
        self.executedFileRepository.insert(executedFile)
        return self.executedFileRepository.findByBroadCastInfo(filename.recorded_at, filename.channel, filename.channelName)

    def createSplittedFileRecord(self, executedFile: ExecutedFileDto) -> SplittedFileDto:
        splittedFile = SplittedFileDto(
            id=0,
            executedFileId=executedFile.id,
            file=executedFile.file,
            size=executedFile.size,
            duration=executedFile.duration,
            status=SplittedFileStatus.COMPRESS_SAVED,
        )
        self.logger.info(f"creating splittedFile. dto:{splittedFile}")
        self.splittedFileRespository.insert(splittedFile)
        return self.splittedFileRespository.selectByExecutedFileId(executedFile.id)[0]

    def getExecutedFile(self, file: SharedFile) -> Union[ExecutedFileDto, None]:
        """
        ファイル名についている放送情報からexecutedFileを特定する。ある時間にある放送局(チャンネル)で放送している番組は一つしかないはず。
        物理チャンネルと放送局名を両方検証することで、他地域で録画されたファイルも考慮する。
        """
        filename = FileName(file.filename)
        return self.executedFileRepository.findByBroadCastInfo(filename.recorded_at, filename.channel, filename.channelName)

    def moveFiles(self, oldDirectory: Path, files: Iterable[SharedFile]) -> str:
        """
        ファイルを実際に移動する。もし存在しない場合、移動先ディレクトリの作成も同時に行う。
        移動元ディレクトリには何も行わないので、空になった場合でもそのまま存在する（削除しない）。
        """
        newDirectoryName = self.normalize.normalize(oldDirectory.name)
        targetDirectory: Path = NAS_ROOT_DIR.joinpath(newDirectoryName[0:1]).joinpath(newDirectoryName)
        self.logger.info(f"create directory! directory:{targetDirectory}")
        self.nas.createDirectory(targetDirectory)
        for file in files:
            self.logger.info(f"move file! original:{oldDirectory.joinpath(file.filename)}, target:{targetDirectory.joinpath(file.filename)}")
            if not self.nas.rename(oldDirectory.joinpath(file.filename), targetDirectory.joinpath(file.filename)):
                self.logger.error(f"move file failed. target already exist. file:{file.filename}")
                raise Exception(f"move file failed. target already exist. file:{file.filename}")
        return targetDirectory

    def createProgramRecord(self, files: Iterable[SharedFile], executedFile: ExecutedFileDto) -> None:
        """
        programテーブルの行を作成する。
        """
        tsFileName = executedFile.file.name

        self.logger.info(f"insert program record. fileName:{tsFileName}, executedFileId:{executedFile.id}")
        self.programRepository.insert(
            ProgramDto(
                id=0,
                name=tsFileName,
                executedFileId=executedFile.id,
                status=ProgramStatus.COMPLETED
            )
        )

    def createCreatedFileRecords(self, targetDirectory: Path, files: Iterable[SharedFile], splittedFile: SplittedFileDto) -> None:
        for file in files:
            mime: tuple[Union[str, None] , Union[str, None]] = mimetypes.guess_type(file.filename)
            dto = CreatedFileDto(
                    id=0,
                    splittedFileId=splittedFile.id,
                    file=targetDirectory.joinpath(file.filename),
                    size=file.file_size,
                    mime=mime[0],
                    encoding=mime[1],
                    status=CreatedFileStatus.FILE_MOVED,
                )
            self.logger.info(f"insert createdFile record. dto:{dto}")
            self.createdFileRepository.insert(dto)

def main():
    """
    対象動画ファイルの入っているディレクトリを引数へ与えて起動する場合。
    """
    moveOldFiles = MoveOldFiles()
    for input in sys.argv[1:]:
        moveOldFiles.processPath(Path(input))

def mainWithDirectory():
    """
    対象動画ファイルの入っているディレクトリの親ディレクトリを引数に与えて起動する場合。
    """
    moveOldFiles = MoveOldFiles()
    dir = sys.argv[1]
    files = moveOldFiles.nas.getList(dir)
    for file in files:
        if file.isDirectory and file.filename not in [".", ".."]:
            # print(Path(dir).joinpath(file.filename))
            moveOldFiles.processPath(Path(dir).joinpath(file.filename))

if __name__ == "__main__":
    main()
