from dataclasses import dataclass
from pathlib import Path

@dataclass
class SplittedFileDto:
    id: int
    executedFileId: int
    file: Path
    size: int
    duration: float
