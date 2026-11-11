import os

import redis
from flask import Flask

app = Flask(__name__)

ENV_NAME = os.getenv("ENV_NAME", "local")

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    password=os.getenv("REDIS_PASSWORD") or None,
    socket_connect_timeout=2,
    socket_timeout=2,
    decode_responses=True,
)


@app.route("/")
def home():
    try:
        count = r.incr("visitors")
        return f"[{ENV_NAME}] Visitor number {count}\n"
    except redis.exceptions.RedisError as e:
        return f"Cannot reach Redis: {e}\n", 503


@app.route("/health")
def health():
    # Liveness: the web process is alive (does not depend on Redis)
    return "ok", 200


@app.route("/ready")
def ready():
    # Readiness: only receive traffic when Redis answers
    try:
        r.ping()
        return "ready", 200
    except redis.exceptions.RedisError:
        return "redis unavailable", 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
