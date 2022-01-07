from dataclasses import dataclass
from pathlib import Path
from typing import Union

@dataclass
class CreatedFileDto:
    id: int
    splittedFileId: int
    file: Path
    size: int
    mime: Union[str, None]
    encoding: Union[str, None]
