import asyncio
import json
import os
from downloader.executor import fetch_all_pages
from downloader.strategy.bibliocommons import BibliocommonsFetchStrategy
from downloader.notifier import notify
from downloader.save_handler import save_json

if __name__ == "__main__":
    strategy = BibliocommonsFetchStrategy()
    max_pages = 2
    strategy_name = strategy.__class__.__name__
    # 新增原始和解析数据的文件夹
    raw_dir = os.path.join("downloads", strategy_name, "raw")
    parsed_dir = os.path.join("downloads", strategy_name, "parsed")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(parsed_dir, exist_ok=True)

    notify(f"开始抓取 {max_pages} 页...")
    results = asyncio.run(fetch_all_pages(strategy, max_pages=max_pages))

    valid_results = [r for r in results if isinstance(r, dict) and "events" in r]

    # 解析所有页面
    parsed_events = []
    for idx, page_data in enumerate(valid_results, 1):
        filename = os.path.join(raw_dir, f"raw_page_{idx}.json")
        save_json(page_data, filename, strategy_name=strategy_name)
        # 解析
        parsed = strategy.parse_page(page_data)
        parsed_events.extend(parsed)

    # 保存解析后的数据
    parsed_filename = os.path.join(parsed_dir, "parsed_events.json")
    save_json(parsed_events, parsed_filename, strategy_name=strategy_name)

    print(f"成功抓取 {len(valid_results)} 页, 解析出 {len(parsed_events)} 条事件")
    notify(f"抓取完成，共 {len(valid_results)} 页，解析出 {len(parsed_events)} 条事件。")