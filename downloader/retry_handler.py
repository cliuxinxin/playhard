import asyncio
import random

async def fetch_with_retry(fetch_func, retries=3, backoff=1):
    for i in range(retries):
        try:
            return await fetch_func()
        except Exception as e:
            if i < retries - 1:
                await asyncio.sleep(backoff * (2 ** i) + random.random())
            else:
                raise e