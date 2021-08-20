import sys
from pathlib import Path
from typing import Iterable

from command.dropChk import DropChk
from command.tsSplitter import TsSplitter

if __name__ == "__main__":
    dropCheck = DropChk()
    tsSplitter = TsSplitter()

    path: Path = Path(sys.argv[1])
    print(path)
    files: Iterable[Path]

    if(not path.exists):
        print("path not exist")
        sys.exit(1)
    
    if(path.is_dir()):
        print("given path is directory")
        files = path.glob("*.m2ts")
    else:
        print("given path is file")
        files = list()
        files.append(path)

    for file in files:
        print(f"processing file:{file}")
        dropCheck.dropChk(file)
        tsSplitter.tsSplitter(file)
