import sys
from typing import Union
from os.path import join, dirname
from dotenv import load_dotenv
from main.dto.programDto import ProgramDto

from main.repository.createdFileRepository import CreatedFileRepository
from main.repository.splittedFileRepository import SplittedFileRepository
from main.repository.programRepository import ProgramRepository

import os

def main():
    """
    録画済み番組検索スクリプト
    """
    os.system("")
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    splittedFileRepository = SplittedFileRepository()
    createdFileRepository = CreatedFileRepository()
    programRepository = ProgramRepository()

    programId = sys.argv[1]

    program: Union[ProgramDto, None] = programRepository.find(programId)
    if program is None:
        print("not found")
        return

    splittedFiles = splittedFileRepository.selectByExecutedFileId(program.executedFileId)
    createdFiles = sum([createdFileRepository.selectBySplittedFileId(splittedFile.id) for splittedFile in splittedFiles], [])
    print("created Files")
    print("id\tsize\tpath\t\tmime\tencoding")
    for createdFile in createdFiles:
        print(f"{createdFile.id}\t{createdFile.size}\t{createdFile.file}\t{createdFile.mime}\t{createdFile.encoding}")

if __name__ == "__main__":
    main()
