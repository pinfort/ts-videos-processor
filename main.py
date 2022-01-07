import sys
from pathlib import Path
from tsVideosProcessor import TsVideosProcessor

def main():
    """
    コマンドラインから処理を行わせるときに使うスクリプト。引数に任意の個数ファイルパスを渡すことで処理を行わせることができる。
    """
    tsVideosProcessor = TsVideosProcessor()
    for input in sys.argv[1:]:
        tsVideosProcessor.processPath(Path(input))

if __name__ == "__main__":
    main()
