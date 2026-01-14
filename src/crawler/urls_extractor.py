""" Modulo para extraer el arbol de urls de una web """

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys, urllib.parse

import logging

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    encoding='utf-8',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_netloc(url):
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc

def is_file(url):
    # Check if a url is pointing to a file, like .docx, .pdf, etc.
    parsed = urllib.parse.urlparse(url)
    return parsed.path.endswith(('.docx', '.pdf', '.doc', '.zip', '.rar', '.7z'))

def normalize_url(url):
    url = url.replace('https://', '')
    if url.endswith('/'):
        url = url[:-1]
    
    url = url.replace('.', '_').replace('/', '_')
    return url


class URLCrawler:
    def __init__(self):
        self.base_url = ""
        self.base_netloc = ""
        self.urls = []

        self.seens = set()
        self.seens_lock = asyncio.Lock()

        self.concurrency = 3
        self.semaphore = asyncio.Semaphore(self.concurrency)
        self.base_delay = 1

    async def update_urls(self, url):
        async with self.seens_lock:
            norm = normalize_url(url)
            if norm not in self.seens:
                logging.info('Adding url: %s', url)
                self.seens.add(norm)
                self.urls.append(url)
                return True
        return False

    async def url_exists(self, url):
        async with self.seens_lock:
            return normalize_url(url) in self.seens

    def run(self, url):
        self.base_url = url
        self.base_netloc = get_netloc(url)
        asyncio.run(self.update_urls(url))
        asyncio.run(self._run())

    async def _run(self):
        async with aiohttp.ClientSession() as session:
            await self.crawl(session, self.base_url)

    async def crawl(self, session, url):
        html = await self.fetch(session, url)
        if not html:
            return

        soup = BeautifulSoup(html, 'html.parser')
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]

        tasks = []

        for link in links:
            if get_netloc(link) != self.base_netloc or is_file(link):
                continue
            added = await self.update_urls(link)
            if added:
                tasks.append(asyncio.create_task(self.crawl(session, link)))

        if tasks:
            await asyncio.gather(*tasks)

    async def fetch(self, session, url):
        
        async with self.semaphore:
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.text()
            except Exception:
                return None


if __name__ == "__main__":
    crawler = URLCrawler()
    crawler.run(url="https://www.lasmarias.com.ar")
    print(crawler.urls)

    # test url_parser:
    #print(parse_url("https://www.lasmarias.com.ar"))
