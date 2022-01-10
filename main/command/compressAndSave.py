from logging import Logger, getLogger
from pathlib import Path
import mimetypes
from typing import Union

from main.component.nas import Nas
from main.component.compress import Compress
from main.config.nas import NAS_ROOT_DIR_ZIPED
from main.component.database import Database
from main.dto.createdFileDto import CreatedFileDto
from main.dto.splittedFileDto import SplittedFileDto
from main.enum.createdFileStatus import CreatedFileStatus
from main.enum.splittedFileStatus import SplittedFileStatus
from main.repository.createdFileRepository import CreatedFileRepository
from main.repository.splittedFileRepository import SplittedFileRepository

class CompressAndSave:
    logger: Logger
    nas: Nas
    compress: Compress
    database: Database
    createdFileRepository: CreatedFileRepository
    splittedFileRespository: SplittedFileRepository

    def __init__(self) -> None:
        self.compress = Compress()
        self.nas = Nas()
        self.database = Database()
        self.createdFileRepository = CreatedFileRepository(self.database)
        self.splittedFileRespository = SplittedFileRepository(self.database)
        self.logger = getLogger(__name__)
    
    def execute(self, splittedFile: SplittedFileDto) -> None:
        self.logger.info(f"compressing file started. target:{splittedFile.file}")
        # そのファイルのディレクトリ名を引き継ぐ
        # parentが一つだとtssplitterディレクトリになる
        target_directory: Path = NAS_ROOT_DIR_ZIPED.joinpath(splittedFile.file.parent.parent.name[0:1]).joinpath(splittedFile.file.parent.parent.name)
        self.logger.info(f"target path caliculated. path:{target_directory}")
        compressed_file_name: str = splittedFile.file.name + ".gz"
        compressed_path: Path = splittedFile.file.parent.joinpath(Path(compressed_file_name))
        if not self.compress.compress(splittedFile.file, compressed_path):
            self.logger.error(f"compress failed. target:{splittedFile.file}")
            return
        self.nas.save(compressed_path, target_directory)
        mime: tuple[Union[str, None] , Union[str, None]] = mimetypes.guess_type(compressed_path)
        self.createdFileRepository.insert(
            CreatedFileDto(
                id=0,
                splittedFileId=splittedFile.id,
                file=target_directory.joinpath(compressed_path.name),
                size=compressed_path.stat().st_size,
                mime=mime[0],
                encoding=mime[1],
                status=CreatedFileStatus.FILE_MOVED,
            )
        )
        self.splittedFileRespository.updateStatus(splittedFile.id, SplittedFileStatus.COMPRESS_SAVED)
        self.logger.info(f"file compressed and saved. target:{target_directory.joinpath(compressed_path.name)}")
        compressed_path.unlink()

    def rollback(self, splittedFile: SplittedFileDto) -> None:
        self.logger.warn(f"compressAndSaveTask. rollbacking and deleting files. splittedFile:{splittedFile.file}, splittedFileId:{splittedFile.id}")
        # createdFileのうちgzipファイルだけ実ファイルを削除
        createdFiles: list[CreatedFileDto] = self.createdFileRepository.selectBySplittedFileId(splittedFile.id)
        for file in createdFiles:
            if(file.encoding == "gzip" and file.file.exists()):
                self.logger.warn(f"file deleted. file:{file.file}")
                file.file.unlink()

        # gzipなファイルだけDBから削除
        self.createdFileRepository.deleteBySplittedFileIdAndEncoding(splittedFile.id, "gzip")

        self.logger.warn(f"compress and save rollback task completed. splittedFile:{splittedFile.file}, splittedFileId:{splittedFile.id}")
