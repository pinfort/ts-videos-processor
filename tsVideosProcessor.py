import traceback
import json
import requests
from pathlib import Path
from typing import Iterable
from logging import Logger, config, getLogger
from os.path import join, dirname
from dotenv import load_dotenv

from main.command.dropChk import DropChk
from main.command.tsSplitter import TsSplitter
from main.command.amatsukazeAddTask import AmatsukazeAddTask
from main.command.compressAndSave import CompressAndSave
from main.config.slack import SLACK_WEBHOOK_URL
from main.dto.splittedFileDto import SplittedFileDto

class TsVideosProcessor:
    """
    全処理をまとめるメインクラス
    """
    logger: Logger
    dropChk: DropChk
    tsSplitter: TsSplitter
    amatsukazeAddTask: AmatsukazeAddTask
    compressAndSave: CompressAndSave

    def __init__(self) -> None:
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        with open("log_config.json", 'r') as f:
            config.dictConfig(json.load(f))
        self.logger = getLogger(__name__)

        self.dropCheck = DropChk()
        self.tsSplitter = TsSplitter()
        self.amatsukazeAddTask = AmatsukazeAddTask()
        self.compressAndSave = CompressAndSave()

    def processPath(self, path: Path):
        self.logger.info("processing path started.")
        self.logger.info(path)
        files: Iterable[Path]

        if(not path.exists):
            self.logger.error(f"""path not exist path:{str(path)}""")
            requests.post(SLACK_WEBHOOK_URL, json.dumps({
                    "text" : f"""path not exist path:{str(path)}""",
                }))
            return

        if(path.is_dir()):
            self.logger.info("given path is directory")
            files = path.glob("*.m2ts")
        else:
            self.logger.info("given path is file")
            files = list()
            files.append(path)

        for file in files:
            try:
                self.processFile(file)
            except Exception as e:
                self.logger.error(f"processing file failed. file:{file} reason:{e} stackTrace:{traceback.format_exc()}")
                requests.post(SLACK_WEBHOOK_URL, json.dumps({
                    "text" : f"processing file failed. file:{file} reason:{e}",
                }))
        self.logger.info("processing path finished.")

    def processFile(self, file: Path):
        """
        一ファイルごとに処理を行います
        """
        self.logger.info(f"processing file:{file}")
        try:
            result: bool = self.dropCheck.dropChk(file)
            if not result:
                self.logger.info(f"the file already registered! file:{file}")
                return
        except Exception as e:
            self.dropCheck.rollback(file)
            raise e

        splittedFile: SplittedFileDto
        try:
            splittedFile = self.tsSplitter.tsSplitter(file)
        except Exception as e:
            self.tsSplitter.rollback(file)
            self.dropCheck.rollback(file)
            raise e

        try:
            self.compressAndSave.execute(splittedFile)
        except Exception as e:
            self.compressAndSave.rollback(splittedFile)
            self.tsSplitter.rollback(file)
            self.dropCheck.rollback(file)
            raise e

        try:
            self.amatsukazeAddTask.amatsukaze(splittedFile)
        except Exception as e:
            self.amatsukazeAddTask.rollback(splittedFile)
            self.compressAndSave.rollback(splittedFile)
            self.tsSplitter.rollback(file)
            self.dropCheck.rollback(file)
            raise e
