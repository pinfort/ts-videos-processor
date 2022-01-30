from redis.client import Redis as RedisClient
from main.component.dependencyInjector import register

from main.config import redis

class Redis:
    connection: RedisClient

    def __init__(self):
        self.connect()

    def connect(self) -> None:
        self.connection = RedisClient(
            host=redis.REDIS_HOST,
            password=redis.REDIS_PASSWORD,
        )

    def disConnect(self) -> None:
        if self.connection is not None:
            self.connection.close()

@register
def registerRedis() -> Redis:
    return Redis()

registerRedis()
