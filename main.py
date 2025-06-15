import asyncio
import json
import os
import aiohttp
from downloader.executor import fetch_all_pages
from downloader.strategy.bibliocommons import BibliocommonsFetchStrategy
from downloader.notifier import notify
from downloader.save_handler import save_json
from models import init_db
from db_handler import save_activities_to_db
from config import PipelineConfig, MAX_CONCURRENCY

class Pipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.strategy = BibliocommonsFetchStrategy()
        self.config.strategy_name = self.strategy.__class__.__name__
        
        # 初始化目录
        self.raw_dir = self.config.raw_dir.format(strategy_name=self.config.strategy_name)
        self.parsed_dir = self.config.parsed_dir.format(strategy_name=self.config.strategy_name)
        self.detail_dir = self.config.detail_dir.format(strategy_name=self.config.strategy_name)
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.parsed_dir, exist_ok=True)
        os.makedirs(self.detail_dir, exist_ok=True)
        
        self.results = []
        self.valid_results = []
        self.parsed_events = []
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async def fetch(self):
        if not self.config.enable_fetch:
            return
            
        notify(f"开始抓取 {self.config.max_pages} 页...")
        self.results = await fetch_all_pages(self.strategy, max_pages=self.config.max_pages)
        self.valid_results = [r for r in self.results if isinstance(r, dict) and "events" in r]

    def parse(self):
        if not self.config.enable_parse:
            return
            
        self.parsed_events = []
        for idx, page_data in enumerate(self.valid_results, 1):
            if self.config.enable_save_raw:
                filename = os.path.join(self.raw_dir, f"raw_page_{idx}.json")
                save_json(page_data, filename, strategy_name=self.config.strategy_name)
            
            parsed = self.strategy.parse_page(page_data)
            self.parsed_events.extend(parsed)

    def save_parsed(self):
        if not self.config.enable_save_parsed:
            return
            
        parsed_filename = os.path.join(self.parsed_dir, "parsed_events.json")
        save_json(self.parsed_events, parsed_filename, strategy_name=self.config.strategy_name)

    def save_to_db(self):
        if not self.config.enable_db_save:
            return
            
        self.strategy.save_to_db(self.parsed_events)
        print("已成功落库！")

    def log_results(self):
        if not self.config.enable_logging:
            return
            
        print(f"解析后数据数量: {len(self.parsed_events)}")
        for i, event in enumerate(self.parsed_events[:2]):
            print(f"第{i+1}条: {event}")
        for i, event in enumerate(self.parsed_events):
            print(f"[{i}] url: {event.get('url')} | title: {event.get('title')} | start_time: {event.get('start_time')} | venue: {event.get('venue')}")

    async def download_detail_page(self, session, event):
        """下载单个详情页"""
        event_id = event.get('id')
        if not event_id:
            return
            
        url = event.get('url')
        if not url:
            return
            
        async with self.semaphore:
            try:
                async with session.get(url, headers=self.strategy.headers, cookies=self.strategy.cookies) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        filename = os.path.join(self.detail_dir, f"{event_id}.html")
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        notify(f"已保存详情页: {event_id}")
                    else:
                        notify(f"下载详情页失败 {event_id}: HTTP {response.status}")
            except Exception as e:
                notify(f"下载详情页失败 {event_id}: {str(e)}")

    async def download_all_details(self):
        """下载所有事件的详情页"""
        if not self.config.enable_detail_download or not self.parsed_events:
            return
            
        notify(f"开始下载 {len(self.parsed_events)} 个详情页...")
        async with aiohttp.ClientSession() as session:
            tasks = [self.download_detail_page(session, event) for event in self.parsed_events]
            await asyncio.gather(*tasks)
        notify("详情页下载完成")

    async def run(self):
        await self.fetch()
        self.parse()
        self.save_parsed()
        self.save_to_db()
        await self.download_all_details()
        self.log_results()
        
        notify(f"抓取完成，共 {len(self.valid_results)} 页，解析出 {len(self.parsed_events)} 条事件。")

if __name__ == "__main__":
    init_db()
    
    # 示例配置：只进行抓取和解析，不保存数据
    config = PipelineConfig(
        max_pages=1,
        enable_fetch=True,
        enable_parse=True,
        enable_save_raw=False,
        enable_save_parsed=False,
        enable_db_save=False,
        enable_logging=True
    )
    
    pipeline = Pipeline(config)
    asyncio.run(pipeline.run())