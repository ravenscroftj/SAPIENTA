import dramatiq
import os
import minio
from dotenv import load_dotenv
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results.backends import RedisBackend
from dramatiq.results import Results

load_dotenv()

redis_broker = RedisBroker(host=os.environ.get("REDIS_HOST", 'localhost'), 
    password=os.environ.get("REDIS_PASSWORD", None))

result_backend = RedisBackend(host=os.environ.get("REDIS_HOST", 'localhost'), 
    password=os.environ.get("REDIS_PASSWORD", None))

redis_broker.add_middleware(Results(backend=result_backend))

dramatiq.set_broker(redis_broker)

def get_minio_client() -> minio.Minio:

    use_ssl = os.environ.get("MINIO_USE_SSL", "localhost:9000") == '1'

    return minio.Minio(os.environ.get("MINIO_HOST", "localhost:9000"),
        access_key=os.environ.get("MINIO_ACCESS_KEY",""),
        secret_key=os.environ.get("MINIO_SECRET_KEY",""), secure=use_ssl)