import asyncio
import json
import os
from downloader.executor import fetch_all_pages
from downloader.strategy.bibliocommons import BibliocommonsFetchStrategy
from downloader.notifier import notify
from downloader.save_handler import save_json

if __name__ == "__main__":
    strategy = BibliocommonsFetchStrategy()
    max_pages = 5
    strategy_name = strategy.__class__.__name__
    output_dir = os.path.join("downloads", strategy_name)
    os.makedirs(output_dir, exist_ok=True)

    notify(f"开始抓取 {max_pages} 页...")
    results = asyncio.run(fetch_all_pages(strategy, max_pages=max_pages))

    valid_results = [r for r in results if isinstance(r, dict) and "events" in r]

    for idx, page_data in enumerate(valid_results, 1):
        filename = os.path.join(output_dir, f"raw_page_{idx}.json")
        save_json(page_data, filename, strategy_name=strategy_name)

    print(f"成功抓取 {len(valid_results)} 页")
    notify(f"抓取完成，共 {len(valid_results)} 页。")