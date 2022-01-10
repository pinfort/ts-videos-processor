from enum import Enum, auto

class CreatedFileStatus(Enum):
    REGISTERED = auto()
    ENCODE_SUCCESS = auto()
    """
    エンコードが成功した
    """
    FILE_MOVED = auto()
    """
    ファイルはNASに移動された
    """
