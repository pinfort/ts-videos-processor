from pathlib import Path
from redis.client import PubSub
from logging import getLogger, Logger, config
import json

from tsVideosProcessor import TsVideosProcessor
from main.component.redis import Redis
from main.config.redis import REDIS_PROCESS_TOPIC

def worker():
    with open("log_config.json", 'r') as f:
        config.dictConfig(json.load(f))
    logger: Logger = getLogger(__name__)
    redis: Redis = Redis()
    processor: TsVideosProcessor = TsVideosProcessor()

    pubsub: PubSub  = redis.connection.pubsub()
    pubsub.subscribe(REDIS_PROCESS_TOPIC)

    for message in pubsub.listen():
        logger.info(f"received data {message}")
        if message["type"] != "message":
            continue
        data: bytes = message["data"]
        path: Path = Path(data.decode("utf-8"))
        processor.processPath(path)

if __name__ == "__main__":
    worker()
