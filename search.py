import sys
from logging import getLogger, Logger, config
import json
from os.path import join, dirname
from dotenv import load_dotenv
from main.dto.programWithExecuted import ProgramWithExecuted
from main.enum.programStatus import ProgramStatus

from main.repository.programWithExecutedRepository import ProgramWithExecutedRepository
from main.repository.createdFileRepository import CreatedFileRepository
from main.repository.splittedFileRepository import SplittedFileRepository

import os

def main():
    """
    録画済み番組検索スクリプト
    """
    os.system("")
    COLOR = {
        "HEADER": "\033[95m",
        "RED": "\033[41m",
        "GREEN": "\033[42m",
        "ENDC": "\033[0m",
    }
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    programWithExecutedRepository = ProgramWithExecutedRepository()
    splittedFileRepository = SplittedFileRepository()
    createdFileRepository = CreatedFileRepository()

    keyword = sys.argv[1]

    programs: list[ProgramWithExecuted] = programWithExecutedRepository.selectByNameAndStatus(keyword, ProgramStatus.COMPLETED)
    print("凡例:", COLOR["RED"], "DROPあり", COLOR["ENDC"], " ", COLOR["GREEN"], "DROP数不明", COLOR["ENDC"], " ")
    print("id\trecorded_at\t\tchannelName\t\tdrops\ttsExists\ttitle")
    for program in programs:
        splittedFiles = splittedFileRepository.selectByExecutedFileId(program.executedFileId)
        createdFiles = sum([createdFileRepository.selectBySplittedFileId(splittedFile.id) for splittedFile in splittedFiles], [])
        createdFileMimes = [createdFile.mime for createdFile in createdFiles]
        tsExists: bool = "video/vnd.dlna.mpeg-tts" in createdFileMimes
        if program.drops == 0:
            lineColor = "ENDC"
        elif program.drops > 0:
            lineColor = "RED"
        else:
            lineColor = "GREEN"
        print(COLOR[lineColor], f"{program.id}\t{program.recorded_at}\t{program.channelName}\t{program.drops}\t{tsExists}\t{program.title}", COLOR["ENDC"])
    print(f"{len(programs)} programs found.")

if __name__ == "__main__":
    main()
