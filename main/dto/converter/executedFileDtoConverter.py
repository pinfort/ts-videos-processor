from pathlib import Path
from main.dto.executedFileDto import ExecutedFileDto


from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip

from main.component.fileName import FileName
from main.enum.executedFileStatus import ExecutedFileStatus

class ExecutedFileDtoConverter:
    @staticmethod
    def convert(filePath: Path, drops: int, id = None) -> ExecutedFileDto:
        fileName: FileName = FileName.fromPath(filePath)
        duration: int = 0

        try:
            with VideoFileClip(str(filePath)) as video:
                duration = video.duration
        except Exception as e:
            print(e)

        return ExecutedFileDto(
            id=1 if id is None else id,
            file=filePath,
            drops=drops,
            size=filePath.stat().st_size,
            recorded_at=fileName.recorded_at,
            channel=fileName.channel,
            channelName=fileName.channelName,
            duration=duration,
            title=fileName.title,
            status=ExecutedFileStatus.DROPCHECKED,
        )
