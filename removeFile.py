import sys
import json
from ctypes import Union
from os.path import join, dirname
from dotenv import load_dotenv
from logging import Logger, config, getLogger

from main.component.dependencyInjector import getInstance
from main.component.subNas import SubNas
from main.dto.createdFileDto import CreatedFileDto
from main.repository.createdFileRepository import CreatedFileRepository
from main.component.nas import Nas

def man() -> str:
    return """
    This is script for remove specified createdFile.

    How to use
    python removeFile.py {createdFileId}
    """

def main():
    """
    createdFile削除
    """
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    with open("log_config.json", 'r') as f:
        config.dictConfig(json.load(f))
    logger = getLogger(__name__)

    createdFileRepository: CreatedFileRepository = CreatedFileRepository()
    logger: Logger = getLogger(__name__)
    nas: Nas = getInstance(Nas)
    subNas: SubNas = getInstance(SubNas)

    if len(sys.argv) <= 1:
        print(man())
        return
    createdFileId = sys.argv[1]

    createdFile: Union[CreatedFileDto, None] = createdFileRepository.find(createdFileId)
    logger.info(f"created file found. removing. path:{createdFile.file}")
    response = input("is it OK? [y/N]>")
    if response.lower() != "y":
        logger.error(f"cancelled. aborting. id:{createdFileId}")
        return
    if nas.fileOrDirectoryExists(createdFile.file):
        logger.info(f"file deleted from firstNas. file:{createdFile.file}")
        nas.removeFile(createdFile.file)
    elif subNas.fileOrDirectoryExists(createdFile.file):
        logger.info(f"file deleted from subNas. file:{createdFile.file}")
        subNas.removeFile(createdFile.file)
    else:
        logger.warn("target file not found.")
    createdFileRepository.delete(createdFileId)
    logger.info(f"createdFile deleted. createdFileId:{createdFileId}")

if __name__ == "__main__":
    main()
