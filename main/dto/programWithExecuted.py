from dataclasses import dataclass
from datetime import datetime

from main.enum.programStatus import ProgramStatus


@dataclass
class ProgramWithExecuted:
    id: int
    name: str
    executedFileId: int
    status: ProgramStatus
    drops: int
    size: int
    recorded_at: datetime
    channel: str
    channelName: str
    title: str
    duration: float
