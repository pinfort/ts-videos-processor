import sys
from logging import getLogger, Logger, config
import json
from os.path import join, dirname
from dotenv import load_dotenv
from main.component.database import Database
from main.dto.programWithExecuted import ProgramWithExecuted
from main.enum.programStatus import ProgramStatus

from main.repository.programWithExecutedRepository import ProgramWithExecutedRepository

import os

def main():
    """
    録画済み番組検索スクリプト
    """
    os.system("")
    COLOR = {
        "HEADER": "\033[95m",
        "RED": "\033[41m",
        "ENDC": "\033[0m",
    }
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    database = Database()
    programWithExecutedRepository = ProgramWithExecutedRepository(database)

    keyword = sys.argv[1]

    programs: list[ProgramWithExecuted] = programWithExecutedRepository.selectByNameAndStatus(keyword, ProgramStatus.COMPLETED)
    print("id\trecorded_at\tchannelName\tdrops\tname")
    for program in programs:
        lineColor = "RED" if program.drops > 0 else "ENDC"
        print(COLOR[lineColor], f"{program.id}\t{program.recorded_at}\t{program.channelName}\t{program.drops}\t{program.name}", COLOR["ENDC"])


if __name__ == "__main__":
    main()
