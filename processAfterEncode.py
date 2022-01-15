import os
import json
import mimetypes

from pathlib import Path
from datetime import datetime
from os.path import join, dirname
from typing import Union
from dotenv import load_dotenv
from logging import Logger, config, getLogger
from main.component.database import Database

from main.component.nas import Nas
from main.enum.createdFileStatus import CreatedFileStatus
from main.enum.programStatus import ProgramStatus
from main.repository.createdFileRepository import CreatedFileRepository
from main.repository.programRepository import ProgramRepository
from main.repository.splittedFileRepository import SplittedFileRepository
from main.dto.createdFileDto import CreatedFileDto
from main.config.nas import NAS_ROOT_DIR
from main.command.validateCompleted import ValidateCompleted

class ProcessAfterEncode:
    """
    Amatsukazeの実行後バッチで呼び出すスクリプト
    bat/実行後_NAS移動.batで呼び出される
    """
    logger: Logger

    item_id: int
    """
    アイテムに一意に振られるID。
    追加時、実行前、実行後で同じアイテムを追跡できる。
    Amatsukazeを再起動するとIDが変わるので注意。
    """
    in_path: Path
    """
    入力ファイルパス
    """
    out_path: Path
    """
    出力ファイルパス（拡張子を含まない）
    """
    service_id: int
    """
    サービスID（チャンネルID）
    """
    service_name: str
    """
    サービス名（チャンネル名）
    """
    ts_time: datetime
    """
    TSファイルの時刻
    """
    item_mode: str
    """
    モード
    """
    item_priority: int
    """
    アイテム優先度(1-5)
    """
    event_genre: str
    """
    番組ジャンル
    """
    image_width: int
    """
    映像幅
    """
    image_height: int
    """
    映像高さ
    """
    event_name: str
    """
    番組名
    """
    tag: list[str]
    """
    タグ（セミコロン区切り）
    """

    profile_name: str

    success: bool
    error_message: str
    in_duration: float
    out_duration: float
    in_size: int
    out_size: int
    logo_file: str
    num_incident: int
    json_path: Path
    log_path: Path

    files: list[Path]

    nas: Nas
    createdFileRepository: CreatedFileRepository
    splittedFileRepository: SplittedFileRepository
    programRepository: ProgramRepository
    database: Database
    validateCompleted: ValidateCompleted

    def __init__(self) -> None:
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        with open("log_config.json", 'r') as f:
            config.dictConfig(json.load(f))
        self.logger = getLogger(__name__)
        self.__loadEnvs()
        self.logger.info(self.files)
        self.database = Database()
        self.nas = Nas()
        self.createdFileRepository = CreatedFileRepository(self.database)
        self.splittedFileRepository = SplittedFileRepository(self.database)
        self.programRepository = ProgramRepository(self.database)
        self.validateCompleted = ValidateCompleted()

    def __loadEnvs(self) -> None:
        self.item_id = int(os.getenv("ITEM_ID"))
        self.in_path = Path(os.getenv("IN_PATH"))
        self.out_path = Path(os.getenv("OUT_PATH"))
        self.service_id = int(os.getenv("SERVICE_ID"))
        self.service_name = os.getenv("SERVICE_NAME")
        self.ts_time = datetime.strptime(os.getenv("TS_TIME"), "%Y/%m/%d %H:%M:%S")
        self.item_mode = os.getenv("ITEM_MODE")
        self.item_priority = int(os.getenv("ITEM_PRIORITY"))
        self.event_genre = os.getenv("EVENT_GENRE")
        self.image_width = int(os.getenv("IMAGE_WIDTH"))
        self.image_height = int(os.getenv("IMAGE_HEIGHT"))
        self.event_name = os.getenv("EVENT_NAME")
        self.tag = os.getenv("TAG").split(";")

        self.profile_name = os.getenv("PROFILE_NAME")

        self.success = True if os.getenv("SUCCESS") == "1" else False
        self.error_message = os.getenv("ERROR_MESSAGE")
        self.in_duration = float(os.getenv("IN_DURATION"))
        self.out_duration = float(os.getenv("OUT_DURATION"))
        self.in_size = int(os.getenv("IN_SIZE"))
        self.out_size = int(os.getenv("OUT_SIZE"))
        self.logo_file = os.getenv("LOGO_FILE")
        self.num_incident = int(os.getenv("NUM_INCIDENT"))
        self.json_path = Path(os.getenv("JSON_PATH"))
        self.log_path = Path(os.getenv("LOG_PATH"))

        self.files = [Path(file) for file in os.getenv("FILES", "").split(";")]

    def registerFiles(self) -> int:
        """
        @return executedFileId
        """
        splittedFileId: int = 0
        # ファイルはsuccessedフォルダに移動されているのでそれを加味して検索
        original_file_path: Path = self.in_path.parent.parent.joinpath(self.in_path.name)
        original_file = self.splittedFileRepository.findByFile(original_file_path)
        if original_file is None:
            self.logger.warn(f"original_file not found. in_path:{self.in_path}")
        else:
            splittedFileId = original_file.id

        for file in self.files:
            mime: tuple[Union[str, None] , Union[str, None]] = mimetypes.guess_type(file)
            target_directory: Path = NAS_ROOT_DIR.joinpath(file.parent.parent.parent.name[0:1]).joinpath(file.parent.parent.parent.name)
            self.createdFileRepository.insert(
                CreatedFileDto(
                    id=0,
                    splittedFileId=splittedFileId,
                    file=target_directory.joinpath(file.name),
                    size=file.stat().st_size,
                    mime=mime[0],
                    encoding=mime[1],
                    status=CreatedFileStatus.ENCODE_SUCCESS,
                )
            )
            self.logger.info(f"created file registered. file:{file}, splittedFileId:{splittedFileId}")
        return original_file.executedFileId

    def moveFiles(self):
        for file in self.files:
            target_directory: Path = NAS_ROOT_DIR.joinpath(file.parent.parent.parent.name[0:1]).joinpath(file.parent.parent.parent.name)
            createdFile: CreatedFileDto = self.createdFileRepository.findByFile(target_directory.joinpath(file.name))
            self.nas.save(file, target_directory)
            self.createdFileRepository.updateStatus(createdFile.id, CreatedFileStatus.FILE_MOVED)
            self.logger.info(f"file uploaded. file:{file.name}, target:{target_directory}")
            file.unlink()

    def finishProcess(self, executedFileId: int):
        program = self.programRepository.findByExecutedFileId(executedFileId)
        if program is None:
            self.logger.error(f"program not found. executedFileId:{executedFileId}")
            return
        if self.validateCompleted.validate(program.id):
            self.logger.info(f"program valid. status will be completed. programId:{program.id}")
            self.programRepository.updateStatusByexecutedFileId(executedFileId, ProgramStatus.COMPLETED)
        else:
            self.logger.error(f"program invalid. programId:{program.id}")
            self.programRepository.updateStatusByexecutedFileId(executedFileId, ProgramStatus.ERROR)

    def notifyError(self):
        self.logger.error(f"encode failed. amatsukaze_id:{self.item_id}, in_path:{self.in_path}")

    def execute(self):
        if not self.success:
            # エンコード失敗の場合通知して終了
            self.notifyError()
            return

        # ファイル群をDBに登録
        executedFileId: int = self.registerFiles()
        # エンコード済みファイルをNASに移動
        self.moveFiles()
        self.finishProcess(executedFileId)
        self.logger.info(f"uploading file completed. targets:{self.files}")

def main():
    task = ProcessAfterEncode()
    task.execute()

if __name__ == "__main__":
    main()
