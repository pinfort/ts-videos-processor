from pathlib import Path
import glob

from main.dto.splittedFileDto import SplittedFileDto
from main.dto.executedFileDto import ExecutedFileDto
from main.component.database import Database
from main.component.executer import executeCommand
from main.repository.splittedFileRepository import SplittedFileRepository
from main.repository.executedFileRepository import ExecutedFileRepository

class TsSplitter():
    APPLICATION_PATH: str = str(Path(__file__).parent.parent.parent.joinpath("libraries\\TsSplitter128\\TsSplitter.exe").absolute())
    OPTIONS = "-SD -EIT -1SEG"
    WORK_DIRECTORY = "tssplitter"
    splittedFileRepository: SplittedFileRepository
    executedFileRepository: ExecutedFileRepository
    database: Database

    def __init__(self):
        self.database = Database()
        self.splittedFileRepository = SplittedFileRepository(self.database)
        self.executedFileRepository = ExecutedFileRepository(self.database)

    def tsSplitter(self, path: Path):
        if(not path.exists()):
            raise Exception(f"file not found path:{path}")
        outputPath = path.parent.joinpath(TsSplitter.WORK_DIRECTORY)
        if(not outputPath.exists()):
            outputPath.mkdir()
        originalFile: ExecutedFileDto = self.executedFileRepository.findByFile(path)
        existingFiles = self.findFiles(originalFile)
        if(len(existingFiles) > 0):
            print(f"ERROR: splitted file already exist! original:{originalFile}")
            for file in existingFiles:
                print(file)
            raise Exception("splitted file already exist!")

        command = TsSplitter.APPLICATION_PATH + " " + TsSplitter.OPTIONS + " -OUT \"" + str(outputPath.absolute()) + "\" -SEP \"" + str(path.absolute()) + "\""
        print(f"tsSpliter starting with command:{command}")
        try:
            exitCode: int = executeCommand(command)
            if(exitCode != 0):
                print("splitting file become error!")
                raise Exception("splitting file become error!")
        except:
            pass

        files = self.findFiles(originalFile)
        if(len(files) == 0):
            raise Exception("splitted file not found")

        for file in files:
            print(f"found splitted file. path:{file}")
            self.splittedFileRepository.insert(file)
            print(f"""
            File Splitting executed.
            id={file.id},
            executeFileId={file.executedFileId},
            file={file.file},
            size={file.size}
            """)

    def findFiles(self, originalFile:ExecutedFileDto) -> list[SplittedFileDto]:
        files: list[SplittedFileDto] = list()
        directory = originalFile.file.parent.joinpath(TsSplitter.WORK_DIRECTORY)
        pattern = glob.escape(originalFile.file.stem) + "*.m2ts"
        print(f"search pattern {pattern}")
        for file in directory.glob(pattern):
            files.append(
                SplittedFileDto(
                    id=1,
                    executedFileId=originalFile.id,
                    file=file,
                    size=file.stat().st_size
                )
            )
        return files