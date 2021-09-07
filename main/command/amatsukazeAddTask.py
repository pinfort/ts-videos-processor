from main.dto.splittedFileDto import SplittedFileDto
from main.dto.executedFileDto import ExecutedFileDto
from pathlib import Path

from main.component.executer import executeCommand
from main.component.database import Database
from main.repository.executedFileRepository import ExecutedFileRepository
from main.component.mainSplittedFileFinder import MainSplittedFileFinder

class AmatsukazeAddTask():
    APPLICATION_PATH: str = str(Path(__file__).parent.parent.parent.joinpath("libraries\\Amatsukaze\\exe_files\\AmatsukazeAddTask.exe").absolute())
    AMATSUKAZE_ROOT: str = str(Path(__file__).parent.parent.parent.joinpath("libraries\\Amatsukaze").absolute())
    OPTIONS: list[str] = ["--priority", "3", "--no-move"]
    executedFileRepository: ExecutedFileRepository
    mainSplittedFileFinder: MainSplittedFileFinder
    database: Database

    def __init__(self) -> None:
        self.database = Database()
        self.executedFileRepository = ExecutedFileRepository(self.database)
        self.mainSplittedFileFinder = MainSplittedFileFinder(self.database)


    def amatsukaze(self, executedFilePath: Path):
        executedFile: ExecutedFileDto = self.executedFileRepository.findByFile(executedFilePath)
        splittedFile: SplittedFileDto = self.mainSplittedFileFinder.splittedFileFromExecutedFile(executedFile)
        outputPath: Path = splittedFile.file.parent.joinpath("encoded") # 入力ファイルのある場所のencodedフォルダに出力する
        self.addTask(splittedFile.file, outputPath)

    def addTask(self, filePath: Path, outputPath: Path, host: str = "localhost", port: int = 32768, profile_name: str = "デフォルトのコピー") -> None:
        if(not outputPath.exists()):
            outputPath.mkdir()

        command: list[str] = list()
        command.append(self.APPLICATION_PATH)
        command.append("-f")
        command.append(str(filePath))
        command.append("-ip")
        command.append(host)
        command.append("-p")
        command.append(str(port))
        command.append("-o")
        command.append(str(outputPath))
        command.append("-s")
        command.append(profile_name)
        command.extend(self.OPTIONS)
        print(f"""
        executing Amatsukaze command.
        command: {" ".join(command)}
        """)

        executeCommand(commands=command)
