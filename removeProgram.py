import sys
import json
from os.path import join, dirname
from dotenv import load_dotenv

from logging import Logger, config, getLogger
from pathlib import Path
from main.command.removeProgram import RemoveProgram

def main():
    """
    処理をリセットする。生成されたファイルは軒並み削除される。一部削除されないことがある。
    """
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    with open("log_config.json", 'r') as f:
        config.dictConfig(json.load(f))
    logger = getLogger(__name__)

    programId: int = Path(sys.argv[1])
    logger.info(f"removing program:{programId}")
    removeProgram = RemoveProgram()
    removeProgram.remove(programId)

if __name__ == "__main__":
    main()
