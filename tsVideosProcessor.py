import sys
import json
from pathlib import Path
from typing import Iterable
from logging import config, getLogger

from main.command.dropChk import DropChk
from main.command.tsSplitter import TsSplitter
from main.command.amatsukazeAddTask import AmatsukazeAddTask

class TsVideosProcessor:
    def processPath(self, path: Path):
        with open("log_config.json", 'r') as f:
            config.dictConfig(json.load(f))
        logger = getLogger(__name__)
        logger.info("processing path started.")
        dropCheck = DropChk()
        tsSplitter = TsSplitter()
        amatsukazeAddTask = AmatsukazeAddTask()
        logger.info(path)
        files: Iterable[Path]

        if(not path.exists):
            logger.error(f"""path not exist path:{str(path)}""")
            sys.exit(1)

        if(path.is_dir()):
            logger.info("given path is directory")
            files = path.glob("*.m2ts")
        else:
            logger.info("given path is file")
            files = list()
            files.append(path)

        for file in files:
            logger.info(f"processing file:{file}")
            dropCheck.dropChk(file)
            tsSplitter.tsSplitter(file)
            amatsukazeAddTask.amatsukaze(file)
        logger.info("processing path finished.")
