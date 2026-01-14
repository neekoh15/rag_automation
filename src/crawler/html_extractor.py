import asyncio
import aiohttp
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    encoding='utf-8',
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class HTMLExtractor:
    """Stream HTML content from URLs."""

    def __init__(self, concurrency=5, timeout=10):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.timeout = timeout

    async def stream_html(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.create_task(self._fetch(session, url))
                for url in urls
            ]

            for task in asyncio.as_completed(tasks):
                result = await task
                if result:
                    yield result  # (url, html)

    async def _fetch(self, session, url):
        async with self.semaphore:
            try:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status == 200:
                        html = await response.text()
                        logging.info(f"Fetched {url}")
                        return url, html
            except Exception as e:
                logging.warning(f"{url} → {e}")
        return None
