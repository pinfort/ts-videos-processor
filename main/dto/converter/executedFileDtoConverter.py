from pathlib import Path
from main.dto.executedFileDto import ExecutedFileDto


from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip

from main.component.fileName import FileName

class ExecutedFileDtoConverter:
    @staticmethod
    def convert(filePath: Path, drops: int, id = None) -> ExecutedFileDto:
        fileName: FileName = FileName.fromPath(filePath)

        with VideoFileClip(str(filePath)) as video:
            return ExecutedFileDto(
                id=1 if id is None else id,
                file=filePath,
                drops=drops,
                size=filePath.stat().st_size,
                recorded_at=fileName.recorded_at,
                channel=fileName.channel,
                channelName=fileName.channelName,
                duration=video.duration,
                title=fileName.title
            )
