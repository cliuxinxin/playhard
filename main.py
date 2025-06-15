import asyncio
import json
import os
from downloader.executor import fetch_all_pages
from downloader.strategy.bibliocommons import BibliocommonsFetchStrategy
from downloader.notifier import notify
from downloader.save_handler import save_json
from models import init_db
from db_handler import save_activities_to_db

if __name__ == "__main__":
    init_db()
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

    # 日志：打印解析后数据数量和前两条内容
    print(f"解析后数据数量: {len(parsed_events)}")
    for i, event in enumerate(parsed_events[:2]):
        print(f"第{i+1}条: {event}")
    # 日志：打印每条数据的url和唯一性关键字段
    for i, event in enumerate(parsed_events):
        print(f"[{i}] url: {event.get('url')} | title: {event.get('title')} | start_time: {event.get('start_time')} | venue: {event.get('venue')}")

    # 落库前做字段过滤
    ORM_FIELDS = [
        "title", "city", "venue", "address", "start_time", "end_time", "age_range",
        "tags", "url", "is_free", "requires_registration", "source", "last_updated"
    ]
    def filter_event_fields(event):
        return {k: event.get(k) for k in ORM_FIELDS}
    filtered_events = [filter_event_fields(e) for e in parsed_events]

    # 落库
    save_activities_to_db(filtered_events)
    print("已成功落库！")
    notify(f"抓取完成，共 {len(valid_results)} 页，解析出 {len(parsed_events)} 条事件。")