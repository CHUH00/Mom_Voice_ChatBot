import os
from rq import Worker, Queue, Connection
from redis import Redis
from backend.core.config import settings

redis_url = os.getenv("REDIS_URL", settings.REDIS_URL)
redis_conn = Redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(['default'])
        print("Starting RQ Worker...")
        worker.work()
