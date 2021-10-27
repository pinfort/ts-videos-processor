import sys
import json
from pathlib import Path
from typing import Iterable
from logging import config, getLogger

from main.command.dropChk import DropChk
from main.command.tsSplitter import TsSplitter
from main.command.amatsukazeAddTask import AmatsukazeAddTask

def processPath(path: Path):
    with open("log_config.json", 'r') as f:
        config.dictConfig(json.load(f))
    logger = getLogger(__name__)
    dropCheck = DropChk()
    tsSplitter = TsSplitter()
    amatsukazeAddTask = AmatsukazeAddTask()
    logger.info(path)
    files: Iterable[Path]

    if(not path.exists):
        logger.error("path not exist")
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

def main():
    for input in sys.argv[1:]:
        processPath(Path(input))

if __name__ == "__main__":
    main()
