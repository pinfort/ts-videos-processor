from main.dto.splittedFileDto import SplittedFileDto
from pathlib import Path
from logging import Logger, getLogger

from main.component.executer import executeCommand

class AmatsukazeAddTask():
    APPLICATION_PATH: str = str(Path(__file__).parent.parent.parent.joinpath("libraries\\Amatsukaze\\exe_files\\AmatsukazeAddTask.exe").absolute())
    AMATSUKAZE_ROOT: str = str(Path(__file__).parent.parent.parent.joinpath("libraries\\Amatsukaze").absolute())
    OPTIONS: list[str] = ["--priority", "3", "--no-move"]
    logger: Logger

    def __init__(self) -> None:
        self.logger = getLogger(__name__)

    def amatsukaze(self, splittedFile: SplittedFileDto):
        outputPath: Path = splittedFile.file.parent.joinpath("encoded") # 入力ファイルのある場所のencodedフォルダに出力する
        self.addTask(splittedFile.file, outputPath)

    def addTask(self, filePath: Path, outputPath: Path, host: str = "localhost", port: int = 32768, profile_name: str = "30fps_light") -> None:
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
        self.logger.info(f"""
        executing Amatsukaze command.
        command: {" ".join(command)}
        """)

        executeCommand(commands=command)
