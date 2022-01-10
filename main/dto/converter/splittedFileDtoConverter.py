from main.dto.executedFileDto import ExecutedFileDto
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip

from main.dto.splittedFileDto import SplittedFileDto
from main.dto.executedFileDto import ExecutedFileDto
from main.enum.splittedFileStatus import SplittedFileStatus

class SplittedFileDtoConverter:
    @staticmethod
    def convert(filePath: Path, originalFile: ExecutedFileDto, id = None) -> SplittedFileDto:
        duration: int = 0

        try:
            with VideoFileClip(str(filePath)) as video:
                duration = video.duration
        except Exception as e:
            print(e)

        return SplittedFileDto(
            id=1 if id is None else id,
            executedFileId=originalFile.id,
            file=filePath,
            size=filePath.stat().st_size,
            duration=duration,
            status=SplittedFileStatus.REGISTERED
        )
