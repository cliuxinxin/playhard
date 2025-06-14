import asyncio
import json
from downloader.executor import fetch_all_pages
from downloader.strategy.bibliocommons import BibliocommonsFetchStrategy

if __name__ == "__main__":
    strategy = BibliocommonsFetchStrategy()
    results = asyncio.run(fetch_all_pages(strategy, max_pages=5))

    valid_results = [r for r in results if isinstance(r, dict) and "events" in r]

    with open("raw_pages.json", "w", encoding="utf-8") as f:
        json.dump(valid_results, f, ensure_ascii=False, indent=2)

    print(f"成功抓取 {len(valid_results)} 页")