import sys
import json
from os.path import join, dirname
from dotenv import load_dotenv

from logging import Logger, config, getLogger
from pathlib import Path
from main.command.removeProgram import RemoveProgram

from main.repository.executedFileRepository import ExecutedFileRepository
from main.repository.programRepository import ProgramRepository

def main():
    """
    処理をリセットする。生成されたファイルは軒並み削除される。一部削除されないことがある。
    """
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    with open("log_config.json", 'r') as f:
        config.dictConfig(json.load(f))
    logger = getLogger(__name__)

    file: Path = Path(sys.argv[1])
    logger.info(f"removing file:{file}")
    programRepository = ProgramRepository()
    executedFileRepository = ExecutedFileRepository()
    executedFile = executedFileRepository.findByFile(file)
    if executedFile is None:
        logger.error("executed file not found. aborting.")
        return
    program = programRepository.findByExecutedFileId(executedFile.id)
    if program is None:
        logger.error("program not found. aborting.")
        return
    removeProgram = RemoveProgram()
    removeProgram.remove(program.id)

if __name__ == "__main__":
    main()
