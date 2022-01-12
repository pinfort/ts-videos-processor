import sys
import json
from pathlib import Path
from redis.client import Redis as RedisClient
from logging import Logger, config, getLogger

from main.component.redis import Redis
from main.config.redis import REDIS_PROCESS_TOPIC

def addQueue():
    """
    worker.pyが起動していることを前提に、Redis経由でキューを積むスクリプト。
    ファイルパスを引数に入れて起動することで、Redisにメッセージを送信する。worker.pyが監視していれば、そのメッセージを拾って処理してくれる。
    Redisの仕様上、workerが監視していない時に送ったメッセージは消えてしまうので注意が必要。
    送信するパスは、与えられたパスそのものではなく、与えられたパスの子ディレクトリすべて。孫以下は含まれない。
    """
    with open("log_config.json", 'r') as f:
        config.dictConfig(json.load(f))
        logger = getLogger(__name__)
    connection: RedisClient = Redis().connection
    for input in sys.argv[1:]:
        path = Path(input)
        for p in path.iterdir():
            if p.is_dir():
                logger.info(f"publishing path path:{p}")
                connection.publish(REDIS_PROCESS_TOPIC, str(p))

if __name__ == "__main__":
    addQueue()
