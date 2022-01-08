import sys
import json
from pathlib import Path
from typing import Iterable
from logging import Logger, config, getLogger
from os.path import join, dirname
from dotenv import load_dotenv

from main.command.dropChk import DropChk
from main.command.tsSplitter import TsSplitter
from main.command.amatsukazeAddTask import AmatsukazeAddTask
from main.command.compressAndSave import CompressAndSave

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
            sys.exit(1)

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
                self.logger.error("processing file failed. reason:" + str(e))
        self.logger.info("processing path finished.")

    def processFile(self, file: Path):
        """
        一ファイルごとに処理を行います
        """
        self.logger.info(f"processing file:{file}")
        self.dropCheck.dropChk(file)
        splittedFile = self.tsSplitter.tsSplitter(file)
        self.compressAndSave.execute(splittedFile)
        self.amatsukazeAddTask.amatsukaze(splittedFile)
