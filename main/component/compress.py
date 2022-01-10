import gzip
from logging import Logger, getLogger
from pathlib import Path

class Compress:
    logger: Logger

    def __init__(self) -> None:
        self.logger = getLogger(__name__)

    def compress(self, original_path: Path, compressed_path: Path, force: bool = False) -> bool:
        if compressed_path.exists() and not force:
            self.logger.error("compress target file already exist. if allow overwrite it, set force = true.")
            return False
        with gzip.open(compressed_path, mode='wb') as target:
            self.logger.info(f"compressing... original:{original_path}, target:{compressed_path}")
            target.write(original_path.read_bytes())
        return True