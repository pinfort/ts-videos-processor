import sys
from pathlib import Path
from redis.client import Redis as RedisClient

from main.component.redis import Redis
from main.config.redis import REDIS_PROCESS_TOPIC
from main.component.dependencyInjector import getInstance

def addQueue():
    """
    worker.pyが起動していることを前提に、Redis経由でキューを積むスクリプト。
    ファイルパスを引数に入れて起動することで、Redisにメッセージを送信する。worker.pyが監視していれば、そのメッセージを拾って処理してくれる。
    Redisの仕様上、workerが監視していない時に送ったメッセージは消えてしまうので注意が必要。
    """
    connection: RedisClient = getInstance(Redis).connection
    for input in sys.argv[1:]:
        connection.publish(REDIS_PROCESS_TOPIC, str(Path(input)))

if __name__ == "__main__":
    addQueue()
