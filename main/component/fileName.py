from datetime import datetime

class FileName:
    recorded_at: datetime
    channel: str
    title: str
    channelName: str

    def __init__(self, fileName: str) -> None:
        fileNameParts: list[str] = fileName.split("]")
        self.recorded_at = datetime.strptime(fileNameParts[0][1:], "%y%m%d-%H%M")
        self.channel = fileNameParts[1][1:]
        self.channelName = fileNameParts[2][1:]
        self.title = "]".join(fileNameParts[3:])
