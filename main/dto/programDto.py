from dataclasses import dataclass

from main.enum.programStatus import ProgramStatus

@dataclass
class ProgramDto:
    id: int
    name: str
    executedFileId: int
    status: ProgramStatus
