import redis
import json
from typing import Optional

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def get_cache(key: str) -> Optional[dict]:
    data = r.get(key)
    if data:
        return json.loads(data)
    return None


def set_cache(key: str, value: dict, ttl: int = 300):
    r.setex(key, ttl, json.dumps(value))


def delete_cache(key: str):
    r.delete(key)
