from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

@dataclass
class ExecutedFileDto:
    id: int
    file: Path
    drops: int
    size: int
    recorded_at: datetime
    channel: str
    channelName: str
    title: str
