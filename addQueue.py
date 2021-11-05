import sys
from pathlib import Path
from redis.client import Redis as RedisClient

from main.component.redis import Redis
from main.config.redis import REDIS_PROCESS_TOPIC

def addQueue():
    connection: RedisClient = Redis().connection
    for input in sys.argv[1:]:
        connection.publish(REDIS_PROCESS_TOPIC, str(Path(input)))

if __name__ == "__main__":
    addQueue()
