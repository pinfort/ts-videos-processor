from enum import Enum, auto

class ProgramStatus(Enum):
    REGISTERED = auto()
    COMPLETED = auto()
    """
    完了
    """
    ERROR = auto()
