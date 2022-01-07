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
from main.repository.createdFileRepository import CreatedFileRepository

class CompressAndSave:
    logger: Logger
    nas: Nas
    compress: Compress
    database: Database
    createdFileRepository: CreatedFileRepository

    def __init__(self) -> None:
        self.compress = Compress()
        self.nas = Nas()
        self.database = Database()
        self.createdFileRepository = CreatedFileRepository(self.database)
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
            )
        )
        self.logger.info(f"file compressed and saved. target:{target_directory.joinpath(compressed_path.name)}")
        compressed_path.unlink()
