from main.dto.executedFileDto import ExecutedFileDto
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip

from main.dto.splittedFileDto import SplittedFileDto
from main.dto.executedFileDto import ExecutedFileDto

class SplittedFileDtoConverter:
    @staticmethod
    def convert(filePath: Path, originalFile: ExecutedFileDto, id = None) -> SplittedFileDto:
        with VideoFileClip(str(filePath)) as video:
            return SplittedFileDto(
                id=1 if id is None else id,
                executedFileId=originalFile.id,
                file=filePath,
                size=filePath.stat().st_size,
                duration=video.duration
            )
