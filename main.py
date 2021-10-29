import sys
from pathlib import Path
from tsVideosProcessor import TsVideosProcessor

def main():
    tsVideosProcessor = TsVideosProcessor()
    for input in sys.argv[1:]:
        tsVideosProcessor.processPath(Path(input))

if __name__ == "__main__":
    main()
