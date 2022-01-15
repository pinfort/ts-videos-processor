from multiprocessing.pool import ApplyResult
from pathlib import Path
from multiprocessing import Pool, TimeoutError
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
            with Pool(processes=1) as p:
                applyResult: ApplyResult = p.apply_async(ExecutedFileDtoConverter.getDuration, (filePath,))
                duration = applyResult.get(timeout=60)
        except TimeoutError as e:
            raise e

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

    @staticmethod
    def getDuration(filePath: Path) -> int:
        """
        動画ファイルの再生時間取得。
        dropの多いファイルを与えるとフリーズすることがあるので、別関数に分けてタイムアウトを設定して呼び出す。
        """
        try:
            with VideoFileClip(str(filePath)) as video:
                return video.duration
        except Exception as e:
            print(e)
            return 0
