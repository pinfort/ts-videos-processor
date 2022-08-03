from ctypes import Union
from operator import index
import sys
import json
from pathlib import Path
from main.component.dependencyInjector import getInstance
from main.component.nas import Nas
from main.dto.createdFileDto import CreatedFileDto
from main.dto.programDto import ProgramDto
from os.path import join, dirname
from typing import Union
from dotenv import load_dotenv
from logging import Logger, config, getLogger
from main.component.database import Database
from main.repository.programRepository import ProgramRepository
from main.repository.createdFileRepository import CreatedFileRepository
from main.repository.splittedFileRepository import SplittedFileRepository

def main():
    """
    処理済みの番組を移動させるときにつかう。
    """
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    with open("log_config.json", 'r') as f:
        config.dictConfig(json.load(f))
    logger: Logger = getLogger(__name__)

    programRepository = ProgramRepository()
    createdFileRepository = CreatedFileRepository()
    splittedFileRepository = SplittedFileRepository()
    nas: Nas = getInstance(Nas, None)

    programId = int(sys.argv[1])
    targetName = sys.argv[2]

    program: Union[ProgramDto, None] = programRepository.find(programId)
    if program is None:
        logger.error("target program not found.")

    answer: str = input(f"you are moving programId:{program.id}, name:{program.name} to targetDirectory:{targetName}. Are you OK? [N/y] >>>")
    if answer != "y" and answer != "Y":
        logger.info("work cancelled.")

    logger.debug(f"processing executedFileId:{program.executedFileId}")
    splittedFiles = splittedFileRepository.selectByExecutedFileId(program.executedFileId)
    logger.debug(f"found {len(splittedFiles)} splitted files.")
    zippedFiles: list[CreatedFileDto] = []
    movieOrOtherFiles: list[CreatedFileDto] = []
    for splittedFile in splittedFiles:
        logger.debug(f"processing splittedFileId:{splittedFile.id}")
        createdFiles = createdFileRepository.selectBySplittedFileId(splittedFile.id)
        logger.debug(f"{len(createdFiles)} created files found by splittedFileId:{splittedFile.id}")
        zippedFiles.extend([file for file in createdFiles if file.encoding == "gzip" and file.mime == "video/vnd.dlna.mpeg-tts"])
        movieOrOtherFiles.extend([file for file in createdFiles if file.encoding != "gzip" or file.mime != "video/vnd.dlna.mpeg-tts"])

    zippedFileExists = False
    for file in zippedFiles:
        logger.debug(f"existance checking path:{file.file}")
        if nas.fileOrDirectoryExists(file.file):
            zippedFileExists = True

    if zippedFileExists:
        filePath = zippedFiles[0].file
        originalDirectory = filePath.parent
        basePath = originalDirectory.parent.parent
        indexDirectory = basePath.joinpath(targetName[0:1])
        targetDirectory = indexDirectory.joinpath(targetName)
        if not nas.fileOrDirectoryExists(indexDirectory):
            nas.createDirectory(indexDirectory)
        logger.info(f"you are moving original:{originalDirectory} to target:{targetDirectory}")
        for file in zippedFiles:
            logger.info(f"updating file original:{originalDirectory.joinpath(file.file.name)}, target:{targetDirectory.joinpath(file.file.name)}")
            if not nas.rename(originalDirectory.joinpath(file.file.name), targetDirectory.joinpath(file.file.name)):
                logger.error(f"rename failed. target already exist. you must do it on your hand. file:{file.file}")
            logger.info(f"updating file file:{targetDirectory.joinpath(file.file.name)}")
            createdFileRepository.updateFile(file.id, targetDirectory.joinpath(file.file.name))
    else:
        logger.info("gzip files in DB but not in nas.")
    
    movieOrOtherFilesExists = False
    for file in movieOrOtherFiles:
        logger.info(f"existance checking path:{file.file}")
        if nas.fileOrDirectoryExists(file.file):
            movieOrOtherFilesExists = True

    if movieOrOtherFilesExists:
        filePath = movieOrOtherFiles[0].file
        originalDirectory = filePath.parent
        basePath = originalDirectory.parent.parent
        indexDirectoryPath = basePath.joinpath(targetName[0:1])
        targetDirectory = indexDirectoryPath.joinpath(targetName)
        if not nas.fileOrDirectoryExists(targetDirectory):
            nas.createDirectory(targetDirectory)
        logger.info(f"you are moving original:{originalDirectory} to target:{targetDirectory}")
        for file in movieOrOtherFiles:
            logger.info(f"updating file original:{originalDirectory.joinpath(file.file.name)}, target:{targetDirectory.joinpath(file.file.name)}")
            if not nas.rename(originalDirectory.joinpath(file.file.name), targetDirectory.joinpath(file.file.name)):
                logger.error(f"rename failed. target already exist. you must do it on your hand. file:{file.file}")
            createdFileRepository.updateFile(file.id, targetDirectory.joinpath(file.file.name))
    else:
        logger.info("movie files in DB but not in nas.")
    logger.info("process finished.")

if __name__ == "__main__":
    main()
