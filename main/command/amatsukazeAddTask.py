import re

from main.dto.splittedFileDto import SplittedFileDto
from main.dto.executedFileDto import ExecutedFileDto
from pathlib import Path
from logging import Logger, getLogger
from main.repository.executedFileRepository import ExecutedFileRepository

from main.component.executer import executeCommand
from main.config import amatsukaze

class AmatsukazeAddTask():
    APPLICATION_PATH: str = str(Path(__file__).parent.parent.parent.joinpath("libraries\\Amatsukaze\\exe_files\\AmatsukazeAddTask.exe").absolute())
    AMATSUKAZE_ROOT: str = str(Path(__file__).parent.parent.parent.joinpath("libraries\\Amatsukaze").absolute())
    OPTIONS: list[str] = ["--priority", "3", "--no-move"]
    logger: Logger = getLogger(__name__)
    regex: str = r"#[0-9]{1,3}-#[0-9]{1,3}"
    executedFileRepository = ExecutedFileRepository()

    def decideUseJLFile(self, executedFile: ExecutedFileDto) -> str:
        # AT-Xの一挙放送の時だけ、mp4ファイルを分割するようなprofileに切り替える
        if executedFile.channelName == "ＡＴ－Ｘ" and executedFile.duration > 10800 and bool(re.search(self.regex, executedFile.title)):
            return "30fps_light_atx_div"
        return "30fps_light"

    def amatsukaze(self, splittedFile: SplittedFileDto):
        executedFile = self.executedFileRepository.find(splittedFile.executedFileId)
        profile: str = self.decideUseJLFile(executedFile)
        outputPath: Path = splittedFile.file.parent.joinpath("encoded") # 入力ファイルのある場所のencodedフォルダに出力する
        self.addTask(splittedFile.file, outputPath, amatsukaze.AMATSUKAZE_HOST, amatsukaze.AMATSUKAZE_PORT, profile)

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

    def rollback(self, splittedFile: SplittedFileDto) -> None:
        self.logger.warn("amatsukazeAddTask rollbacking. nothing todo.")
