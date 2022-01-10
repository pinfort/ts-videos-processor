from enum import Enum, auto

class ExecutedFileStatus(Enum):
    REGISTERED = auto
    DROPCHECKED = auto
    """
    tsDropChk完了
    """
    SPLITTED = auto
    """
    tsSplitterが完了
    """
