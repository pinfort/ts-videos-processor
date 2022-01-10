from enum import Enum, auto

class SplittedFileStatus(Enum):
    REGISTERED = auto
    """
    tsSplitterでファイルが生成された
    """
    COMPRESS_SAVED = auto
    """
    圧縮保存が完了。メインファイルの場合のみ
    """
    ENCODE_TASK_ADDED = auto
    """
    Amatsukazeにタスク登録された
    """
