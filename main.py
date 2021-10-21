import sys, os
from pathlib import Path
from typing import Iterable

from main.command.dropChk import DropChk
from main.command.tsSplitter import TsSplitter
from main.command.amatsukazeAddTask import AmatsukazeAddTask

def processPath(path: Path):
    dropCheck = DropChk()
    tsSplitter = TsSplitter()
    amatsukazeAddTask = AmatsukazeAddTask()
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
        amatsukazeAddTask.amatsukaze(file)

def main():
    for input in sys.argv[1:]:
        processPath(Path(input))

if __name__ == "__main__":
    main()
