from dataclasses import dataclass
from pathlib import Path

from main.enum.splittedFileStatus import SplittedFileStatus

@dataclass
class SplittedFileDto:
    id: int
    executedFileId: int
    file: Path
    size: int
    duration: float
    status: SplittedFileStatus
