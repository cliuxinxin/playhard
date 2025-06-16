import asyncio
import aiohttp
from config import MAX_CONCURRENCY, MAX_RETRIES, RETRY_BACKOFF
from downloader.retry_handler import fetch_with_retry
from downloader.notifier import notify

semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

async def bounded_fetch(session, url, headers, cookies, params, page):
    async with semaphore:
        try:
            async with session.get(url, headers=headers, cookies=cookies, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return data
        except Exception as e:
            notify(f"下载第 {page} 页失败: {e}")
            raise

async def fetch_all_pages(fetch_strategy, max_pages=5):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page in range(1, max_pages + 1):
            task = fetch_with_retry(
                lambda: bounded_fetch(
                    session,
                    fetch_strategy.url,
                    fetch_strategy.headers,
                    fetch_strategy.cookies,
                    fetch_strategy.build_params(page),
                    page
                ),
                retries=MAX_RETRIES,
                backoff=RETRY_BACKOFF
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results