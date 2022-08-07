import asyncio
import nats
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError
import time
import httpx
import os

async def main():
    nc = await nats.connect(os.getenv("NATS","nats://127.0.0.1:4222"))
    sub = await nc.subscribe("todos")
    while True:
      try:
        msg = await sub.next_msg(timeout=60)
        httpx.post(os.getenv("POSTURL",""), json={"user":"bot","message":msg.data.decode()})
      except nats.errors.TimeoutError:
        pass

if __name__ == '__main__':
    asyncio.run(main())
