import asyncio
import os

from src.utils import get_hash

from src.crawler.urls_extractor import URLCrawler
from src.crawler.html_extractor import HTMLExtractor
from src.crawler.markdown_parser import MarkdownParser


import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    encoding='utf-8',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Pipeline:
    def __init__(self, base_url):
        self.base_url = base_url
        self.urls = None
        self.temp_output = ".src/crawler/output"

        self.url_crawler = URLCrawler()
        self.html_extractor = HTMLExtractor()
        self.markdown_parser = MarkdownParser()

    def run(self):
        self.url_crawler.run(self.base_url)

        asyncio.run(self._run_async())

    async def _run_async(self):
        async for url, html in self.html_extractor.stream_html(
            self.url_crawler.urls
        ):
            md = self.markdown_parser.parse(html)

            md_hash = get_hash(md)
            url_hash = get_hash(url)

            self.save_md(md, md_hash, url_hash)
            
            
    def save_md(self, md, md_hash, url_hash):

        updating = False


        # check if url_hash exists
        if os.path.exists(f"{self.temp_output}/{url_hash}.md"):
            # if exists, check if the hash of the content is the same as the hash of the new md
            with open(f"{self.temp_output}/{url_hash}.md", "r", encoding="utf-8") as f:
                content = f.read()
                if get_hash(content) == md_hash:
                    logging.info(f"Skipping {url_hash}.md - No changes detected")
                    return
                else:
                    updating = True
        
        if not os.path.exists(self.temp_output):
            os.makedirs(self.temp_output)

        with open(f"{self.temp_output}/{url_hash}.md", "w", encoding="utf-8") as f:
            logging.info(f"{"Saving" if not updating else "Updating"} {url_hash}.md")
            f.write(md)

if __name__ == "__main__":
    pipeline = Pipeline("https://www.lasmarias.com.ar")
    pipeline.run()