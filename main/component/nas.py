from logging import Logger, getLogger
from pathlib import Path
from typing import Iterable, Iterator
from pymysql.connections import Connection
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure
import platform

from smb.base import SharedFile

from main.config import nas

class Nas:
    logger: Logger
    connection: SMBConnection

    def __init__(self) -> None:
        self.logger = getLogger(__name__)
        self.connect()

    def connect(self) -> None:
        self.connection = SMBConnection(
            nas.NAS_USER,
            nas.NAS_PASSWORD,
            platform.uname().node,
            nas.NAS_NAME,
        )
        self.connection.connect(nas.NAS_HOST, nas.NAS_PORT)

    def disConnect(self) -> None:
        self.connection.close()
    
    def reconnect(self) -> None:
        self.disConnect()
        self.connect()

    def save(self, file_path: Path, target_directory: Path) -> None:
        self.reconnect()
        target_path: Path = target_directory.joinpath(file_path.name)
        if not file_path.exists():
            self.logger.info(f"file not found. aborting. file:{file_path}")
            return
        if self.fileOrDirectoryExists(target_path):
            self.logger.info(f"file already exists. aborting. target:{target_path}")
            return
        self.logger.info(f"starting copy... target:{target_path}")

        self.createDirectory(target_directory)
        with open(str(file_path), "rb") as f:
            self.connection.storeFile(nas.NAS_SERVICE_NAME, str(target_path), f)
        self.logger.info(f"file copied. target:{target_path}")

    def createDirectory(self, target_directory: Path) -> None:
        if self.fileOrDirectoryExists(target_directory):
            return
        pathList: list[str] = []
        while (not self.fileOrDirectoryExists(target_directory)) and (not str(target_directory) == "."):
            self.logger.debug(f"directory not found :{target_directory}")
            pathList.append(target_directory.name)
            target_directory = target_directory.parent

        pathList.reverse()

        for p in pathList:
            target_directory = target_directory.joinpath(Path(p))
            self.logger.debug(f"directory to be created:{target_directory}")
            self.connection.createDirectory(nas.NAS_SERVICE_NAME, str(target_directory))

    def fileOrDirectoryExists(self, target: Path) -> bool:
        try:
            self.connection.getAttributes(nas.NAS_SERVICE_NAME, str(target))
            return True
        except OperationFailure as e:
            return False

    def rename(self, old: Path, new: Path) -> bool:
        if self.fileOrDirectoryExists(new):
            self.logger.info(f"file or directory already exists. aborting. target:{new}")
            return False
        self.connection.rename(nas.NAS_SERVICE_NAME, str(old), str(new))
        return True

    def filterExistPath(self, pathList: Iterable[Path]) -> Iterator[Path]:
        for path in pathList:
            if self.fileOrDirectoryExists(path):
                yield path
