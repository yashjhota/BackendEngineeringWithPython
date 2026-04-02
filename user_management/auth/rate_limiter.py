import redis
from fastapi import HTTPException, Request

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def rate_limit(request: Request, max_requests: int = 10, window: int = 60):
    # use IP address as key
    ip = request.client.host
    key = f"rate_limit:{ip}"

    # get current request count
    current = r.get(key)

    if current is None:
        # first request — start counter with TTL
        r.setex(key, window, 1)
    elif int(current) >= max_requests:
        raise HTTPException(
            status_code=429, detail=f"Too many requests. Try again in {window} seconds."
        )
    else:
        # increment counter
        r.incr(key)
